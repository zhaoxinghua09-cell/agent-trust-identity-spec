# TC-02 UIBC 身份与标准概念对齐 · 技术设计稿（内部草案）

**日期**：2026-11-20　**关联**：P0 任务卡 TC-02、五阶段交付物 C、领先性总纲 G1/G3 门禁
**状态**：本地设计草案；**未对接外部身份提供方、未投稿标准组织、未改 uibc-core 现行协议**。批准立项后才进入实现。

## 1. 目标与范围

先做术语与字段口径对齐：把 UIBC 身份/凭证/委托概念映射到成熟身份模型与在研草案，明确对应关系、差异与缺口，产出可验证的身份/委托样例与第二实现互操作检查清单。

**本期范围**：概念映射表、委托授权字段草案、互操作检查清单、标准状态登记、缺口清单。
**不在本期**：实现 SPIFFE/DID/VC 对接、接入外部身份服务、向 IETF/W3C/ITU 提交或评论、对外宣称标准兼容。

## 2. 身份栈五层对照（外部共识框架）

| 层 | 外部典型工件 | 作用 | UIBC 对应现状（待源码核对） |
|---|---|---|---|
| 稳定标识 | Agent ID、SPIFFE ID、DID | 持久命名、治理归属与生命周期 | 身份胶囊/标识概念雏形；全局可解析性未验证 |
| 受保护密钥 | HSM/TPM/TEE/passkey 绑定的私钥 | 证明持有者控制绑定身份的密钥 | 未见密钥保管与证明机制记录 |
| 凭证/断言 | X.509/SVID/JWS/JWT/VC | 机器可验证的身份主张 | 凭证/锚点概念存在；可验证凭证格式未定 |
| 委托工件 | 短时令牌、令牌交换、授权断言 | 携带有界权限、主体上下文、受众与有效期 | 委托范围/衰减/吊销字段草案，未落地 |
| 证据工件 | 证明证据、签名收据、可信时间戳、追加日志 | 审计、争议解决、不可否认、取证 | 证据目录/指纹雏形；缺收据、时间戳与追加日志 |

## 3. 概念映射表

| UIBC 概念（待源码核对定名） | WIMSE-ID 标识模型 | SPIFFE/SPIRE | W3C DID/VC | AIP（draft-singla-03） | AAE（draft-kroehl-01） | 对齐状态 |
|---|---|---|---|---|---|---|
| Agent 身份标识 | WIMSE 信任域内 URI 唯一标识 | SPIFFE ID（`spiffe://trust-domain/path`） | DID 可解析标识 | AIP Agent DID | 主体标识 | 待对齐：标识命名域、稳定性、可解析性规则 |
| 身份凭证 | 凭证绑定标识与属性 | SVID（X.509/JWT） | Verifiable Credential | Credential Token（签名 JWT） | 授权断言 | 待对齐：凭证格式、签名方、校验方、有效期 |
| 工作负载/运行时证明 | 平台证明层 | 节点/工作负载证明 | — | Registry 签发 SET | — | 缺口：运行时状态证明未纳入 |
| 委托授权 | 委托语义与审计记录 | 平台授权（WAG） | VC 授权/委托表达 | Principal Token 委托链（委托深度计数） | MANDATE 范围与允许动作清单 | 缺口：委托链、深度、衰减表达 |
| 权限约束 | 授权决策依据 | 上下文感知授权（部分专有） | 凭证约束 | 能力授权 | CONSTRAINTS 最小权限与价值边界 | 缺口：最小权限/边界/拒绝路径 |
| 有效期与不可转让 | 审计记录 | 短时凭证轮换 | 凭证有效期 | SET 短时令牌 | VALIDITY 时限、不可转让 | 缺口：时限、吊销、不可转让约束 |
| 证据收据 | 审计追溯 | 运行时身份复核 | 可验证披露 | 委托链记录 | 委托来源记录 | 缺口：签名收据、时间戳、追加日志 |
| 跨组织可移植 | 跨信任域标识 | 边界：依赖签发方对基础设施可见 | 跨组织可携带身份 | 去中心身份框架取向 | 中央 DID 注册表取向 | 缺口：无共享基础设施下的信任与携带方案 |

> 映射仅为概念对照；各草案仍在演进，不构成兼容认证或标准采纳声明。

## 4. 委托授权样例字段草案（合成样例）

```json
{
  "delegation_id": "del-20261120-001",
  "principal": {"id": "did:example:principal-001", "type": "human-or-agent"},
  "delegate": {"id": "uibc:agent:adapter-sample", "relation": "child-agent"},
  "delegation_depth": 1,
  "mandate": {
    "scope": ["read:profile", "call:registry-lookup"],
    "deny": ["write:identity", "admin:policy"],
    "actions_allowlist": ["lookup", "verify"]
  },
  "constraints": {
    "least_privilege": true,
    "value_bound": "none",
    "bounded_arguments": true,
    "context": {"owner": "principal-001", "device_posture": "unverified"}
  },
  "validity": {
    "issued_at": "2026-11-20T10:00:00+08:00",
    "expires_at": "2026-11-20T11:00:00+08:00",
    "transferable": false,
    "revocable": true,
    "revocation_id": null
  },
  "evidence": {
    "receipt_ref": null,
    "trusted_timestamp": null,
    "append_only_log_ref": null,
    "signed_by": null
  },
  "status": "draft"
}
```

