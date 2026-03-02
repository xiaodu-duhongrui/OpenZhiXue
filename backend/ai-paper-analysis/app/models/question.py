from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Enum, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class QuestionType(str, enum.Enum):
    """题目类型枚举"""
    SINGLE_CHOICE = "single_choice"      # 单选题
    MULTIPLE_CHOICE = "multiple_choice"  # 多选题
    FILL_BLANK = "fill_blank"            # 填空题
    TRUE_FALSE = "true_false"            # 判断题
    SHORT_ANSWER = "short_answer"        # 简答题
    ESSAY = "essay"                      # 论述题
    CALCULATION = "calculation"          # 计算题
    PROOF = "proof"                      # 证明题


class DifficultyLevel(str, enum.Enum):
    """难度等级枚举"""
    EASY = "easy"           # 简单
    MEDIUM = "medium"       # 中等
    HARD = "hard"           # 困难
    VERY_HARD = "very_hard" # 非常困难


class Question(Base):
    """题目模型"""
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analysis_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    content = Column(Text, nullable=False)
    question_type = Column(
        Enum(QuestionType),
        default=QuestionType.SHORT_ANSWER,
        nullable=False
    )
    difficulty = Column(
        Enum(DifficultyLevel),
        default=DifficultyLevel.MEDIUM,
        nullable=False
    )
    knowledge_points = Column(JSONB, nullable=True)
    answer = Column(Text, nullable=True)
    analysis = Column(Text, nullable=True)
    is_generated = Column(Boolean, default=False, nullable=False)
    score = Column(Integer, nullable=True)  # 题目分值
    options = Column(JSONB, nullable=True)  # 选项（用于选择题）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('ix_questions_task_type', 'task_id', 'question_type'),
        Index('ix_questions_difficulty', 'difficulty'),
    )

    # 关联关系
    task = relationship("AnalysisTask", backref="questions")

    def __repr__(self):
        return f"<Question(id={self.id}, type={self.question_type}, difficulty={self.difficulty})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "task_id": str(self.task_id),
            "content": self.content,
            "question_type": self.question_type.value if self.question_type else None,
            "difficulty": self.difficulty.value if self.difficulty else None,
            "knowledge_points": self.knowledge_points,
            "answer": self.answer,
            "analysis": self.analysis,
            "is_generated": self.is_generated,
            "score": self.score,
            "options": self.options,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
