from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.services import embedding, gemini_image


@pytest.mark.asyncio
async def test_embed_text_uses_supported_model_with_768_dimensions(monkeypatch):
    embed_content = Mock(
        return_value=SimpleNamespace(
            embeddings=[SimpleNamespace(values=[0.1] * 768)],
        )
    )
    monkeypatch.setattr(
        embedding,
        "_get_client",
        lambda: SimpleNamespace(models=SimpleNamespace(embed_content=embed_content)),
    )

    vector = await embedding.embed_text("test")

    assert len(vector) == 768
    assert embed_content.call_args.kwargs["model"] == "gemini-embedding-001"
    assert embed_content.call_args.kwargs["config"].output_dimensionality == 768


@pytest.mark.parametrize(
    ("source_uri", "expected"),
    [
        ("s3://aikon/sources/1.jpg", "image/jpeg"),
        ("s3://aikon/sources/1.png", "image/png"),
        ("s3://aikon/sources/1.webp", "image/webp"),
    ],
)
def test_infer_image_mime_type(source_uri, expected):
    assert gemini_image.infer_image_mime_type(source_uri) == expected


@pytest.mark.asyncio
async def test_generate_avatar_image_reports_finish_reason(monkeypatch):
    generate_content = AsyncMock(
        return_value=SimpleNamespace(
            candidates=[
                SimpleNamespace(
                    content=None,
                    finish_reason="SAFETY",
                    finish_message="blocked",
                    safety_ratings=["unsafe"],
                )
            ],
            prompt_feedback=None,
        )
    )
    monkeypatch.setattr(
        gemini_image,
        "_get_client",
        lambda: SimpleNamespace(
            aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
        ),
    )

    with pytest.raises(ValueError, match="finishReason=SAFETY"):
        await gemini_image.generate_avatar_image(b"jpeg", "prompt", "image/jpeg")

    image_part = generate_content.call_args.kwargs["contents"][0]
    assert image_part.inline_data.mime_type == "image/jpeg"


@pytest.mark.asyncio
async def test_generate_avatar_image_returns_raw_image_bytes(monkeypatch):
    image_bytes = b"\x89PNG\r\n\x1a\n"
    generate_content = AsyncMock(
        return_value=SimpleNamespace(
            candidates=[
                SimpleNamespace(
                    content=SimpleNamespace(
                        parts=[
                            SimpleNamespace(
                                inline_data=SimpleNamespace(data=image_bytes),
                            )
                        ]
                    )
                )
            ]
        )
    )
    monkeypatch.setattr(
        gemini_image,
        "_get_client",
        lambda: SimpleNamespace(
            aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
        ),
    )

    result = await gemini_image.generate_avatar_image(b"source", "prompt", "image/png")

    assert result == image_bytes
