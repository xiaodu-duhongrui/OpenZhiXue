"""
OCR 路由模块
提供 OCR 识别相关的 API 接口
"""

import logging
import time
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.schemas.ocr import (
    OCRRequest,
    OCRResponse,
    OCRBatchRequest,
    OCRStatus,
    OCRStatusResponse,
    PDFOCRRequest,
    PDFOCRResponse,
    OCRResult,
    PDFPageOCRResult,
)
from app.services.ocr_service import get_ocr_service, OCRServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["ocr"])


def _validate_file_path(file_path: str) -> Path:
    """
    验证文件路径

    Args:
        file_path: 文件路径

    Returns:
        Path 对象

    Raises:
        HTTPException: 文件不存在或路径无效
    """
    path = Path(file_path)
    
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")
    
    if not path.is_file():
        raise HTTPException(status_code=400, detail=f"路径不是文件: {file_path}")
    
    return path


def _get_file_extension(file_path: str) -> str:
    """获取文件扩展名"""
    return Path(file_path).suffix.lower()


@router.post("/recognize", response_model=OCRResponse)
async def recognize_image(request: OCRRequest):
    """
    OCR 识别单张图片或 PDF 文档

    Args:
        request: OCR 请求

    Returns:
        OCR 响应
    """
    start_time = time.time()
    task_id = f"ocr_{uuid.uuid4().hex[:12]}"

    try:
        # 验证文件
        file_path = _validate_file_path(request.file_path)
        extension = _get_file_extension(request.file_path)

        ocr_service = get_ocr_service()

        results = []

        # 根据文件类型处理
        if extension == ".pdf":
            # PDF 文档
            pdf_results = await ocr_service.recognize_pdf(
                pdf_path=str(file_path),
                prompt=request.prompt,
                enable_crop=request.enable_crop,
                max_new_tokens=request.max_new_tokens
            )

            # 转换为 OCRResult 格式
            for page_result in pdf_results:
                results.append(OCRResult(
                    file_path=request.file_path,
                    text=page_result.text,
                    page_number=page_result.page_number,
                    processing_time=page_result.processing_time,
                    success=True
                ))

            total_pages = len(pdf_results)
            processed_pages = len([r for r in pdf_results if r.text])

        elif extension in [".png", ".jpg", ".jpeg"]:
            # 图片文件
            result = await ocr_service.recognize_image_async(
                image_path=str(file_path),
                prompt=request.prompt,
                max_new_tokens=request.max_new_tokens,
                enable_crop=request.enable_crop
            )
            results.append(result)
            total_pages = 1
            processed_pages = 1 if result.success else 0

        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {extension}"
            )

        total_time = time.time() - start_time

        return OCRResponse(
            task_id=task_id,
            status=OCRStatus.COMPLETED if all(r.success for r in results) else OCRStatus.FAILED,
            results=results,
            total_pages=total_pages,
            processed_pages=processed_pages,
            total_time=total_time,
            message="OCR 识别完成" if all(r.success for r in results) else "部分页面识别失败"
        )

    except OCRServiceError as e:
        logger.error(f"OCR service error: {e}")
        raise HTTPException(status_code=500, detail=f"OCR 服务错误: {str(e)}")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error during OCR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"OCR 识别失败: {str(e)}")


