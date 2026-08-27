# AI 助手整合使用指南

本指南說明如何在 Claude Code、Claude Projects、Cursor 或其他支援專案指令與本地檔案的 AI 助手中載入 `tw-mobile-accessibility-consultant`。本 Skill 的目標是協助執行台灣行動 App、行動網站與 Web App 的無障礙檢測，不是取代 TalkBack、VoiceOver、人工 QA 或主管機關正式認證。

> **整合原則：** 讓 AI 助手讀取 `SKILL.md` 作為工作流程，按需讀取 `references/`、`schemas/` 與 `templates/`；不要把測試帳密、權杖、真實個資或付款資料放進對話、repository 或測試附件。

## 1. 準備 repository

先複製公開 repository，並確認核心檔案存在：

```bash
git clone https://github.com/xuan905/tw-mobile-accessibility-consultant.git
cd tw-mobile-accessibility-consultant
find SKILL.md references schemas templates -maxdepth 2 -type f | sort
```

若只需要在 AI 助手中使用，不必安裝整個應用程式。若要驗證案件 JSON，額外安裝 Python 開發依賴：

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_audit_case.py examples/audit-case.example.json
```

## 2. 在 Claude Code 中使用

Claude Code 官方文件將 Skill 作為可擴充 Claude Code 能力的模組化工作單元。[1] 最穩定的做法是把 Skill 放進專案可讀取的 `.claude/skills/`，或依團隊管理方式放入 Claude Code 的使用者級 Skill 目錄；實際目錄位置請以你安裝版本的官方文件為準。

### 專案級安裝

```bash
mkdir -p .claude/skills
git clone https://github.com/xuan905/tw-mobile-accessibility-consultant.git \
  .claude/skills/tw-mobile-accessibility-consultant
```

進入專案後，先用明確提示詞要求 Claude Code 讀取 Skill 與必要參考資料：

```text
請載入 .claude/skills/tw-mobile-accessibility-consultant/SKILL.md。
依該 Skill 執行本專案的行動 App 無障礙檢測。
先不要下結論，先列出需要的版本、平台、裝置、輔助工具、核心流程與證據。
```

接著提供案件資料與檔案位置：

```text
案件資訊：
- App：城市購物
- 版本：1.4.2
- 平台：Android
- 裝置：Pixel 8，Android 15
- 輔助工具：TalkBack
- 流程：登入、搜尋商品、加入購物車、結帳

請先讀取 schemas/audit-case.schema.json 與 references/platform-manual-testing.md。
依 42 項 AA 檢核架構建立檢測計畫。截圖只能做視覺初判；沒有 TalkBack 錄音或實機紀錄的項目必須標為待確認。
```

### Claude Code 的建議工作順序

| 階段 | 建議指令或提示 | 目的 |
|---|---|---|
| 探索 | 「先列出缺少的案件欄位與證據」 | 防止資料不足時過度推論。 |
| 規劃 | 「建立 audit-case JSON 草稿並依 Schema 驗證」 | 固定案件結構。 |
| 檢測 | 「逐項執行 AA-01 至 AA-42，引用 E-* 證據」 | 保留可追溯性。 |
| 修正 | 「只列出可重現缺失與修正後預期結果」 | 轉成工程工作。 |
| 回歸 | 「為每個 fail finding 建立 TalkBack／VoiceOver 回歸步驟」 | 形成驗收條件。 |

## 3. 在 Claude Projects 中使用

Claude Projects 可建立具有獨立對話歷史與知識庫的工作空間，適合把 `SKILL.md`、檢核清單、平台測試流程、JSON Schema 與報告模板作為專案知識。[2]

建議建立一個專案，例如「行動 App 無障礙 QA」，並上傳以下檔案：

```text
SKILL.md
references/taiwan-aa-checklist.md
references/platform-manual-testing.md
schemas/audit-case.schema.json
templates/accessibility-audit-report.md
```

專案指令可使用下列內容：

```text
你是本專案的行動 App 無障礙 QA 顧問。
使用上傳的 SKILL.md 作為主要工作流程；只有在需要時讀取檢核清單、平台測試流程、JSON Schema 與報告模板。
任何只有截圖或原始碼支持的結論都必須標示證據限制。
不可將視覺初判稱為 TalkBack／VoiceOver 通過，也不可宣稱官方認證。
所有報告都要包含範圍、環境、證據、逐項狀態、重大缺失、回歸測試與待確認事項。
```

每次新案件建議先上傳去識別化的 `audit-case.json`、證據索引與必要截圖，再開始對話。若案件包含原始碼，優先提供特定畫面或元件，不要一次上傳不必要的整個私有 codebase。

## 4. 在 Cursor 中使用

Cursor 官方 Rules 文件支援專案級與使用者級規則，以及 `AGENTS.md` 等專案指令檔。[3] 對本 Skill 而言，建議把「何時使用 Skill、不可過度宣稱、如何引用證據」放進專案規則，把完整檢核清單留在 repository 內按需讀取。

### 方法 A：使用 AGENTS.md

在專案根目錄建立 `AGENTS.md`：

```markdown
# Mobile Accessibility Audit Instructions

