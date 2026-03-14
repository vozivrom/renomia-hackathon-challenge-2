"""
Remove 'label' from every object in a JSON list and save as input_custom.json.

Usage: python strip_labels.py ground_truth.json
"""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

filename = sys.argv[1] if len(sys.argv) > 1 else "ground_truth.json"
filepath = os.path.join(PROJECT_ROOT, filename)
output = os.path.join(PROJECT_ROOT, "input_custom.json")

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for doc in data:
    doc.pop("label", None)

with open(output, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done. {len(data)} documents, labels removed. Saved to input_custom.json")