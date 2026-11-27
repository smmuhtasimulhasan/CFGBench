"""Standalone example evaluator for the released dataset, not the paper's original runner.

Install: python -m pip install lark
Run from any directory: python path/to/Code/cfg_output.py
By default evaluates the supplied lang01 reference grammar on suite 1.
Use --language langXX --grammar path/to/grammar.lark --suite all for another grammar.
This lightweight evaluator does not implement per-case timeouts or experimental aggregation.
"""
import argparse
import json
from pathlib import Path
from cfg_parser import build_grammar, accepts_input

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "Dataset"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--language", default="lang01")
    ap.add_argument("--grammar", type=Path, default=HERE / "input.txt")
    ap.add_argument("--suite", choices=["1", "2", "3", "all"], default="1")
    args = ap.parse_args()
    if args.language != "lang01" and args.grammar == HERE / "input.txt":
        ap.error("Specify a matching grammar with --grammar for languages other than lang01.")
    try:
        parser = build_grammar(args.grammar.read_text(encoding="utf-8"))
    except Exception as error:
        print(json.dumps({"build_ok": False, "error": str(error)}, indent=2))
        return 1
    correct = total = pos_correct = neg_correct = pos = neg = 0
    for suite in (range(1, 4) if args.suite == "all" else [int(args.suite)]):
        languages = json.loads((DATA / f"CFGBench_Suite_{suite}.json").read_text(encoding="utf-8"))
        record = next((r for r in languages if r["id"] == args.language), None)
        if record is None:
            ap.error(f"Unknown language: {args.language}")
        for case in record["test_cases"]:
            expected = case["label"]
            match = accepts_input(parser, case["w"]) == expected
            total += 1
            correct += match
            if expected:
                pos += 1
                pos_correct += match
            else:
                neg += 1
                neg_correct += match
    print(json.dumps({"language": args.language, "suite": args.suite,
                      "build_ok": True, "correct": correct, "total": total,
                      "positive_recall": pos_correct / pos, "negative_recall": neg_correct / neg,
                      "balanced_accuracy": (pos_correct / pos + neg_correct / neg) / 2,
                      "all_selected_cases_correct": correct == total}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
