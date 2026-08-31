import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import imageio_ffmpeg

BASE_DIR = r"D:\Android\PC Support\DroidDoctor"
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
AUDIO_DIR = os.path.join(TOOLS_DIR, "audio_reels")
OUTPUT_VIDEO = os.path.join(BASE_DIR, "release_v1.1.1", "DroidDoctor_Reels_Promo_v1.1.1.mp4")
TEMP_FRAME_DIR = os.path.join(TOOLS_DIR, "reels_frames")
os.makedirs(TEMP_FRAME_DIR, exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
FPS = 30

def get_font(size: int, bold: bool = False):
    font_names = [
        "seguisb.ttf" if bold else "segoeui.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "tahomabd.ttf" if bold else "tahoma.ttf"
    ]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            continue
    return ImageFont.load_default()

FONT_HERO = get_font(56, bold=True)
FONT_TITLE = get_font(44, bold=True)
FONT_CARD_TITLE = get_font(34, bold=True)
FONT_BODY = get_font(26, bold=False)
FONT_BODY_BOLD = get_font(28, bold=True)
FONT_BADGE = get_font(22, bold=True)
FONT_SMALL = get_font(20, bold=False)

ICON_PATH = os.path.join(BASE_DIR, "assets", "app_icon.png")
app_icon_img = None
if os.path.exists(ICON_PATH):
    try:
        app_icon_img = Image.open(ICON_PATH).convert("RGBA")
    except Exception:
        pass

def draw_gradient_background(draw, t: float):
    top_color = (8, 12, 20)
    bot_color = (15, 23, 42)
    for y in range(0, HEIGHT, 4):
        ratio = y / HEIGHT
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * ratio)
        draw.rectangle([(0, y), (WIDTH, y + 4)], fill=(r, g, b))

def draw_ambient_glow(img, cx, cy, radius, color):
    glow = Image.new("RGBA", (radius * 2, radius * 2), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for r in range(radius, 0, -8):
        alpha = int(color[3] * (1.0 - (r / radius) ** 0.5))
        gdraw.ellipse([(radius - r, radius - r), (radius + r, radius + r)], fill=(color[0], color[1], color[2], alpha))
    img.paste(glow, (cx - radius, cy - radius), glow)

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(bbox, radius=int(radius), fill=fill, outline=outline, width=int(width))

def draw_header(draw, img, subtitle_badge="ANDROID DIAGNOSTICS SUITE"):
    draw_rounded_rect(draw, (80, 70, 1000, 160), radius=22, fill=(22, 31, 48, 230), outline=(37, 99, 235, 120), width=2)
    if app_icon_img:
        icon_resized = app_icon_img.resize((64, 64), Image.Resampling.LANCZOS)
        img.paste(icon_resized, (110, 83), icon_resized)
    draw.text((195, 82), "DroidDoctor", fill=(255, 255, 255), font=get_font(32, bold=True))
    draw.text((195, 120), "v1.1.1 Pro • " + subtitle_badge, fill=(96, 165, 250), font=FONT_SMALL)
    draw_rounded_rect(draw, (810, 92, 970, 138), radius=10, fill=(37, 99, 235), outline=None)
    draw.text((832, 102), "OPEN SOURCE", fill=(255, 255, 255), font=get_font(18, bold=True))

def render_scene_1(t: float, duration: float) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 12, 20, 255))
    draw = ImageDraw.Draw(img)
    draw_gradient_background(draw, t)
    draw_ambient_glow(img, 540, 650, 450, (239, 68, 68, 50))
    draw_ambient_glow(img, 540, 1250, 400, (37, 99, 235, 60))
    draw_header(draw, img, "SYSTEM PROBLEM IDENTIFIER")
    
    pulse = 1.0 + 0.05 * math.sin(t * 5.0)
    center_y = 480
    draw_rounded_rect(draw, (540 - int(120 * pulse), center_y - int(120 * pulse), 540 + int(120 * pulse), center_y + int(120 * pulse)), radius=35, fill=(239, 68, 68, 40), outline=(239, 68, 68, 220), width=3)
    draw.text((540, center_y), "⚠️", fill=(255, 255, 255), font=get_font(72, bold=True), anchor="mm")
    
    draw.text((540, 720), "HP ANDROID KAMU", fill=(255, 255, 255), font=FONT_HERO, anchor="mm")
    draw.text((540, 790), "SERING LEMOT & DROP?", fill=(239, 68, 68), font=FONT_HERO, anchor="mm")
    
    cards = [
        ("🔋 Baterai Cepat Habis Tapi Gak Tahu Health Aslinya?", (245, 158, 11)),
        ("🗑️ Memori Cepat Penuh Karena Bloatware Bawaan?", (239, 68, 68)),
        ("❓ Mau Cek Jeroan Hardware Tapi Tertutup Sistem?", (147, 51, 234))
    ]
    
    start_y = 920
    for idx, (txt, clr) in enumerate(cards):
        y_pos = start_y + idx * 160
        offset = max(0.0, 1.0 - (t - idx * 0.4) * 3.0) * 200
        x_left = 80 + offset
        x_right = 1000 + offset
        draw_rounded_rect(draw, (int(x_left), y_pos, int(x_right), y_pos + 125), radius=18, fill=(22, 31, 48, 240), outline=(clr[0], clr[1], clr[2], 160), width=2)
        draw_rounded_rect(draw, (int(x_left) + 20, y_pos + 20, int(x_left) + 60, y_pos + 105), radius=8, fill=clr, outline=None)
        draw.text((int(x_left) + 80, y_pos + 45), txt, fill=(248, 250, 252), font=FONT_BODY_BOLD)
    
    draw_rounded_rect(draw, (180, 1550, 900, 1660), radius=25, fill=(37, 99, 235, 40), outline=(37, 99, 235, 180), width=2)
    draw.text((540, 1605), "SEKARANG ADA SOLUSI PRAKTISNYA! 👇", fill=(96, 165, 250), font=FONT_CARD_TITLE, anchor="mm")
    return img

