"""Gera vídeos Juh Quiz: uma afirmação V/F, pausa de 3 s e explicação."""

from __future__ import annotations

import asyncio
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
import wave
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from PIL import Image, ImageDraw, ImageFont, ImageOps

from dados_vf import PERGUNTAS


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "saida_vf"
VOICE = "pt-BR-AntonioNeural"
RATE = "+10%"
VIDEO_W, VIDEO_H = 1080, 1920
IMAGE_BOX = (55, 500, 1025, 1470)  # left, top, right, bottom: 970 x 970 px
ANSWER_IMAGE_BOX = (55, 235, 1025, 1205)  # same 970 x 970 px on the answer screen
IMAGE_INSET = 50  # caricature appears 870 x 870 px inside the fixed 970 x 970 px frame
FPS = 30
DRIVE_BASE = "DESTINO:saida/Juh-Quiz-19/verdadeiro-ou-falso"
PALETTES = [
    {"name": "VERDE ELÉTRICO", "bg": ((10, 72, 50), (12, 116, 74)), "band": (10, 93, 62), "band2": (255, 196, 40), "accent": "#ffd84d", "card": "#f8f4e9", "ink": "#17251f", "muted": "#e5f5eb", "line": "#ffc42d"},
    {"name": "AZUL IMPACTO", "bg": ((8, 42, 113), (13, 93, 167)), "band": (8, 45, 128), "band2": (0, 205, 224), "accent": "#35d7df", "card": "#fff9e9", "ink": "#14253a", "muted": "#e0f4ff", "line": "#35d7df"},
    {"name": "VERMELHO SHOW", "bg": ((113, 20, 36), (180, 37, 47)), "band": (137, 17, 36), "band2": (255, 171, 31), "accent": "#ffb52e", "card": "#fff5e8", "ink": "#32151b", "muted": "#ffe9dc", "line": "#ffb52e"},
    {"name": "ROXO DIVERTIDO", "bg": ((71, 20, 111), (128, 23, 139)), "band": (79, 19, 122), "band2": (255, 191, 0), "accent": "#ffc43d", "card": "#fff8e9", "ink": "#2a1635", "muted": "#f4e4ff", "line": "#ffc43d"},
]
TRUE = "#18b844"
FALSE = "#ed2929"
CREAM = "#fff9ed"


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL)


def require_program(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"Não encontrei {name}. Instale o FFmpeg e tente novamente.")
    return path


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=font) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.ImageFont,
    fill: str,
    width: int,
    line_gap: int = 16,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrap_lines(draw, text, font, width)
    if max_lines and len(lines) > max_lines:
        raise ValueError(
            f"Texto longo demais para a tela ({len(lines)} linhas; máximo {max_lines}): {text}"
        )
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_gap
    return y


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill: str, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_height(lines: list[str], font: ImageFont.ImageFont, gap: int) -> int:
    return len(lines) * font.size + max(0, len(lines) - 1) * gap


def fit_text(draw: ImageDraw.ImageDraw, text: str, width: int, height: int,
             sizes=range(42, 19, -2), gap: int = 8) -> tuple[ImageFont.ImageFont, list[str]]:
    """Choose a readable font that fits; never clip text at the bottom of a card."""
    for size in sizes:
        font = load_font(size, True)
        lines = wrap_lines(draw, text, font, width)
        if text_height(lines, font, gap) <= height:
            return font, lines
    raise ValueError(f"Texto não cabe nem com fonte 20 px: {text[:90]}")


