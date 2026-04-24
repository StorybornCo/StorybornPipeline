#!/usr/bin/env python3
"""
Storyborn Style Creator
Run this once to create your permanent Recraft style ID.

Usage:
  1. pip install fal-client
  2. Put your 4 reference images in the same folder as this script
  3. Run: python3 create_style.py
  4. Copy the style ID it prints at the end
"""

import os
import glob

# ── CONFIG — paste your fal.ai key here ──
FAL_KEY = "8dbfa2c7-693e-48aa-800d-a898ec380935:76aa3b1cee5d23964fd0a9406bd4ee11"

# Set BEFORE importing fal_client
os.environ["FAL_KEY"] = FAL_KEY

import fal_client

# Put your reference images in the same folder as this script
IMAGE_FOLDER = "."  # current folder

def main():
    # Find all images in the folder
    extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.JPG", "*.JPEG", "*.PNG"]
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(IMAGE_FOLDER, ext)))
    
    # Filter out any non-reference files (skip this script itself etc)
    images = [f for f in images if os.path.isfile(f)]
    
    if len(images) < 2:
        print("❌ No images found in current folder.")
        print("   Save your reference images (JPG/PNG) in the same folder as this script.")
        print("   Recommended: 4-8 images showing the illustration style you want.")
        return
    
    print(f"✓ Found {len(images)} reference images:")
    for img in images:
        size_kb = os.path.getsize(img) // 1024
        print(f"  • {os.path.basename(img)} ({size_kb}KB)")
    
    # Upload all images to fal storage
    print("\n→ Uploading images to fal.ai storage...")
    uploaded_urls = []
    for img_path in images:
        print(f"  Uploading {os.path.basename(img_path)}...", end=" ", flush=True)
        with open(img_path, "rb") as f:
            url = fal_client.upload(f.read(), content_type="image/jpeg")
        uploaded_urls.append(url)
        print(f"✓")
    
    print(f"\n✓ Uploaded {len(uploaded_urls)} images")
    
    # Resize images to under 5MB limit and build ZIP
    print("\n→ Resizing images for Recraft's 5MB limit...")
    try:
        from PIL import Image
    except ImportError:
        print("  Installing Pillow...")
        os.system("pip3 install Pillow -q")
        from PIL import Image
    import io, zipfile

    MAX_BYTES = 4 * 1024 * 1024  # 4MB safety margin
    resized = []
    for i, img_path in enumerate(images):
        img = Image.open(img_path).convert("RGB")
        w, h = img.size
        if w > 2048 or h > 2048:
            img.thumbnail((2048, 2048), Image.LANCZOS)
        quality = 90
        while True:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            if buf.tell() <= MAX_BYTES or quality <= 40:
                break
            quality -= 10
        buf.seek(0)
        data = buf.read()
        resized.append((f"style_ref_{i+1:02d}.jpg", data))
        print(f"  OK {os.path.basename(img_path)} -> {len(data)//1024}KB (quality={quality})")

    print("\n-> Building ZIP archive...")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in resized:
            zf.writestr(name, data)
    zip_bytes = zip_buffer.getvalue()
    
    print(f"✓ ZIP created: {len(zip_bytes)//1024}KB with {len(images)} images")
    
    # Upload ZIP to fal storage
    print("\n→ Uploading ZIP to fal.ai storage...")
    zip_url = fal_client.upload(zip_bytes, content_type="application/zip")
    print(f"✓ ZIP uploaded: {zip_url}")
    
    # Submit Recraft Create Style job
    print("\n→ Submitting Recraft Create Style training job...")
    print("  This takes 5-10 minutes...")
    
    result = fal_client.subscribe(
        "fal-ai/recraft/v3/create-style",
        arguments={
            "images_data_url": zip_url,
            "style": "digital_illustration/grain",
        },
        with_logs=True,
        on_queue_update=lambda update: print(f"  Status: {update.status}") if hasattr(update, 'status') else None,
    )
    
    print("\n" + "="*50)
    print("✅ STYLE CREATED SUCCESSFULLY!")
    print("="*50)
    
    # Extract style ID
    style_id = None
    if hasattr(result, 'style_id'):
        style_id = result.style_id
    elif isinstance(result, dict):
        style_id = result.get('style_id') or result.get('id') or str(result)
    else:
        style_id = str(result)
    
    print(f"\nYour Storyborn Style ID:")
    print(f"\n  {style_id}\n")
    print("Copy this and paste it into the Storyborn pipeline.")
    print("="*50)

if __name__ == "__main__":
    main()
