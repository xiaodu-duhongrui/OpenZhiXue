import uuid
from datetime import datetime
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.config import settings


class StorageClient:
    _instance: Optional[Minio] = None

    @classmethod
    def get_instance(cls) -> Minio:
        if cls._instance is None:
            cls._instance = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        return cls._instance

    @classmethod
    async def ensure_buckets(cls):
        client = cls.get_instance()
        buckets = [
            settings.MINIO_BUCKET_VIDEOS,
            settings.MINIO_BUCKET_RESOURCES,
        ]
        for bucket in buckets:
            try:
                if not client.bucket_exists(bucket):
                    client.make_bucket(bucket)
            except S3Error as e:
                pass

    @classmethod
    def get_presigned_url(
        cls,
        bucket_name: str,
        object_name: str,
        expires: int = 3600,
    ) -> str:
        client = cls.get_instance()
        from datetime import timedelta
        url = client.presigned_get_object(
            bucket_name,
            object_name,
            expires=timedelta(seconds=expires),
        )
        return url

    @classmethod
    def upload_file(
        cls,
        bucket_name: str,
        object_name: str,
        file_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        client = cls.get_instance()
        client.fput_object(
            bucket_name,
            object_name,
            file_path,
            content_type=content_type,
        )
        return f"{bucket_name}/{object_name}"


def get_storage() -> Minio:
    return StorageClient.get_instance()
