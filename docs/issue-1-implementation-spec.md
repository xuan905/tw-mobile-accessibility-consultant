# Issue #1 實作規格：audit-case v2.0 資料模型與 JSON Schema

對應 GitHub Issue：[建立 audit-case v2.0 資料模型與 JSON Schema](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/1)

## 1. 目標與非目標

本 Issue 的目標是建立一份穩定、可驗證、可被報告與工單流程重複使用的 audit-case 資料模型。模型必須能描述產品與版本、檢測範圍、核心流程、測試環境、證據、42 項 AA 檢核結果、回歸測試與摘要。

本 Issue 不包含自動操作真實 App、視覺模型判定、GitHub Issue 自動建立、Jira 整合、官方認證判定或規範內容自動同步。這些功能保留給後續 Milestones。

## 2. 設計原則

| 原則 | 實作要求 |
|---|---|
| Schema-first | `schemas/audit-case.schema.json` 是資料格式的唯一規格來源。 |
| 可追溯 | 每個 finding 以 `AA-*` 對應檢核，以 `E-*` 對應證據，並可關聯流程與環境。 |
| 證據分層 | 使用 `verification_level` 區分 observed、reproducible、inferred、pending_review。 |
| 不過度宣稱 | 缺少實機或讀屏證據時，狀態應為 pending，不得自動轉為 pass。 |
| 部分完成可用 | findings 可以只記錄已觀察項目，其餘 AA 項目由摘要中的 pending 表示。 |
| 平台可比較 | 平台、裝置、OS、App 版本與輔助工具必須可獨立記錄。 |
| 隱私優先 | Schema 不保存秘密資料；證據只保存來源指標與去識別化說明。 |

## 3. 頂層結構

```text
AuditCase
├── schema_version
├── case
│   ├── case_id / product / version / product_type
│   ├── platforms / scope / flows
│   ├── test_environments / test_accounts / out_of_scope
│   └── standard
├── evidence[]
├── findings[]
├── summary
└── metadata
```

### 3.1 `case`

`case` 定義檢測的對象與邊界。`case_id` 是案件的穩定識別碼；`flows` 描述可重現的使用者任務；`test_environments` 描述平台與輔助工具；`standard` 記錄規範名稱、版本、來源與完整 AA 清單總數。

### 3.2 `evidence[]`

每個證據都要有 `evidence_id`、類型、標題、來源與驗證層級。來源可以是相對檔案路徑、測試紀錄名稱或外部 URI；不應在此欄位放置密碼、權杖或未遮罩個資。

### 3.3 `findings[]`

`finding` 描述一個檢核發現。`check_id` 必須符合 `AA-01` 至 `AA-42` 的識別碼格式；`status` 是標準化判定；`evidence_ids`、`flow_ids` 與 `environment_ids` 必須指向同一份文件中已存在的識別碼。`next_action` 是必要欄位，確保 pending 或 fail 不會沒有後續行動。

### 3.4 `summary`

`summary.total` 固定為 42。當 findings 只記錄部分項目時，未記錄的 AA 項目視為 implicit pending。驗證器必須檢查 pass、fail、not_applicable 與 pending 的合計與 findings／未記錄項目一致。

## 4. 識別碼與狀態

| 欄位 | 格式／值 | 說明 |
|---|---|---|
| `case_id` | 英數、點、底線、連字號 | 案件全域識別碼。 |
| `flow_id` | `FLOW-01` | 可重現的核心操作流程。 |
| `environment_id` | `ENV-01` | 平台與輔助工具設定。 |
| `evidence_id` | `E-001` | 截圖、錄影、原始碼或人工紀錄。 |
| `finding_id` | `F-001` | 一個可追蹤的檢測發現。 |
| `check_id` | `AA-01`–`AA-42` | 對應 42 項 AA 檢核。 |
| `status` | `pass`／`fail`／`not_applicable`／`pending` | 檢核判定，不代表官方認證。 |
| `verification_level` | `observed`／`reproducible`／`inferred`／`pending_review` | 證據可靠程度與測試層級。 |

## 5. 驗證規則

### Schema 層

Schema 必須檢查必要欄位、資料型別、列舉值、識別碼 pattern、URI、日期時間、`checklist_total: 42`、`summary.total: 42` 與禁止未定義欄位。使用 JSON Schema Draft 2020-12。

### 文件一致性層

由驗證器執行跨欄位規則：finding 引用的證據、流程與環境必須存在；summary 狀態數量必須符合明確 findings 加上未記錄 AA 項目的 implicit pending；findings 不可超過 42 筆。

### 安全層

範例與測試不得包含真實秘密。若 `contains_sensitive_data` 為 true，文件應被拒絕或至少產生明確錯誤；目前 Schema 將它限制為 false，促使提交者先完成遮罩。

## 6. 初始程式碼框架

目前 repository 已具備：

```text
schemas/audit-case.schema.json       # 正式資料格式
examples/audit-case.example.json     # 最小可用案例
scripts/validate_audit_case.py       # Schema + 跨引用驗證器
src/audit_case_model.py              # 型別化的 Python 框架
requirements-dev.txt                 # jsonschema
tests/test_validate_audit_case.py    # CLI 驗證測試
```

`src/audit_case_model.py` 只提供型別化存取與狀態統計的輕量框架，不重新定義 Schema。未來若新增欄位，應先更新 JSON Schema，再同步更新 Python 型別與測試。

## 7. 測試策略

第一階段至少要通過以下案例：

1. `examples/audit-case.example.json` 可通過 Schema 與摘要驗證。
2. 缺少必要的 `case.product` 時失敗。
3. 無效 JSON 時輸出可讀錯誤並回傳 exit code 1。
4. 引用不存在的 `E-*` 或 `FLOW-*` 時失敗。
5. summary 與 findings 不一致時失敗。
6. `--format json` 產生可被 CI 解析的結果。
7. 多檔案驗證中只要一份失敗，整體回傳 1。
8. 輸入含秘密資料的案例不應進入公開範例或測試 fixture。

## 8. 完成定義

- [x] Schema 使用 Draft 2020-12。
- [x] 定義案件、流程、環境、證據、finding、回歸與摘要結構。
- [x] 定義識別碼格式與必要欄位。
- [x] 定義四種檢核狀態與四種證據驗證層級。
- [x] 提供可驗證的範例 JSON。
- [x] 提供本地驗證器與自動化測試。
- [ ] 在後續 PR 中由產品、工程、QA 與無障礙專業人員共同審查欄位命名與規範對照。

## 9. 後續相容性政策

v2.x 只允許向後相容的非必要欄位新增；修改既有欄位型別、狀態值、識別碼格式或必要欄位時，必須提高 `schema_version` 的 major 或 minor 版本，更新範例、遷移說明與測試。任何正式版本都應保留對應的 JSON Schema 檔案或可取得的版本標籤。
