# 翻譯品質與資料維護

借鏡 game-doc-template 的術語、結構、來源及語義分層流程，保留目前的桌邊速查介面與永久 ID。這是流程採用，並非將該工具全部程式或翻譯風格直接套入。

## 單一資料來源

- `project.json` 明列正式內容檔，避免把草稿或分段備份一起發布。
- `../content/` 保存實際標準譯文。建置不再執行全域用詞替換。
- `glossary.json` 是中英用詞與禁用譯名的唯一來源；`established` 表示既有用詞，不等於有人作過最終核准。
- `sources.json` 保存原書 SHA-256、PDF 總頁數與印刷頁偏移。
- `provenance.json` 保存明確的 PDF／印刷頁範圍；目前為頁範圍定位，不能當作段落完整性證據。
- `alignment.json` 為每個中文段落／列表項建立穩定識別與指紋。原文區塊對照尚未完成者保留空白。
- `source-blocks.json` 逐批保存實際原文與定位；對照必須指向這份清單中的同版原文，不能只填任意雜湊。
- `reviews.json` 的校對結論綁定譯文及來源指紋；修改內容後不得沿用過期結論。
- `artifacts.json` 記錄既有中文 PDF、原文參考檔與已知差異。
- `correction-log.json` 記錄本次修正的原句、新句與來源證據。

## 四個不同的狀態

1. 已收錄：網站中有該條目。
2. 結構通過：欄位、連結、頁碼、術語及發布資料一致。
3. 段落對齊：每個目標區塊都有可核對的原文區塊。
4. 語義核對：獨立審稿者已檢查規則、數字、時機、否定、例外、選擇權、表格與範例。

匯入的 208 條既有內容沒有足以逐段重現的歷史審稿證據，因此不追認為已完成語義核對。這不表示全部有錯，也不能以條目數或頁碼涵蓋率宣稱全文完整。

2026-10-24 已完成網站現有 **208 條、1,382 個中文區塊**的逐段原文初校，全部保存實際原文對照。十八批累計 215 項修正，具體範圍、修正與原文疑義見 [完整初校紀錄](PROOFREADING.md)。`reviews.json` 的 `source_check` 全為 compared；`semantic_status` 仍為 pending，等待獨立第二輪複核。原文清單尚未建立全書來源區塊分母，不能以中文對齊率宣稱原書每段均已全譯。

## 維護順序

1. 在原文中定位待修改的段落，核對來源版本；必要時目視檢查圖表。
2. 先確認術語與相關章節上下文，直接修改對應 `content/` 條目。
3. 記錄變更原因與來源。更新受影響區塊的 alignment 與 reviews 指紋；尚未核對的狀態必須保持 pending。
4. 逐段檢查是否遺漏數字、條件、例外、選擇權或範例；獨立審稿後才可標 verified，且須記錄 reviewer、evidence 及非空的 source_blocks。
5. 執行 `python scripts/sync-data.py`。
6. 安裝開發檢查依賴：`python -m pip install -r requirements-quality.txt`。
7. 執行 `python scripts/quality_check.py`、`python -m unittest discover -s tests` 及 `node scripts/validate.mjs`。

`quality_check.py --require-semantic` 是嚴格的全條目語義關卡；目前應失敗，不能將一般結構檢查通過等同於它通過。每次推送都檢查來源變更、過期校對指紋與 content→data.js 漂移。

## 跨成果與版本

目前 GitHub 儲存庫是後續維護入口。先前的 Sites 副本是舊版發布快照，不再作第二個可編輯的資料源。既有中文 PDF 保留原檔及已知差異；若重製 PDF，須從同一來源產生並更新 artifacts 指紋，不能僅根據檔名或修改日期判定同步。

## 參考

- https://github.com/wayne930242/game-doc-template
- `glossary.schema.json`、`scripts/validate_translation_structure.py`、`scripts/translation_completion.py`、語義審稿提示皆已靜態檢視。
- 保留範本中「結構與語義分開」的原則，另補上目前資料需要的指紋、發布一致性及既有成果版本紀錄。
