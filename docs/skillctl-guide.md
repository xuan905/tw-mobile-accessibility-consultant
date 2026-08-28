# skillctl 使用指南

`skillctl` 是一個不依賴第三方套件的本地 CLI，用來整理採用 `SKILL.md` 契約的 Skill 目錄。它把人工容易遺漏的結構檢查、清單盤點、新 Skill 初始化與 ZIP 打包集中成一致的命令列流程。

## 快速開始

在 repository 根目錄執行：

```bash
python scripts/skillctl.py inventory .
python scripts/skillctl.py validate .
python scripts/skillctl.py validate . --json > skill-inventory.json
```

`inventory` 會遞迴尋找所有 `SKILL.md`，列出 Skill 名稱、描述、狀態與 `scripts`、`references`、`templates` 資源數量。`validate` 會檢查 frontmatter、kebab-case 名稱、描述、body 行數、空 body，以及不應放在 Skill package 內的 `README.md`／`CHANGELOG.md`。

## 建立與打包

使用 `init` 建立符合 Skill Creator 基本契約的新骨架：

```bash
python scripts/skillctl.py init tw-example-skill --output ./skills
```

使用 `package` 產生可分享的 ZIP；工具會排除 `.git`、Python cache 與測試 cache：

```bash
python scripts/skillctl.py package ./skills/tw-example-skill \
  --output ./dist/tw-example-skill.zip
```

ZIP 內的根目錄會保留 Skill 名稱，例如 `tw-example-skill/SKILL.md`，因此可直接解壓到 Skill collection。

## 機器可讀輸出

CI 或其他工具可以使用 `--json`：

```bash
python scripts/skillctl.py validate ./skills --json
python scripts/skillctl.py inventory ./skills --json
```

`validate` JSON 包含 `valid` 與 `skills`；每個 Skill 會包含 `path`、`name`、`description`、`status`、`errors`、`resources` 與 `body_lines`。驗證成功回傳 exit code `0`，資料找不到回傳 `2`，檢查失敗回傳 `1`。

## 目錄契約

```text
skills/
└── tw-example-skill/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── templates/
```

`SKILL.md` 必須以 `---` 開始與結束 frontmatter，並包含 `name` 與 `description`。Skill 的使用者文件應放在 repository 的 `docs/` 或根目錄，而不是放進可載入的 Skill package。

## 限制

這個 CLI 只負責本地結構與格式檢查，不取代 Skill Creator 的完整語意審查、官方規範驗證或實際任務測試。它也不會自動修改既有 Skill；遇到錯誤時會輸出診斷，讓開發者決定如何修正。

## Markdown 內部連結與死鏈檢查

`validate` 與 `inventory` 預設會解析 `SKILL.md` 中的相對 Markdown 連結。外部 HTTP、mailto、tel 與頁內 anchor 不會被本地檢查；相對路徑必須存在於 Skill 目錄內，否則會回傳失敗。這也會阻擋 `../` 越出 Skill 目錄的連結，避免文件意外引用 package 外部檔案。

```bash
./bin/skillctl validate ./skills --json
./bin/skillctl validate ./skills --skip-links
```

只有在明確需要忽略連結檢查時才使用 `--skip-links`。CI 應保留預設檢查，讓缺少的 `references/*.md` 或其他內部文件在 Pull Request 階段就被發現。

## Pull Request collection CI

`.github/workflows/skills-collection.yml` 會在 Pull Request 開啟、更新或重新開啟時掃描整個 `skills/` 目錄；若 repository 沒有 collection 目錄，則驗證 repository 根目錄的 Skill workspace。工作流會上傳 JSON 診斷 artifact，方便查看哪個 Skill、哪一條連結或哪一個 frontmatter 欄位失敗。

## Publish：GitHub Release 與 Registry

`publish` 會先執行嚴格 Skill 驗證，再產生 ZIP。實際網路操作預設被阻擋，必須明確使用 `--confirm`；建議先用 `--dry-run` 檢查 package 與發佈計畫：

```bash
./bin/skillctl publish . \
  --target github-release \
  --repo owner/repository \
  --tag v2.0.0 \
  --dry-run
```

GitHub Release 實際發佈需要 `GITHUB_TOKEN` 或自訂環境變數，並指定 repository 與 tag：

```bash
GITHUB_TOKEN="$TOKEN" ./bin/skillctl publish . \
  --target github-release \
  --repo owner/repository \
  --tag v2.0.0 \
  --token-env GITHUB_TOKEN \
  --confirm
```

Registry adapter 使用 JSON `POST`，payload 會包含 Skill 名稱、版本、描述、ZIP 檔名與 Base64 package；endpoint 與 token 由使用者提供：

```bash
SKILL_REGISTRY_TOKEN="$TOKEN" ./bin/skillctl publish ./skills/my-skill \
  --target registry \
  --registry-url https://registry.example.test/api/skills \
  --token-env SKILL_REGISTRY_TOKEN \
  --confirm
```

請不要把 token 寫入規則檔、repository 或 shell history。`skillctl` 不會在 dry-run 中發出網路請求，也不會在缺少 `--confirm` 時執行實際 publish。