def render_scene_2(t: float, duration: float) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 12, 20, 255))
    draw = ImageDraw.Draw(img)
    draw_gradient_background(draw, t)
    draw_ambient_glow(img, 540, 600, 500, (37, 99, 235, 80))
    draw_ambient_glow(img, 540, 1400, 450, (6, 182, 212, 70))
    draw_header(draw, img, "OFFLINE HARDWARE DATABASE")
    
    draw.text((540, 240), "SOLUSI SEMUA HP ANDROID", fill=(148, 163, 184), font=get_font(28, bold=True), anchor="mm")
    draw.text((540, 310), "DROIDDOCTOR v1.1.1 PRO", fill=(96, 165, 250), font=FONT_HERO, anchor="mm")
    
    draw_rounded_rect(draw, (80, 400, 1000, 720), radius=25, fill=(22, 31, 48, 245), outline=(6, 182, 212, 200), width=3)
    draw_rounded_rect(draw, (120, 440, 340, 490), radius=12, fill=(6, 182, 212, 40), outline=(6, 182, 212), width=1)
    draw.text((230, 465), "DATABASE OFFLINE", fill=(6, 182, 212), font=FONT_BADGE, anchor="mm")
    
    draw.text((540, 560), "50.835+", fill=(255, 255, 255), font=get_font(74, bold=True), anchor="mm")
    draw.text((540, 645), "Model Ponsel Terdaftar Secara Lengkap!", fill=(203, 213, 225), font=FONT_BODY_BOLD, anchor="mm")
    
    brands = ["Samsung Galaxy", "Xiaomi & Redmi", "POCO Series", "Infinix & Tecno", "OPPO & Realme", "Vivo & iQOO", "Google Pixel", "ASUS ROG"]
    grid_start_y = 770
    for idx, b in enumerate(brands):
        col = idx % 2
        row = idx // 2
        bx = 80 if col == 0 else 560
        by = grid_start_y + row * 95
        draw_rounded_rect(draw, (bx, by, bx + 440, by + 75), radius=16, fill=(15, 23, 42, 230), outline=(37, 99, 235, 140), width=2)
        draw.text((bx + 30, by + 37), "📱 " + b, fill=(241, 245, 249), font=FONT_BODY_BOLD, anchor="lm")
    
    draw_rounded_rect(draw, (80, 1230, 1000, 1660), radius=22, fill=(22, 31, 48, 230), outline=(37, 99, 235, 120), width=2)
    features = [
        ("⚡ Lookup Super Instan (<0.5 milidetik)", "Respon data hardware langsung tanpa loading."),
        ("📶 100% Mandiri & Bebas Internet", "Bisa digunakan sepenuhnya secara offline tanpa kuota."),
        ("🛡️ Deteksi Otomatis via USB & Wi-Fi", "Cukup colokkan HP, spesifikasi langsung muncul.")
    ]
    for i, (title, desc) in enumerate(features):
        fy = 1270 + i * 125
        draw.text((120, fy), title, fill=(255, 255, 255), font=FONT_BODY_BOLD)
        draw.text((120, fy + 40), desc, fill=(148, 163, 184), font=FONT_BODY)
    return img