def make_paper(palette: dict) -> Image.Image:
    """Dark 3D quiz board with the red notebook header from the approved layout."""
    canvas = Image.new("RGB", (VIDEO_W, VIDEO_H), "#111519")
    draw = ImageDraw.Draw(canvas)
    top, bottom = (226, 17, 22), (155, 8, 18)
    for y in range(450):
        t = y / 449
        color = tuple(round(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        draw.line((0, y, VIDEO_W, y), fill=color)
    # Subtle charcoal pattern continues behind the cards.
    for x in range(-20, VIDEO_W + 80, 150):
        draw.ellipse((x, 465, x + 86, 551), outline="#1a2025", width=7)
        draw.line((x + 16, 480, x + 70, 534), fill="#1a2025", width=6)
        draw.line((x + 70, 480, x + 16, 534), fill="#1a2025", width=6)
    return canvas


def paste_optional_image(
    canvas: Image.Image,
    image_path: Path | None,
    box: tuple[int, int, int, int],
) -> None:
    # Imagem é realmente opcional: sem arquivo, não desenhe moldura nem placeholder.
    if image_path is None:
        return
    left, top, right, bottom = box
    box_w, box_h = right - left, bottom - top
    draw = ImageDraw.Draw(canvas)
    inner_w, inner_h = box_w, box_h
    if not image_path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {image_path.relative_to(ROOT)}")
    with Image.open(image_path) as source:
        source = ImageOps.exif_transpose(source).convert("RGBA")
        # Keep the whole illustration visible; long questions give the image less height.
        fitted = ImageOps.contain(source, (inner_w, inner_h), method=Image.Resampling.LANCZOS)
        mask = Image.new("L", fitted.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, fitted.width - 1, fitted.height - 1), radius=28, fill=255)
        px = left + (box_w - fitted.width) // 2
        py = top + (box_h - fitted.height) // 2
        canvas.paste(fitted, (px, py), mask)


def shadow_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int,
                fill: str, outline: str, width: int = 7, depth: int = 12) -> None:
    x1, y1, x2, y2 = box
    rounded(draw, (x1 + 7, y1 + depth, x2 + 7, y2 + depth), radius, "#07090b", "#07090b", 1)
    rounded(draw, box, radius, fill, outline, width)


def draw_3d_text(draw: ImageDraw.ImageDraw, text: str, center: tuple[int, int], font,
                 fill: str, stroke: str = "#090a0b", stroke_width: int = 8) -> None:
    bounds = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    x = center[0] - (bounds[2] - bounds[0]) / 2 - bounds[0]
    y = center[1] - (bounds[3] - bounds[1]) / 2 - bounds[1]
    draw.text((x + 3, y + 10), text, font=font, fill="#111111", stroke_width=stroke_width + 4,
              stroke_fill="#111111")
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke)


