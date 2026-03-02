"""
独立模型加载测试脚本
直接测试 Qwen3-0.5B 模型加载，不依赖 FastAPI
"""

import sys
import os
import json
from pathlib import Path

# 模型路径
MODEL_PATH = r"e:\openzhixue\model\qwen3-0.5b"

def check_model_files():
    """检查模型文件是否完整"""
    print("=" * 50)
    print("检查模型文件...")
    print("=" * 50)
    
    model_path = Path(MODEL_PATH)
    
    if not model_path.exists():
        print(f"错误: 模型路径不存在: {model_path}")
        return False
    
    print(f"模型路径: {model_path}")
    
    # 列出所有文件
    files = list(model_path.glob("*"))
    print(f"\n目录中的文件:")
    for f in files:
        print(f"  - {f.name} ({f.stat().st_size / 1024 / 1024:.2f} MB)")
    
    # 检查必要文件
    required_files = ["config.json", "tokenizer.json"]
    missing_files = []
    
    for file_name in required_files:
        if not (model_path / file_name).exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\n错误: 缺少必要文件: {missing_files}")
        return False
    
    # 检查模型权重文件
    safetensors_files = list(model_path.glob("*.safetensors"))
    bin_files = list(model_path.glob("*.bin"))
    
    if not safetensors_files and not bin_files:
        print("\n错误: 未找到模型权重文件 (.safetensors 或 .bin)")
        return False
    
    print(f"\n模型文件检查通过!")
    return True


def test_imports():
    """测试必要的导入"""
    print("\n" + "=" * 50)
    print("测试依赖导入...")
    print("=" * 50)
    
    try:
        import torch
        print(f"PyTorch 版本: {torch.__version__}")
        print(f"CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA 版本: {torch.version.cuda}")
            print(f"GPU 设备: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"错误: 无法导入 torch: {e}")
        return False
    
    try:
        import transformers
        print(f"Transformers 版本: {transformers.__version__}")
    except ImportError as e:
        print(f"错误: 无法导入 transformers: {e}")
        return False
    
    print("\n依赖导入成功!")
    return True


def test_model_loading():
    """测试模型加载"""
    print("\n" + "=" * 50)
    print("测试模型加载...")
    print("=" * 50)
    
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # 确定设备
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用设备: {device}")
        
        # 加载分词器
        print("\n加载分词器...")
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            use_fast=False
        )
        print("分词器加载成功!")
        
        # 确保 pad_token 存在
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print("设置 pad_token = eos_token")
        
        # 加载模型
        print("\n加载模型...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map=device if device == "cuda" else None,
            low_cpu_mem_usage=True
        )
        
        if device == "cpu":
            model = model.to("cpu")
        
        model.eval()
        print("模型加载成功!")
        
        # 打印模型信息
        total_params = sum(p.numel() for p in model.parameters())
        print(f"模型参数量: {total_params:,}")
        
        return True, model, tokenizer, device
        
    except Exception as e:
        print(f"错误: 模型加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None, None


def test_generation(model, tokenizer, device):
    """测试文本生成"""
    print("\n" + "=" * 50)
    print("测试文本生成...")
    print("=" * 50)
    
    try:
        prompt = "你好，请介绍一下自己。"
        print(f"输入: {prompt}")
        
        # 编码
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        if device == "cuda":
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # 生成
        print("\n生成中...")
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        
        # 解码
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = generated_text[len(prompt):].strip()
        
        print(f"\n输出: {response}")
        print("\n文本生成测试成功!")
        return True
        
    except Exception as e:
        print(f"错误: 文本生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("Qwen3-0.5B 模型加载测试")
    print("=" * 50)
    
    results = {}
    
    # 测试 1: 检查模型文件
    results["model_files"] = check_model_files()
    if not results["model_files"]:
        print("\n模型文件检查失败，退出测试")
        return
    
    # 测试 2: 测试导入
    results["imports"] = test_imports()
    if not results["imports"]:
        print("\n依赖导入失败，退出测试")
        return
    
    # 测试 3: 加载模型
    success, model, tokenizer, device = test_model_loading()
    results["model_loading"] = success
    if not success:
        print("\n模型加载失败，退出测试")
        return
    
    # 测试 4: 文本生成
    results["generation"] = test_generation(model, tokenizer, device)
    
    # 打印结果摘要
    print("\n" + "=" * 50)
    print("测试结果摘要")
    print("=" * 50)
    for test_name, passed in results.items():
        status = "通过" if passed else "失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\n总体结果: {'全部通过' if all_passed else '存在失败'}")


if __name__ == "__main__":
    main()
