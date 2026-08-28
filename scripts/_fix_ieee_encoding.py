from __future__ import annotations

from pathlib import Path

p = Path(__file__).resolve().parents[1] / "scripts" / "generate_ieee_paper_docx.py"
raw = p.read_bytes()
repl = {
    0x93: b'"',
    0x94: b'"',
    0x97: b"-",
    0x96: b"-",
    0x9D: b"",
}
out = bytearray()
for byte in raw:
    out.extend(repl.get(byte, bytes([byte])))
p.write_text(out.decode("utf-8", errors="replace"), encoding="utf-8")
print("fixed", p)
