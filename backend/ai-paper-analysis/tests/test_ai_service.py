"""
AI 模型服务测试脚本
验证 Qwen3-0.5B 模型加载和基本功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from app.services.ai_service import get_ai_service
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_model_loading():
    """测试模型加载"""
    logger.info("=" * 50)
    logger.info("测试 1: 模型加载")
    logger.info("=" * 50)

    ai_service = get_ai_service()

    # 检查初始状态
    status = ai_service.get_model_status()
    logger.info(f"初始状态: {status}")

    # 加载模型
    logger.info("开始加载模型...")
    success = ai_service.load_model()

    if success:
        logger.info("模型加载成功!")
        status = ai_service.get_model_status()
        logger.info(f"加载后状态: {status}")
        return True
    else:
        logger.error("模型加载失败!")
        logger.error(f"错误信息: {status.get('error')}")
        return False


def test_question_analysis():
    """测试题目分析功能"""
    logger.info("\n" + "=" * 50)
    logger.info("测试 2: 题目分析")
    logger.info("=" * 50)

    ai_service = get_ai_service()

    test_question = """
已知函数 f(x) = x^3 - 3x + 1，求：
(1) 函数的单调区间；
(2) 函数的极值。
"""

    logger.info(f"测试题目: {test_question.strip()}")

    result = ai_service.analyze_questions(test_question)

    if result.get("success"):
        logger.info("题目分析成功!")
        import json
        logger.info(f"分析结果:\n{json.dumps(result.get('data'), ensure_ascii=False, indent=2)}")
        return True
    else:
        logger.error(f"题目分析失败: {result.get('error')}")
        return False


def test_similar_question_generation():
    """测试相似题生成功能"""
    logger.info("\n" + "=" * 50)
    logger.info("测试 3: 相似题生成")
    logger.info("=" * 50)

    ai_service = get_ai_service()

    test_question = "已知等差数列 {an} 的首项 a1=2，公差 d=3，求前 10 项的和 S10。"

    logger.info(f"原题目: {test_question}")

    result = ai_service.generate_similar_questions(
        question=test_question,
        count=2,
        question_type="计算题",
        difficulty="中等",
        knowledge_points=["等差数列", "数列求和"]
    )

    if result.get("success"):
        logger.info("相似题生成成功!")
        import json
        logger.info(f"生成结果:\n{json.dumps(result.get('data'), ensure_ascii=False, indent=2)}")
        return True
    else:
        logger.error(f"相似题生成失败: {result.get('error')}")
        return False


def test_knowledge_extraction():
    """测试知识点提取功能"""
    logger.info("\n" + "=" * 50)
    logger.info("测试 4: 知识点提取")
    logger.info("=" * 50)

    ai_service = get_ai_service()

    test_question = "求函数 y = sin(x) + cos(x) 的最大值和最小值。"

    logger.info(f"测试题目: {test_question}")

    result = ai_service.extract_knowledge_points(test_question)

    if result.get("success"):
        logger.info("知识点提取成功!")
        import json
        logger.info(f"提取结果:\n{json.dumps(result.get('data'), ensure_ascii=False, indent=2)}")
        return True
    else:
        logger.error(f"知识点提取失败: {result.get('error')}")
        return False


def main():
    """主测试函数"""
    logger.info("开始 AI 模型服务测试")
    logger.info(f"模型路径: {settings.QWEN_MODEL_PATH}")
    logger.info(f"设备设置: {settings.MODEL_DEVICE}")

    results = {}

    # 测试 1: 模型加载
    results["model_loading"] = test_model_loading()

    if not results["model_loading"]:
        logger.error("模型加载失败，跳过后续测试")
        return results

    # 测试 2: 题目分析
    results["question_analysis"] = test_question_analysis()

    # 测试 3: 相似题生成
    results["similar_question_generation"] = test_similar_question_generation()

    # 测试 4: 知识点提取
    results["knowledge_extraction"] = test_knowledge_extraction()

    # 打印测试结果摘要
    logger.info("\n" + "=" * 50)
    logger.info("测试结果摘要")
    logger.info("=" * 50)
    for test_name, passed in results.items():
        status = "通过" if passed else "失败"
        logger.info(f"{test_name}: {status}")

    all_passed = all(results.values())
    logger.info(f"\n总体结果: {'全部通过' if all_passed else '存在失败'}")

    return results


if __name__ == "__main__":
    main()