def draw_bulb(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    r = int(48 * scale)
    draw.ellipse((x - r, y - r, x + r, y + r), fill="#ffcf19", outline="#101215", width=max(4, int(8 * scale)))
    draw.arc((x - r + 10, y - r + 9, x + r - 10, y + r - 10), 195, 320,
             fill="#fff4a3", width=max(3, int(8 * scale)))
    draw.line((x - 14 * scale, y + 28 * scale, x - 10 * scale, y + 58 * scale), fill="#16181a", width=max(5, int(11 * scale)))
    draw.line((x + 14 * scale, y + 28 * scale, x + 10 * scale, y + 58 * scale), fill="#16181a", width=max(5, int(11 * scale)))
    draw.rounded_rectangle((x - 20 * scale, y + 50 * scale, x + 20 * scale, y + 81 * scale),
                           radius=int(8 * scale), fill="#22272d", outline="#08090b", width=max(3, int(6 * scale)))
    for yy in (60, 70, 80):
        draw.line((x - 16 * scale, y + yy * scale, x + 16 * scale, y + yy * scale),
                  fill="#777d83", width=max(2, int(3 * scale)))


def draw_header(canvas: Image.Image, question: dict, palette: dict, response: bool = False) -> None:
    draw = ImageDraw.Draw(canvas)
    # Deep extrusion behind the cream spiral notebook.
    shadow_card(draw, (194, 36, 886, 425), 45, "#fff7e9", "#17191b", 12, 22)
    draw.rounded_rectangle((207, 48, 874, 416), radius=38, outline="#ee2730", width=8)
    for y in range(128, 395, 54):
        draw.line((235, y, 850, y), fill="#eee7da", width=2)
    # Eight heavy spiral loops, matching the notebook reference.
    for x in range(267, 838, 82):
        draw.rounded_rectangle((x - 12, 22, x + 12, 105), radius=12, fill="#08090b", outline="#393c40", width=4)
        draw.rounded_rectangle((x - 5, 38, x + 5, 96), radius=6, fill="#25282c")
    draw_bulb(draw, 113, 178, 0.84)
    question_mark = load_font(230, True)
    draw_3d_text(draw, "?", (956, 191), question_mark, "#f42c34", stroke_width=10)
    draw_3d_text(draw, "VERDADEIRO", (540, 155), load_font(75, True), "#28df18", stroke_width=8)
    draw_3d_text(draw, "OU", (540, 238), load_font(53, True), "#fffdf8", stroke_width=6)
    draw_3d_text(draw, "FALSO?", (540, 321), load_font(85, True), "#fa343c", stroke_width=8)
    # Theme label floats above the statement card.
    fallback_theme = Path(str(question.get("imagem") or "DESAFIO DE HOJE")).stem.replace("_", " ")
    label = "RESPOSTA" if response else str(question.get("tema", fallback_theme)).upper()
    badge = (298, 420, 782, 500)
    rounded(draw, (badge[0] + 5, badge[1] + 10, badge[2] + 5, badge[3] + 10), 38, "#08090b")
    rounded(draw, badge, 38, "#15191d", "#ed2932", 8)
    font, lines = fit_text(draw, label, 430, 48, range(39, 22, -1), 0)
    label = " ".join(lines)
    bounds = draw.textbbox((0, 0), label, font=font)
    draw.text(((VIDEO_W - (bounds[2] - bounds[0])) / 2, 437 - bounds[1]), label, font=font,
              fill="#fffdf8", stroke_width=2, stroke_fill="#101215")


def draw_answer_button(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str,
                       color: str, symbol: str) -> None:
    x1, y1, x2, y2 = box
    dark = "#087d24" if color == TRUE else "#a90d20"
    shadow_card(draw, box, 54, dark, "#090b0d", 8, 13)
    # Keep the button face continuous: the old inset outlines left a horizontal
    # seam across the answer text and made the label look like it escaped its box.
    draw.rounded_rectangle((x1 + 7, y1 + 7, x2 - 7, y2 - 7), radius=47,
                           fill=color, outline="#ffffff", width=4)
    circle_size = min(y2 - y1 - 24, 112)
    cx, cy = x1 + 68, (y1 + y2) // 2
    draw.ellipse((cx - circle_size // 2, cy - circle_size // 2 + 5,
                  cx + circle_size // 2, cy + circle_size // 2 + 5), fill="#101215", outline="#070809", width=5)
    draw.ellipse((cx - circle_size // 2 + 8, cy - circle_size // 2 + 13,
                  cx + circle_size // 2 - 8, cy + circle_size // 2 - 3), fill=color, outline="#ffffff", width=4)
    if symbol == "✓":
        draw.line((cx - 25, cy + 1, cx - 6, cy + 21, cx + 31, cy - 25), fill="#ffffff", width=14, joint="curve")
    else:
        draw.line((cx - 22, cy - 22, cx + 22, cy + 22), fill="#ffffff", width=14)
        draw.line((cx + 22, cy - 22, cx - 22, cy + 22), fill="#ffffff", width=14)
    text_left, text_right = x1 + 137, x2 - 27
    text = label
    max_text_width = text_right - text_left - 16
    font = load_font(28, True)
    for size in range(53, 27, -1):
        candidate = load_font(size, True)
        candidate_bounds = draw.textbbox((0, 0), text, font=candidate, stroke_width=3)
        if candidate_bounds[2] - candidate_bounds[0] <= max_text_width:
            font = candidate
            break
    bounds = draw.textbbox((0, 0), text, font=font, stroke_width=3)
    tx = text_left + (text_right - text_left - (bounds[2] - bounds[0])) / 2 - bounds[0]
    ty = cy - (bounds[3] - bounds[1]) / 2 - bounds[1]
    draw.text((tx + 2, ty + 5), text, font=font, fill="#101215", stroke_width=7, stroke_fill="#101215")
    draw.text((tx, ty), text, font=font, fill="#ffffff", stroke_width=3, stroke_fill="#101215")


def draw_explanation_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str,
                          explanation: bool = False) -> tuple[int, int, int]:
    shadow_card(draw, box, 40, "#fff5e3", "#ffc51b", 9, 13)
    x1, y1, x2, y2 = box
    badge_w = 410
    badge = ((VIDEO_W - badge_w) // 2, y1 - 36, (VIDEO_W + badge_w) // 2, y1 + 43)
    rounded(draw, (badge[0] + 5, badge[1] + 9, badge[2] + 5, badge[3] + 9), 38, "#a86600")
    rounded(draw, badge, 38, "#ffc21a", "#f09f00", 5)
    heading = "EXPLICAÇÃO" if explanation else "EXPLICAÇÃO"
    font = load_font(38, True)
    bounds = draw.textbbox((0, 0), heading, font=font)
    draw.text(((VIDEO_W - (bounds[2] - bounds[0])) / 2, y1 - 24 - bounds[1]), heading,
              font=font, fill="#17110a", stroke_width=1, stroke_fill="#17110a")
    draw_bulb(draw, 87, y1 + 36, .45)
    return (x1 + 80, y1 + 67, x2 - 45)


def render_question_frame(question: dict, image_path: Path | None, palette: dict,
                          countdown: int | None = None) -> Image.Image:
    canvas = make_paper(palette)
    draw_header(canvas, question, palette)
    draw = ImageDraw.Draw(canvas)
    with_image = image_path is not None
    question_box = (28, 472, 1052, 712 if with_image else 888)
    shadow_card(draw, question_box, 42, "#fbfaf9", "#ed2932", 8, 12)
    text_top, text_bottom = question_box[1] + 31, question_box[3] - 25
    qfont, qlines = fit_text(draw, question["pergunta"], 920, text_bottom - text_top,
                             range(65, 31, -2), 8)
    line_height = qfont.size + 8
    y = text_top + max(0, (text_bottom - text_top - text_height(qlines, qfont, 8)) // 2)
    for line in qlines:
        bounds = draw.textbbox((0, 0), line, font=qfont)
        draw.text(((VIDEO_W - (bounds[2] - bounds[0])) / 2, y), line, font=qfont, fill="#15191d")
        y += line_height
    # The theme tab sits in front of the top edge of the statement card.
    draw_header(canvas, question, palette)
    if with_image:
        image_box = (28, 736, 1052, 1197)
        shadow_card(draw, image_box, 42, "#208de0", "#ffffff", 8, 9)
        inner = (image_box[0] + 8, image_box[1] + 8, image_box[2] - 8, image_box[3] - 8)
        paste_optional_image(canvas, image_path, inner)
        button_box = (38, 1230, 527, 1417)
        button_box2 = (553, 1230, 1042, 1417)
        explanation_box = (28, 1480, 1052, 1774)
    else:
        button_box = (38, 946, 527, 1152)
        button_box2 = (553, 946, 1042, 1152)
        explanation_box = (28, 1218, 1052, 1774)
    draw = ImageDraw.Draw(canvas)
    draw_answer_button(draw, button_box, "VERDADEIRO", TRUE, "✓")
    draw_answer_button(draw, button_box2, "FALSO", FALSE, "×")
    body_box = draw_explanation_card(draw, explanation_box,
                                     "A resposta será explicada depois do tempo para responder.")
    body_font, body_lines = fit_text(draw, "A resposta será explicada depois do tempo para responder.",
                                     body_box[2] - body_box[0], explanation_box[3] - body_box[1] - 84,
                                     range(34, 22, -2), 7)
    ty = explanation_box[1] + 100
    for line in body_lines:
        width = draw.textlength(line, font=body_font)
        draw.text(((VIDEO_W - width) / 2, ty), line, font=body_font, fill="#1a1b1b")
        ty += body_font.size + 7
    draw_header_brand(draw)
    if countdown is not None:
        if with_image:
            circle = (468, 897, 612, 1041)
            draw.ellipse(circle, fill="#ffd527", outline="#ffffff", width=8)
            label = str(countdown)
            font = load_font(100, True)
            bounds = draw.textbbox((0, 0), label, font=font)
            draw.text(((VIDEO_W - (bounds[2] - bounds[0])) / 2, 935 - bounds[1]), label,
                      font=font, fill="#101215")
        else:
            badge = (397, 892, 683, 944)
            rounded(draw, (badge[0] + 3, badge[1] + 5, badge[2] + 3, badge[3] + 5), 25, "#8e5500")
            rounded(draw, badge, 25, "#ffd527", "#ffffff", 4)
            label = f"{countdown} SEGUNDOS"
            font = load_font(28, True)
            bounds = draw.textbbox((0, 0), label, font=font)
            draw.text(((VIDEO_W - (bounds[2] - bounds[0])) / 2, 902 - bounds[1]), label,
                      font=font, fill="#101215")
    return canvas


def draw_header_brand(draw: ImageDraw.ImageDraw) -> None:
    draw.rounded_rectangle((374, 1812, 706, 1889), radius=19, fill="#ed1b2f", outline="#a9001c", width=5)
    font = load_font(46, True)
    bounds = draw.textbbox((0, 0), "Juh Quiz", font=font)
    draw.text(((VIDEO_W - (bounds[2] - bounds[0])) / 2, 1821 - bounds[1]), "Juh Quiz",
              font=font, fill="#fffdf8", stroke_width=2, stroke_fill="#a9001c")


def render_answer_frame(question: dict, image_path: Path | None, palette: dict,
                        explanation_visible: str, base_canvas: Image.Image | None = None,
                        full_explanation: str | None = None) -> Image.Image:
    canvas = make_paper(palette)
    draw_header(canvas, question, palette, response=True)
    draw = ImageDraw.Draw(canvas)
    with_image = image_path is not None
    question_box = (28, 472, 1052, 712 if with_image else 888)
    shadow_card(draw, question_box, 42, "#fbfaf9", "#ed2932", 8, 12)
    text_top, text_bottom = question_box[1] + 31, question_box[3] - 25
    qfont, qlines = fit_text(draw, question["pergunta"], 920, text_bottom - text_top, range(65, 31, -2), 8)
    y = text_top + max(0, (text_bottom - text_top - text_height(qlines, qfont, 8)) // 2)
    for line in qlines:
        bounds = draw.textbbox((0, 0), line, font=qfont)
        draw.text(((VIDEO_W - (bounds[2] - bounds[0])) / 2, y), line, font=qfont, fill="#15191d")
        y += qfont.size + 8
    draw_header(canvas, question, palette, response=True)
    if with_image:
        image_box = (28, 736, 1052, 1197)
        shadow_card(draw, image_box, 42, "#208de0", "#ffffff", 8, 9)
        paste_optional_image(canvas, image_path, (image_box[0] + 8, image_box[1] + 8,
                                                  image_box[2] - 8, image_box[3] - 8))
        answer_box = (38, 1230, 527, 1417)
        explanation_box = (28, 1480, 1052, 1774)
    else:
        answer_box = (38, 946, 527, 1152)
        explanation_box = (28, 1218, 1052, 1774)
    label = "VERDADEIRO" if question["verdadeiro"] else "FALSO"
    draw_answer_button(draw, answer_box, label, TRUE if question["verdadeiro"] else FALSE,
                       "✓" if question["verdadeiro"] else "×")
    full_text = full_explanation or explanation_visible or " "
    text_box = draw_explanation_card(draw, explanation_box, full_text, explanation=True)
    text_height_available = explanation_box[3] - explanation_box[1] - 108
    font, lines = fit_text(draw, full_text, text_box[2] - text_box[0], text_height_available,
                           range(39, 23, -1), 8)
    y = explanation_box[1] + 94
    for line in wrap_lines(draw, explanation_visible or " ", font, text_box[2] - text_box[0]):
        width = draw.textlength(line, font=font)
        draw.text(((VIDEO_W - width) / 2, y), line, font=font, fill="#17191b")
        y += font.size + 8
    draw_header_brand(draw)
    return canvas


def write_beep(path: Path, frequency: int = 950, seconds: float = 1.0) -> None:
    sample_rate = 48000
    total = int(sample_rate * seconds)
    beep_len = int(sample_rate * 0.12)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        frames = bytearray()
        for i in range(total):
            if i < beep_len:
                fade = min(1.0, i / (sample_rate * 0.008), (beep_len - i) / (sample_rate * 0.025))
                value = int(7000 * fade * math.sin(2 * math.pi * frequency * i / sample_rate))
            else:
                value = 0
            frames.extend(value.to_bytes(2, "little", signed=True) * 2)
        output.writeframes(frames)


_EDGE_CONFIGURED = False


def configure_edge() -> None:
    """Use the Edge Services endpoint and current Edge browser headers."""
    global _EDGE_CONFIGURED
    import edge_tts.constants as constants
    import edge_tts.communicate as communicate
    import edge_tts.voices as voices

    version = os.getenv("QUIZ_EDGE_VERSION", "").strip()
    if version and not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", version):
        raise ValueError("QUIZ_EDGE_VERSION precisa ser uma versão completa do Edge.")
    if not version:
        try:
            with urlopen("https://edgeupdates.microsoft.com/api/products?view=enterprise", timeout=15) as response:
                products = json.load(response)
            versions = [release["ProductVersion"]
                        for product in products if product.get("Product") == "Stable"
                        for release in product.get("Releases", [])
                        if release.get("Platform") == "Windows"
                        and release.get("Architecture") == "x64"
                        and re.fullmatch(r"\d+\.\d+\.\d+\.\d+", release.get("ProductVersion", ""))]
            version = max(versions, key=lambda item: tuple(map(int, item.split("."))))
        except (URLError, TimeoutError, OSError, ValueError, KeyError, TypeError):
            version = "155.0.4283.45"
            print("Catálogo Edge indisponível; usando a versão validada 155.0.4283.45.", flush=True)

    major = version.split(".")[0]
    constants.CHROMIUM_FULL_VERSION = version
    constants.CHROMIUM_MAJOR_VERSION = major
    constants.SEC_MS_GEC_VERSION = communicate.SEC_MS_GEC_VERSION = voices.SEC_MS_GEC_VERSION = "1-" + version
    base = "api.msedgeservices.com/tts/cognitiveservices"
    token = constants.TRUSTED_CLIENT_TOKEN
    constants.WSS_URL = communicate.WSS_URL = f"wss://{base}/websocket/v1?Ocp-Apim-Subscription-Key={token}"
    constants.VOICE_LIST = voices.VOICE_LIST = f"https://{base}/voices/list?Ocp-Apim-Subscription-Key={token}"
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        f"(KHTML, like Gecko) Chrome/{major}.0.0.0 Safari/537.36 Edg/{major}.0.0.0"
    )
    for headers in (constants.BASE_HEADERS, constants.WSS_HEADERS, constants.VOICE_HEADERS,
                    communicate.WSS_HEADERS, voices.VOICE_HEADERS):
        headers["User-Agent"] = user_agent
    communicate.WSS_HEADERS["Sec-WebSocket-Protocol"] = "synthesize"
    voices.VOICE_HEADERS["Authority"] = "api.msedgeservices.com"
    voices.VOICE_HEADERS["Sec-CH-UA"] = (
        f'" Not;A Brand";v="99", "Microsoft Edge";v="{major}", "Chromium";v="{major}"'
    )
    for module in (communicate, voices):
        context = getattr(module, "_SSL_CTX", None)
        if context is not None:
            context.load_default_certs()
    _EDGE_CONFIGURED = True
    print(f"Voz {VOICE}: conexão Edge Services, versão {version}, sem chave Azure.", flush=True)


async def synthesize(text: str, destination: Path) -> None:
    """Use Edge TTS with retries, then local Brazilian Portuguese speech as fallback."""
    try:
        import edge_tts
        from aiohttp import ClientError

        if not _EDGE_CONFIGURED:
            await asyncio.to_thread(configure_edge)

        temporary = destination.with_name(destination.name + ".parcial.mp3")
        waits = (5, 10, 20)
        for attempt in range(len(waits) + 1):
            try:
                temporary.unlink(missing_ok=True)
                communicator = edge_tts.Communicate(
                    text, VOICE, rate=RATE, connect_timeout=30, receive_timeout=90,
                )
                await communicator.save(str(temporary))
                if not temporary.exists() or temporary.stat().st_size == 0:
                    raise edge_tts.exceptions.NoAudioReceived("Áudio vazio.")
                if probe_duration(temporary) <= 0:
                    raise ValueError("Áudio da voz Antonio sem duração.")
                temporary.replace(destination)
                return
            except (ClientError, asyncio.TimeoutError, edge_tts.exceptions.NoAudioReceived) as error:
                temporary.unlink(missing_ok=True)
                if attempt == len(waits):
                    print(
                        f"Edge TTS falhou após {attempt + 1} tentativas ({error}). "
                        "Usando a voz local pt-br para concluir o vídeo.", flush=True
                    )
                    break
                wait = waits[attempt]
                print(f"Voz Antonio: tentativa {attempt + 1} falhou ({type(error).__name__}); nova tentativa em {wait}s.", flush=True)
                await asyncio.sleep(wait)
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
    except ImportError as error:
        print(f"Edge TTS indisponível ({error}). Usando a voz local pt-br.")

    local_wav = destination.with_name(f"{destination.stem}_local.wav")
    run([
        "espeak-ng", "-v", "pt-br", "-s", "165",
        "-w", str(local_wav), text,
    ])
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(local_wav), "-codec:a", "libmp3lame", "-q:a", "3",
        str(destination),
    ])


def probe_duration(path: Path) -> float:
    output = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        text=True,
    ).strip()
    return float(output)


def convert_to_wav(source: Path, destination: Path) -> None:
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-ar", "48000", "-ac", "2",
        "-c:a", "pcm_s16le", str(destination),
    ])


def build_segment(frame_path: Path, audio_path: Path, output_path: Path, duration: float) -> None:
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(frame_path),
        "-i", str(audio_path), "-t", f"{duration:.3f}", "-map", "0:v:0", "-map", "1:a:0",
        "-vf", "format=yuv420p", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-shortest", str(output_path),
    ])