When the user asks to inspect Android, iOS, mobile web, or Web App accessibility, read:
- `SKILL.md`
- `references/taiwan-aa-checklist.md` when running checklist items
- `references/platform-manual-testing.md` when planning TalkBack or VoiceOver testing
- `schemas/audit-case.schema.json` when creating or validating an audit case
- `templates/accessibility-audit-report.md` when producing a report

Use evidence-first judgments. Distinguish pass, fail, not_applicable, and pending.
Screenshots alone cannot establish screen-reader, focus-order, dynamic-announcement, or real-device results.
Never expose secrets from uploaded files and never claim official certification.
```

### 方法 B：使用 Cursor Project Rules

在 Cursor 的專案規則中加入等價內容，或建立可納入版本控制的規則檔，例如 `.cursor/rules/mobile-accessibility.mdc`。規則本身保持短小，並指向 repository 內的詳細文件：

```text
---
description: Taiwan mobile accessibility audit workflow
alwaysApply: false
---

Use this rule when inspecting mobile accessibility.
Read SKILL.md first, then load only the relevant references.
Require platform, version, device, assistive technology, scope, and evidence before making conclusions.
Use pending when evidence is insufficient.
```

在 Cursor Agent 對話中可使用：

```text
請依 mobile-accessibility rule 執行這個 React Native 登入流程的無障礙初檢。
先讀取 SKILL.md、Schema 與平台測試流程，檢查目前 repository 的登入元件，
輸出 audit-case 草稿、疑似缺失、證據限制與需要在 Android TalkBack／iOS VoiceOver 上回歸的步驟。
```

## 5. 建議的案件工作流

無論使用哪一種 AI 助手，都應維持相同的六階段流程：

1. **初始化案件。** 建立產品名稱、版本、平台、裝置、OS、輔助工具、核心流程與排除範圍。
2. **整理證據。** 將截圖、錄影、錄音、原始碼與人工紀錄命名為 `E-001` 等證據 ID。
3. **建立案件 JSON。** 依 `schemas/audit-case.schema.json` 填寫 `case`、`evidence` 與 `findings`。
4. **執行檢測。** 讀取相應平台流程，逐項記錄 `pass`、`fail`、`not_applicable` 或 `pending`。
5. **本地驗證。** 執行 `scripts/validate_audit_case.py`，修正 Schema、跨引用與摘要錯誤。
6. **產出報告與回歸。** 使用報告模板，讓每一個重大缺失都有重現步驟、修正方向與回歸條件。

## 6. 本地驗證與 CI

本地執行：

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_audit_case.py examples/audit-case.example.json
python -m unittest discover -s tests -v
```

Repository 的 GitHub Actions 會在 push 與 Pull Request 時執行同一支驗證器、JSON 格式檢查、自動化測試與必要檔案檢查。若 CI 失敗，先查看錯誤位置，再把修正提交到同一個分支；不要以忽略測試的方式合併。

## 7. 安全與隱私檢查表

| 檢查 | 原則 |
|---|---|
| 測試帳號 | 只使用專用測試帳號，並移除真實個資。 |
| 螢幕錄影 | 遮罩密碼、權杖、信用卡、地址、電話與個人通知。 |
| 原始碼 | 移除 `.env`、私鑰、API key 與未授權的內部程式。 |
| AI 上傳 | 先確認組織政策與資料處理條件，再上傳案件材料。 |
| 報告 | 只引用去識別化證據，避免把敏感資料重複寫入 Markdown。 |
| 結論 | 清楚標示測試版本、裝置、平台與證據限制。 |

## 8. 常見問題

### 為什麼 AI 說截圖無法證明通過？

因為截圖通常只能支持視覺觀察；它無法直接證明讀屏名稱、焦點順序、動態訊息、手勢操作、鍵盤行為或錯誤恢復流程。這是本 Skill 有意保留的證據門檻。

### Claude 或 Cursor 能不能自動操作真實 App？

只有在使用者提供安全、可授權且可重現的測試環境時，才應考慮自動化操作。沒有實機或操作錄影時，AI 應輸出測試計畫與待確認事項，而不是虛構測試結果。

### 可以把這份報告當成官方認證嗎？

不可以。報告是工程與 QA 輔助文件；正式認證、標章申請與主管機關審查必須依最新官方規範與程序辦理。

## 參考資料

[1]: https://code.claude.com/docs/en/skills "Claude Code 官方文件：Extend Claude with skills"
[2]: https://support.claude.com/en/articles/9517075-what-are-projects "Anthropic Help Center：What are projects?"
[3]: https://cursor.com/docs/rules "Cursor 官方文件：Rules"
[4]: https://github.com/xuan905/tw-mobile-accessibility-consultant "本 Skill 公開 GitHub repository"