def render_scene_3(t: float, duration: float) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 12, 20, 255))
    draw = ImageDraw.Draw(img)
    draw_gradient_background(draw, t)
    draw_ambient_glow(img, 540, 750, 500, (16, 185, 129, 90))
    draw_header(draw, img, "BATTERY & POWER DIAGNOSTICS")
    
    draw.text((540, 240), "DIAGNOSTIK KESEHATAN DAYA", fill=(148, 163, 184), font=get_font(28, bold=True), anchor="mm")
    draw.text((540, 310), "CEK KESEHATAN BATERAI (SoH)", fill=(16, 185, 129), font=FONT_HERO, anchor="mm")
    
    draw_rounded_rect(draw, (80, 390, 1000, 1180), radius=25, fill=(22, 31, 48, 245), outline=(16, 185, 129, 220), width=3)
    draw_rounded_rect(draw, (120, 430, 220, 480), radius=10, fill=(16, 185, 129, 40), outline=(16, 185, 129), width=1)
    draw.text((170, 455), "BAT", fill=(16, 185, 129), font=FONT_BADGE, anchor="mm")
    draw.text((245, 455), "Battery & Power Diagnostic", fill=(255, 255, 255), font=FONT_CARD_TITLE, anchor="lm")
    
    pb_width = 800
    pb_x = 120
    pb_y = 510
    draw_rounded_rect(draw, (pb_x, pb_y, pb_x + pb_width, pb_y + 16), radius=8, fill=(15, 23, 42))
    draw_rounded_rect(draw, (pb_x, pb_y, pb_x + int(pb_width * 0.66), pb_y + 16), radius=8, fill=(16, 185, 129))
    
    metrics = [
        ("Level Baterai Saat Ini", "66%", (255, 255, 255)),
        ("Kesehatan Baterai (SoH)", "Good (89% SoH)", (16, 185, 129)),
        ("Kapasitas Desain Pabrik", "5000 mAh", (96, 165, 250)),
        ("Kapasitas Riil Maksimal", "4428 mAh (Learned Actual)", (245, 158, 11)),
        ("Suhu & Voltase Sensor", "35.5°C • 3.90V", (255, 255, 255)),
        ("Status & Daya Pengisian", "Discharging (1.4W)", (241, 245, 249))
    ]
    for i, (k, v, clr) in enumerate(metrics):
        ry = 560 + i * 95
        draw.line([(120, ry), (960, ry)], fill=(30, 41, 59), width=1)
        draw.text((120, ry + 45), k, fill=(148, 163, 184), font=FONT_BODY_BOLD, anchor="lm")
        draw.text((960, ry + 45), v, fill=clr, font=FONT_BODY_BOLD, anchor="rm")
    
    draw_rounded_rect(draw, (80, 1230, 1000, 1660), radius=22, fill=(22, 31, 48, 230), outline=(37, 99, 235, 140), width=2)
    draw.text((540, 1290), "🌟 Kenapa Fitur Ini Sangat Penting?", fill=(255, 255, 255), font=FONT_CARD_TITLE, anchor="mm")
    benefits = [
        "✅ Menghitung State of Health (SoH) dari algoritma kernel riil.",
        "✅ Mendeteksi baterai drop/rusak sebelum membeli HP bekas.",
        "✅ Memantau suhu overheat & voltase pengisian fast charging."
    ]
    for i, b in enumerate(benefits):
        draw.text((120, 1370 + i * 85), b, fill=(203, 213, 225), font=FONT_BODY)
    return img

