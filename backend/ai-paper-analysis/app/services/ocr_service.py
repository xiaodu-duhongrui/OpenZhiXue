"""
OCR 服务模块
使用 DeepSeek-OCR2 模型提供扫描件 OCR 识别功能
"""

import logging
import threading
import time
import os
import tempfile
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from io import BytesIO

import torch
from PIL import Image, ImageOps
import numpy as np

from app.config import settings
from app.schemas.ocr import OCRResult, PDFPageOCRResult

logger = logging.getLogger(__name__)


class OCRServiceError(Exception):
    """OCR 服务错误"""
    pass


class OCRService:
    """
    OCR 服务类
    实现 DeepSeek-OCR2 模型的懒加载和 OCR 识别功能
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
        """初始化 OCR 服务"""
        if self._initialized:
            return

        self._model = None
        self._tokenizer = None
        self._device = None
        self._model_loaded = False
        self._load_error = None
        self._initialized = True

        # 检查依赖
        self._check_dependencies()

        logger.info("OCRService instance created")

    def _check_dependencies(self) -> None:
        """检查必要的依赖库是否安装"""
        self.pdf2image_available = False

        try:
            import pdf2image
            self.pdf2image_available = True
            logger.info("pdf2image is available")
        except ImportError:
            logger.warning("pdf2image is not installed. PDF OCR will not be available.")

    def _get_device(self) -> str:
        """
        获取模型运行设备

        Returns:
            设备名称 (cuda/cpu)
        """
        device_setting = settings.OCR_DEVICE.lower()

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
        model_path = Path(settings.DEEPSEEK_OCR_MODEL_PATH)

        if not model_path.exists():
            logger.error(f"OCR model path does not exist: {model_path}")
            return False

        # 检查必要文件
        required_files = ["config.json", "tokenizer.json", "modeling_deepseekocr2.py"]
        for file_name in required_files:
            file_path = model_path / file_name
            if not file_path.exists():
                logger.error(f"Required file not found: {file_path}")
                return False

        # 检查模型文件
        model_files = list(model_path.glob("*.safetensors")) + list(model_path.glob("*.bin"))
        if not model_files:
            logger.error("No model weight files found (safetensors or bin)")
            return False

        logger.info(f"OCR model path validated: {model_path}")
        return True

    def load_model(self) -> bool:
        """
        加载 OCR 模型和分词器

        Returns:
            是否加载成功
        """
        if self._model_loaded:
            logger.info("OCR model already loaded")
            return True

        if self._load_error:
            logger.warning(f"Previous load failed: {self._load_error}")
            return False

        try:
            logger.info("Starting OCR model loading...")

            # 验证模型路径
            if not self._validate_model_path():
                raise ValueError(f"Invalid model path: {settings.DEEPSEEK_OCR_MODEL_PATH}")

            # 获取设备
            self._device = self._get_device()

            # 添加模型路径到 Python 路径，以便加载自定义模型类
            import sys
            model_path_str = str(settings.DEEPSEEK_OCR_MODEL_PATH)
            if model_path_str not in sys.path:
                sys.path.insert(0, model_path_str)

            # 加载分词器
            logger.info("Loading OCR tokenizer...")
            from transformers import AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                settings.DEEPSEEK_OCR_MODEL_PATH,
                trust_remote_code=True,
                use_fast=False
            )

            # 加载模型
            logger.info("Loading OCR model...")
            from transformers import AutoModelForCausalLM
            
            # 使用 bfloat16 以获得更好的性能
            torch_dtype = torch.bfloat16 if self._device == "cuda" else torch.float32
            
            self._model = AutoModelForCausalLM.from_pretrained(
                settings.DEEPSEEK_OCR_MODEL_PATH,
                trust_remote_code=True,
                torch_dtype=torch_dtype,
                device_map=self._device if self._device == "cuda" else None,
                low_cpu_mem_usage=True
            )

            # 如果是 CPU，手动移动模型
            if self._device == "cpu":
                self._model = self._model.to("cpu")

            # 设置为评估模式
            self._model.eval()

            self._model_loaded = True
            logger.info(f"OCR model loaded successfully on {self._device}")

            return True

        except Exception as e:
            self._load_error = str(e)
            logger.error(f"Failed to load OCR model: {e}", exc_info=True)
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
        logger.info("OCR model unloaded and memory released")

    def is_model_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self._model_loaded

    def get_model_status(self) -> Dict[str, Any]:
        """
        获取模型状态信息

        Returns:
            模型状态字典
        """
        status = {
            "loaded": self._model_loaded,
            "device": self._device,
            "model_path": settings.DEEPSEEK_OCR_MODEL_PATH,
            "error": self._load_error,
            "cuda_available": torch.cuda.is_available(),
        }

        # 添加内存使用信息
        if self._device == "cuda" and torch.cuda.is_available():
            status["memory_usage"] = {
                "gpu_memory_allocated": f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB",
                "gpu_memory_reserved": f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB",
            }

        return status

    def _load_image(self, image_path: str) -> Optional[Image.Image]:
        """
        加载图像文件

        Args:
            image_path: 图像文件路径

        Returns:
            PIL Image 对象
        """
        try:
            image = Image.open(image_path)
            # 处理 EXIF 方向
            corrected_image = ImageOps.exif_transpose(image)
            return corrected_image.convert("RGB")
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            return None

    def _preprocess_image(
        self,
        image: Image.Image,
        base_size: int = 1024,
        image_size: int = 640,
        crop_mode: bool = True
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[int]]:
        """
        预处理图像

        Args:
            image: PIL Image 对象
            base_size: 基础尺寸
            image_size: 图像尺寸
            crop_mode: 是否启用裁剪模式

        Returns:
            处理后的图像张量和相关信息
        """
        from torchvision import transforms

        # 图像转换
        image_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

        images_list = []
        images_crop_list = []
        images_spatial_crop = []

        if crop_mode:
            # 动态预处理
            if image.size[0] <= 768 and image.size[1] <= 768:
                crop_ratio = [1, 1]
                images_crop_raw = []
            else:
                images_crop_raw, crop_ratio = self._dynamic_preprocess(
                    image, min_num=2, max_num=6, image_size=image_size
                )

            # 处理全局视图
            global_view = ImageOps.pad(
                image, (base_size, base_size),
                color=(255, 255, 255)
            )
            images_list.append(image_transform(global_view).to(torch.bfloat16))

            width_crop_num, height_crop_num = crop_ratio
            images_spatial_crop.append([width_crop_num, height_crop_num])

            # 处理局部视图
            if width_crop_num > 1 or height_crop_num > 1:
                for crop_img in images_crop_raw:
                    images_crop_list.append(image_transform(crop_img).to(torch.bfloat16))
        else:
            # 简单缩放模式
            if image.size[0] <= image_size and image.size[1] <= image_size:
                resized = image
            else:
                resized = image.resize((image_size, image_size))
            
            global_view = ImageOps.pad(
                resized, (image_size, image_size),
                color=(255, 255, 255)
            )
            images_list.append(image_transform(global_view).to(torch.bfloat16))
            images_spatial_crop.append([1, 1])

        # 转换为张量
        images_ori = torch.stack(images_list, dim=0) if images_list else torch.zeros((1, 3, base_size, base_size))
        images_spatial_crop_tensor = torch.tensor(images_spatial_crop, dtype=torch.long)
        
        if images_crop_list:
            images_crop = torch.stack(images_crop_list, dim=0)
        else:
            images_crop = torch.zeros((1, 3, base_size, base_size))

        return images_ori, images_crop, images_spatial_crop_tensor, images_spatial_crop[0]

    def _dynamic_preprocess(
        self,
        image: Image.Image,
        min_num: int = 2,
        max_num: int = 6,
        image_size: int = 640
    ) -> Tuple[List[Image.Image], List[int]]:
        """
        动态预处理图像，根据图像比例进行裁剪

        Args:
            image: PIL Image 对象
            min_num: 最小裁剪数
            max_num: 最大裁剪数
            image_size: 图像尺寸

        Returns:
            裁剪后的图像列表和裁剪比例
        """
        orig_width, orig_height = image.size
        aspect_ratio = orig_width / orig_height

        # 计算目标比例
        target_ratios = set(
            (i, j) for n in range(min_num, max_num + 1)
            for i in range(1, n + 1)
            for j in range(1, n + 1)
            if i * j <= max_num and i * j >= min_num
        )
        target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

        # 找到最接近的比例
        best_ratio = self._find_closest_aspect_ratio(
            aspect_ratio, target_ratios, orig_width, orig_height, image_size
        )

        # 计算目标尺寸
        target_width = image_size * best_ratio[0]
        target_height = image_size * best_ratio[1]
        blocks = best_ratio[0] * best_ratio[1]

        # 调整图像大小
        resized_img = image.resize((target_width, target_height))
        processed_images = []

        for i in range(blocks):
            box = (
                (i % (target_width // image_size)) * image_size,
                (i // (target_width // image_size)) * image_size,
                ((i % (target_width // image_size)) + 1) * image_size,
                ((i // (target_width // image_size)) + 1) * image_size
            )
            split_img = resized_img.crop(box)
            processed_images.append(split_img)

        return processed_images, list(best_ratio)

    def _find_closest_aspect_ratio(
        self,
        aspect_ratio: float,
        target_ratios: List[Tuple[int, int]],
        width: int,
        height: int,
        image_size: int
    ) -> Tuple[int, int]:
        """
        找到最接近的宽高比

        Args:
            aspect_ratio: 原始宽高比
            target_ratios: 目标比例列表
            width: 原始宽度
            height: 原始高度
            image_size: 图像尺寸

        Returns:
            最佳比例
        """
        best_ratio_diff = float('inf')
        best_ratio = (1, 1)
        area = width * height

        for ratio in target_ratios:
            target_aspect_ratio = ratio[0] / ratio[1]
            ratio_diff = abs(aspect_ratio - target_aspect_ratio)

            if ratio_diff < best_ratio_diff:
                best_ratio_diff = ratio_diff
                best_ratio = ratio
            elif ratio_diff == best_ratio_diff:
                if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                    best_ratio = ratio

        return best_ratio

    def _text_encode(self, text: str, bos: bool = True, eos: bool = False) -> List[int]:
        """
        文本编码

        Args:
            text: 输入文本
            bos: 是否添加 BOS token
            eos: 是否添加 EOS token

        Returns:
            token ID 列表
        """
        t = self._tokenizer.encode(text, add_special_tokens=False)
        bos_id = 0
        eos_id = 1

        if bos:
            t = [bos_id] + t
        if eos:
            t = t + [eos_id]

        return t

    def _format_prompt(self, prompt: str, has_image: bool = True) -> str:
        """
        格式化提示词

        Args:
            prompt: 原始提示词
            has_image: 是否包含图像

        Returns:
            格式化后的提示词
        """
        if has_image:
            conversation = [
                {
                    "role": "<|User|>",
                    "content": prompt,
                },
                {"role": "<|Assistant|>", "content": ""},
            ]
        else:
            conversation = [
                {
                    "role": "<|User|>",
                    "content": prompt,
                },
                {"role": "<|Assistant|>", "content": ""},
            ]

        # 简单格式化
        formatted = ""
        for msg in conversation:
            if msg["role"] == "<|User|>":
                formatted += f"<|User|>{msg['content']}"
            else:
                formatted += f"<|Assistant|>"

        return formatted

    def recognize_image(
        self,
        image_path: str,
        prompt: str = "<image>\nExtract all text from this image and convert to markdown format.",
        max_new_tokens: Optional[int] = None,
        enable_crop: bool = True
    ) -> OCRResult:
        """
        识别单张图像

        Args:
            image_path: 图像文件路径
            prompt: OCR 提示词
            max_new_tokens: 最大生成 token 数
            enable_crop: 是否启用裁剪模式

        Returns:
            OCR 结果
        """
        start_time = time.time()

        try:
            # 确保模型已加载
            if not self._model_loaded:
                if not self.load_model():
                    raise OCRServiceError("Failed to load OCR model")

            # 加载图像
            image = self._load_image(image_path)
            if image is None:
                raise OCRServiceError(f"Failed to load image: {image_path}")

            # 预处理图像
            images_ori, images_crop, images_spatial_crop, crop_ratio = self._preprocess_image(
                image,
                base_size=settings.OCR_BASE_SIZE,
                image_size=settings.OCR_IMAGE_SIZE,
                crop_mode=enable_crop
            )

            # 准备输入
            prompt_formatted = self._format_prompt(prompt, has_image=True)
            
            # 编码文本
            image_token = '<image>'
            image_token_id = 128815
            text_splits = prompt_formatted.split(image_token)

            tokenized_str = []
            images_seq_mask = []

            for text_sep in text_splits[:-1]:
                tokenized_sep = self._text_encode(text_sep, bos=False, eos=False)
                tokenized_str += tokenized_sep
                images_seq_mask += [False] * len(tokenized_sep)

                # 添加图像 token
                patch_size = 16
                downsample_ratio = 4
                num_queries = math.ceil((settings.OCR_IMAGE_SIZE // patch_size) / downsample_ratio)
                num_queries_base = math.ceil((settings.OCR_BASE_SIZE // patch_size) / downsample_ratio)

                tokenized_image = ([image_token_id] * num_queries_base) * num_queries_base
                tokenized_image += [image_token_id]

                if crop_ratio[0] > 1 or crop_ratio[1] > 1:
                    tokenized_image += ([image_token_id] * (num_queries * crop_ratio[0])) * (num_queries * crop_ratio[1])

                tokenized_str += tokenized_image
                images_seq_mask += [True] * len(tokenized_image)

            # 处理最后的文本
            tokenized_sep = self._text_encode(text_splits[-1], bos=False, eos=False)
            tokenized_str += tokenized_sep
            images_seq_mask += [False] * len(tokenized_sep)

            # 添加 BOS token
            bos_id = 0
            tokenized_str = [bos_id] + tokenized_str
            images_seq_mask = [False] + images_seq_mask

            # 转换为张量
            input_ids = torch.LongTensor(tokenized_str)
            images_seq_mask_tensor = torch.tensor(images_seq_mask, dtype=torch.bool)

            # 移动到设备
            if self._device == "cuda":
                input_ids = input_ids.cuda()
                images_ori = images_ori.cuda()
                images_crop = images_crop.cuda()
                images_seq_mask_tensor = images_seq_mask_tensor.cuda()
                images_spatial_crop = images_spatial_crop.cuda()

            # 生成
            max_tokens = max_new_tokens or settings.OCR_MAX_NEW_TOKENS

            with torch.autocast(self._device, dtype=torch.bfloat16):
                with torch.no_grad():
                    output_ids = self._model.generate(
                        input_ids.unsqueeze(0),
                        images=[(images_crop, images_ori)],
                        images_seq_mask=images_seq_mask_tensor.unsqueeze(0),
                        images_spatial_crop=images_spatial_crop,
                        temperature=settings.OCR_TEMPERATURE,
                        eos_token_id=self._tokenizer.eos_token_id,
                        max_new_tokens=max_tokens,
                        no_repeat_ngram_size=20,
                        use_cache=True
                    )

            # 解码输出
            outputs = self._tokenizer.decode(
                output_ids[0, input_ids.unsqueeze(0).shape[1]:],
                skip_special_tokens=True
            )

            # 清理输出
            stop_str = '<｜end▁of▁sentence｜>'
            if outputs.endswith(stop_str):
                outputs = outputs[:-len(stop_str)]
            outputs = outputs.strip()

            processing_time = time.time() - start_time

            return OCRResult(
                file_path=image_path,
                text=outputs,
                processing_time=processing_time,
                success=True
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"OCR failed for {image_path}: {e}", exc_info=True)
            
            return OCRResult(
                file_path=image_path,
                text="",
                processing_time=processing_time,
                success=False,
                error=str(e)
            )

    async def recognize_image_async(
        self,
        image_path: str,
        prompt: str = "<image>\nExtract all text from this image and convert to markdown format.",
        max_new_tokens: Optional[int] = None,
        enable_crop: bool = True
    ) -> OCRResult:
        """
        异步识别单张图像

        Args:
            image_path: 图像文件路径
            prompt: OCR 提示词
            max_new_tokens: 最大生成 token 数
            enable_crop: 是否启用裁剪模式

        Returns:
            OCR 结果
        """
        # 在线程池中执行同步操作
        result = await asyncio.to_thread(
            self.recognize_image,
            image_path,
            prompt,
            max_new_tokens,
            enable_crop
        )
        return result

    def pdf_to_images(
        self,
        pdf_path: str,
        dpi: int = 200,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None
    ) -> List[Tuple[int, Image.Image]]:
        """
        将 PDF 转换为图像列表

        Args:
            pdf_path: PDF 文件路径
            dpi: 转换 DPI
            start_page: 起始页码（从1开始）
            end_page: 结束页码

        Returns:
            (页码, 图像) 列表
        """
        if not self.pdf2image_available:
            raise OCRServiceError("pdf2image is not installed")

        try:
            from pdf2image import convert_from_path

            # 获取 PDF 页数
            import PyPDF2
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                total_pages = len(pdf_reader.pages)

            # 设置页码范围
            first_page = start_page or 1
            last_page = min(end_page or total_pages, total_pages)

            logger.info(f"Converting PDF {pdf_path} to images (pages {first_page}-{last_page})")

            # 转换为图像
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                first_page=first_page,
                last_page=last_page
            )

            result = []
            for idx, img in enumerate(images):
                page_num = first_page + idx
                result.append((page_num, img))

            return result

        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            raise OCRServiceError(f"PDF conversion failed: {str(e)}")

    async def recognize_pdf(
        self,
        pdf_path: str,
        prompt: str = "<image>\nExtract all text from this image and convert to markdown format.",
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        enable_crop: bool = True,
        dpi: int = 200
    ) -> List[PDFPageOCRResult]:
        """
        识别 PDF 文档

        Args:
            pdf_path: PDF 文件路径
            prompt: OCR 提示词
            start_page: 起始页码
            end_page: 结束页码
            enable_crop: 是否启用裁剪模式
            dpi: PDF 转图像的 DPI

        Returns:
            各页 OCR 结果列表
        """
        start_time = time.time()
        results = []

        try:
            # 转换 PDF 为图像
            page_images = await asyncio.to_thread(
                self.pdf_to_images,
                pdf_path,
                dpi,
                start_page,
                end_page
            )

            # 创建临时目录保存图像
            temp_dir = tempfile.mkdtemp(prefix="ocr_pdf_")

            try:
                for page_num, image in page_images:
                    page_start = time.time()

                    # 保存图像到临时文件
                    temp_image_path = os.path.join(temp_dir, f"page_{page_num}.png")
                    image.save(temp_image_path)

                    # OCR 识别
                    ocr_result = await self.recognize_image_async(
                        temp_image_path,
                        prompt,
                        enable_crop=enable_crop
                    )

                    results.append(PDFPageOCRResult(
                        page_number=page_num,
                        text=ocr_result.text,
                        image_path=temp_image_path,
                        processing_time=time.time() - page_start
                    ))

                    logger.info(f"OCR completed for page {page_num}")

            finally:
                # 清理临时文件
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp directory: {e}")

            total_time = time.time() - start_time
            logger.info(f"PDF OCR completed: {len(results)} pages in {total_time:.2f}s")

            return results

        except Exception as e:
            logger.error(f"PDF OCR failed: {e}", exc_info=True)
            raise OCRServiceError(f"PDF OCR failed: {str(e)}")

    def batch_recognize(
        self,
        image_paths: List[str],
        prompt: str = "<image>\nExtract all text from this image and convert to markdown format.",
        enable_crop: bool = True
    ) -> List[OCRResult]:
        """
        批量识别图像

        Args:
            image_paths: 图像路径列表
            prompt: OCR 提示词
            enable_crop: 是否启用裁剪模式

        Returns:
            OCR 结果列表
        """
        results = []
        for path in image_paths:
            result = self.recognize_image(path, prompt, enable_crop=enable_crop)
            results.append(result)
        return results

    async def batch_recognize_async(
        self,
        image_paths: List[str],
        prompt: str = "<image>\nExtract all text from this image and convert to markdown format.",
        enable_crop: bool = True
    ) -> List[OCRResult]:
        """
        异步批量识别图像

        Args:
            image_paths: 图像路径列表
            prompt: OCR 提示词
            enable_crop: 是否启用裁剪模式

        Returns:
            OCR 结果列表
        """
        results = []
        for path in image_paths:
            result = await self.recognize_image_async(path, prompt, enable_crop=enable_crop)
            results.append(result)
        return results


# 导入 math 模块
import math

# 全局单例实例
ocr_service = OCRService()


def get_ocr_service() -> OCRService:
    """
    获取 OCR 服务单例

    Returns:
        OCRService 实例
    """
    return ocr_service
