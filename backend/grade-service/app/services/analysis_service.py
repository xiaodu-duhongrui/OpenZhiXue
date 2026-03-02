from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional, Dict, Any
from uuid import UUID
import numpy as np
from collections import Counter

from app.models.grade import Grade
from app.models.exam import Exam
from app.models.subject import Subject
from app.models.grade_analysis import GradeAnalysis
from app.schemas.analysis import (
    GradeStatisticsResponse, GradeRankingItem, GradeRankingResponse,
    GradeTrendItem, GradeTrendResponse, RadarChartItem, RadarChartResponse,
    ClassComparisonItem, ClassComparisonResponse
)


class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_statistics(
        self,
        exam_id: UUID,
        subject_id: Optional[UUID] = None,
        class_id: Optional[UUID] = None
    ) -> GradeStatisticsResponse:
        query = select(Grade.score).where(Grade.exam_id == exam_id)
        
        if subject_id:
            query = query.where(Grade.subject_id == subject_id)
        if class_id:
            query = query.where(Grade.class_id == class_id)
        
        result = await self.db.execute(query)
        scores = [row[0] for row in result.fetchall()]
        
        if not scores:
            return GradeStatisticsResponse(
                exam_id=exam_id,
                subject_id=subject_id,
                class_id=class_id,
                avg_score=0.0,
                max_score=0.0,
                min_score=0.0,
                median_score=0.0,
                std_deviation=0.0,
                pass_count=0,
                pass_rate=0.0,
                excellent_count=0,
                excellent_rate=0.0,
                fail_count=0,
                fail_rate=0.0,
                total_count=0,
                score_distribution={},
                percentile_25=0.0,
                percentile_50=0.0,
                percentile_75=0.0,
                percentile_90=0.0,
            )
        
        scores_array = np.array(scores)
        
        subject = None
        if subject_id:
            subject = await self.db.get(Subject, subject_id)
        
        pass_score = subject.pass_score if subject else 60.0
        excellent_score = subject.excellent_score if subject else 90.0
        
        pass_count = sum(1 for s in scores if s >= pass_score)
        excellent_count = sum(1 for s in scores if s >= excellent_score)
        fail_count = len(scores) - pass_count
        
        score_ranges = {
            "0-60": 0,
            "60-70": 0,
            "70-80": 0,
            "80-90": 0,
            "90-100": 0,
        }
        for score in scores:
            if score < 60:
                score_ranges["0-60"] += 1
            elif score < 70:
                score_ranges["60-70"] += 1
            elif score < 80:
                score_ranges["70-80"] += 1
            elif score < 90:
                score_ranges["80-90"] += 1
            else:
                score_ranges["90-100"] += 1
        
        return GradeStatisticsResponse(
            exam_id=exam_id,
            subject_id=subject_id,
            class_id=class_id,
            avg_score=float(np.mean(scores_array)),
            max_score=float(np.max(scores_array)),
            min_score=float(np.min(scores_array)),
            median_score=float(np.median(scores_array)),
            std_deviation=float(np.std(scores_array)),
            pass_count=pass_count,
            pass_rate=pass_count / len(scores) * 100,
            excellent_count=excellent_count,
            excellent_rate=excellent_count / len(scores) * 100,
            fail_count=fail_count,
            fail_rate=fail_count / len(scores) * 100,
            total_count=len(scores),
            score_distribution=score_ranges,
            percentile_25=float(np.percentile(scores_array, 25)),
            percentile_50=float(np.percentile(scores_array, 50)),
            percentile_75=float(np.percentile(scores_array, 75)),
            percentile_90=float(np.percentile(scores_array, 90)),
        )
    
    async def get_rankings(
        self,
        exam_id: UUID,
        class_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 50
    ) -> GradeRankingResponse:
        subquery = (
            select(
                Grade.student_id,
                func.sum(Grade.score).label("total_score")
            )
            .where(Grade.exam_id == exam_id)
            .group_by(Grade.student_id)
        )
        
        if class_id:
            subquery = subquery.where(Grade.class_id == class_id)
        
        subquery = subquery.subquery()
        
        count_query = select(func.count()).select_from(subquery)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = (
            select(subquery)
            .order_by(subquery.c.total_score.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await self.db.execute(query)
        rankings_data = result.fetchall()
        
        rankings = []
        for rank, row in enumerate(rankings_data, start=(page - 1) * page_size + 1):
            student_id = row.student_id
            total_score = row.total_score
            
            subject_scores_query = (
                select(Grade.score, Subject.name)
                .join(Subject, Grade.subject_id == Subject.id)
                .where(and_(Grade.exam_id == exam_id, Grade.student_id == student_id))
            )
            subject_result = await self.db.execute(subject_scores_query)
            subject_scores = {row.name: row.score for row in subject_result.fetchall()}
            
            rankings.append(GradeRankingItem(
                rank=rank,
                student_id=student_id,
                total_score=total_score,
                subject_scores=subject_scores,
            ))
        
        return GradeRankingResponse(
            exam_id=exam_id,
            class_id=class_id,
            rankings=rankings,
            total=total,
            page=page,
            page_size=page_size,
        )
    
    async def get_trends(
        self,
        student_id: UUID,
        subject_id: Optional[UUID] = None,
        limit: int = 10
    ) -> GradeTrendResponse:
        query = (
            select(Grade, Exam)
            .join(Exam, Grade.exam_id == Exam.id)
            .where(Grade.student_id == student_id)
            .where(Exam.status == "published")
        )
        
        if subject_id:
            query = query.where(Grade.subject_id == subject_id)
        
        query = query.order_by(Exam.start_time.desc()).limit(limit)
        
        result = await self.db.execute(query)
        grades_with_exams = result.fetchall()
        
        trends = []
        for grade, exam in grades_with_exams:
            avg_query = select(func.avg(Grade.score)).where(
                and_(Grade.exam_id == exam.id, Grade.subject_id == grade.subject_id)
            )
            avg_result = await self.db.execute(avg_query)
            avg_score = avg_result.scalar() or 0
            
            class_avg = None
            if grade.class_id:
                class_avg_query = select(func.avg(Grade.score)).where(
                    and_(
                        Grade.exam_id == exam.id,
                        Grade.subject_id == grade.subject_id,
                        Grade.class_id == grade.class_id
                    )
                )
                class_avg_result = await self.db.execute(class_avg_query)
                class_avg = class_avg_result.scalar()
            
            trends.append(GradeTrendItem(
                exam_id=exam.id,
                exam_name=exam.name,
                exam_date=exam.start_time,
                score=grade.score,
                rank=grade.rank,
                avg_score=float(avg_score),
                class_avg_score=float(class_avg) if class_avg else None,
            ))
        
        subject_name = None
        if subject_id:
            subject = await self.db.get(Subject, subject_id)
            subject_name = subject.name if subject else None
        
        return GradeTrendResponse(
            student_id=student_id,
            subject_id=subject_id,
            subject_name=subject_name,
            trends=list(reversed(trends)),
        )
    
    async def get_radar_chart(
        self,
        student_id: UUID,
        exam_id: UUID
    ) -> RadarChartResponse:
        grades_query = (
            select(Grade, Subject)
            .join(Subject, Grade.subject_id == Subject.id)
            .where(and_(Grade.student_id == student_id, Grade.exam_id == exam_id))
        )
        grades_result = await self.db.execute(grades_query)
        grades_with_subjects = grades_result.fetchall()
        
        data = []
        for grade, subject in grades_with_subjects:
            avg_query = select(func.avg(Grade.score)).where(
                and_(Grade.exam_id == exam_id, Grade.subject_id == subject.id)
            )
            avg_result = await self.db.execute(avg_query)
            avg_score = avg_result.scalar() or 0
            
            max_query = select(func.max(Grade.score)).where(
                and_(Grade.exam_id == exam_id, Grade.subject_id == subject.id)
            )
            max_result = await self.db.execute(max_query)
            max_score = max_result.scalar() or subject.total_score
            
            data.append(RadarChartItem(
                subject=subject.name,
                score=grade.score,
                avg_score=float(avg_score),
                max_score=float(max_score),
            ))
        
        return RadarChartResponse(
            student_id=student_id,
            exam_id=exam_id,
            data=data,
        )
    
    async def get_class_comparison(
        self,
        exam_id: UUID,
        subject_id: UUID
    ) -> ClassComparisonResponse:
        subject = await self.db.get(Subject, subject_id)
        subject_name = subject.name if subject else ""
        
        class_ids_query = (
            select(Grade.class_id)
            .where(and_(Grade.exam_id == exam_id, Grade.subject_id == subject_id, Grade.class_id != None))
            .distinct()
        )
        class_ids_result = await self.db.execute(class_ids_query)
        class_ids = [row[0] for row in class_ids_result.fetchall()]
        
        classes = []
        for class_id in class_ids:
            scores_query = select(Grade.score).where(
                and_(Grade.exam_id == exam_id, Grade.subject_id == subject_id, Grade.class_id == class_id)
            )
            scores_result = await self.db.execute(scores_query)
            scores = [row[0] for row in scores_result.fetchall()]
            
            if not scores:
                continue
            
            pass_score = subject.pass_score if subject else 60.0
            excellent_score = subject.excellent_score if subject else 90.0
            
            pass_count = sum(1 for s in scores if s >= pass_score)
            excellent_count = sum(1 for s in scores if s >= excellent_score)
            
            classes.append(ClassComparisonItem(
                class_id=class_id,
                class_name=f"班级 {str(class_id)[:8]}",
                avg_score=float(np.mean(scores)),
                max_score=float(max(scores)),
                min_score=float(min(scores)),
                pass_rate=pass_count / len(scores) * 100,
                excellent_rate=excellent_count / len(scores) * 100,
                student_count=len(scores),
            ))
        
        classes.sort(key=lambda x: x.avg_score, reverse=True)
        
        return ClassComparisonResponse(
            exam_id=exam_id,
            subject_id=subject_id,
            subject_name=subject_name,
            classes=classes,
        )
    
    async def save_analysis(
        self,
        exam_id: UUID,
        subject_id: UUID,
        class_id: Optional[UUID],
        statistics: GradeStatisticsResponse
    ) -> GradeAnalysis:
        analysis = GradeAnalysis(
            exam_id=exam_id,
            subject_id=subject_id,
            class_id=class_id,
            avg_score=statistics.avg_score,
            max_score=statistics.max_score,
            min_score=statistics.min_score,
            median_score=statistics.median_score,
            std_deviation=statistics.std_deviation,
            pass_count=statistics.pass_count,
            pass_rate=statistics.pass_rate,
            excellent_count=statistics.excellent_count,
            excellent_rate=statistics.excellent_rate,
            total_count=statistics.total_count,
            score_distribution=statistics.score_distribution,
        )
        
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis
