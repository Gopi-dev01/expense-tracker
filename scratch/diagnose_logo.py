import os
import imghdr
import mimetypes

static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
logo_path = os.path.join(static_dir, "images", "logo.png")
css_path = os.path.join(static_dir, "css", "style.css")

output = []

# 1. Check logo image
output.append(f"Logo Path: {logo_path}")
if os.path.exists(logo_path):
    size = os.path.getsize(logo_path)
    output.append(f"Logo exists, size: {size} bytes")
    # Verify image type
    img_type = imghdr.what(logo_path)
    output.append(f"Image header type (imghdr): {img_type}")
    # Read first few bytes to check if it looks like HTML or png
    with open(logo_path, "rb") as f:
        head = f.read(50)
        output.append(f"First 50 bytes of logo: {head!r}")
else:
    output.append("Logo does NOT exist!")

# 2. Check css file for .logo
output.append("\nCSS search for '.logo':")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if ".logo" in line:
            output.append(f"Line {idx+1}: {line.strip()}")
            # Print context of 5 lines after
            for i in range(1, 10):
                if idx + i < len(lines):
                    output.append(f"  Line {idx+1+i}: {lines[idx+i].strip()}")
else:
    output.append("CSS file does NOT exist!")

with open(os.path.join(os.path.dirname(__file__), "diagnostic_result.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(output))
print("Diagnostic script run completed.")
