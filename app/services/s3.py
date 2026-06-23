import asyncio

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


def _make_client():
    kwargs = {
        "aws_access_key_id": settings.s3_access_key_id,
        "aws_secret_access_key": settings.s3_secret_access_key,
        "region_name": settings.s3_region,
    }
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url
    return boto3.client("s3", **kwargs)


def _download_sync(s3_uri: str) -> bytes:
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"올바르지 않은 S3 URI 형식입니다: {s3_uri}")
    without_scheme = s3_uri[len("s3://") :]
    bucket, _, key = without_scheme.partition("/")
    if not bucket or not key:
        raise ValueError(f"S3 URI에서 버킷 또는 키를 파싱할 수 없습니다: {s3_uri}")
    client = _make_client()
    response = client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()


def _upload_sync(data: bytes, key: str, content_type: str) -> str:
    client = _make_client()
    client.put_object(Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=content_type)
    return f"s3://{settings.s3_bucket}/{key}"


async def download_image(s3_uri: str) -> bytes:
    return await asyncio.to_thread(_download_sync, s3_uri)


async def upload_image(data: bytes, avatar_id: int) -> str:
    return await asyncio.to_thread(_upload_sync, data, f"avatars/{avatar_id}.png", "image/png")


async def upload_text(data: str, key: str, content_type: str = "application/json") -> str:
    return await asyncio.to_thread(_upload_sync, data.encode("utf-8"), key, content_type)


__all__ = ["download_image", "upload_image", "upload_text", "ClientError"]
