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