字段说明：
- `mandate.scope/deny/actions_allowlist`：允许与禁止边界；
- `constraints`：最小权限、参数边界、上下文姿态；
- `validity`：时限、不可转让、可吊销；
- `evidence`：委托收据、时间戳、追加日志占位（当前缺口）；
- `status=draft`：字段草案，未接入任何签发/校验实现。

## 5. 第二实现互操作检查清单

| 编号 | 检查点 | 断言要点 | 对应外部概念 |
|---|---|---|---|
| I1 身份绑定 | 标识与凭证可绑定；标识在生命周期内稳定 | 同一主体重发凭证标识一致；未知/伪造标识被拒 | WIMSE-ID / SVID / DID |
| I2 凭证校验 | 校验方可验证签名、有效期、受众与主体 | 过期/篡改/受众不符凭证被拒 | SVID / VC / Credential Token |
| I3 委托链 | 委托深度可计数；链上每环可追溯到根主体 | 断链/超深/越权委托被拒 | Principal Token 链 |
| I4 权限衰减 | 子代理权限不得超出父代理；允许清单外动作拒绝 | 越权动作拒绝并记录 | MANDATE / CONSTRAINTS |
| I5 时限与不可转让 | 过期失效；不可转让；吊销即时生效 | 过期/转让/已吊销凭证被拒 | VALIDITY |
| I6 运行时证明 | 运行时状态与声明一致（占位扩展） | 状态不符的声明不予采信 | SET / SPIRE 复核 |
| I7 证据工件 | 每次委托/校验产出可追溯收据与时间戳占位 | 缺证据记未闭环，不判通过 | 证据工件层 |
| I8 拒绝路径 | 拒绝/失败用例可复现并归档 | 拒绝路径有样例与回执 | 套件通用要求 |
| I9 前向兼容 | 旧实现可读新记录的新增可选字段 | 新增字段不破坏历史成绩 | 版本兼容政策 |

## 6. 标准状态登记（2026-11-20 检索，待月度复核）

| 草案/标准 | 版本/阶段 | 状态口径 | 来源 |
|---|---|---|---|
| draft-klrc-aiagent-auth | -03 | IETF 个人提交草案，非 RFC | ietf.org/archive/id/draft-klrc-aiagent-auth-03.txt |
| draft-singla-agent-identity-protocol (AIP) | -03 | IETF 个人提交草案 | ietf.org/archive/id/draft-singla-agent-identity-protocol-03.html |
| draft-sweeney-wimse-credential-delegation | -01（2027-04-16 到期） | IETF 个人提交草案 | ietf.org/archive/id/draft-sweeney-wimse-credential-delegation-01.txt |
| draft-kroehl-agentic-trust-aae | -01（2027-02-12 到期） | IETF 个人提交草案 | ietf.org/archive/id/draft-kroehl-agentic-trust-aae-01.txt |
| SPIFFE/SPIRE | 开放标准 + 参考实现 | 工作负载身份成熟基线 | 见总纲附录来源 |
| W3C DID / VC Data Model | 标准族 | 跨组织可携带身份方向 | 待复核最新版本 |
| W3C Agentic Web WG | 章程草案进展中 | 身份与委托授权纳入范畴，未定稿 | w3.org 简报 |

> 规则：登记只记官方页面可核状态；内部投稿材料不等于被采纳；不得在对外材料中使用“已对齐标准/获标准支持”等表述。

## 7. 与现有 uibc-core 资产对接点（前序口径，待源码复核）

- 已有：adapters、registry、second-impl 检查、一致性/互操作样例；15 兼容文件、7 回归、2 对抗；6 次 Release；Apache-2.0。
- 可承接：I1–I5、I7–I9 检查点先落到现有套件；I6 运行时证明列为扩展缺口。
- 关联风险：`ai-passport-spec`、`uibc-competition`、`uibc-iverify` 等关联仓许可为 NOASSERTION/NONE/待核，权属厘清前按限制使用处理（见九阶段交付物 2）。

## 8. 缺口与优先级

| 缺口 | 优先级 | 说明 |
|---|---|---|
| 标识命名域与可解析性规则未定 | P0 | 跨组织可移植前提 |
| 凭证格式/签名方/校验方未定 | P0 | 互操作基础 |
| 委托链、衰减、吊销字段未落地 | P1 | 对应 I3–I5 |
| 证据收据/时间戳/追加日志缺失 | P1 | 对应 I7，衔接 Evidence Engine |
| 运行时状态证明未纳入 | P2 | 扩展项，依赖运行时环境 |
| 标准草案跟踪机制 | P1 | 月度复核状态，避免口径过时 |

## 9. 验收对照（任务卡 TC-02）

- [x] UIBC 概念与外部模型字段逐条对照，差异与缺口显式列出；
- [x] 委托范围/最小权限/时限/不可转让/吊销字段草案成文；
- [x] 互操作检查清单可被测试用例引用（I1–I9）；
- [x] 标准状态与“非认证/未采纳”口径登记；
- [ ] 样例身份/委托记录可被校验脚本解析（待立项实现）；
- [ ] 第二实现互操作用例在套件中复跑（待立项实现）。

## 10. 禁区
- 不实现未批准的外部身份提供方对接；
- 不向 IETF/W3C/ITU 投稿、评论或提交提案；
- 不对外宣称标准兼容、认证或被采纳；
- 不引入客户身份数据；样例一律合成/内部占位。
