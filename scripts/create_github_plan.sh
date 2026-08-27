#!/usr/bin/env bash
set -euo pipefail

REPO="xuan905/tw-mobile-accessibility-consultant"

milestone_number() {
  local title="$1"
  gh api "repos/${REPO}/milestones?state=all&per_page=100" --jq ".[] | select(.title == \"${title}\") | .number" | head -n 1
}

ensure_milestone() {
  local title="$1"
  local description="$2"
  local due_on="$3"
  local number
  number="$(milestone_number "$title")"
  if [[ -z "$number" ]]; then
    number="$(gh api "repos/${REPO}/milestones" -f title="$title" -f description="$description" -f due_on="$due_on" --jq '.number')"
    echo "created milestone ${title} (#${number})"
  else
    echo "existing milestone ${title} (#${number})"
  fi
  printf '%s\n' "$number"
}

ensure_issue() {
  local title="$1"
  local body="$2"
  local milestone="$3"
  local existing
  existing="$(gh issue list --repo "$REPO" --state all --search "in:title ${title}" --json title,number --jq ".[] | select(.title == \"${title}\") | .number" | head -n 1)"
  if [[ -n "$existing" ]]; then
    echo "existing issue #${existing}: ${title}"
  else
    gh api "repos/${REPO}/issues" -f title="$title" -f body="$body" -F milestone="$milestone" --jq '"created issue #" + (.number|tostring) + ": " + .title'
  fi
}

M20="$(ensure_milestone "v2.0 — 核心案件資料與證據" "建立可追蹤的 audit case 資料模型、證據索引、驗證器、報告與工程工單輸出。" "2026-10-31T23:59:59Z" | tail -n 1)"
M21="$(ensure_milestone "v2.1 — 平台與框架支援" "補強 Android、iOS 與 React Native、Flutter、Compose、SwiftUI 的平台修正指南。" "2026-12-31T23:59:59Z" | tail -n 1)"
M22="$(ensure_milestone "v2.2 — CI 與回歸自動化" "加入 CI/PR 檢查、版本差異、回歸矩陣與專案管理整合。" "2027-02-28T23:59:59Z" | tail -n 1)"
M23="$(ensure_milestone "v2.3 — 規範治理與品質" "建立規範版本管理、可配置檢核集合、品質閘門與歷史趨勢。" "2027-04-30T23:59:59Z" | tail -n 1)"

ensure_issue "建立 audit-case v2.0 資料模型與 JSON Schema" "## 目標\n把案件、流程、環境、證據、檢核發現、回歸測試與摘要定義成穩定資料模型。\n\n## 驗收條件\n- [ ] Schema 採 JSON Schema Draft 2020-12。\n- [ ] 定義識別碼格式與必要欄位。\n- [ ] 定義 pass/fail/not_applicable/pending 狀態。\n- [ ] 提供範例 JSON 與欄位說明。" "$M20"
ensure_issue "建立本地 audit-case 驗證器與 CLI 輸出" "## 目標\n提供 Python 驗證器，支援單檔、多檔、文字輸出與 JSON 輸出。\n\n## 驗收條件\n- [ ] 執行 JSON Schema 驗證。\n- [ ] 檢查證據、流程與環境的跨引用。\n- [ ] 檢查摘要統計一致性。\n- [ ] 成功回傳 exit code 0，失敗回傳 1。\n- [ ] 文件包含安裝與使用範例。" "$M20"
ensure_issue "建立證據索引與可追溯報告輸出" "## 目標\n讓截圖、錄影、音訊、原始碼與測試紀錄以證據 ID 被檢核結果引用。\n\n## 驗收條件\n- [ ] 支援 evidence ID 與 verification level。\n- [ ] 報告逐項結果可回溯至證據。\n- [ ] 區分觀察、推定與待人工確認。\n- [ ] 敏感資料欄位有遮罩與提醒。" "$M20"
ensure_issue "將無障礙缺失輸出為 GitHub Issue 與 QA 測試案例" "## 目標\n把 fail finding 轉換成工程可執行的工單與回歸測試。\n\n## 驗收條件\n- [ ] 包含重現步驟、實際/預期結果與證據。\n- [ ] 支援嚴重度、負責角色與外部 Issue ID。\n- [ ] 每項修正都有回歸條件。\n- [ ] 可避免共用元件造成的重複工單。" "$M20"
ensure_issue "補強 Android 原生無障礙修正指南" "## 目標\n涵蓋 Views/XML、Compose、TalkBack、名稱、狀態、焦點與動態通知。\n\n## 驗收條件\n- [ ] 提供常見元件的修正模式。\n- [ ] 附 TalkBack 回歸步驟。\n- [ ] 說明可能的副作用與平台差異。" "$M21"
ensure_issue "補強 iOS 原生與 VoiceOver 修正指南" "## 目標\n涵蓋 UIKit、SwiftUI、VoiceOver、traits、label、value、hint 與焦點管理。\n\n## 驗收條件\n- [ ] 提供常見元件的修正模式。\n- [ ] 附 VoiceOver 回歸步驟。\n- [ ] 涵蓋動態內容、表單與頁面轉場。" "$M21"
ensure_issue "加入跨平台框架支援範例" "## 目標\n補充 React Native、Flutter、Jetpack Compose 與 SwiftUI 的對照與限制。\n\n## 驗收條件\n- [ ] 同一需求有框架對照。\n- [ ] 明確區分靜態分析與實機驗證。\n- [ ] 範例可被開發者直接改寫。" "$M21"
ensure_issue "建立 CI/PR 無障礙風險檢查" "## 目標\n在 Pull Request 階段攔截常見語意、標籤、名稱與測試缺漏。\n\n## 驗收條件\n- [ ] 既有 JSON/單元測試納入 CI。\n- [ ] 輸出可讀錯誤與機器可讀結果。\n- [ ] 支援可配置的 warning 與 failure。\n- [ ] 不宣稱取代 TalkBack/VoiceOver 人工測試。" "$M22"
ensure_issue "建立版本差異與回歸測試矩陣" "## 目標\n比較兩次案件結果，識別改善、退化、新增、未變更與待確認項目。\n\n## 驗收條件\n- [ ] 依 finding/check ID 穩定比較。\n- [ ] 能輸出平台與版本差異。\n- [ ] 每個退化項目有警示。" "$M22"
ensure_issue "整合 GitHub Issue 狀態與報告追蹤" "## 目標\n讓檢測報告、工程 Issue、修正 PR 與回歸證據可互相追蹤。\n\n## 驗收條件\n- [ ] 建立穩定外部 Issue ID。\n- [ ] 能回寫或匯入修正狀態。\n- [ ] 採最小權限與敏感資料原則。" "$M22"
ensure_issue "建立規範版本與來源治理" "## 目標\n記錄規範版本、來源、查閱日期與變更差異。\n\n## 驗收條件\n- [ ] 報告包含規範版本欄位。\n- [ ] 來源更新不會靜默改變結論。\n- [ ] 提供人工審查變更流程。" "$M23"
ensure_issue "建立可配置檢核集合與報告品質閘門" "## 目標\n支援快速檢查、完整 AA、上市前驗收與回歸測試視圖。\n\n## 驗收條件\n- [ ] 清楚標示省略項目。\n- [ ] 缺證據、不適用無理由或無回歸條件時可被發現。\n- [ ] 產出品質檢查摘要。" "$M23"