def render_scene_4(t: float, duration: float) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 12, 20, 255))
    draw = ImageDraw.Draw(img)
    draw_gradient_background(draw, t)
    draw_ambient_glow(img, 540, 750, 500, (239, 68, 68, 70))
    draw_header(draw, img, "SAFE DEBLOATER & SYSTEM CLEAN")
    
    draw.text((540, 240), "BERSIHKAN APLIKASI SAMPAH", fill=(148, 163, 184), font=get_font(28, bold=True), anchor="mm")
    draw.text((540, 310), "NON-ROOT SAFE DEBLOATER", fill=(239, 68, 68), font=FONT_HERO, anchor="mm")
    
    draw_rounded_rect(draw, (80, 390, 1000, 1150), radius=25, fill=(22, 31, 48, 245), outline=(239, 68, 68, 200), width=3)
    draw_rounded_rect(draw, (120, 430, 240, 480), radius=10, fill=(239, 68, 68, 40), outline=(239, 68, 68), width=1)
    draw.text((180, 455), "DEBLOAT", fill=(239, 68, 68), font=FONT_BADGE, anchor="mm")
    draw.text((265, 455), "System Package Manager", fill=(255, 255, 255), font=FONT_CARD_TITLE, anchor="lm")
    
    bloat_list = [
        ("com.miui.analytics (Xiaomi Tracking)", "Uninstalled (Clean)", (16, 185, 129)),
        ("com.facebook.system (Meta Services)", "Disabled (Safe)", (16, 185, 129)),
        ("com.google.android.apps.tachyon (Duo)", "Uninstalled (Clean)", (16, 185, 129)),
        ("com.tencent.ig (Old Game Leftover)", "Uninstalled (Clean)", (16, 185, 129)),
        ("com.android.systemui (Core System)", "🔒 PROTECTED (Anti-Bootloop)", (239, 68, 68)),
        ("com.android.settings (System Settings)", "🔒 PROTECTED (Anti-Bootloop)", (239, 68, 68))
    ]
    for i, (pkg, status, clr) in enumerate(bloat_list):
        ry = 510 + i * 100
        draw.line([(120, ry), (960, ry)], fill=(30, 41, 59), width=1)
        draw.text((120, ry + 45), pkg, fill=(226, 232, 240), font=FONT_BODY_BOLD, anchor="lm")
        draw.text((960, ry + 45), status, fill=clr, font=FONT_BODY_BOLD, anchor="rm")
    
    draw_rounded_rect(draw, (80, 1200, 1000, 1660), radius=22, fill=(22, 31, 48, 230), outline=(16, 185, 129, 140), width=2)
    draw.text((540, 1260), "🛡️ Garansi Keamanan 100% Tanpa Risiko", fill=(16, 185, 129), font=FONT_CARD_TITLE, anchor="mm")
    guards = [
        "🔒 Tanpa Root (User 0 Isolation) — Sistem /system tetap utuh.",
        "🔄 1-Click Restore — Aplikasi bisa dikembalikan kapan saja.",
        "📁 Storage Safe — Foto, WA & Dokumen pribadi dijamin aman."
    ]
    for i, g in enumerate(guards):
        draw.text((120, 1340 + i * 95), g, fill=(203, 213, 225), font=FONT_BODY)
    return img

