"""Generate a beautiful VoxFlow .ico icon."""
from PIL import Image, ImageDraw, ImageFilter
import os


def create_icon():
    """Create a premium VoxFlow icon at multiple resolutions."""
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        s = size / 256  # scale factor

        # Background — rounded square with purple gradient
        pad = max(1, int(8 * s))
        radius = max(2, int(48 * s))
        # Dark purple base
        draw.rounded_rectangle([pad, pad, size - pad, size - pad],
                               radius=radius, fill=(109, 40, 217, 255))
        # Lighter purple overlay on top half for gradient effect
        overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle([pad, pad, size - pad, size // 2 + int(30 * s)],
                             radius=radius, fill=(139, 92, 246, 120))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        cx, cy = size // 2, size // 2

        # ─── Sound wave arcs (behind mic) ───
        for i in range(3):
            wave_r = int((60 + i * 28) * s)
            width = max(1, int((4 - i) * s))
            alpha = 255 - i * 60
            if wave_r > 3 and width >= 1:
                draw.arc(
                    [cx + int(5 * s) - wave_r, cy - int(25 * s) - wave_r,
                     cx + int(5 * s) + wave_r, cy - int(25 * s) + wave_r],
                    start=300, end=60,
                    fill=(255, 255, 255, alpha), width=width,
                )

        # ─── Microphone body (capsule shape) ───
        mic_w = int(24 * s)
        mic_h = int(50 * s)
        mic_top = cy - int(42 * s)

        # Mic head (rounded top)
        draw.rounded_rectangle(
            [cx - mic_w, mic_top, cx + mic_w, mic_top + mic_h],
            radius=mic_w,
            fill=(255, 255, 255, 255),
        )

        # ─── Mic arc (U-shape holder) ───
        arc_w = int(34 * s)
        arc_top = mic_top + int(20 * s)
        arc_width = max(1, int(4 * s))
        draw.arc(
            [cx - arc_w, arc_top, cx + arc_w, arc_top + int(50 * s)],
            start=0, end=180,
            fill=(255, 255, 255, 230), width=arc_width,
        )

        # ─── Mic stand ───
        stand_w = max(1, int(3 * s))
        stand_top = arc_top + int(50 * s) // 2
        stand_bottom = cy + int(45 * s)
        draw.rectangle(
            [cx - stand_w, stand_top, cx + stand_w, stand_bottom],
            fill=(255, 255, 255, 230),
        )

        # ─── Mic base ───
        base_w = int(22 * s)
        base_h = max(1, int(4 * s))
        draw.rounded_rectangle(
            [cx - base_w, stand_bottom - base_h, cx + base_w, stand_bottom + base_h],
            radius=max(1, int(2 * s)),
            fill=(255, 255, 255, 230),
        )

        images.append(img)

    # Save as ICO
    icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(icon_dir, exist_ok=True)
    icon_path = os.path.join(icon_dir, "voxflow.ico")

    images[-1].save(icon_path, format="ICO",
                    sizes=[(s, s) for s in sizes],
                    append_images=images[:-1])

    # Also save PNG for shortcut/readme
    png_path = os.path.join(icon_dir, "voxflow_256.png")
    images[-1].save(png_path, format="PNG")

    print(f"✅ Icon: {icon_path}")
    print(f"✅ PNG:  {png_path}")
    return icon_path


if __name__ == "__main__":
    create_icon()
