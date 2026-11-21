#!/usr/bin/env python3
"""
validate_delegation.py — TC-02 委托授权样例校验脚本（本地草案，标准库实现）。

仅校验本地 JSON 委托记录的字段一致性与约束；不联网、不读取/修改远程仓库、不签发或校验真实身份。
用法: python validate_delegation.py <delegation.json> [--json]
退出码: 0 = draft-valid / valid；1 = incomplete / rejected
"""
import json, sys, re
from datetime import datetime

PLACEHOLDER = re.compile(r"example|placeholder|localhost|uibc:agent:adapter", re.I)


def _iso(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def validate(d: dict):
    issues, warnings = [], []

    for f in ("delegation_id", "status"):
        if not d.get(f):
            issues.append({"rule": "D1", "field": f, "issue": "必填字段缺失"})

    p = d.get("principal") or {}
    g = d.get("delegate") or {}
    if not p.get("id"):
        issues.append({"rule": "D1", "field": "principal.id", "issue": "缺主体标识"})
    if not g.get("id"):
        issues.append({"rule": "D1", "field": "delegate.id", "issue": "缺委托方标识"})
    for label, ident in (("principal", p.get("id", "")), ("delegate", g.get("id", ""))):
        if ident and PLACEHOLDER.search(ident):
            warnings.append({"rule": "D7", "field": f"{label}.id", "issue": "占位/合成标识，禁止用于真实委托"})

    depth = d.get("delegation_depth")
    if not isinstance(depth, int) or depth < 0:
        issues.append({"rule": "D2", "field": "delegation_depth", "issue": "委托深度须为非负整数"})

    m = d.get("mandate") or {}
    for f in ("scope", "deny", "actions_allowlist"):
        if not isinstance(m.get(f), list):
            issues.append({"rule": "D3", "field": f"mandate.{f}", "issue": "须为动作/范围数组"})
    overlap = set(m.get("scope", [])) & set(m.get("deny", []))
    if overlap:
        issues.append({"rule": "D3", "field": "mandate.scope/deny", "issue": f"范围与拒绝清单冲突: {sorted(overlap)}"})

    c = d.get("constraints") or {}
    if c.get("least_privilege") is not True:
        issues.append({"rule": "D4", "field": "constraints.least_privilege", "issue": "最小权限须为 true"})
    if c.get("bounded_arguments") is not True:
        issues.append({"rule": "D4", "field": "constraints.bounded_arguments", "issue": "参数边界须为 true"})

    v = d.get("validity") or {}
    ia, ea = _iso(v.get("issued_at", "")), _iso(v.get("expires_at", ""))
    if not ia or not ea:
        issues.append({"rule": "D5", "field": "validity", "issue": "签发/到期时间须为 ISO 8601"})
    elif ia >= ea:
        issues.append({"rule": "D5", "field": "validity.expires_at", "issue": "到期时间须晚于签发时间"})
    if v.get("transferable") is not False:
        issues.append({"rule": "D5", "field": "validity.transferable", "issue": "委托须不可转让"})
    if not isinstance(v.get("revocable"), bool):
        issues.append({"rule": "D5", "field": "validity.revocable", "issue": "须标明是否可吊销"})

    ev = d.get("evidence") or {}
    ev_fields = ("receipt_ref", "trusted_timestamp", "append_only_log_ref", "signed_by")
    missing_ev = [f for f in ev_fields if not ev.get(f)]
    if d.get("status") == "active":
        if missing_ev:
            issues.append({"rule": "D6", "field": "evidence", "issue": f"生效委托须齐备证据工件: {missing_ev}"})
    else:
        if missing_ev:
            warnings.append({"rule": "D6", "field": "evidence", "issue": f"草案状态证据工件待补: {missing_ev}"})

    if any(x["rule"] in ("D1", "D2", "D3", "D4", "D5") for x in issues):
        status = "rejected" if any("冲突" in x["issue"] or "必填" in x["issue"] for x in issues) else "incomplete"
    elif missing_ev and d.get("status") != "active":
        status = "draft-valid"
    else:
        status = "valid"

    return {"status": status, "issues": issues, "warnings": warnings,
            "delegation_id": d.get("delegation_id"), "schema_version": d.get("schema_version")}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        d = json.load(f)
    r = validate(d)
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"delegation: {r['delegation_id']}  schema: {r['schema_version']}")
        print(f"status: {r['status']}")
        for x in r["issues"]:
            print(f"  [ISSUE {x['rule']}] {x['field']}: {x['issue']}")
        for x in r["warnings"]:
            print(f"  [WARN  {x['rule']}] {x['field']}: {x['issue']}")
    return 1 if r["status"] in ("incomplete", "rejected") else 0


if __name__ == "__main__":
    sys.exit(main())