def render_scene_5(t: float, duration: float) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 12, 20, 255))
    draw = ImageDraw.Draw(img)
    draw_gradient_background(draw, t)
    draw_ambient_glow(img, 540, 750, 500, (147, 51, 234, 90))
    draw_header(draw, img, "SCREEN MIRROR & HID CONTROL")
    
    draw.text((540, 240), "KENDALI PENUH DARI KOMPUTER", fill=(148, 163, 184), font=get_font(28, bold=True), anchor="mm")
    draw.text((540, 310), "SCREEN MIRROR 60 FPS", fill=(192, 132, 252), font=FONT_HERO, anchor="mm")
    
    draw_rounded_rect(draw, (240, 390, 840, 1280), radius=35, fill=(15, 23, 42, 250), outline=(192, 132, 252, 220), width=4)
    draw_rounded_rect(draw, (480, 415, 600, 430), radius=6, fill=(51, 65, 85))
    draw_rounded_rect(draw, (265, 455, 815, 1250), radius=20, fill=(8, 12, 20))
    
    draw_rounded_rect(draw, (300, 520, 780, 780), radius=18, fill=(37, 99, 235, 60), outline=(37, 99, 235), width=2)
    draw.text((540, 630), "⚡ 60 FPS HD STREAM", fill=(255, 255, 255), font=FONT_CARD_TITLE, anchor="mm")
    draw.text((540, 690), "Low-Latency Scrcpy 4.0", fill=(147, 197, 253), font=FONT_BODY, anchor="mm")
    
    draw_rounded_rect(draw, (300, 830, 780, 1180), radius=18, fill=(22, 31, 48, 230), outline=(16, 185, 129, 140), width=2)
    draw.text((540, 900), "⌨️ USB HID KEYBOARD", fill=(16, 185, 129), font=FONT_BODY_BOLD, anchor="mm")
    draw.text((540, 960), "Ketik pesan & main game", fill=(203, 213, 225), font=FONT_BODY, anchor="mm")
    draw.text((540, 1010), "langsung pakai keyboard PC!", fill=(203, 213, 225), font=FONT_BODY, anchor="mm")
    draw.text((540, 1100), "🔴 Screenshot & MP4 Record", fill=(239, 68, 68), font=FONT_BODY_BOLD, anchor="mm")
    
    features = ["🎮 Tanpa Lag", "📸 Lossless Screenshot", "🎥 Perekam Layar MP4", "⚡ Shortcut Home/Back"]
    for idx, f in enumerate(features):
        col = idx % 2
        row = idx // 2
        bx = 80 if col == 0 else 560
        by = 1350 + row * 95
        draw_rounded_rect(draw, (bx, by, bx + 440, by + 75), radius=16, fill=(22, 31, 48, 240), outline=(147, 51, 234, 140), width=2)
        draw.text((bx + 220, by + 37), f, fill=(241, 245, 249), font=FONT_BODY_BOLD, anchor="mm")
    return img

