from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AvatarGenerationJob(Base):
    __tablename__ = "avatar_generation_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    avatar_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    style: Mapped[str] = mapped_column(String(30), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    age_range: Mapped[str] = mapped_column(String(15), nullable=False)
    source_image_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    callback_url: Mapped[str] = mapped_column(String(500), nullable=False)
    generated_image_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    prompt_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class AvatarFeedback(Base):
    __tablename__ = "avatar_feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    avatar_id: Mapped[int] = mapped_column(Integer, nullable=False)
    job_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("avatar_generation_jobs.id"), nullable=True
    )
    rating: Mapped[str] = mapped_column(String(10), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    training_consent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    feedback_use_consent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    style: Mapped[str] = mapped_column(String(30), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    age_range: Mapped[str] = mapped_column(String(15), nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    reasons: Mapped[list[AvatarFeedbackReason]] = relationship(
        "AvatarFeedbackReason", back_populates="feedback", cascade="all, delete-orphan"
    )


class AvatarFeedbackReason(Base):
    __tablename__ = "avatar_feedback_reasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feedback_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("avatar_feedbacks.id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String(50), nullable=False)

    feedback: Mapped[AvatarFeedback] = relationship("AvatarFeedback", back_populates="reasons")
