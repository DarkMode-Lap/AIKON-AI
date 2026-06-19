import pytest

from app.schemas.avatar import AvatarAgeRange, AvatarGender, AvatarStyle
from app.services.prompt import build_prompt


@pytest.mark.parametrize(
    "style",
    [
        AvatarStyle.STUDIO,
        AvatarStyle.ZOOTOPIA,
        AvatarStyle.TRADITIONAL_HANBOK,
        AvatarStyle.DISNEY_PIXAR,
        AvatarStyle.GHIBLI,
        AvatarStyle.LIGHT_ART,
    ],
)
def test_build_prompt_returns_nonempty_for_all_styles(style):
    text, version = build_prompt(style, AvatarAgeRange.AGE_20_PLUS, AvatarGender.MALE)
    assert len(text) > 0
    assert version == "v1"


def test_build_prompt_differs_by_gender():
    male, _ = build_prompt(AvatarStyle.STUDIO, AvatarAgeRange.AGE_20_PLUS, AvatarGender.MALE)
    female, _ = build_prompt(AvatarStyle.STUDIO, AvatarAgeRange.AGE_20_PLUS, AvatarGender.FEMALE)
    assert male != female


def test_build_prompt_differs_by_age_range():
    child, _ = build_prompt(AvatarStyle.GHIBLI, AvatarAgeRange.AGE_0_7, AvatarGender.FEMALE)
    adult, _ = build_prompt(AvatarStyle.GHIBLI, AvatarAgeRange.AGE_20_PLUS, AvatarGender.FEMALE)
    assert child != adult
