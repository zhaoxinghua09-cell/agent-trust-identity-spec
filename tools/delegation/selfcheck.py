#!/usr/bin/env python3
"""
selfcheck.py — delegation 本地自检（离线，Python 标准库）。

仅校验 TC-02 委托授权样例（draft-valid / rejected）。
评测登记样例属另一工件，不在本目录，故本自检不引用评测校验器。
不联网、不读取或修改远程仓库、不签发或校验真实身份。

用法: python selfcheck.py [--json]
退出码: 0 = 全部符合预期；1 = 有断言失败。
"""
import json
import os
import sys

import validate_delegation as dg

HERE = os.path.dirname(os.path.abspath(__file__))

CASES = [
    ("samples/delegation_sample.json", "draft-valid"),
    ("samples/delegation_bad_sample.json", "rejected"),
]


def load(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as f:
        return json.load(f)


def main():
    results = []
    ok = True

    for rel, expected in CASES:
        rec = load(rel)
        r = dg.validate(rec)
        passed = r["status"] == expected
        ok &= passed
        results.append({
            "case": rel,
            "expected": expected,
            "actual": r["status"],
            "passed": passed,
            "issues": len(r["issues"]),
            "warnings": len(r["warnings"]),
        })

    if "--json" in sys.argv:
        print(json.dumps({"all_passed": ok, "results": results}, ensure_ascii=False, indent=2))
    else:
        print("delegation self-check")
        for r in results:
            mark = "PASS" if r["passed"] else "FAIL"
            print(f"  [{mark}] {r['case']}: expected={r['expected']} actual={r['actual']} "
                  f"(issues={r['issues']}, warnings={r['warnings']})")
        print(f"\nall_passed={ok}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
