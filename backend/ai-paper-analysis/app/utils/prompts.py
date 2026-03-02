"""
提示词模板模块
用于题目分析和相似题生成的提示词模板
"""

from typing import Optional


# 题目分析提示词模板
QUESTION_ANALYSIS_PROMPT = """你是一位专业的教育专家和试题分析师。请分析以下题目，并按照JSON格式返回分析结果。

题目内容：
{question_text}

请从以下几个方面进行分析，并以JSON格式返回结果：

1. 出题技巧：分析题目的出题方式、考查角度、命题特点
2. 知识点：识别题目涉及的主要知识点和次要知识点
3. 难度评估：评估题目难度（简单/中等/困难），并说明理由
4. 解题思路：提供解题的关键步骤和方法
5. 易错点：指出学生容易犯的错误

请严格按照以下JSON格式返回，不要添加任何其他内容：

{{
    "question_type": "选择题/填空题/简答题/计算题/综合题",
    "difficulty": "简单/中等/困难",
    "difficulty_score": 1-5的整数,
    "main_knowledge_points": ["主要知识点1", "主要知识点2"],
    "secondary_knowledge_points": ["次要知识点1"],
    "question_techniques": [
        {{
            "technique": "技巧名称",
            "description": "技巧描述"
        }}
    ],
    "solution_approach": "解题思路描述",
    "common_mistakes": ["易错点1", "易错点2"],
    "estimated_time": 预计答题时间（分钟）,
    "difficulty_reason": "难度评估理由"
}}
"""


# 相似题生成提示词模板
SIMILAR_QUESTION_GENERATION_PROMPT = """你是一位专业的教育专家和试题编写专家。请根据给定的原题目，生成{count}道相似题目。

原题目：
{original_question}

原题目分析：
- 题型：{question_type}
- 难度：{difficulty}
- 主要知识点：{knowledge_points}

请生成与原题目相似的新题目，要求：
1. 保持相同的题型和难度
2. 覆盖相同的知识点
3. 题目情境和数值不同
4. 包含完整的答案和解析

请严格按照以下JSON格式返回{count}道题目，不要添加任何其他内容：

{{
    "similar_questions": [
        {{
            "question_number": 1,
            "question_content": "题目内容",
            "options": ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"],
            "correct_answer": "正确答案",
            "analysis": "详细解析",
            "knowledge_points": ["知识点1", "知识点2"],
            "difficulty": "简单/中等/困难"
        }}
    ]
}}

注意：如果是非选择题，options字段返回空数组[]。
"""


# 批量题目分析提示词模板
BATCH_QUESTION_ANALYSIS_PROMPT = """你是一位专业的教育专家和试题分析师。请分析以下试卷中的所有题目，并返回整体分析结果。

试卷内容：
{paper_text}

请从以下几个方面进行整体分析，并以JSON格式返回结果：

1. 题目分布统计
2. 知识点覆盖情况
3. 难度分布
4. 出题特点总结

请严格按照以下JSON格式返回：

{{
    "total_questions": 题目总数,
    "question_types": {{
        "选择题": 数量,
        "填空题": 数量,
        "简答题": 数量,
        "计算题": 数量,
        "综合题": 数量
    }},
    "difficulty_distribution": {{
        "简单": 数量,
        "中等": 数量,
        "困难": 数量
    }},
    "knowledge_points_coverage": [
        {{
            "knowledge_point": "知识点名称",
            "count": 出现次数,
            "percentage": 占比百分比
        }}
    ],
    "question_techniques_summary": [
        {{
            "technique": "技巧名称",
            "count": 使用次数,
            "examples": ["示例题目编号"]
        }}
    ],
    "overall_difficulty_score": 1-5的难度评分,
    "suggestions": ["改进建议1", "改进建议2"]
}}
"""


# JSON格式输出提示
JSON_OUTPUT_INSTRUCTION = """
重要提示：
1. 请确保返回的内容是有效的JSON格式
2. 不要在JSON之外添加任何解释性文字
3. 所有字符串值使用双引号
4. 数值类型不要加引号
5. 如果某个字段没有内容，使用空数组[]或空字符串""
"""


def get_question_analysis_prompt(question_text: str) -> str:
    """
    获取题目分析提示词

    Args:
        question_text: 题目文本

    Returns:
        完整的提示词
    """
    return QUESTION_ANALYSIS_PROMPT.format(question_text=question_text) + JSON_OUTPUT_INSTRUCTION


def get_similar_question_prompt(
    original_question: str,
    question_type: str,
    difficulty: str,
    knowledge_points: list,
    count: int = 3
) -> str:
    """
    获取相似题生成提示词

    Args:
        original_question: 原题目
        question_type: 题目类型
        difficulty: 难度
        knowledge_points: 知识点列表
        count: 生成数量

    Returns:
        完整的提示词
    """
    knowledge_points_str = "、".join(knowledge_points) if knowledge_points else "无"
    return SIMILAR_QUESTION_GENERATION_PROMPT.format(
        count=count,
        original_question=original_question,
        question_type=question_type,
        difficulty=difficulty,
        knowledge_points=knowledge_points_str
    ) + JSON_OUTPUT_INSTRUCTION


def get_batch_analysis_prompt(paper_text: str) -> str:
    """
    获取批量题目分析提示词

    Args:
        paper_text: 试卷文本

    Returns:
        完整的提示词
    """
    return BATCH_QUESTION_ANALYSIS_PROMPT.format(paper_text=paper_text) + JSON_OUTPUT_INSTRUCTION


# 知识点提取提示词模板
KNOWLEDGE_EXTRACTION_PROMPT = """请从以下题目中提取所有涉及的知识点，并按照学科分类。

题目内容：
{question_text}

请以JSON格式返回知识点：

{{
    "subject": "学科名称",
    "knowledge_points": [
        {{
            "name": "知识点名称",
            "level": "主要/次要",
            "category": "所属章节或类别"
        }}
    ]
}}
"""


def get_knowledge_extraction_prompt(question_text: str) -> str:
    """
    获取知识点提取提示词

    Args:
        question_text: 题目文本

    Returns:
        完整的提示词
    """
    return KNOWLEDGE_EXTRACTION_PROMPT.format(question_text=question_text) + JSON_OUTPUT_INSTRUCTION
