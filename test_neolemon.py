#!/usr/bin/env python3
"""
Neolemon V3 Character Consistency Test
Tests whether Neolemon keeps the same child consistent across 4 different scenes.

Setup:
  1. pip3 install requests pillow
  2. Get a Segmind API key at segmind.com (free tier available)
  3. Paste your key below
  4. Run: python3 test_neolemon.py
  5. Open neolemon_comparison.jpg to see all 4 scenes side by side
"""

import requests, json, base64, os
from io import BytesIO

# ── CONFIG — paste your Segmind key here ──
SEGMIND_KEY = "SG_4ee069c38d7aa3ef"

CHARACTER = (
    "toddler girl aged 3, chubby round cheeks, small nose, large green eyes, "
    "medium length straight light brown hair with a small red bow clip on the right side, "
    "fair light skin, small freckles on nose, "
    "wearing a navy blue school dress with a white peter pan collar, "
    "white frilly ankle socks, small black Mary Jane shoes"
)

SCENES = [
    {
        "name": "1_wide_establishing",
        "prompt": CHARACTER + ". WIDE SHOT: tiny child walking through school gate, "
                  "suburban street behind her, morning light, full environment visible, "
                  "character is small in the frame. Children's picture book illustration, "
                  "modern gouache, warm muted palette, flat colour shapes, grain texture.",
    },
    {
        "name": "2_close_up_reaction",
        "prompt": CHARACTER + ". CLOSE-UP: face and shoulders only, wide eyes full of wonder, "
                  "joyful expression, soft warm background. Children's picture book illustration, "
                  "modern gouache, warm muted palette, flat colour shapes, grain texture.",
    },
    {
        "name": "3_medium_seated",
        "prompt": CHARACTER + ". MEDIUM SHOT: full body, child sitting cross-legged on "
                  "classroom floor reading a book, concentrating, warm classroom visible around her. "
                  "Children's picture book illustration, modern gouache, warm muted palette.",
    },
    {
        "name": "4_wide_action",
        "prompt": CHARACTER + ". WIDE ACTION SHOT: child running across playground with "
                  "arms wide open laughing, full body in motion, playground visible in background. "
                  "Children's picture book illustration, modern gouache, warm muted palette.",
    },
]

def generate(prompt, name, key):
    print(f"  [{name}] generating...", end=" ", flush=True)
    r = requests.post(
        "https://api.segmind.com/v1/consistent-character-AI-neolemon-v3",
        headers={"x-api-key": key, "Content-Type": "application/json"},
        json={"prompt": prompt, "steps": 20, "guidance_scale": 5,
              "width": 1024, "height": 1024, "seed": 42},
        timeout=120,
    )
    if r.status_code == 200:
        # Try to decode image from various response formats
        try:
            data = r.json()
            if "image" in data:
                img = base64.b64decode(data["image"])
            elif "data" in data:
                img = base64.b64decode(data["data"][0]["b64_json"])
            else:
                img = r.content
        except Exception:
            img = r.content
        fname = f"neolemon_{name}.png"
        with open(fname, "wb") as f:
            f.write(img)
        print(f"OK saved {fname}")
        return img
    else:
        print(f"ERROR {r.status_code}: {r.text[:150]}")
        return None

def make_grid(images, names):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Run: pip3 install Pillow")
        return
    sz, pad, lh = 512, 16, 30
    w = 2*sz + 3*pad
    h = 2*(sz+lh) + 3*pad
    sheet = Image.new("RGB", (w, h), (245, 240, 230))
    draw  = ImageDraw.Draw(sheet)
    for i, (img_data, name) in enumerate(zip(images, names)):
        if not img_data: continue
        col, row = i%2, i//2
        x = pad + col*(sz+pad)
        y = pad + row*(sz+lh+pad)
        img = Image.open(BytesIO(img_data)).resize((sz, sz))
        sheet.paste(img, (x, y))
        draw.text((x+8, y+sz+4), name.replace("_"," ").upper(), fill=(80,50,20))
    sheet.save("neolemon_comparison.jpg", quality=92)
    print("\nComparison sheet saved: neolemon_comparison.jpg")

def main():
    if "PASTE" in SEGMIND_KEY:
        print("Paste your Segmind key first. Get it at segmind.com/dashboard")
        return
    print(f"Generating {len(SCENES)} scenes @ ~$0.58 each = ~${len(SCENES)*0.58:.2f}\n")
    images, names = [], []
    for s in SCENES:
        images.append(generate(s["prompt"], s["name"], SEGMIND_KEY))
        names.append(s["name"])
    ok = sum(1 for i in images if i)
    print(f"\n{ok}/{len(SCENES)} generated")
    if ok >= 2:
        make_grid(images, names)
    print("\nCheck neolemon_comparison.jpg:")
    print("  Same face? Same hair/bow? Same outfit? Correct age?")
    print("  Wide shot actually wide? Style consistent?")

if __name__ == "__main__":
    main()
