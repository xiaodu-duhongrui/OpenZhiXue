"""
文件存储服务
提供本地文件存储、文件路径生成、文件类型验证和文件大小限制功能
"""

import os
import uuid
import hashlib
import aiofiles
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, BinaryIO, Tuple
from fastapi import UploadFile, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """文件存储服务类"""

    # 支持的文件类型及其MIME类型
    ALLOWED_EXTENSIONS = {
        "pdf": ["application/pdf"],
        "doc": ["application/msword"],
        "docx": [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ],
    }

    # 文件扩展名映射
    EXTENSION_MAP = {
        "application/pdf": "pdf",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    }

    def __init__(self, base_path: Optional[str] = None):
        """
        初始化存储服务

        Args:
            base_path: 基础存储路径，默认使用配置中的UPLOAD_DIR
        """
        self.base_path = Path(base_path or settings.UPLOAD_DIR)
        self.max_file_size = settings.MAX_UPLOAD_SIZE  # 50MB
        self._ensure_base_path()

    def _ensure_base_path(self) -> None:
        """确保基础存储路径存在"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage base path ensured: {self.base_path}")

    def _generate_date_path(self) -> Path:
        """
        生成按日期组织的存储路径

        Returns:
            按年/月/日组织的路径
        """
        now = datetime.now()
        date_path = self.base_path / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
        date_path.mkdir(parents=True, exist_ok=True)
        return date_path

    def _generate_filename(self, original_filename: str) -> str:
        """
        生成唯一的文件名

        Args:
            original_filename: 原始文件名

        Returns:
            唯一的文件名（UUID + 原始扩展名）
        """
        # 获取文件扩展名
        ext = Path(original_filename).suffix.lower()
        if not ext:
            ext = ".bin"

        # 生成UUID文件名
        unique_id = uuid.uuid4().hex
        return f"{unique_id}{ext}"

    def _calculate_file_hash(self, file_content: bytes) -> str:
        """
        计算文件的SHA256哈希值

        Args:
            file_content: 文件内容

        Returns:
            文件的SHA256哈希值
        """
        return hashlib.sha256(file_content).hexdigest()

    def validate_file_type(self, file: UploadFile) -> Tuple[bool, str]:
        """
        验证文件类型

        Args:
            file: 上传的文件对象

        Returns:
            (是否有效, 错误信息)
        """
        if not file.filename:
            return False, "文件名不能为空"

        # 获取文件扩展名
        ext = Path(file.filename).suffix.lower().lstrip(".")

        # 检查扩展名是否支持
        if ext not in self.ALLOWED_EXTENSIONS:
            allowed = ", ".join(self.ALLOWED_EXTENSIONS.keys())
            return False, f"不支持的文件类型: .{ext}。支持的类型: {allowed}"

        # 检查Content-Type
        content_type = file.content_type or ""
        if content_type not in self.EXTENSION_MAP:
            # 某些客户端可能不发送正确的Content-Type，允许通过
            logger.warning(f"Unknown content type: {content_type} for file {file.filename}")
        elif self.EXTENSION_MAP[content_type] != ext:
            # Content-Type与扩展名不匹配
            return False, f"文件类型不匹配: 扩展名为 .{ext}，但Content-Type为 {content_type}"

        return True, ""

    async def validate_file_size(self, file: UploadFile) -> Tuple[bool, str]:
        """
        验证文件大小

        Args:
            file: 上传的文件对象

        Returns:
            (是否有效, 错误信息)
        """
        # 读取文件内容以获取大小
        content = await file.read()
        await file.seek(0)  # 重置文件指针

        file_size = len(content)
        max_size_mb = self.max_file_size / (1024 * 1024)

        if file_size > self.max_file_size:
            actual_size_mb = file_size / (1024 * 1024)
            return False, f"文件大小超出限制: {actual_size_mb:.2f}MB > {max_size_mb:.0f}MB"

        return True, ""

    async def save_file(
        self,
        file: UploadFile,
        subdirectory: Optional[str] = None
    ) -> dict:
        """
        保存上传的文件

        Args:
            file: 上传的文件对象
            subdirectory: 可选的子目录

        Returns:
            包含文件信息的字典:
            - file_id: 文件唯一ID
            - original_filename: 原始文件名
            - stored_filename: 存储的文件名
            - file_path: 文件存储路径
            - file_size: 文件大小（字节）
            - file_hash: 文件SHA256哈希值
            - content_type: 文件Content-Type
            - upload_time: 上传时间
        """
        # 验证文件类型
        is_valid, error_msg = self.validate_file_type(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # 验证文件大小
        is_valid, error_msg = await self.validate_file_size(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # 生成存储路径
        if subdirectory:
            storage_path = self.base_path / subdirectory
            storage_path.mkdir(parents=True, exist_ok=True)
        else:
            storage_path = self._generate_date_path()

        # 生成唯一文件名
        stored_filename = self._generate_filename(file.filename)
        file_path = storage_path / stored_filename

        # 读取文件内容
        content = await file.read()
        file_size = len(content)
        file_hash = self._calculate_file_hash(content)

        # 异步写入文件
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        logger.info(f"File saved: {file_path}")

        return {
            "file_id": uuid.uuid4(),
            "original_filename": file.filename,
            "stored_filename": stored_filename,
            "file_path": str(file_path),
            "relative_path": str(file_path.relative_to(self.base_path)),
            "file_size": file_size,
            "file_hash": file_hash,
            "content_type": file.content_type,
            "extension": Path(file.filename).suffix.lower().lstrip("."),
            "upload_time": datetime.now(),
        }

    async def save_file_content(
        self,
        content: bytes,
        filename: str,
        content_type: str,
        subdirectory: Optional[str] = None
    ) -> dict:
        """
        保存文件内容（直接传入字节内容）

        Args:
            content: 文件内容
            filename: 文件名
            content_type: Content-Type
            subdirectory: 可选的子目录

        Returns:
            包含文件信息的字典
        """
        # 检查文件大小
        file_size = len(content)
        if file_size > self.max_file_size:
            max_size_mb = self.max_file_size / (1024 * 1024)
            actual_size_mb = file_size / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超出限制: {actual_size_mb:.2f}MB > {max_size_mb:.0f}MB"
            )

        # 生成存储路径
        if subdirectory:
            storage_path = self.base_path / subdirectory
            storage_path.mkdir(parents=True, exist_ok=True)
        else:
            storage_path = self._generate_date_path()

        # 生成唯一文件名
        stored_filename = self._generate_filename(filename)
        file_path = storage_path / stored_filename

        # 计算哈希值
        file_hash = self._calculate_file_hash(content)

        # 异步写入文件
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        logger.info(f"File content saved: {file_path}")

        return {
            "file_id": uuid.uuid4(),
            "original_filename": filename,
            "stored_filename": stored_filename,
            "file_path": str(file_path),
            "relative_path": str(file_path.relative_to(self.base_path)),
            "file_size": file_size,
            "file_hash": file_hash,
            "content_type": content_type,
            "extension": Path(filename).suffix.lower().lstrip("."),
            "upload_time": datetime.now(),
        }

    def get_file_path(self, relative_path: str) -> Optional[Path]:
        """
        获取文件的完整路径

        Args:
            relative_path: 相对于基础路径的相对路径

        Returns:
            文件的完整路径，如果文件不存在则返回None
        """
        full_path = self.base_path / relative_path
        if full_path.exists() and full_path.is_file():
            return full_path
        return None

    async def read_file(self, relative_path: str) -> Optional[bytes]:
        """
        读取文件内容

        Args:
            relative_path: 相对于基础路径的相对路径

        Returns:
            文件内容，如果文件不存在则返回None
        """
        file_path = self.get_file_path(relative_path)
        if not file_path:
            return None

        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()

        return content

    def delete_file(self, relative_path: str) -> bool:
        """
        删除文件

        Args:
            relative_path: 相对于基础路径的相对路径

        Returns:
            是否删除成功
        """
        file_path = self.get_file_path(relative_path)
        if not file_path:
            return False

        try:
            file_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def file_exists(self, relative_path: str) -> bool:
        """
        检查文件是否存在

        Args:
            relative_path: 相对于基础路径的相对路径

        Returns:
            文件是否存在
        """
        return self.get_file_path(relative_path) is not None

    def get_file_info(self, relative_path: str) -> Optional[dict]:
        """
        获取文件信息

        Args:
            relative_path: 相对于基础路径的相对路径

        Returns:
            文件信息字典，如果文件不存在则返回None
        """
        file_path = self.get_file_path(relative_path)
        if not file_path:
            return None

        stat = file_path.stat()
        return {
            "file_path": str(file_path),
            "relative_path": relative_path,
            "file_size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "extension": file_path.suffix.lower().lstrip("."),
        }


# 创建全局存储服务实例
storage_service = StorageService()
