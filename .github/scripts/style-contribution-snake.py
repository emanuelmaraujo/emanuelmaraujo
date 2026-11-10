"""Frame the generated Platane contribution snake as a telemetry panel."""

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
PALETTE = ("#192340", "#364681", "#5860b9", "#8374ef", "#c09dff")

FRAME = """<g xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
<defs>
 <linearGradient id="telemetry-bg" x2="1" y2="1"><stop stop-color="#091122"/><stop offset="1" stop-color="#1b1736"/></linearGradient>
 <linearGradient id="pulse-tail"><stop stop-color="#4ea2ff"/><stop offset="1" stop-color="#b18dff"/></linearGradient>
</defs>
<path d="M-2 -51H851l12 12v205l-14 14H-15V-38z" fill="url(#telemetry-bg)" stroke="#43537b"/>
<path d="M-2 -51h103M752 180h97l14-14" fill="none" stroke="#68f8e7" stroke-width="1.5"/>
<path d="M1 -23h844M1 162h844" stroke="#3a4b70"/>
<circle cx="6" cy="-35" r="3.5" fill="#68f8e7"/>
<g font-family="monospace" font-size="12" letter-spacing="1.25">
 <text x="18" y="-31" fill="#edf4ff">06 / CONTRIBUTION TELEMETRY</text>
 <text x="845" y="-31" text-anchor="end" fill="#c5b7ff">GITHUB ACTIVITY / 52 WEEKS</text>
 <text x="1" y="175" fill="#b8c8ec">CONTRIBUTION INTENSITY</text>
 <text x="845" y="175" text-anchor="end" fill="#68f8e7">NEON TRACE</text>
</g>
</g>"""

def render(source: Path, target: Path) -> None:
    root = ET.parse(source).getroot()
    style = root.find(f"{{{SVG}}}style")
    if root.tag != f"{{{SVG}}}svg" or style is None:
        raise ValueError("Expected the Platane/snk SVG format")
    # Keep the generator's coordinate system and make room for the HUD.
    x, y, width, height = map(float, root.attrib["viewBox"].split())
    if (x, y, width, height) != (-16, -32, 880, 192):
        raise ValueError("Unexpected Platane/snk grid dimensions")
    root.set("viewBox", "-16 -52 880 233")
    root.set("height", "233")
    root.set("role", "img")
    root.set("aria-label", "Animated GitHub contribution grid with a neon snake")
    root.insert(0, ET.fromstring(FRAME))
    classes = {}
    for name, level in re.findall(r"\.c\.(\w+)\{fill:var\(--c([0-4])\)", style.text or ""):
        classes[name] = int(level)
    style.text = (style.text or "") + f"""
:root {{--cb:#10172c;--cs:#67fce3;--ce:{PALETTE[0]};{''.join(f'--c{i}:{c};' for i,c in enumerate(PALETTE))}}}
.s {{fill:url(#pulse-tail);}}
.s.s0 {{fill:#83ffe8;filter:drop-shadow(0 0 3px #54ffe6);}}
@media (prefers-reduced-motion:reduce) {{
 .c,.u {{animation:none!important;}}
 .s {{display:none;}}
}}
"""
    for rect in root.findall(f"{{{SVG}}}rect"):
        class_names = rect.get("class", "").split()
        if class_names[:1] == ["c"]:
            level = classes.get(class_names[-1], 0)
            rect.attrib.update(width="12", height="12", fill=PALETTE[level])
        elif class_names[:1] == ["s"]:
            rect.set("fill", "#83ffe8" if "s0" in class_names else "url(#pulse-tail)")
    for i, color in enumerate(PALETTE):
        ET.SubElement(root, f"{{{SVG}}}rect", x=str(195 + i * 14), y="166", width="9", height="9", rx="2", fill=color)
    ET.ElementTree(root).write(target, encoding="unicode")

if __name__ == "__main__":
    render(Path(sys.argv[1]), Path(sys.argv[2]))