def build_typewriter_segment(frame_dir: Path, audio_path: Path, output_path: Path,
                            duration: float, frame_rate: int = 8) -> None:
    pattern = str(frame_dir / "%04d.jpg")
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-framerate", str(frame_rate), "-i", pattern, "-i", str(audio_path),
        "-t", f"{duration:.3f}", "-map", "0:v:0", "-map", "1:a:0",
        "-vf", f"fps={FPS},tpad=stop_mode=clone:stop_duration={duration:.3f},format=yuv420p", "-r", str(FPS), "-c:v", "libx264",
        "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
        "-ar", "48000", "-ac", "2", "-af", f"apad=pad_dur={duration:.3f}", "-shortest", str(output_path),
    ])


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", normalized.lower()).strip("_")[:64] or "pergunta"


def resolve_image(value: str | None) -> Path | None:
    if not value:
        return None
    path = (ROOT / value).resolve()
    if ROOT not in path.parents:
        raise ValueError("O caminho da imagem precisa ficar dentro do repositório.")
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError(f"Formato de imagem não suportado: {path.suffix}")
    return path


def validate(question: dict, index: int) -> None:
    required = ("pergunta", "verdadeiro", "explicacao", "legenda", "hashtags")
    missing = [field for field in required if field not in question]
    if missing:
        raise ValueError(f"Pergunta {index}: faltam os campos {', '.join(missing)}.")
    if not isinstance(question["pergunta"], str) or not question["pergunta"].strip():
        raise ValueError(f"Pergunta {index}: o campo pergunta precisa ter texto.")
    if not isinstance(question["verdadeiro"], bool):
        raise ValueError(f"Pergunta {index}: verdadeiro precisa ser True ou False.")
    if not isinstance(question["explicacao"], str) or not question["explicacao"].strip():
        raise ValueError(f"Pergunta {index}: escreva uma explicação.")
    if not isinstance(question["legenda"], str) or not question["legenda"].strip():
        raise ValueError(f"Pergunta {index}: escreva a legenda para publicação.")
    tags = question["hashtags"]
    if not isinstance(tags, list) or not 1 <= len(tags) <= 4:
        raise ValueError(f"Pergunta {index}: informe de 1 a 4 hashtags relacionadas ao tema.")
    if any(not isinstance(tag, str) or not tag.startswith("#") or len(tag) < 2 for tag in tags):
        raise ValueError(f"Pergunta {index}: cada hashtag deve começar com #.")


