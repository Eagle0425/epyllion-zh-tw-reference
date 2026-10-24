# 龍族史詩 Epyllion · 繁體中文手冊

供電腦、手機及桌上遊戲查閱的非官方翻譯參考網站。

公開網站：**https://eagle0425.github.io/epyllion-zh-tw-reference/**

## 內容

- 208 個翻譯條目，涵蓋核心規則、龍域、六大家族、創角及成長。
- 六種核心扮演書與三十個專屬動作、四種擴充扮演書。
- 九項基本動作、友誼寶石、月之魔法及暗影。
- 獨立龍主工作台：目標、原則、動作、首場流程、危害及遊玩範例。
- 《龍族百科》十七篇文章與特殊動作。
- 中英全文搜尋、來源篩選、條目永久連結、瀏覽器收藏與 PDF 下載。

無外部字體、分析追蹤或網頁登入要求。收藏僅儲存在使用者瀏覽器，玩家與龍主分開。兩個入口是閱讀分區，不是權限控制。

## 維護及部署

網站直接發布 `dist/`，不需安裝套件或建置。所有資源使用相對路徑，適用 GitHub Pages 子目錄。

1. 修改 `content/` 中相應的 JSON；保留 ID，避免破壞連結與收藏。
2. 執行 `python scripts/sync-data.py`，同步 `dist/data.js`。PDF 已保存在 `dist/downloads/`；若上一層另有原文／翻譯資料夾，會優先同步其原檔。
3. 執行 `node scripts/validate.mjs`，核對資料、角色、重要規則與下載檔。
4. 推送至 `main`，GitHub Actions 驗證後自動部署 GitHub Pages。

本機預覽：`python -m http.server 8765 --directory dist`。

GitHub Pages 的發布來源使用 **GitHub Actions**。玩家入口是 `index.html`；龍主入口是 `gm.html`。

## 校訂與來源

譯文依提供的 Epyllion 核心書、獨立扮演書、基本動作表及 Encyclopedia Draconica 整理。頁碼指書內印刷頁碼，另標 PDF 者除外。既有中文 PDF 保留原始版本，尚未同步網站的規則校訂；差異請見網站「來源、譯名與校訂」。

查閱方式參考 [Root RPG 玩家手冊](https://github.com/Eagle0425/root-rpg-player-reference)。Epyllion 的介面與資料另行建立。

Epyllion © Magpie Games；設計 Marissa Kelly；插畫 Jason Poole；製圖 Stentor Danielson。原作文字、圖片與商標的權利屬各權利人，本儲存庫未將其宣告為開源授權。
