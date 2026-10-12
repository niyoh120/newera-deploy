#!/usr/bin/env python3
"""Patch newera-draw/src/raster.rs to load a CJK font at runtime when present.

Upstream hardcodes the bundled Latin-only epaint font, so server-side plan
PNGs render CJK room names as tofu on a headless box. This swaps the font
init to prefer a CJK-capable system font (installed in our deploy image),
falling back to the bundled font. Run against the checked-out upstream
source at Docker build time:

    python3 patches/cjk_font.py src

Fails loudly (exit 1) if upstream changed the patched lines, so a silent
no-op can never ship.
"""
import pathlib
import sys

root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("src")
src = root / "crates/newera-draw/src/raster.rs"
text = src.read_text(encoding="utf-8")

OLD_USE = "use ab_glyph::{Font, FontRef, PxScale, ScaleFont};"
NEW_USE = (
    "use ab_glyph::{Font, FontRef, PxScale, ScaleFont}; "
    "// deploy patch: CJK font support (patches/cjk_font.py)\n"
    "use std::sync::OnceLock;"
)

OLD_INIT = (
    "    let font =\n"
    '        FontRef::try_from_slice(epaint_default_fonts::UBUNTU_LIGHT).expect("bundled font is valid");'
)
NEW_INIT = """    let font = { // deploy patch (patches/cjk_font.py): prefer a CJK-capable font when present
        static CJK_FONT: OnceLock<Vec<u8>> = OnceLock::new();
        let data = CJK_FONT.get_or_init(|| {
            ["/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
             "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
             "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
                .iter()
                .find_map(|p| std::fs::read(p).ok())
                .unwrap_or_default()
        });
        if data.is_empty() {
            FontRef::try_from_slice(epaint_default_fonts::UBUNTU_LIGHT).expect("bundled font is valid")
        } else {
            FontRef::try_from_slice_and_index(data, 0).expect("loaded CJK font is valid")
        }
    };"""

for old, new, what in [(OLD_USE, NEW_USE, "use line"), (OLD_INIT, NEW_INIT, "font init")]:
    if new in text:
        print(f"already patched: {what}")
        continue
    if old not in text:
        sys.exit(f"PATCH FAILED: upstream {what} not found — check patches/cjk_font.py against upstream raster.rs")
    text = text.replace(old, new, 1)
    print(f"patched: {what}")

src.write_text(text, encoding="utf-8")
print("ok:", src)
