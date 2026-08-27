# 台灣行動 App 無障礙檢測與改善顧問

[![Validate Skill](https://github.com/xuan905/tw-mobile-accessibility-consultant/actions/workflows/validate.yml/badge.svg)](https://github.com/xuan905/tw-mobile-accessibility-consultant/actions/workflows/validate.yml)
[![GitHub release](https://img.shields.io/github/v/release/xuan905/tw-mobile-accessibility-consultant?sort=semver&color=2f80ed)](https://github.com/xuan905/tw-mobile-accessibility-consultant/releases)
[![ClawHub](https://img.shields.io/badge/ClawHub-published-d94f3d)](https://clawhub.ai/xuan905/tw-mobile-accessibility-consultant)
[![License](https://img.shields.io/badge/license-MIT--0-1f2937)](https://github.com/xuan905/tw-mobile-accessibility-consultant)

![台灣行動 App 無障礙檢測與改善顧問專案展示圖](assets/project-showcase.png)

`tw-mobile-accessibility-consultant` 是一個面向台灣繁體中文情境的行動 App、行動網站與 Web App 無障礙檢測 Skill。它將無障礙規範轉換成可執行的 QA 流程，協助產品、設計、工程、QA、稽核與專案管理人員從「發現問題」一路做到「提出修正、建立證據與安排回歸測試」。

本 Skill 特別適合需要依台灣政府無障礙規範建立檢測紀錄的專案。它包含 42 項 AA 工作化檢核架構、Android TalkBack 與 iOS VoiceOver 的基本人工測試流程，以及可直接複製使用的檢測報告模板。官方規範、最新申請程序與正式認證結果仍應以主管機關公布的最新版本為準。[1] [2]

> **重要聲明：** 本 Skill 是工程與 QA 輔助工具，不是官方認證、標章核發或法律意見。檢測結論只適用於指定產品版本、裝置、作業系統、測試範圍與提供的證據。

## 主要能力

| 能力 | 說明 |
|---|---|
| 檢測範圍規劃 | 依產品類型、平台、版本與核心流程建立檢測計畫。 |
| 42 項 AA 檢核 | 將官方架構轉為可逐項記錄狀態、證據、缺失、修正與回歸測試的清單。 |
| 平台人工測試 | 提供 Android TalkBack、iOS VoiceOver 與行動 Web 的基本操作流程。 |
| 證據導向判定 | 區分通過、不通過、不適用與待確認，避免僅憑截圖過度宣稱合規。 |
| 修正建議 | 依產品、設計、工程與 QA 角色提供可執行的改善方向。 |
| 報告輸出 | 產出執行摘要、環境限制、逐項結果、重大缺失與回歸測試計畫。 |

## 何時使用

當使用者提出下列需求時，應使用本 Skill：

- 檢查 Android 或 iOS App 是否有無障礙問題。
- 依截圖、錄影、原始碼或操作描述進行初步診斷。
- 規劃 TalkBack 或 VoiceOver 的人工檢測流程。
- 將無障礙缺失整理成工程修正清單、QA 測試案例或驗收報告。
- 準備網站或 App 的無障礙內部稽核、版本驗收與回歸測試。
- 需要把台灣無障礙規範轉成產品團隊可以執行的工作項目。

若需求是一般 UI 美感評估、效能壓力測試、資安滲透測試或正式標章申請，應明確區分本 Skill 的協助範圍，不要將結果誤稱為完整認證。

## 安裝方式

### 安裝到 Skill 工作區

將本 repository 複製到你的 Skill 目錄，並保留 `SKILL.md`、`references/` 與 `templates/` 的相對結構：

```bash
git clone https://github.com/xuan905/tw-mobile-accessibility-consultant.git
cp -R tw-mobile-accessibility-consultant /path/to/skills/
```

本 Skill 不需要額外 API 金鑰，也沒有必要的外部服務。若要分析圖片、錄影或原始碼，請依執行環境提供相應檔案或內容；沒有實機資料時，Skill 會將結果標為「待確認」。

### 從 ClawHub 安裝

公開版本可從 [ClawHub Skill 頁面](https://clawhub.ai/xuan905/tw-mobile-accessibility-consultant) 查看與安裝。ClawHub 發佈版本採用其頁面所載的 MIT-0 授權說明；若你從其他來源取得內容，請以該來源的授權與版本資訊為準。

## 快速開始

最簡單的使用方式是先描述產品與要驗證的核心流程：

```text
請檢查「城市購物」App 的 Android 版本。
範圍是登入、商品搜尋、商品詳情、加入購物車與結帳。
目前有登入頁、商品頁與結帳頁截圖，沒有實機錄影。
請依 42 項 AA 架構輸出：通過、不通過、不適用、待確認，並列出修正優先順序。
```

Skill 應先確認產品範圍與證據，再執行以下順序：

1. 建立產品、版本、平台、裝置、OS、輔助工具與核心流程紀錄。
2. 判斷目前材料能支持的檢測層級；截圖只能做視覺初判，不能直接證明讀屏或焦點通過。
3. 依 42 項 AA 清單逐項記錄狀態、證據、觀察、建議與回歸測試。
4. 將阻斷操作、核心流程失敗、錯誤訊息不可感知與焦點遺失列為高優先級。
5. 輸出平台限制、未驗證事項與下一步測試建議。

## v2.0 核心案件資料模型

第二版的核心資料模型以案件、測試流程、測試環境、證據、檢核發現、回歸測試與摘要為主要實體。正式規格位於 [`schemas/audit-case.schema.json`](schemas/audit-case.schema.json)，可用於驗證案件檔案的欄位、型別、識別碼格式、狀態值與必要資訊。

```bash
python -m json.tool schemas/audit-case.schema.json >/dev/null
python -m json.tool examples/audit-case.example.json >/dev/null
```

完整範例位於 [`examples/audit-case.example.json`](examples/audit-case.example.json)。案件模型刻意將「證據」與「檢核結果」分開，讓同一份截圖、錄音、原始碼或實機紀錄可以被多個檢核引用；每個發現則以 `AA-01` 等穩定檢核編號與 `E-001` 等證據編號建立可追溯關係。

模型中的 `verification_level` 用來區分已觀察、可重現、由材料推定與待人工審查；`status` 則固定使用 `pass`、`fail`、`not_applicable` 與 `pending`。這兩組欄位不可混用：例如「由截圖推定沒有問題」仍可能是 `pending`，而不是 `pass`。

## 輸入材料

提供的材料越完整，檢測結論越可靠。建議依下表準備資料：

| 材料 | 用途 | 沒有材料時的限制 |
|---|---|---|
| App 名稱、版本與平台 | 確定檢測對象與版本邊界 | 無法判定結論適用範圍。 |
| 裝置型號與 OS | 確定平台測試環境 | 只能提供一般性建議。 |
| 核心流程描述 | 界定測試路徑與完成條件 | 可能遺漏關鍵狀態。 |
| 截圖或畫面錄影 | 視覺、版面與可見狀態初判 | 無法證明讀屏、焦點與動態通知。 |
| TalkBack／VoiceOver 錄影或逐字結果 | 驗證元件名稱、順序、狀態與操作 | 讀屏相關項目應標為待確認。 |
| 原始碼或元件設定 | 分析語意、標籤、角色與狀態 | 只能指出風險，不能取代實機測試。 |
| 測試帳號與測試資料 | 執行登入、表單、錯誤與交易流程 | 不應使用真實個資、密碼或付款資訊。 |

請在上傳前移除密碼、權杖、個資、真實付款資訊與未經授權的內部資料。啟用 Android 或 iOS 輔助工具前，測試人員必須先確認關閉方式與相關手勢，避免操作中無法恢復裝置控制。

## 檢測流程

### 第一步：建立範圍與測試假設

先記錄產品名稱、版本、平台、裝置、OS、輔助工具、文字大小、顯示大小、測試帳號、核心流程與排除範圍。若使用者只提供單張截圖，應將任務定義為「視覺初檢」，不要包裝成完整 AA 檢測。

### 第二步：執行視覺與材料審查

檢查文字是否截斷、資訊是否只靠顏色、控制項是否有可理解的名稱、錯誤訊息是否明確、觸控目標是否容易操作、版面在放大文字後是否仍可使用。這一階段可以分析截圖、設計稿與原始碼，但應把尚未經實機驗證的結果保留為待確認。

### 第三步：執行 Android 人工測試

使用 TalkBack 進行線性瀏覽、探索觸控、輸入、頁面切換、彈窗、載入、錯誤、成功、權限拒絕、網路中斷與重新連線測試。接著改變字級、顯示大小、方向與相關顯示設定，再重跑核心流程。詳細步驟請參考 [`references/platform-manual-testing.md`](references/platform-manual-testing.md)。

### 第四步：執行 iOS 人工測試

使用 VoiceOver 檢查左右滑動順序、元件名稱、角色、提示、狀態、可執行動作、轉子導覽、輸入、返回、彈窗、鍵盤、載入、錯誤與成功狀態。再以文字大小、粗體文字、增加對比、減少動態效果、方向與縮放設定重跑核心流程。

### 第五步：逐項填寫 42 項 AA 清單

每個項目至少要有檢核狀態、證據位置、觀察結果、影響使用者、建議修正與回歸測試。狀態使用以下四種值：

| 狀態 | 定義 |
|---|---|
| 通過 | 已有足夠證據顯示指定範圍與環境符合該項要求。 |
| 不通過 | 已重現問題，或證據明確顯示不符合。 |
| 不適用 | 該項要求不適用於本產品或指定流程，並記錄理由。 |
| 待確認 | 需要實機、其他平台、完整流程或更多證據才能判定。 |

### 第六步：輸出修正與回歸計畫

先處理阻斷使用者完成核心流程的問題，再處理影響大量畫面或共用元件的問題，最後安排低風險的視覺與一致性改善。每項修正都應配對回歸步驟與預期結果，避免只寫「請改善無障礙」而沒有可驗證的完成條件。

## v2.0 檢測規則引擎

第二階段新增可配置的 [`rules/default-rules.json`](rules/default-rules.json) 與 [`scripts/evaluate_audit_rules.py`](scripts/evaluate_audit_rules.py)。規則引擎會檢查案件紀錄是否具備證據、修正建議、下一步行動、測試環境與一致的整體結論；它不會把截圖或原始碼誤當成實機讀屏通過，也不取代人工 TalkBack／VoiceOver 測試。

```bash
python scripts/validate_audit_case.py examples/audit-case.example.json
python scripts/evaluate_audit_rules.py examples/audit-case.example.json
python scripts/evaluate_audit_rules.py --format json examples/audit-case.example.json
```

詳細規格請見 [`docs/v2.0-rules-engine-spec.md`](docs/v2.0-rules-engine-spec.md)。目前支援 `finding`、`case` 與 `document` 三種規則作用域，並提供 high／medium／low 嚴重度與可供 CI 解析的 JSON 輸出。

## 本地驗證與自動化測試

安裝開發依賴後，可以直接驗證一份或多份 audit-case JSON：

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_audit_case.py examples/audit-case.example.json
python scripts/validate_audit_case.py --format json path/to/audit-case.json
```

驗證器會執行兩層檢查：第一層依 `schemas/audit-case.schema.json` 檢查 JSON Schema；第二層檢查完整文件內的證據、流程與環境引用，以及 `summary` 是否與實際 findings 統計一致。成功時回傳 exit code `0`，失敗時回傳 `1`，適合放入本地 Git hook 或 CI。

執行自動化測試：

```bash
python -m unittest discover -s tests -v
```

測試案例涵蓋有效範例、必要欄位缺失、無效 JSON、未知證據引用、未知流程引用、摘要不一致、機器可讀 JSON 輸出、多檔案驗證，以及空值、錯誤列舉、錯誤識別碼、額外欄位、日期格式、空流程與負數統計等邊界條件。規則引擎另有專用測試，覆蓋證據、修正、下一步與 pending 結論規則。Skill 的行為層級測試規格另見 [`tests/skill-test-cases.md`](tests/skill-test-cases.md)，涵蓋平台差異、證據限制、敏感資料、42 項檢核與非認證聲明。

## 輸出格式

預設輸出應包含以下章節：

1. 執行摘要與整體結論。
2. 檢測範圍、環境、材料與限制。
3. 重大缺失與優先級。
4. 42 項逐項檢核結果。
5. Android／iOS／行動 Web 平台測試紀錄。
6. 修正後回歸測試計畫。
7. 待確認事項與下一步。
8. 非官方認證聲明。

可直接使用 [`templates/accessibility-audit-report.md`](templates/accessibility-audit-report.md) 作為報告起點。若要轉成工程工作單，建議每項問題額外加入：問題標題、重現步驟、實際結果、預期結果、影響、建議元件或程式位置、負責角色、優先級與驗證條件。

## 範例：從問題到可驗證修正

### 問題描述

在登入頁，錯誤訊息只以紅色文字顯示，且沒有與帳號輸入欄位建立關聯。使用 TalkBack 或 VoiceOver 時，使用者可能只聽到「帳號」與「密碼」，不知道送出後發生了什麼錯誤。

### 不足的建議

```text
請改善登入錯誤提示。
```

### 可執行的建議

```text
將錯誤訊息設為可被輔助工具讀取的文字，與對應輸入欄位建立關聯，並在送出失敗後讓焦點或可感知通知落在可理解的位置。以 TalkBack 與 VoiceOver 重新執行：空白送出、格式錯誤、帳密錯誤、網路中斷與重新輸入；預期使用者能得知錯誤原因、受影響欄位與修正方式，且不需依賴顏色才能理解。
```

## 專案檔案

```text
.
├── SKILL.md
├── README.md
├── assets/
│   └── project-showcase.png
├── rules/
│   └── default-rules.json
├── examples/
│   └── audit-case.example.json
├── schemas/
│   └── audit-case.schema.json
├── .github/workflows/
│   └── validate.yml
├── scripts/
│   ├── validate_audit_case.py
│   ├── evaluate_audit_rules.py
│   └── create_github_plan.sh
├── src/
│   ├── __init__.py
│   └── audit_case_model.py
├── tests/
│   ├── test_validate_audit_case.py
│   ├── test_evaluate_audit_rules.py
│   └── skill-test-cases.md
├── requirements-dev.txt
├── docs/
│   ├── integration-guide.md
│   ├── issue-1-implementation-spec.md
│   ├── v2.0-rules-engine-spec.md
│   ├── v2-roadmap.md
│   └── v2-github-plan.md
├── references/
│   ├── platform-manual-testing.md
│   └── taiwan-aa-checklist.md
└── templates/
    └── accessibility-audit-report.md
```

- [`SKILL.md`](SKILL.md)：供 AI Agent 載入的核心工作指令與觸發條件。
- [`schemas/audit-case.schema.json`](schemas/audit-case.schema.json)：v2.0 核心案件資料模型的 JSON Schema。
- [`scripts/validate_audit_case.py`](scripts/validate_audit_case.py)：本地 JSON Schema 與跨引用一致性驗證器。
- [`scripts/evaluate_audit_rules.py`](scripts/evaluate_audit_rules.py)：v2.0 可配置檢測規則引擎。
- [`rules/default-rules.json`](rules/default-rules.json)：預設品質規則包。
- [`scripts/create_github_plan.sh`](scripts/create_github_plan.sh)：建立 v2.x Milestones 與 Issues 的可重複執行腳本。
- [`tests/test_validate_audit_case.py`](tests/test_validate_audit_case.py)：驗證器的自動化測試案例。
- [`tests/skill-test-cases.md`](tests/skill-test-cases.md)：Skill 行為層級與回歸測試規格。
- [`requirements-dev.txt`](requirements-dev.txt)：本地驗證與測試所需的 Python 開發依賴。
- [`examples/audit-case.example.json`](examples/audit-case.example.json)：可供複製修改的案件資料範例。
- [`.github/workflows/validate.yml`](.github/workflows/validate.yml)：提交與 Pull Request 的 JSON 及必要檔案驗證工作流。
- [`assets/project-showcase.png`](assets/project-showcase.png)：GitHub README 專案展示主視覺。
- [`references/taiwan-aa-checklist.md`](references/taiwan-aa-checklist.md)：42 項 AA 工作化檢核清單。
- [`references/platform-manual-testing.md`](references/platform-manual-testing.md)：Android、iOS 與行動 Web 人工測試流程。
- [`templates/accessibility-audit-report.md`](templates/accessibility-audit-report.md)：檢測報告與回歸測試模板。
- [`docs/integration-guide.md`](docs/integration-guide.md)：Claude Code、Claude Projects、Cursor 與其他 AI 助手的整合使用指南。
- [`docs/issue-1-implementation-spec.md`](docs/issue-1-implementation-spec.md)：v2.0 #1 Issue 的詳細實作規格與完成定義。
- [`docs/v2.0-rules-engine-spec.md`](docs/v2.0-rules-engine-spec.md)：v2.0 第二階段檢測規則引擎規格。
- [`docs/v2-roadmap.md`](docs/v2-roadmap.md)：第二版功能與擴充規劃。
- [`docs/v2-github-plan.md`](docs/v2-github-plan.md)：GitHub Milestones 與 Issues 對照表。

## 開發者文件

- [AI 助手整合使用指南](docs/integration-guide.md)
- [v2.0 #1 實作規格](docs/issue-1-implementation-spec.md)
- [v2.x GitHub 開發計畫](docs/v2-github-plan.md)

## GitHub 開發追蹤

v2.x 的開發工作已拆成 GitHub Milestones 與 Issues，對照表請見 [`docs/v2-github-plan.md`](docs/v2-github-plan.md)。目前分為 v2.0 核心案件資料與證據、v2.1 平台與框架支援、v2.2 CI 與回歸自動化，以及 v2.3 規範治理與品質四個里程碑。

## 版本與發佈

目前公開 repository 為第一版基礎版本。版本更新應同步調整 `SKILL.md`、參考資料、模板、README 與變更紀錄，並重新執行 Skill 結構驗證。若規範內容或主管機關程序更新，應在文件中標註查閱日期與來源，不要只依賴舊版 PDF。

## 授權與責任

本 repository 的程式與文件內容依 repository 所載授權與 ClawHub 發佈頁資訊使用。使用者必須自行確認其輸入材料、測試資料、截圖與程式碼具備合法使用權。任何檢測結果都不應被解讀為官方認證、法律意見或對特定產品的合規保證。

## 參考資料

[1]: https://accessibility.moda.gov.tw/Download/Detail/1425?Category=51 "數位發展部無障礙網路空間服務網：行動版無障礙規範相關文件"
[2]: https://docs.openclaw.ai/clawhub/ "ClawHub 官方文件：Skill 發佈與格式說明"
