# v2.x GitHub 開發計畫

本文件將 [`docs/v2-roadmap.md`](v2-roadmap.md) 轉換成 GitHub 可追蹤的 Milestones 與 Issues。每個 Milestone 代表一個可獨立交付的階段；Issue 則描述一項可以被開發、審查與驗收的工作。實際狀態以 [GitHub Issues](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues) 與 [Milestones](https://github.com/xuan905/tw-mobile-accessibility-consultant/milestones) 為準。

## Milestones

| Milestone | 目標 | 預定日期 | Issues |
|---|---|---:|---|
| [v2.0 — 核心案件資料與證據](https://github.com/xuan905/tw-mobile-accessibility-consultant/milestone/1) | 完成案件資料模型、證據索引、驗證器、報告與工單基礎。 | 2026-10-31 | #1–#4 |
| [v2.1 — 平台與框架支援](https://github.com/xuan905/tw-mobile-accessibility-consultant/milestone/2) | 補強 Android、iOS 與跨平台框架的修正指南。 | 2026-12-31 | #5–#7 |
| [v2.2 — CI 與回歸自動化](https://github.com/xuan905/tw-mobile-accessibility-consultant/milestone/3) | 建立 CI／PR 檢查、版本差異、回歸矩陣與專案管理整合。 | 2027-02-28 | #8–#10 |
| [v2.3 — 規範治理與品質](https://github.com/xuan905/tw-mobile-accessibility-consultant/milestone/4) | 建立規範版本、可配置檢核集合與報告品質閘門。 | 2027-04-30 | #11–#12 |

## Issue 對照

### v2.0 — 核心案件資料與證據

| Issue | 工作 | 完成定義 |
|---:|---|---|
| [#1](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/1) | 建立 audit-case v2.0 資料模型與 JSON Schema | Schema、識別碼格式、狀態值與範例完成。 |
| [#2](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/2) | 建立本地 audit-case 驗證器與 CLI 輸出 | 支援 Schema、跨引用、摘要一致性與 exit code。 |
| [#3](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/3) | 建立證據索引與可追溯報告輸出 | 證據可被多項 finding 引用，且能標示驗證層級。 |
| [#4](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/4) | 將缺失輸出為 GitHub Issue 與 QA 測試案例 | 工單包含重現、預期、證據、責任角色與回歸條件。 |

### v2.1 — 平台與框架支援

| Issue | 工作 | 完成定義 |
|---:|---|---|
| [#5](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/5) | 補強 Android 原生無障礙修正指南 | 涵蓋 Views/XML、Compose、TalkBack、焦點與動態通知。 |
| [#6](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/6) | 補強 iOS 原生與 VoiceOver 修正指南 | 涵蓋 UIKit、SwiftUI、traits、label、value、hint 與焦點。 |
| [#7](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/7) | 加入跨平台框架支援範例 | 提供 React Native、Flutter、Compose、SwiftUI 對照。 |

### v2.2 — CI 與回歸自動化

| Issue | 工作 | 完成定義 |
|---:|---|---|
| [#8](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/8) | 建立 CI／PR 無障礙風險檢查 | 可配置 warning／failure，並保留人工測試界線。 |
| [#9](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/9) | 建立版本差異與回歸測試矩陣 | 能辨識改善、退化、新增、未變更與待確認。 |
| [#10](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/10) | 整合 GitHub Issue 狀態與報告追蹤 | Finding、Issue、PR、版本與回歸證據可互相追蹤。 |

### v2.3 — 規範治理與品質

| Issue | 工作 | 完成定義 |
|---:|---|---|
| [#11](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/11) | 建立規範版本與來源治理 | 報告記錄規範版本、來源、查閱日期與差異。 |
| [#12](https://github.com/xuan905/tw-mobile-accessibility-consultant/issues/12) | 建立可配置檢核集合與報告品質閘門 | 快速檢查、完整 AA、回歸視圖與品質缺漏檢查完成。 |

## 開發規則

每個 Issue 完成前，應更新文件、範例與測試，並確認不會將視覺初判誤稱為實機讀屏通過。涉及外部服務的功能要採最小權限，所有測試應使用去識別化資料。完成一個 Milestone 時，應建立版本標籤、更新 `CHANGELOG.md`，並重新執行本地驗證器與自動化測試。
