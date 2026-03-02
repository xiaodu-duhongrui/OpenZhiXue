from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, Dict, Any
from uuid import UUID
import os
import json
from datetime import datetime

from app.models.grade import Grade
from app.models.exam import Exam
from app.models.subject import Subject
from app.schemas.report import (
    ReportCreate, ReportType, ReportStatus,
    StudentReportData, ClassReportData
)
from app.services.analysis_service import AnalysisService
from app.config import settings


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.analysis_service = AnalysisService(db)
    
    async def generate_report(self, report_data: ReportCreate) -> Dict[str, Any]:
        report_id = None
        
        try:
            if report_data.report_type == ReportType.STUDENT:
                if not report_data.student_id or not report_data.exam_id:
                    raise ValueError("student_id and exam_id are required for student report")
                
                report_data_dict = await self._generate_student_report(
                    report_data.student_id,
                    report_data.exam_id,
                    report_data.include_trends
                )
                
            elif report_data.report_type == ReportType.CLASS:
                if not report_data.class_id or not report_data.exam_id:
                    raise ValueError("class_id and exam_id are required for class report")
                
                report_data_dict = await self._generate_class_report(
                    report_data.class_id,
                    report_data.exam_id
                )
                
            elif report_data.report_type == ReportType.EXAM:
                if not report_data.exam_id:
                    raise ValueError("exam_id is required for exam report")
                
                report_data_dict = await self._generate_exam_report(
                    report_data.exam_id
                )
            else:
                raise ValueError(f"Unsupported report type: {report_data.report_type}")
            
            os.makedirs(settings.REPORT_STORAGE_PATH, exist_ok=True)
            
            report_id = UUID(os.urandom(16).hex())
            file_name = f"report_{report_data.report_type}_{report_id}.json"
            file_path = os.path.join(settings.REPORT_STORAGE_PATH, file_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data_dict, f, ensure_ascii=False, indent=2, default=str)
            
            return {
                "id": str(report_id),
                "report_type": report_data.report_type,
                "status": ReportStatus.COMPLETED,
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "data": report_data_dict,
            }
            
        except Exception as e:
            return {
                "id": str(report_id) if report_id else None,
                "report_type": report_data.report_type,
                "status": ReportStatus.FAILED,
                "error_message": str(e),
            }
    
    async def _generate_student_report(
        self,
        student_id: UUID,
        exam_id: UUID,
        include_trends: bool = False
    ) -> Dict[str, Any]:
        exam = await self.db.get(Exam, exam_id)
        
        grades_query = (
            select(Grade, Subject)
            .join(Subject, Grade.subject_id == Subject.id)
            .where(and_(Grade.student_id == student_id, Grade.exam_id == exam_id))
        )
        grades_result = await self.db.execute(grades_query)
        grades_with_subjects = grades_result.fetchall()
        
        subject_scores = []
        radar_data = []
        total_score = 0
        
        for grade, subject in grades_with_subjects:
            subject_scores.append({
                "subject_id": str(subject.id),
                "subject_name": subject.name,
                "score": grade.score,
                "total_score": subject.total_score,
                "rank": grade.rank,
                "class_rank": grade.class_rank,
            })
            total_score += grade.score
            
            radar_data.append({
                "subject": subject.name,
                "score": grade.score,
                "max_score": subject.total_score,
            })
        
        total_rank_query = (
            select(func.count())
            .select_from(
                select(Grade.student_id)
                .where(Grade.exam_id == exam_id)
                .distinct()
                .subquery()
            )
        )
        total_students_result = await self.db.execute(total_rank_query)
        total_students = total_students_result.scalar() or 0
        
        rankings = await self.analysis_service.get_rankings(exam_id, page=1, page_size=1000)
        total_rank = None
        for item in rankings.rankings:
            if item.student_id == student_id:
                total_rank = item.rank
                break
        
        class_avg = await self.analysis_service.calculate_statistics(
            exam_id, class_id=grades_with_subjects[0][0].class_id if grades_with_subjects else None
        )
        grade_avg = await self.analysis_service.calculate_statistics(exam_id)
        
        strengths = []
        weaknesses = []
        for item in subject_scores:
            avg_stat = await self.analysis_service.calculate_statistics(
                exam_id, subject_id=UUID(item["subject_id"])
            )
            if item["score"] >= avg_stat.avg_score + 10:
                strengths.append(item["subject_name"])
            elif item["score"] <= avg_stat.avg_score - 10:
                weaknesses.append(item["subject_name"])
        
        trend_data = None
        if include_trends:
            trends = await self.analysis_service.get_trends(student_id)
            trend_data = [t.model_dump() for t in trends.trends]
        
        recommendations = []
        if weaknesses:
            recommendations.append(f"建议加强{', '.join(weaknesses)}的学习")
        if strengths:
            recommendations.append(f"继续保持{', '.join(strengths)}的优势")
        
        return {
            "report_type": "student",
            "student_id": str(student_id),
            "exam_id": str(exam_id),
            "student_name": f"学生 {str(student_id)[:8]}",
            "class_name": f"班级 {str(grades_with_subjects[0][0].class_id)[:8]}" if grades_with_subjects else "",
            "exam_name": exam.name if exam else "",
            "exam_date": exam.start_time.isoformat() if exam else None,
            "total_score": total_score,
            "total_rank": total_rank,
            "total_students": total_students,
            "subject_scores": subject_scores,
            "radar_chart_data": radar_data,
            "class_avg_score": class_avg.avg_score,
            "grade_avg_score": grade_avg.avg_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "trend_data": trend_data,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    async def _generate_class_report(
        self,
        class_id: UUID,
        exam_id: UUID
    ) -> Dict[str, Any]:
        exam = await self.db.get(Exam, exam_id)
        
        student_count_query = (
            select(func.count(func.distinct(Grade.student_id)))
            .where(and_(Grade.exam_id == exam_id, Grade.class_id == class_id))
        )
        student_count_result = await self.db.execute(student_count_query)
        total_students = student_count_result.scalar() or 0
        
        subjects = await self.db.execute(select(Subject).where(Subject.is_active == True))
        subjects_list = subjects.scalars().all()
        
        subject_analyses = []
        for subject in subjects_list:
            stats = await self.analysis_service.calculate_statistics(
                exam_id, subject_id=subject.id, class_id=class_id
            )
            if stats.total_count > 0:
                subject_analyses.append({
                    "subject_id": str(subject.id),
                    "subject_name": subject.name,
                    "avg_score": stats.avg_score,
                    "max_score": stats.max_score,
                    "min_score": stats.min_score,
                    "pass_rate": stats.pass_rate,
                    "excellent_rate": stats.excellent_rate,
                })
        
        score_distribution = {"0-60": 0, "60-70": 0, "70-80": 0, "80-90": 0, "90-100": 0}
        
        rankings = await self.analysis_service.get_rankings(exam_id, class_id=class_id, page=1, page_size=10)
        top_students = [r.model_dump() for r in rankings.rankings[:5]]
        
        grade_stats = await self.analysis_service.calculate_statistics(exam_id)
        class_stats = await self.analysis_service.calculate_statistics(exam_id, class_id=class_id)
        
        comparison = {
            "class_avg": class_stats.avg_score,
            "grade_avg": grade_stats.avg_score,
            "difference": class_stats.avg_score - grade_stats.avg_score,
        }
        
        return {
            "report_type": "class",
            "class_id": str(class_id),
            "exam_id": str(exam_id),
            "class_name": f"班级 {str(class_id)[:8]}",
            "exam_name": exam.name if exam else "",
            "exam_date": exam.start_time.isoformat() if exam else None,
            "total_students": total_students,
            "avg_total_score": class_stats.avg_score,
            "subject_analyses": subject_analyses,
            "score_distribution": score_distribution,
            "top_students": top_students,
            "comparison_with_grade": comparison,
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    async def _generate_exam_report(self, exam_id: UUID) -> Dict[str, Any]:
        exam = await self.db.get(Exam, exam_id)
        
        subjects = await self.db.execute(select(Subject).where(Subject.is_active == True))
        subjects_list = subjects.scalars().all()
        
        subject_stats = []
        for subject in subjects_list:
            stats = await self.analysis_service.calculate_statistics(exam_id, subject_id=subject.id)
            if stats.total_count > 0:
                subject_stats.append({
                    "subject_name": subject.name,
                    "avg_score": stats.avg_score,
                    "max_score": stats.max_score,
                    "min_score": stats.min_score,
                    "pass_rate": stats.pass_rate,
                    "excellent_rate": stats.excellent_rate,
                    "total_count": stats.total_count,
                })
        
        overall_stats = await self.analysis_service.calculate_statistics(exam_id)
        
        return {
            "report_type": "exam",
            "exam_id": str(exam_id),
            "exam_name": exam.name if exam else "",
            "exam_date": exam.start_time.isoformat() if exam else None,
            "exam_type": exam.type if exam else None,
            "overall_statistics": {
                "total_students": overall_stats.total_count,
                "avg_score": overall_stats.avg_score,
                "pass_rate": overall_stats.pass_rate,
                "excellent_rate": overall_stats.excellent_rate,
            },
            "subject_statistics": subject_stats,
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    async def get_report(self, report_id: UUID) -> Optional[Dict[str, Any]]:
        file_pattern = f"report_*_{report_id}.json"
        report_dir = settings.REPORT_STORAGE_PATH
        
        if not os.path.exists(report_dir):
            return None
        
        for filename in os.listdir(report_dir):
            if str(report_id) in filename:
                file_path = os.path.join(report_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        return None
    
    async def export_to_pdf(self, report_data: Dict[str, Any]) -> bytes:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        elements = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,
        )
        
        elements.append(Paragraph("成绩报告", title_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph(f"报告类型: {report_data.get('report_type', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"考试名称: {report_data.get('exam_name', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"生成时间: {report_data.get('generated_at', 'N/A')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        if report_data.get('report_type') == 'student':
            elements.append(Paragraph("学生成绩报告", styles['Heading2']))
            elements.append(Paragraph(f"学生: {report_data.get('student_name', 'N/A')}", styles['Normal']))
            elements.append(Paragraph(f"班级: {report_data.get('class_name', 'N/A')}", styles['Normal']))
            elements.append(Paragraph(f"总分: {report_data.get('total_score', 0)}", styles['Normal']))
            elements.append(Paragraph(f"排名: {report_data.get('total_rank', 'N/A')} / {report_data.get('total_students', 0)}", styles['Normal']))
            elements.append(Spacer(1, 20))
            
            if report_data.get('subject_scores'):
                elements.append(Paragraph("各科成绩", styles['Heading3']))
                table_data = [['科目', '分数', '满分', '排名']]
                for score in report_data['subject_scores']:
                    table_data.append([
                        score.get('subject_name', ''),
                        str(score.get('score', 0)),
                        str(score.get('total_score', 100)),
                        str(score.get('rank', 'N/A')),
                    ])
                
                table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
        
        doc.build(elements)
        return buffer.getvalue()
