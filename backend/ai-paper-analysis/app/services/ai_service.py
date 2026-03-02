"""
AI 模型服务模块
使用 Qwen3-0.5B 模型提供题目分析和相似题生成功能
"""

import json
import logging
import re
import threading
from typing import Optional, Dict, Any, List
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.config import settings
from app.utils.prompts import (
    get_question_analysis_prompt,
    get_similar_question_prompt,
    get_batch_analysis_prompt,
    get_knowledge_extraction_prompt,
)

logger = logging.getLogger(__name__)


class AIModelService:
    """
    AI 模型服务类
    实现 Qwen3-0.5B 模型的懒加载和推理功能
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """单例模式确保只有一个模型实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化模型服务"""
        if self._initialized:
            return

        self._model = None
        self._tokenizer = None
        self._device = None
        self._model_loaded = False
        self._load_error = None
        self._initialized = True

        logger.info("AIModelService instance created")

    def _get_device(self) -> str:
        """
        获取模型运行设备

        Returns:
            设备名称 (cuda/cpu)
        """
        device_setting = settings.MODEL_DEVICE.lower()

        if device_setting == "auto":
            if torch.cuda.is_available():
                device = "cuda"
                logger.info(f"CUDA available, using GPU: {torch.cuda.get_device_name(0)}")
            else:
                device = "cpu"
                logger.info("CUDA not available, using CPU")
        elif device_setting == "cuda":
            if torch.cuda.is_available():
                device = "cuda"
            else:
                logger.warning("CUDA requested but not available, falling back to CPU")
                device = "cpu"
        else:
            device = "cpu"

        return device

    def _validate_model_path(self) -> bool:
        """
        验证模型路径是否存在且包含必要文件

        Returns:
            路径是否有效
        """
        model_path = Path(settings.QWEN_MODEL_PATH)

        if not model_path.exists():
            logger.error(f"Model path does not exist: {model_path}")
            return False

        # 检查必要文件
        required_files = ["config.json", "tokenizer.json"]
        for file_name in required_files:
            file_path = model_path / file_name
            if not file_path.exists():
                logger.error(f"Required file not found: {file_path}")
                return False

        # 检查模型文件（safetensors 或 bin）
        model_files = list(model_path.glob("*.safetensors")) + list(model_path.glob("*.bin"))
        if not model_files:
            logger.error("No model weight files found (safetensors or bin)")
            return False

        logger.info(f"Model path validated: {model_path}")
        return True

    def load_model(self) -> bool:
        """
        加载模型和分词器

        Returns:
            是否加载成功
        """
        if self._model_loaded:
            logger.info("Model already loaded")
            return True

        if self._load_error:
            logger.warning(f"Previous load failed: {self._load_error}")
            return False

        try:
            logger.info("Starting model loading...")

            # 验证模型路径
            if not self._validate_model_path():
                raise ValueError(f"Invalid model path: {settings.QWEN_MODEL_PATH}")

            # 获取设备
            self._device = self._get_device()

            # 加载分词器
            logger.info("Loading tokenizer...")
            self._tokenizer = AutoTokenizer.from_pretrained(
                settings.QWEN_MODEL_PATH,
                trust_remote_code=True,
                use_fast=False
            )

            # 确保 pad_token 存在
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
                logger.info("Set pad_token to eos_token")

            # 加载模型
            logger.info("Loading model...")
            self._model = AutoModelForCausalLM.from_pretrained(
                settings.QWEN_MODEL_PATH,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self._device == "cuda" else torch.float32,
                device_map=self._device if self._device == "cuda" else None,
                low_cpu_mem_usage=True
            )

            # 如果是 CPU，手动移动模型
            if self._device == "cpu":
                self._model = self._model.to("cpu")

            # 设置为评估模式
            self._model.eval()

            self._model_loaded = True
            logger.info(f"Model loaded successfully on {self._device}")

            # 记录模型信息
            total_params = sum(p.numel() for p in self._model.parameters())
            logger.info(f"Total parameters: {total_params:,}")

            return True

        except Exception as e:
            self._load_error = str(e)
            logger.error(f"Failed to load model: {e}", exc_info=True)
            return False

    def unload_model(self):
        """
        卸载模型释放内存
        """
        if self._model is not None:
            del self._model
            self._model = None

        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None

        if self._device == "cuda":
            torch.cuda.empty_cache()

        self._model_loaded = False
        self._load_error = None
        logger.info("Model unloaded and memory released")

    def is_model_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self._model_loaded

    def get_model_status(self) -> Dict[str, Any]:
        """
        获取模型状态信息

        Returns:
            模型状态字典
        """
        return {
            "loaded": self._model_loaded,
            "device": self._device,
            "model_path": settings.QWEN_MODEL_PATH,
            "error": self._load_error,
            "cuda_available": torch.cuda.is_available(),
        }

    def _generate(self, prompt: str, max_new_tokens: Optional[int] = None) -> str:
        """
        生成文本

        Args:
            prompt: 输入提示词
            max_new_tokens: 最大生成 token 数

        Returns:
            生成的文本
        """
        if not self._model_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load model")

        max_tokens = max_new_tokens or settings.MAX_NEW_TOKENS

        # 编码输入
        inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)

        # 移动到正确的设备
        if self._device == "cuda":
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # 生成
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=settings.TEMPERATURE,
                top_p=settings.TOP_P,
                do_sample=True,
                pad_token_id=self._tokenizer.pad_token_id,
                eos_token_id=self._tokenizer.eos_token_id,
                repetition_penalty=1.1,
            )

        # 解码输出
        generated_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)

        # 移除原始提示词部分
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()

        return generated_text

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取 JSON 对象

        Args:
            text: 包含 JSON 的文本

        Returns:
            解析后的字典，如果解析失败返回 None
        """
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 块
        json_patterns = [
            r'\{[\s\S]*\}',  # 匹配整个 JSON 对象
            r'```json\s*([\s\S]*?)\s*```',  # 匹配 markdown 代码块
            r'```\s*([\s\S]*?)\s*```',  # 匹配普通代码块
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    # 如果是代码块，match 就是内容
                    json_str = match if isinstance(match, str) else match[0]
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue

        logger.warning(f"Failed to extract JSON from text: {text[:200]}...")
        return None

    def analyze_questions(self, text: str) -> Dict[str, Any]:
        """
        分析题目

        Args:
            text: 题目文本

        Returns:
            分析结果字典
        """
        try:
            prompt = get_question_analysis_prompt(text)
            logger.info("Analyzing question...")

            response = self._generate(prompt)
            logger.debug(f"Raw response: {response[:500]}...")

            result = self._extract_json(response)

            if result is None:
                return {
                    "success": False,
                    "error": "Failed to parse analysis result",
                    "raw_response": response,
                }

            return {
                "success": True,
                "data": result,
            }

        except Exception as e:
            logger.error(f"Error analyzing question: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def generate_similar_questions(
        self,
        question: str,
        count: int = 3,
        question_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        knowledge_points: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        生成相似题目

        Args:
            question: 原题目
            count: 生成数量
            question_type: 题目类型（可选，如果不提供会自动分析）
            difficulty: 难度（可选）
            knowledge_points: 知识点列表（可选）

        Returns:
            包含相似题目列表的字典
        """
        try:
            # 如果没有提供题目信息，先分析原题目
            if not all([question_type, difficulty, knowledge_points]):
                analysis_result = self.analyze_questions(question)
                if analysis_result.get("success"):
                    data = analysis_result.get("data", {})
                    question_type = question_type or data.get("question_type", "未知题型")
                    difficulty = difficulty or data.get("difficulty", "中等")
                    knowledge_points = knowledge_points or data.get("main_knowledge_points", [])
                else:
                    question_type = question_type or "未知题型"
                    difficulty = difficulty or "中等"
                    knowledge_points = knowledge_points or []

            prompt = get_similar_question_prompt(
                original_question=question,
                question_type=question_type,
                difficulty=difficulty,
                knowledge_points=knowledge_points,
                count=count
            )

            logger.info(f"Generating {count} similar questions...")
            response = self._generate(prompt, max_new_tokens=4096)
            logger.debug(f"Raw response: {response[:500]}...")

            result = self._extract_json(response)

            if result is None:
                return {
                    "success": False,
                    "error": "Failed to parse generated questions",
                    "raw_response": response,
                }

            return {
                "success": True,
                "data": result,
                "original_question": question,
                "question_type": question_type,
                "difficulty": difficulty,
            }

        except Exception as e:
            logger.error(f"Error generating similar questions: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def analyze_paper(self, paper_text: str) -> Dict[str, Any]:
        """
        批量分析试卷

        Args:
            paper_text: 试卷文本

        Returns:
            整体分析结果
        """
        try:
            prompt = get_batch_analysis_prompt(paper_text)
            logger.info("Analyzing paper...")

            response = self._generate(prompt, max_new_tokens=4096)
            logger.debug(f"Raw response: {response[:500]}...")

            result = self._extract_json(response)

            if result is None:
                return {
                    "success": False,
                    "error": "Failed to parse paper analysis result",
                    "raw_response": response,
                }

            return {
                "success": True,
                "data": result,
            }

        except Exception as e:
            logger.error(f"Error analyzing paper: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def extract_knowledge_points(self, question_text: str) -> Dict[str, Any]:
        """
        提取知识点

        Args:
            question_text: 题目文本

        Returns:
            知识点提取结果
        """
        try:
            prompt = get_knowledge_extraction_prompt(question_text)
            logger.info("Extracting knowledge points...")

            response = self._generate(prompt)
            logger.debug(f"Raw response: {response[:500]}...")

            result = self._extract_json(response)

            if result is None:
                return {
                    "success": False,
                    "error": "Failed to parse knowledge points",
                    "raw_response": response,
                }

            return {
                "success": True,
                "data": result,
            }

        except Exception as e:
            logger.error(f"Error extracting knowledge points: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }


# 全局单例实例
ai_service = AIModelService()


def get_ai_service() -> AIModelService:
    """
    获取 AI 服务单例

    Returns:
        AIModelService 实例
    """
    return ai_service
