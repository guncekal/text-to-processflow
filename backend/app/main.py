"""
FlowMind - Text to Process Flow (v1)

Minimal CLI that will later:
- read input text (or a document)
- extract a Process DSL JSON using an LLM
- validate the structure
- optionally render a text-based diagram (e.g., Mermaid)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="FlowMind (v1) - Text to Process Flow")
    parser.add_argument(
        "input_path",
        help="Path to a .txt file containing a process description",
    )
    parser.add_argument(
        "--out",
        default="output.json",
        help="Path to write the output JSON (default: output.json)",
    )
    args = parser.parse_args()

    input_path = Path(args.input_path)
    out_path = Path(args.out)

    text = read_text(input_path)

    # Placeholder output (we'll replace this with LLM extraction in the next steps)
    result = {
        "process": {
            "name": "FlowMind Draft",
            "source_type": "free_text",
            "language": "en",
            "dsl_version": "1.0",
        },
        "input_preview": text[:200],
        "message": "Pipeline skeleton is ready. Next: LLM extraction + validation."
    }

    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