@router.post("/batch", response_model=OCRResponse)
async def batch_recognize(request: OCRBatchRequest):
    """
    批量 OCR 识别多张图片

    Args:
        request: 批量 OCR 请求

    Returns:
        OCR 响应
    """
    start_time = time.time()
    task_id = f"ocr_batch_{uuid.uuid4().hex[:12]}"

    try:
        if not request.file_paths:
            raise HTTPException(status_code=400, detail="文件路径列表不能为空")

        # 验证所有文件
        valid_paths = []
        for path in request.file_paths:
            try:
                file_path = _validate_file_path(path)
                extension = _get_file_extension(path)
                
                if extension not in [".png", ".jpg", ".jpeg"]:
                    logger.warning(f"Skipping unsupported file type: {path}")
                    continue
                
                valid_paths.append(str(file_path))
            except HTTPException as e:
                logger.warning(f"Skipping invalid file: {path}, error: {e.detail}")

        if not valid_paths:
            raise HTTPException(status_code=400, detail="没有有效的图片文件")

        ocr_service = get_ocr_service()

        # 批量识别
        results = await ocr_service.batch_recognize_async(
            image_paths=valid_paths,
            prompt=request.prompt,
            enable_crop=request.enable_crop
        )

        total_time = time.time() - start_time
        successful_count = sum(1 for r in results if r.success)

        return OCRResponse(
            task_id=task_id,
            status=OCRStatus.COMPLETED if successful_count == len(results) else OCRStatus.FAILED,
            results=results,
            total_pages=len(results),
            processed_pages=successful_count,
            total_time=total_time,
            message=f"批量 OCR 完成: {successful_count}/{len(results)} 成功"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error during batch OCR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量 OCR 失败: {str(e)}")


@router.post("/pdf", response_model=PDFOCRResponse)
async def recognize_pdf(request: PDFOCRRequest):
    """
    PDF 文档 OCR 识别

    Args:
        request: PDF OCR 请求

    Returns:
        PDF OCR 响应
    """
    start_time = time.time()
    task_id = f"ocr_pdf_{uuid.uuid4().hex[:12]}"

    try:
        # 验证文件
        file_path = _validate_file_path(request.file_path)
        extension = _get_file_extension(request.file_path)

        if extension != ".pdf":
            raise HTTPException(status_code=400, detail="文件类型必须是 PDF")

        ocr_service = get_ocr_service()

        # 获取 PDF 页数
        import PyPDF2
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)

        # OCR 识别
        results = await ocr_service.recognize_pdf(
            pdf_path=str(file_path),
            prompt=request.prompt,
            start_page=request.start_page,
            end_page=request.end_page,
            enable_crop=request.enable_crop,
            dpi=request.dpi
        )

        # 合并所有页面的文本
        full_text = "\n\n".join(
            f"--- 第 {r.page_number} 页 ---\n{r.text}"
            for r in results
        )

        total_time = time.time() - start_time

        return PDFOCRResponse(
            task_id=task_id,
            status=OCRStatus.COMPLETED,
            file_path=str(file_path),
            total_pages=total_pages,
            processed_pages=len(results),
            results=results,
            full_text=full_text,
            total_time=total_time
        )

    except OCRServiceError as e:
        logger.error(f"OCR service error: {e}")
        raise HTTPException(status_code=500, detail=f"OCR 服务错误: {str(e)}")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error during PDF OCR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF OCR 失败: {str(e)}")


@router.get("/status", response_model=OCRStatusResponse)
async def get_ocr_status():
    """
    获取 OCR 服务状态

    Returns:
        OCR 服务状态响应
    """
    try:
        ocr_service = get_ocr_service()
        status = ocr_service.get_model_status()

        return OCRStatusResponse(
            service_available=True,
            model_loaded=status.get("loaded", False),
            device=status.get("device"),
            model_path=status.get("model_path"),
            cuda_available=status.get("cuda_available", False),
            error=status.get("error"),
            memory_usage=status.get("memory_usage")
        )

    except Exception as e:
        logger.error(f"Failed to get OCR status: {e}")
        return OCRStatusResponse(
            service_available=False,
            error=str(e)
        )


@router.post("/load")
async def load_ocr_model():
    """
    手动加载 OCR 模型

    Returns:
        加载结果
    """
    try:
        ocr_service = get_ocr_service()
        
        if ocr_service.is_model_loaded():
            return {
                "success": True,
                "message": "OCR 模型已加载",
                "status": ocr_service.get_model_status()
            }

        success = ocr_service.load_model()
        
        if success:
            return {
                "success": True,
                "message": "OCR 模型加载成功",
                "status": ocr_service.get_model_status()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="OCR 模型加载失败"
            )

    except Exception as e:
        logger.error(f"Failed to load OCR model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")


@router.post("/unload")
async def unload_ocr_model():
    """
    卸载 OCR 模型释放内存

    Returns:
        卸载结果
    """
    try:
        ocr_service = get_ocr_service()
        ocr_service.unload_model()

        return {
            "success": True,
            "message": "OCR 模型已卸载"
        }

    except Exception as e:
        logger.error(f"Failed to unload OCR model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"模型卸载失败: {str(e)}")
