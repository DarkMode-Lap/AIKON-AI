from app.schemas.avatar import AvatarAgeRange, AvatarGender, AvatarStyle

_PROMPTS: dict[tuple[str, str, str], str] = {
    # STUDIO
    (AvatarStyle.STUDIO, AvatarAgeRange.AGE_0_7, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 밝고 깔끔한 스튜디오 사진 스타일의 남자아이 아바타 이미지를 생성해줘. "
        "배경은 단색으로 처리하고, 조명은 부드럽고 자연스럽게 해줘."
    ),
    (AvatarStyle.STUDIO, AvatarAgeRange.AGE_0_7, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 밝고 깔끔한 스튜디오 사진 스타일의 여자아이 아바타 이미지를 생성해줘. "
        "배경은 단색으로 처리하고, 조명은 부드럽고 자연스럽게 해줘."
    ),
    (AvatarStyle.STUDIO, AvatarAgeRange.AGE_8_13, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 깔끔하고 세련된 스튜디오 사진 스타일의 남자 청소년 아바타 이미지를 생성해줘. "
        "배경은 단색으로 처리하고, 전문 사진작가가 찍은 듯한 조명을 사용해줘."
    ),
    (AvatarStyle.STUDIO, AvatarAgeRange.AGE_8_13, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 깔끔하고 세련된 스튜디오 사진 스타일의 여자 청소년 아바타 이미지를 생성해줘. "
        "배경은 단색으로 처리하고, 전문 사진작가가 찍은 듯한 조명을 사용해줘."
    ),
    (AvatarStyle.STUDIO, AvatarAgeRange.AGE_14_19, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 세련되고 전문적인 스튜디오 사진 스타일의 남성 아바타 이미지를 생성해줘. "
        "배경은 단색, 조명은 전문 스튜디오 촬영 느낌으로 해줘."
    ),
    (AvatarStyle.STUDIO, AvatarAgeRange.AGE_14_19, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 세련되고 전문적인 스튜디오 사진 스타일의 여성 아바타 이미지를 생성해줘. "
        "배경은 단색, 조명은 전문 스튜디오 촬영 느낌으로 해줘."
    ),
    (AvatarStyle.STUDIO, AvatarAgeRange.AGE_20_PLUS, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 전문적이고 세련된 스튜디오 사진 스타일의 성인 남성 아바타 이미지를 생성해줘. "
        "배경은 흰색 또는 회색 단색, 조명은 전문 포트레이트 촬영 스타일로 해줘."
    ),
    (AvatarStyle.STUDIO, AvatarAgeRange.AGE_20_PLUS, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 전문적이고 세련된 스튜디오 사진 스타일의 성인 여성 아바타 이미지를 생성해줘. "
        "배경은 흰색 또는 회색 단색, 조명은 전문 포트레이트 촬영 스타일로 해줘."
    ),
    # ZOOTOPIA
    (AvatarStyle.ZOOTOPIA, AvatarAgeRange.AGE_0_7, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 주토피아 애니메이션 스타일의 귀여운 남자아이 동물 캐릭터 아바타를 생성해줘. "
        "디즈니 주토피아 특유의 색감과 둥글고 귀여운 얼굴 비율을 사용해줘."
    ),
    (AvatarStyle.ZOOTOPIA, AvatarAgeRange.AGE_0_7, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 주토피아 애니메이션 스타일의 귀여운 여자아이 동물 캐릭터 아바타를 생성해줘. "
        "디즈니 주토피아 특유의 색감과 둥글고 귀여운 얼굴 비율을 사용해줘."
    ),
    (AvatarStyle.ZOOTOPIA, AvatarAgeRange.AGE_8_13, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 주토피아 애니메이션 스타일의 활발한 남자 청소년 동물 캐릭터 아바타를 생성해줘. "
        "디즈니 주토피아의 생동감 있는 색채와 표정을 살려줘."
    ),
    (AvatarStyle.ZOOTOPIA, AvatarAgeRange.AGE_8_13, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 주토피아 애니메이션 스타일의 활발한 여자 청소년 동물 캐릭터 아바타를 생성해줘. "
        "디즈니 주토피아의 생동감 있는 색채와 표정을 살려줘."
    ),
    (AvatarStyle.ZOOTOPIA, AvatarAgeRange.AGE_14_19, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 주토피아 애니메이션 스타일의 멋진 남성 동물 캐릭터 아바타를 생성해줘. "
        "디즈니 주토피아 스타일의 세련된 외모와 개성 있는 표정을 표현해줘."
    ),
    (AvatarStyle.ZOOTOPIA, AvatarAgeRange.AGE_14_19, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 주토피아 애니메이션 스타일의 멋진 여성 동물 캐릭터 아바타를 생성해줘. "
        "디즈니 주토피아 스타일의 세련된 외모와 개성 있는 표정을 표현해줘."
    ),
    (AvatarStyle.ZOOTOPIA, AvatarAgeRange.AGE_20_PLUS, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 주토피아 애니메이션 스타일의 성숙한 남성 동물 캐릭터 아바타를 생성해줘. "
        "디즈니 주토피아의 세련되고 프로페셔널한 캐릭터 스타일로 표현해줘."
    ),
    (AvatarStyle.ZOOTOPIA, AvatarAgeRange.AGE_20_PLUS, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 주토피아 애니메이션 스타일의 성숙한 여성 동물 캐릭터 아바타를 생성해줘. "
        "디즈니 주토피아의 세련되고 프로페셔널한 캐릭터 스타일로 표현해줘."
    ),
    # TRADITIONAL_HANBOK
    (AvatarStyle.TRADITIONAL_HANBOK, AvatarAgeRange.AGE_0_7, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 전통 한복을 입은 귀여운 남자아이 아바타를 생성해줘. "
        "조선시대 전통 색상과 문양의 한복을 입히고, 배경은 전통 한국 배경으로 해줘."
    ),
    (AvatarStyle.TRADITIONAL_HANBOK, AvatarAgeRange.AGE_0_7, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 전통 한복을 입은 귀여운 여자아이 아바타를 생성해줘. "
        "조선시대 전통 색상과 문양의 한복을 입히고, 배경은 전통 한국 배경으로 해줘."
    ),
    (AvatarStyle.TRADITIONAL_HANBOK, AvatarAgeRange.AGE_8_13, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 전통 한복을 입은 남자 청소년 아바타를 생성해줘. "
        "전통 한복의 색상과 디자인을 충실히 재현하고 전통적인 분위기를 살려줘."
    ),
    (AvatarStyle.TRADITIONAL_HANBOK, AvatarAgeRange.AGE_8_13, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 전통 한복을 입은 여자 청소년 아바타를 생성해줘. "
        "전통 한복의 색상과 디자인을 충실히 재현하고 전통적인 분위기를 살려줘."
    ),
    (AvatarStyle.TRADITIONAL_HANBOK, AvatarAgeRange.AGE_14_19, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 전통 한복을 입은 젊은 남성 아바타를 생성해줘. "
        "전통 한복의 품격 있는 색상과 디자인으로 단정하고 아름다운 모습을 표현해줘."
    ),
    (AvatarStyle.TRADITIONAL_HANBOK, AvatarAgeRange.AGE_14_19, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 전통 한복을 입은 젊은 여성 아바타를 생성해줘. "
        "전통 한복의 품격 있는 색상과 디자인으로 단정하고 아름다운 모습을 표현해줘."
    ),
    (AvatarStyle.TRADITIONAL_HANBOK, AvatarAgeRange.AGE_20_PLUS, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 전통 한복을 입은 성인 남성 아바타를 생성해줘. "
        "고품격 전통 한복의 색상과 문양을 살리고 품격 있는 분위기로 표현해줘."
    ),
    (AvatarStyle.TRADITIONAL_HANBOK, AvatarAgeRange.AGE_20_PLUS, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 전통 한복을 입은 성인 여성 아바타를 생성해줘. "
        "고품격 전통 한복의 색상과 문양을 살리고 품격 있는 분위기로 표현해줘."
    ),
    # DISNEY_PIXAR
    (AvatarStyle.DISNEY_PIXAR, AvatarAgeRange.AGE_0_7, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 디즈니 픽사 3D 애니메이션 스타일의 귀여운 남자아이 캐릭터 아바타를 생성해줘. "
        "픽사 특유의 크고 표현력 있는 눈, 부드러운 피부 질감, 밝은 색감을 사용해줘."
    ),
    (AvatarStyle.DISNEY_PIXAR, AvatarAgeRange.AGE_0_7, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 디즈니 픽사 3D 애니메이션 스타일의 귀여운 여자아이 캐릭터 아바타를 생성해줘. "
        "픽사 특유의 크고 표현력 있는 눈, 부드러운 피부 질감, 밝은 색감을 사용해줘."
    ),
    (AvatarStyle.DISNEY_PIXAR, AvatarAgeRange.AGE_8_13, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 디즈니 픽사 3D 애니메이션 스타일의 활발한 남자 청소년 캐릭터 아바타를 생성해줘. "
        "픽사의 생동감 있는 캐릭터 디자인과 표정을 살려줘."
    ),
    (AvatarStyle.DISNEY_PIXAR, AvatarAgeRange.AGE_8_13, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 디즈니 픽사 3D 애니메이션 스타일의 활발한 여자 청소년 캐릭터 아바타를 생성해줘. "
        "픽사의 생동감 있는 캐릭터 디자인과 표정을 살려줘."
    ),
    (AvatarStyle.DISNEY_PIXAR, AvatarAgeRange.AGE_14_19, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 디즈니 픽사 3D 애니메이션 스타일의 멋진 남성 캐릭터 아바타를 생성해줘. "
        "픽사 스타일의 세련된 3D 렌더링과 개성 있는 표정을 표현해줘."
    ),
    (AvatarStyle.DISNEY_PIXAR, AvatarAgeRange.AGE_14_19, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 디즈니 픽사 3D 애니메이션 스타일의 멋진 여성 캐릭터 아바타를 생성해줘. "
        "픽사 스타일의 세련된 3D 렌더링과 개성 있는 표정을 표현해줘."
    ),
    (AvatarStyle.DISNEY_PIXAR, AvatarAgeRange.AGE_20_PLUS, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 디즈니 픽사 3D 애니메이션 스타일의 성인 남성 캐릭터 아바타를 생성해줘. "
        "픽사의 성숙하고 세련된 캐릭터 디자인으로 표현해줘."
    ),
    (AvatarStyle.DISNEY_PIXAR, AvatarAgeRange.AGE_20_PLUS, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 디즈니 픽사 3D 애니메이션 스타일의 성인 여성 캐릭터 아바타를 생성해줘. "
        "픽사의 성숙하고 세련된 캐릭터 디자인으로 표현해줘."
    ),
    # GHIBLI
    (AvatarStyle.GHIBLI, AvatarAgeRange.AGE_0_7, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 스튜디오 지브리 애니메이션 스타일의 귀여운 남자아이 캐릭터 아바타를 생성해줘. "
        "지브리 특유의 따뜻한 색감, 섬세한 손그림 스타일, 자연스러운 표정을 살려줘."
    ),
    (AvatarStyle.GHIBLI, AvatarAgeRange.AGE_0_7, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 스튜디오 지브리 애니메이션 스타일의 귀여운 여자아이 캐릭터 아바타를 생성해줘. "
        "지브리 특유의 따뜻한 색감, 섬세한 손그림 스타일, 자연스러운 표정을 살려줘."
    ),
    (AvatarStyle.GHIBLI, AvatarAgeRange.AGE_8_13, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 스튜디오 지브리 애니메이션 스타일의 활발한 남자 청소년 캐릭터 아바타를 생성해줘. "
        "지브리의 모험적이고 생동감 있는 캐릭터 표현을 살려줘."
    ),
    (AvatarStyle.GHIBLI, AvatarAgeRange.AGE_8_13, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 스튜디오 지브리 애니메이션 스타일의 활발한 여자 청소년 캐릭터 아바타를 생성해줘. "
        "지브리의 모험적이고 생동감 있는 캐릭터 표현을 살려줘."
    ),
    (AvatarStyle.GHIBLI, AvatarAgeRange.AGE_14_19, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 스튜디오 지브리 애니메이션 스타일의 젊은 남성 캐릭터 아바타를 생성해줘. "
        "지브리 특유의 시적이고 감성적인 표현으로 개성 있는 캐릭터를 만들어줘."
    ),
    (AvatarStyle.GHIBLI, AvatarAgeRange.AGE_14_19, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 스튜디오 지브리 애니메이션 스타일의 젊은 여성 캐릭터 아바타를 생성해줘. "
        "지브리 특유의 시적이고 감성적인 표현으로 개성 있는 캐릭터를 만들어줘."
    ),
    (AvatarStyle.GHIBLI, AvatarAgeRange.AGE_20_PLUS, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 스튜디오 지브리 애니메이션 스타일의 성인 남성 캐릭터 아바타를 생성해줘. "
        "지브리의 깊이 있고 성숙한 캐릭터 표현으로 자연스럽고 따뜻한 느낌을 살려줘."
    ),
    (AvatarStyle.GHIBLI, AvatarAgeRange.AGE_20_PLUS, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 스튜디오 지브리 애니메이션 스타일의 성인 여성 캐릭터 아바타를 생성해줘. "
        "지브리의 깊이 있고 성숙한 캐릭터 표현으로 자연스럽고 따뜻한 느낌을 살려줘."
    ),
    # LIGHT_ART
    (AvatarStyle.LIGHT_ART, AvatarAgeRange.AGE_0_7, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 빛과 색채를 활용한 아트 스타일의 귀여운 남자아이 아바타를 생성해줘. "
        "밝고 투명한 빛의 효과와 부드러운 색감으로 몽환적이고 아름다운 느낌을 표현해줘."
    ),
    (AvatarStyle.LIGHT_ART, AvatarAgeRange.AGE_0_7, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 빛과 색채를 활용한 아트 스타일의 귀여운 여자아이 아바타를 생성해줘. "
        "밝고 투명한 빛의 효과와 부드러운 색감으로 몽환적이고 아름다운 느낌을 표현해줘."
    ),
    (AvatarStyle.LIGHT_ART, AvatarAgeRange.AGE_8_13, AvatarGender.MALE): (
        "이 아이의 얼굴을 참고하여 빛과 색채를 활용한 아트 스타일의 남자 청소년 아바타를 생성해줘. "
        "다채로운 빛의 효과와 선명한 색감으로 생동감 있는 아트 작품 느낌을 살려줘."
    ),
    (AvatarStyle.LIGHT_ART, AvatarAgeRange.AGE_8_13, AvatarGender.FEMALE): (
        "이 아이의 얼굴을 참고하여 빛과 색채를 활용한 아트 스타일의 여자 청소년 아바타를 생성해줘. "
        "다채로운 빛의 효과와 선명한 색감으로 생동감 있는 아트 작품 느낌을 살려줘."
    ),
    (AvatarStyle.LIGHT_ART, AvatarAgeRange.AGE_14_19, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 빛과 색채를 활용한 아트 스타일의 젊은 남성 아바타를 생성해줘. "
        "빛과 그림자의 조화로 감각적이고 예술적인 분위기를 표현해줘."
    ),
    (AvatarStyle.LIGHT_ART, AvatarAgeRange.AGE_14_19, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 빛과 색채를 활용한 아트 스타일의 젊은 여성 아바타를 생성해줘. "
        "빛과 그림자의 조화로 감각적이고 예술적인 분위기를 표현해줘."
    ),
    (AvatarStyle.LIGHT_ART, AvatarAgeRange.AGE_20_PLUS, AvatarGender.MALE): (
        "이 사람의 얼굴을 참고하여 빛과 색채를 활용한 아트 스타일의 성인 남성 아바타를 생성해줘. "
        "세련된 빛의 효과와 예술적 색채로 고급스럽고 감각적인 분위기를 표현해줘."
    ),
    (AvatarStyle.LIGHT_ART, AvatarAgeRange.AGE_20_PLUS, AvatarGender.FEMALE): (
        "이 사람의 얼굴을 참고하여 빛과 색채를 활용한 아트 스타일의 성인 여성 아바타를 생성해줘. "
        "세련된 빛의 효과와 예술적 색채로 고급스럽고 감각적인 분위기를 표현해줘."
    ),
}


_FALLBACK_KEY = (AvatarStyle.STUDIO, AvatarAgeRange.AGE_20_PLUS, AvatarGender.MALE)


def build_prompt(
    style: AvatarStyle,
    age_range: AvatarAgeRange,
    gender: AvatarGender,
) -> tuple[str, str]:
    from app.core.config import settings

    key = (style, age_range, gender)
    prompt_text = _PROMPTS.get(key, _PROMPTS[_FALLBACK_KEY])
    return prompt_text, settings.gemini_prompt_version