def format_caption(question: dict) -> str:
    tags = " ".join(question["hashtags"])
    return f"CAPA_SEGUNDOS=2\n\n{question['legenda'].strip()}\n{tags}\n"


def make_one_video(index: int, question: dict, send_drive: bool = False, batch: str = "manual", palette: dict | None = None) -> tuple[Path, Path]:
    validate(question, index)
    palette = palette or PALETTES[((index - 1) // 3) % len(PALETTES)]
    image_path = resolve_image(question.get("imagem"))
    answer_label = "verdadeira" if question["verdadeiro"] else "falsa"
    answer_text = f"A resposta é {answer_label}. {question['explicacao']}"
    base_name = f"{index:02d}_{slugify(question['pergunta'])}"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="juh_vf_") as temp_dir:
        temp = Path(temp_dir)
        question_audio_mp3 = temp / "pergunta.mp3"
        answer_audio_mp3 = temp / "resposta.mp3"
        asyncio.run(synthesize(question["pergunta"], question_audio_mp3))
        asyncio.run(synthesize(answer_text, answer_audio_mp3))
        question_audio = temp / "pergunta.wav"
        answer_audio = temp / "resposta.wav"
        convert_to_wav(question_audio_mp3, question_audio)
        convert_to_wav(answer_audio_mp3, answer_audio)

        frames: list[Path] = []
        audios: list[Path] = []
        durations: list[float] = []
        question_frame = temp / "pergunta.png"
        render_question_frame(question, image_path, palette).save(question_frame)
        frames.append(question_frame)
        audios.append(question_audio)
        durations.append(probe_duration(question_audio))

        for count in (3, 2, 1):
            frame_path = temp / f"contagem_{count}.png"
            render_question_frame(question, image_path, palette, countdown=count).save(frame_path)
            beep_path = temp / f"bip_{count}.wav"
            write_beep(beep_path)
            frames.append(frame_path)
            audios.append(beep_path)
            durations.append(1.0)

        segments: list[Path] = []
        for part, (frame, audio, duration) in enumerate(zip(frames, audios, durations, strict=True), start=1):
            segment = temp / f"segmento_{part:02d}.mp4"
            build_segment(frame, audio, segment, duration)
            segments.append(segment)

        answer_duration = probe_duration(answer_audio)
        answer_frames = temp / "resposta_frames"
        answer_frames.mkdir()
        frame_rate = 8
        # Reserve the final second as a still frame so the complete last word
        # remains visible instead of disappearing on the video's last frame.
        typing_duration = max(1.0, len(question["explicacao"].strip()) / 15.0)
        frame_count = max(1, math.ceil(typing_duration * frame_rate))
        explanation = question["explicacao"].strip()
        answer_base = render_answer_frame(question, image_path, palette, " ")
        for frame_no in range(frame_count):
            visible_chars = min(len(explanation), round(len(explanation) * (frame_no + 1) / frame_count))
            frame_path = answer_frames / f"{frame_no + 1:04d}.jpg"
            render_answer_frame(question, image_path, palette, explanation[:visible_chars], answer_base,
                                explanation).save(
                frame_path, quality=88, optimize=True
            )
        answer_segment = temp / "segmento_resposta.mp4"
        build_typewriter_segment(answer_frames, answer_audio, answer_segment, max(answer_duration, typing_duration), frame_rate)
        segments.append(answer_segment)

        concat_file = temp / "segmentos.txt"
        concat_file.write_text("".join(f"file '{segment.as_posix()}'\n" for segment in segments), encoding="utf-8")
        video_path = OUTPUT_DIR / f"{base_name}.mp4"
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(video_path),
        ])

    caption_path = OUTPUT_DIR / f"{base_name}.txt"
    result_word = "Verdadeiro" if question["verdadeiro"] else "Falso"
    caption_path.write_text(format_caption(question), encoding="utf-8")
    if send_drive:
        run([
            "rclone", "copyto", str(video_path),
            f"{DRIVE_BASE}/execucao-{batch}/{video_path.name}",
        ])
        run([
            "rclone", "copyto", str(caption_path),
            f"{DRIVE_BASE}/execucao-{batch}/{caption_path.name}",
        ])
    return video_path, caption_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera vídeos Juh Quiz de Verdadeiro ou Falso.")
    parser.add_argument("--enviar-drive", action="store_true", help="envia MP4 e TXT para a pasta do Quiz-19 no Drive")
    parser.add_argument("--lote", default=None, help="identificador da pasta de execução no Drive")
    args = parser.parse_args()

    require_program("ffmpeg")
    require_program("ffprobe")
    if args.enviar_drive:
        require_program("rclone")
    if not PERGUNTAS:
        raise ValueError("Adicione pelo menos uma pergunta em dados_vf.py.")
    batch = args.lote or "manual"
    for index, question in enumerate(PERGUNTAS, start=1):
        palette = PALETTES[((index - 1) // 3) % len(PALETTES)]
        video, caption = make_one_video(index, question, args.enviar_drive, batch, palette)
        print(f"Criado: {video.name} e {caption.name}")
        if args.enviar_drive:
            print(f"Enviado ao Drive: {DRIVE_BASE}/execucao-{batch}/")


if __name__ == "__main__":
    main()
