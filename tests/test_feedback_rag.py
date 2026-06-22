from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.database import Base, engine, init_db
from app.schemas.avatar import AvatarAgeRange, AvatarGender, AvatarStyle
from app.services.feedback_pipeline import build_rag_document, process_feedback_for_rag
from app.services.rag import build_rag_context, retrieve_rag_context
from main import app


@pytest.fixture
async def initialized_db():
    await init_db()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def _feedback_snapshot() -> dict:
    return {
        "feedbackId": 1,
        "rating": "DISLIKE",
        "reasons": ["FACE_SIMILARITY", "TOO_DIFFERENT"],
        "comment": "원본 얼굴 특징이 약하게 반영되었고 눈매가 달라짐",
        "feedbackUseConsent": True,
        "style": "STUDIO",
        "gender": "MALE",
        "ageRange": "AGE_20_PLUS",
        "promptVersion": "v1",
        "modelName": "gemini-test",
    }


def test_build_rag_document_uses_structured_format():
    document = build_rag_document(_feedback_snapshot())

    assert "style=STUDIO gender=MALE ageRange=AGE_20_PLUS" in document
    assert "rating=DISLIKE reasons=FACE_SIMILARITY,TOO_DIFFERENT" in document
    assert "feedback: 원본 얼굴 특징이 약하게 반영되었고 눈매가 달라짐" in document


@pytest.mark.asyncio
async def test_process_feedback_skips_without_consent(monkeypatch):
    ready = AsyncMock(return_value=True)
    embed = AsyncMock()
    monkeypatch.setattr("app.services.feedback_pipeline.is_feedback_collection_ready", ready)
    monkeypatch.setattr("app.services.feedback_pipeline.embed_text", embed)

    feedback = _feedback_snapshot()
    feedback["feedbackUseConsent"] = False

    await process_feedback_for_rag(feedback)

    ready.assert_not_called()
    embed.assert_not_called()


@pytest.mark.asyncio
async def test_process_feedback_skips_when_qdrant_unavailable(monkeypatch):
    ready = AsyncMock(return_value=False)
    embed = AsyncMock()
    monkeypatch.setattr("app.services.feedback_pipeline.is_feedback_collection_ready", ready)
    monkeypatch.setattr("app.services.feedback_pipeline.embed_text", embed)

    await process_feedback_for_rag(_feedback_snapshot())

    embed.assert_not_called()


def test_build_rag_context_separates_like_and_dislike_in_english():
    context = build_rag_context(
        [
            {
                "payload": {
                    "feedbackId": 1,
                    "rating": "LIKE",
                    "reasons": ["GOOD_QUALITY"],
                    "comment": "clean details",
                }
            },
            {
                "payload": {
                    "feedbackId": 2,
                    "rating": "DISLIKE",
                    "reasons": ["FACE_SIMILARITY"],
                    "comment": "eyes changed too much",
                }
            },
        ]
    )

    assert "Positive feedback patterns to preserve:" in context
    assert "Negative feedback patterns to avoid:" in context
    assert "Preserve clean details and high visual quality." in context
    assert "Preserve stronger facial similarity from the source image." in context
    assert "eyes changed too much" not in context


@pytest.mark.asyncio
async def test_retrieve_rag_context_falls_back_to_style_only(monkeypatch):
    ready = AsyncMock(return_value=True)
    embed = AsyncMock(return_value=[0.1] * 768)
    search = AsyncMock(
        side_effect=[
            [],
            [
                {
                    "payload": {
                        "feedbackId": 7,
                        "rating": "DISLIKE",
                        "reasons": ["TOO_DIFFERENT"],
                        "comment": "preserve facial features",
                    }
                }
            ],
        ],
    )
    monkeypatch.setattr("app.services.rag.is_feedback_collection_ready", ready)
    monkeypatch.setattr("app.services.rag.embed_text", embed)
    monkeypatch.setattr("app.services.rag.search_similar", search)

    result = await retrieve_rag_context(
        AvatarStyle.STUDIO,
        AvatarGender.MALE,
        AvatarAgeRange.AGE_20_PLUS,
    )

    assert search.await_count == 2
    assert search.await_args_list[0].kwargs["gender"] == "MALE"
    assert search.await_args_list[0].kwargs["age_range"] == "AGE_20_PLUS"
    assert search.await_args_list[1].kwargs["gender"] is None
    assert search.await_args_list[1].kwargs["age_range"] is None
    assert result.retrieved_feedback_ids == [7]
    assert "Negative feedback patterns to avoid:" in result.context


@pytest.mark.asyncio
async def test_ingest_feedback_registers_snapshot_background_task(monkeypatch, initialized_db):
    process = AsyncMock()
    monkeypatch.setattr("app.api.ai.feedbacks.process_feedback_for_rag", process)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/ai/feedbacks",
            json={
                "avatarId": 1,
                "jobId": None,
                "rating": "DISLIKE",
                "reasons": ["FACE_SIMILARITY", "TOO_DIFFERENT"],
                "comment": "원본 얼굴 특징이 약하게 반영됨",
                "trainingConsent": True,
                "feedbackUseConsent": True,
                "style": "STUDIO",
                "gender": "MALE",
                "ageRange": "AGE_20_PLUS",
                "promptVersion": "v1",
                "modelName": "gemini-test",
            },
        )

    assert response.status_code == 201
    process.assert_awaited_once()
    snapshot = process.await_args.args[0]
    assert snapshot == {
        "feedbackId": response.json()["feedbackId"],
        "rating": "DISLIKE",
        "reasons": ["FACE_SIMILARITY", "TOO_DIFFERENT"],
        "comment": "원본 얼굴 특징이 약하게 반영됨",
        "feedbackUseConsent": True,
        "style": "STUDIO",
        "gender": "MALE",
        "ageRange": "AGE_20_PLUS",
        "promptVersion": "v1",
        "modelName": "gemini-test",
    }
