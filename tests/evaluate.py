import json
import sys

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate(ground_truth_path="ground_truth.json", predictions_path="predictions.json"):
    gt_data = load_json(ground_truth_path)
    pred_data = load_json(predictions_path)

    # Index predictions by filename
    pred_map = {entry["filename"]: entry["label"] for entry in pred_data}

    total = 0
    correct = 0
    skipped = 0
    missing = 0
    none_labels = 0
    false_positives = {}  # pred_label -> list of (filename, gt_label)

    for entry in gt_data:
        filename = entry["filename"]
        ocr_text = entry.get("ocr_text", "")
        gt_label = entry["label"]

        # Only evaluate entries with non-empty ocr_text
        if not ocr_text.strip():
            skipped += 1
            continue

        if filename not in pred_map:
            print(f"[MISSING] No prediction for: {filename}")
            missing += 1
            continue

        total += 1
        pred_label = pred_map[filename]

        if pred_label == "None":
            none_labels += 1
            print(f"[NONE]  {filename}: expected '{gt_label}', got None")
            continue

        if pred_label == gt_label:
            correct += 1
        else:
            false_positives.setdefault(pred_label, []).append((filename, gt_label))

    classified = total - none_labels

    print()
    print("=" * 50)
    print(f"Evaluated:  {total} samples (non-empty OCR)")
    print(f"Classified: {classified} (excluding None predictions)")
    print(f"Correct:    {correct}")
    print(f"Wrong:      {classified - correct}")
    print(f"None:       {none_labels} (predicted None, excluded)")
    print(f"Skipped:    {skipped} (empty ocr_text)")
    print(f"Missing:    {missing} (no prediction found)")
    print()
    print("False positives per label:")
    if false_positives:
        for pred_label, cases in sorted(false_positives.items(), key=lambda x: -len(x[1])):
            print(f"\n  Predicted '{pred_label}' ({len(cases)} case(s)):")
            for filename, gt_label in cases:
                print(f"    {filename}  |  predicted: {pred_label}  |  ground truth: {gt_label}")
    else:
        print("  None")
    print("=" * 50)

if __name__ == "__main__":
    gt_path = sys.argv[1] if len(sys.argv) > 1 else "ground_truth.json"
    pred_path = sys.argv[2] if len(sys.argv) > 2 else "predictions.json"
    evaluate(gt_path, pred_path)