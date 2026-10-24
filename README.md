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
2. 術語只維護 `translation/glossary.json`；直接修正內容，建置不會再批次改寫譯文。修改後更新相應的來源、段落指紋及待校對紀錄。
3. 執行 `python scripts/sync-data.py`，同步 `dist/data.js`。來源 PDF 版次與指紋保存在 `translation/sources.json`，不會在建置時悄悄換檔。
4. 安裝 `requirements-quality.txt`，執行 `python scripts/quality_check.py`、`python -m unittest discover -s tests` 及 `node scripts/validate.mjs`。
5. 推送至 `main`，GitHub Actions 驗證後自動部署 GitHub Pages。

本機預覽：`python -m http.server 8765 --directory dist`。

GitHub Pages 的發布來源使用 **GitHub Actions**。玩家入口是 `index.html`；龍主入口是 `gm.html`。

## 品質與完整性狀態

已收錄、結構檢查、來源段落對齊及語義校對分開記錄。目前網站全部 208 條、1,382 個段落／列表項已完成逐段原文初校，十八批記錄 215 項修正，並保存原文對照。獨立第二輪語義複核仍待完成；頁碼涵蓋或驗證腳本成功，不能單獨證明原書全文完整與語意正確。完整範圍與原文疑義見 [初校紀錄](translation/PROOFREADING.md)。

資料結構、校對失效規則、既有 PDF 差異及維護順序見 [翻譯品質流程](translation/README.md)。`python scripts/quality_check.py --require-semantic` 為嚴格語義關卡，目前預期不通過。一般發布檢查保留既有內容，但會攔下過期指紋、來源變更、術語錯誤與 content／網站資料漂移。

2026-10-24 的針對性複查修正了 21 處內容，包含擴充成長表的額外升級誤讀、一般敘事詞遭全域替換，以及角色／月亮／特色動作譯名。來源證據見 [修正紀錄](translation/correction-log.json)。

## 校訂與來源

譯文依提供的 Epyllion 核心書、獨立扮演書、基本動作表及 Encyclopedia Draconica 整理。頁碼指書內印刷頁碼，另標 PDF 者除外。既有中文 PDF 保留原始版本，尚未同步網站的規則校訂；差異請見網站「來源、譯名與校訂」。

查閱方式參考 [Root RPG 玩家手冊](https://github.com/Eagle0425/root-rpg-player-reference)。Epyllion 的介面與資料另行建立。

Epyllion © Magpie Games；設計 Marissa Kelly；插畫 Jason Poole；製圖 Stentor Danielson。原作文字、圖片與商標的權利屬各權利人，本儲存庫未將其宣告為開源授權。
