#!/usr/bin/env python3
"""타이틀 화면 로고와 로고 뒤 배경을 만든다.

크기는 기본 로고(images/misc/logo.png)와 같은 600x200이다.

  python utils/samguk/make_logo.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONT = ROOT / "fonts" / "DroidSansFallbackFull.ttf"
OUT_DIR = ROOT / "data" / "samguk" / "images" / "misc"
SIZE = (600, 200)
TITLE = "삼국"
SUBTITLE = "한강의 패권"
GOLD = (232, 196, 104, 255)
INK = (40, 22, 10, 255)


def draw_text(draw, text, font, center_y, fill, stroke):
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    x = (SIZE[0] - (right - left)) // 2 - left
    y = center_y - (bottom - top) // 2 - top
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=INK)


def make_logo():
    img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_text(draw, TITLE, ImageFont.truetype(str(FONT), 112), 78, GOLD, 6)
    draw_text(draw, SUBTITLE, ImageFont.truetype(str(FONT), 40), 164, GOLD, 4)
    return img


def make_background(logo):
    # 글자 모양을 따라 번지는 어두운 그림자. 밝은 타이틀 배경 위에서도 글자가 읽히게 한다.
    alpha = logo.split()[3].filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(12))
    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda a: min(200, a)))
    return shadow


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    logo = make_logo()
    logo.save(OUT_DIR / "samguk-logo.png")
    make_background(logo).save(OUT_DIR / "samguk-logo-bg.png")
    print(f"wrote samguk-logo.png and samguk-logo-bg.png in {OUT_DIR.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
