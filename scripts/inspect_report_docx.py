"""Inspect report text and image locations without altering the Word package."""

import argparse
import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}


def inspect(filename, output):
    output.mkdir(parents=True, exist_ok=True)
    records = []
    with ZipFile(filename) as package:
        document = ET.fromstring(package.read("word/document.xml"))
        relationships = ET.fromstring(package.read("word/_rels/document.xml.rels"))
        targets = {r.attrib["Id"]: r.attrib["Target"] for r in relationships}
        for index, block in enumerate(document.find("w:body", NS)):
            text = "".join(t.text or "" for t in block.findall(".//w:t", NS))
            style = block.find("w:pPr/w:pStyle", NS)
            record = {"index": index, "tag": block.tag.split("}")[-1], "text": text,
                      "style": style.attrib.get(f"{{{NS['w']}}}val") if style is not None else None,
                      "images": []}
            if record["tag"] == "tbl":
                record["rows"] = [["".join(t.text or "" for t in cell.findall(".//w:t", NS))
                                   for cell in row.findall("w:tc", NS)] for row in block.findall("w:tr", NS)]
            for blip in block.findall(".//a:blip", NS):
                target = targets.get(blip.attrib.get(f"{{{NS['r']}}}embed"))
                if target and target.startswith("media/"):
                    asset = output / Path(target).name
                    asset.write_bytes(package.read(f"word/{target}"))
                    record["images"].append(str(asset))
            records.append(record)
        (output / "document.xml").write_bytes(package.read("word/document.xml"))
        (output / "styles.xml").write_bytes(package.read("word/styles.xml"))
    (output / "inventory.json").write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = []
    for record in records:
        lines.append(f"[{record['index']}] {record['tag']} {record['style'] or ''} {record['text']}")
        for row in record.get("rows", []):
            lines.append("  | " + " | ".join(row))
        for asset in record["images"]:
            lines.append(f"  IMAGE: {asset}")
    (output / "text.txt").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"blocks": len(records), "image_locations": sum(bool(r['images']) for r in records),
                      "output": str(output)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inspect(args.source, args.output)
