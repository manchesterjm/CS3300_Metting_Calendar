#!/usr/bin/env python3
"""
Generate PWA icons for Meeting Scheduler app
Creates icons in various sizes required for Progressive Web App
"""

import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow library not installed")
    print("Install with: pip install Pillow")
    exit(1)


def create_icon(size, output_path):
    """
    Create a simple icon with gradient background and text.

    Args:
        size: Icon size (width and height in pixels)
        output_path: Path to save the icon
    """
    # Create image with gradient background
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)

    # Draw gradient background (teal to dark blue)
    for y in range(size):
        # Color interpolation from #1abc9c (teal) to #2c3e50 (dark blue)
        r = int(26 + (44 - 26) * (y / size))
        g = int(188 + (62 - 188) * (y / size))
        b = int(156 + (80 - 156) * (y / size))
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    # Add text "MS" (Meeting Scheduler)
    try:
        # Try to use a nice font
        font_size = int(size * 0.4)
        try:
            # Windows
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # Linux
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                # Fallback to default
                font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Draw text in center
    text = "MS"
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2

    # Draw text with shadow for better visibility
    shadow_offset = max(2, size // 100)
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=(0, 0, 0, 128), font=font)
    draw.text((x, y), text, fill=(255, 255, 255), font=font)

    # Add a subtle border
    border_width = max(1, size // 50)
    draw.rectangle(
        [(0, 0), (size - 1, size - 1)],
        outline=(255, 255, 255, 80),
        width=border_width
    )

    # Save icon
    img.save(output_path, 'PNG')
    print(f"[OK] Created {size}x{size} icon: {output_path}")


def main():
    """Generate all required PWA icons"""
    # Icon sizes required for PWA
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]

    # Create icons directory
    icons_dir = Path(__file__).parent / 'calendar_app' / 'static' / 'calendar_app' / 'icons'
    icons_dir.mkdir(parents=True, exist_ok=True)

    print("Generating PWA icons for Meeting Scheduler...")
    print(f"Output directory: {icons_dir}")
    print()

    # Generate each icon size
    for size in sizes:
        output_path = icons_dir / f'icon-{size}x{size}.png'
        create_icon(size, output_path)

    print()
    print(f"[OK] Successfully generated {len(sizes)} icons")
    print()
    print("Icons created:")
    for size in sizes:
        print(f"  - icon-{size}x{size}.png")
    print()
    print("PWA icons are ready! Your app can now be installed on mobile devices.")


if __name__ == '__main__':
    main()
