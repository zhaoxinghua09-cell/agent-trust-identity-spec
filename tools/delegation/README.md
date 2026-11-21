# delegation · TC-02 委托授权记录本地骨架（0.1-draft）

> **状态：隔离分支底稿，待独立评测与终审，勿合并。**
> 本目录为 P0 地基工件的身份/委托侧骨架；尚未经利益隔离的独立复跑与终审。
> 所有样例为合成占位数据，不含真实身份、客户数据或可识别信息。

## 目录

```
tools/delegation/
├── validate_delegation.py     # TC-02 委托授权记录校验脚本（Python 标准库，离线）
├── interop_checklist.json     # 第二实现互操作检查清单 I1–I9（gap/partial/deferred）
├── selfcheck.py               # 本地自检：断言两份委托样例预期状态
└── samples/
    ├── delegation_sample.json       # 草案占位 → draft-valid
    └── delegation_bad_sample.json   # 冲突/越权/时限错误 → rejected
```

评测登记校验样例属另一工件（TC-01），不在本目录；本自检不引用评测校验器。

## 运行

```powershell
cd tools/delegation
python selfcheck.py            # 一键复跑两份样例断言（推荐先跑）
python validate_delegation.py samples/delegation_sample.json
```

退出码：`0` = draft-valid / valid；`1` = incomplete / rejected。

## 校验规则（D1–D7）

| 规则 | 语义 |
|---|---|
| D1 | 委托标识、主体/委托方标识必填 |
| D2 | 委托深度为非负整数 |
| D3 | 范围/拒绝/允许清单为数组；scope 与 deny 不得冲突 |
| D4 | 最小权限、参数边界须为 true |
| D5 | 时限合法、不可转让、标明可吊销 |
| D6 | 生效委托须齐备收据/时间戳/追加日志/签名；草案状态允许待补并告警 |
| D7 | 占位/合成标识禁止用于真实委托（告警） |

## 边界与禁区

- 脚本不联网、不读取或修改远程仓库、不签发真实身份、不创建分支/PR/Release；
- 样例标识为 `did:example:…`、`uibc:agent:adapter-sample` 占位，禁止用于真实委托；
- 标准草案引用不代表兼容认证或被采纳；对外公开 schema、投稿标准组织、邀请外部复跑均须单独审批；
- 本目录代码随仓库根 LICENSE（MIT）。

## 已知缺口（正文自述，不藏附录）

- 委托/身份样例尚未接入真实签发与校验实现；
- 互操作清单 I1–I9 尚为断言描述，未落成可执行第二实现测试；
- 运行时证明（I6）依赖外部运行时环境，已标 deferred；
- 本骨架未经独立第三方复跑，当前结论仅限本地样例自洽。