def render_scene_6(t: float, duration: float) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 12, 20, 255))
    draw = ImageDraw.Draw(img)
    draw_gradient_background(draw, t)
    draw_ambient_glow(img, 540, 600, 550, (37, 99, 235, 120))
    draw_ambient_glow(img, 540, 1300, 500, (16, 185, 129, 90))
    
    if app_icon_img:
        pulse = 1.0 + 0.04 * math.sin(t * 4.0)
        isz = int(180 * pulse)
        icon_resized = app_icon_img.resize((isz, isz), Image.Resampling.LANCZOS)
        img.paste(icon_resized, (540 - isz // 2, 260 - isz // 2), icon_resized)
    
    draw.text((540, 410), "DROIDDOCTOR", fill=(255, 255, 255), font=get_font(62, bold=True), anchor="mm")
    draw.text((540, 480), "Android Health & Diagnostics Suite", fill=(96, 165, 250), font=FONT_CARD_TITLE, anchor="mm")
    
    values = [
        ("🎉 100% GRATIS & OPEN SOURCE", (16, 185, 129)),
        ("📦 VERSI PORTABEL (Tanpa Perlu Install)", (37, 99, 235)),
        ("💻 SUPPORT WINDOWS 10 & 11 (64-bit)", (147, 51, 234)),
        ("📱 SUPPORT SEMUA MERK ANDROID", (245, 158, 11))
    ]
    for idx, (vtext, vcolor) in enumerate(values):
        vy = 560 + idx * 125
        draw_rounded_rect(draw, (80, vy, 1000, vy + 95), radius=18, fill=(22, 31, 48, 245), outline=(vcolor[0], vcolor[1], vcolor[2], 180), width=2)
        draw.text((540, vy + 47), vtext, fill=(255, 255, 255), font=FONT_BODY_BOLD, anchor="mm")
    
    cta_y = 1120
    draw_rounded_rect(draw, (80, cta_y, 1000, cta_y + 160), radius=28, fill=(37, 99, 235), outline=(96, 165, 250), width=3)
    draw.text((540, cta_y + 55), "DOWNLOAD GRATIS SEKARANG! ⬇️", fill=(255, 255, 255), font=FONT_HERO, anchor="mm")
    draw.text((540, cta_y + 115), "Tersedia di GitHub Releases", fill=(219, 234, 254), font=FONT_BODY, anchor="mm")
    
    draw_rounded_rect(draw, (80, 1340, 1000, 1620), radius=22, fill=(15, 23, 42, 240), outline=(51, 65, 85), width=2)
    draw.text((540, 1410), "🌐 Link Repository GitHub:", fill=(148, 163, 184), font=FONT_BODY, anchor="mm")
    draw.text((540, 1475), "github.com/RianSyrrus/DroidDoctor", fill=(96, 165, 250), font=FONT_CARD_TITLE, anchor="mm")
    draw.text((540, 1550), "Developed with Passion by RianSyrrus", fill=(100, 116, 139), font=FONT_SMALL, anchor="mm")
    return img

SCENE_RENDERERS = [
    (1, render_scene_1, 7.32),
    (2, render_scene_2, 10.32),
    (3, render_scene_3, 7.61),
    (4, render_scene_4, 7.94),
    (5, render_scene_5, 6.55),
    (6, render_scene_6, 7.49)
]

def generate_video():
    print("[1/3] Generating visual frames for all scenes...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    for f in os.listdir(TEMP_FRAME_DIR):
        if f.endswith(".png"):
            os.remove(os.path.join(TEMP_FRAME_DIR, f))
            
    frame_index = 0
    concat_audio_list = []
    
    for s_id, renderer, duration in SCENE_RENDERERS:
        total_frames = int(duration * FPS)
        print(f"  -> Rendering Scene {s_id} ({total_frames} frames)...")
        audio_file = os.path.join(AUDIO_DIR, f"scene{s_id}.mp3")
        concat_audio_list.append(audio_file)
        
        for f_num in range(total_frames):
            t = f_num / FPS
            frame_img = renderer(t, duration)
            frame_path = os.path.join(TEMP_FRAME_DIR, f"frame_{frame_index:06d}.png")
            frame_img.convert("RGB").save(frame_path, "PNG")
            frame_index += 1

    print(f"[2/3] Merging audio tracks ({len(concat_audio_list)} scenes)...")
    concat_txt_path = os.path.join(TOOLS_DIR, "concat_audio.txt")
    with open(concat_txt_path, "w", encoding="utf-8") as f:
        for a in concat_audio_list:
            f.write(f"file '{a.replace(chr(92), "/")}'\n")
            
    unified_audio_path = os.path.join(TOOLS_DIR, "unified_audio.mp3")
    if os.path.exists(unified_audio_path):
        os.remove(unified_audio_path)
        
    cmd_audio = [
        ffmpeg_exe, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt_path, "-c", "copy", unified_audio_path
    ]
    subprocess.run(cmd_audio, check=True)

    print(f"[3/3] Encoding final Reels video to MP4...")
    if os.path.exists(OUTPUT_VIDEO):
        os.remove(OUTPUT_VIDEO)
        
    frame_pattern = os.path.join(TEMP_FRAME_DIR, "frame_%06d.png")
    cmd_video = [
        ffmpeg_exe, "-y",
        "-r", str(FPS),
        "-i", frame_pattern,
        "-i", unified_audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_VIDEO
    ]
    subprocess.run(cmd_video, check=True)
    
    for f in os.listdir(TEMP_FRAME_DIR):
        if f.endswith(".png"):
            os.remove(os.path.join(TEMP_FRAME_DIR, f))
            
    print("\n=======================================================")
    print("[SUCCESS] Reels Promo Video created successfully!")
    print(f"File Path : {OUTPUT_VIDEO}")
    print(f"File Size : {os.path.getsize(OUTPUT_VIDEO) / (1024*1024):.2f} MB")
    print("=======================================================")

if __name__ == "__main__":
    generate_video()
