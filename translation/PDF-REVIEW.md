# 2026-10-24 角色卡檢查與重製

已檢查原中文核心角色卡十二頁，並依獨立英文角色卡與網站標準正文重製。新增四種擴充角色卡八頁；每種角色固定兩頁 A4，可填寫姓名、色彩、屬性、經驗軌與友誼寶石。原始檔留在工作區「翻譯／原始版本」，GitHub 歷史亦保留舊版。

## 核對結果

| 範圍 | 處理 |
| --- | --- |
| 六份共用成長表 | 成年牙龍可取得另一份扮演書的動作；經驗格數 5／4／4／3／3；前三齡各三項成長、後兩齡各兩項。依圖表處理，不新增不存在的升級選項。 |
| 學者／工匠 | 保留完整名著與媒材清單、問題選項及特色動作進階；潛力鞍囊失手為最近用過，不武斷說已用掉。 |
| 勇者 | 原中文卡家族名及義務組合有誤，以英文鋼鐵／黃金家族配對校正；清晰思緒補回依答案行動單次＋1、完整進出路線與失手受突襲、陷入困境及分離的後果；承擔黑暗不限龍群夥伴。 |
| 自然之民 | 精魂嚮導失手後須彌補過失，不只是改變心意；大地獸靈的 what last visited 不限人物，what spirits dance 為起舞。 |
| 先知 | 家族義務與起始值依原書保留；黑暗之觸明確為吞食一塊黑暗，區分命中恩惠、7–9額外代價與失手。 |
| 戰士 | 寶藏恩賜明確對應屈服於黑暗／暗影魔法；敞開心胸最後一題是曾真正傷害或虧欠誰，而非單指錯怪。 |
| 四份擴充 | 元素使構造體恩賜、使節社交圈、孤龍預兆與持有、反叛者進階全部附在各自角色頁；孤龍及反叛者成長差異保留。 |
| 暗影行為 | 使用者明確偏好「玻璃心」，網站與兩份 PDF 同步使用「嘲笑或貶低玻璃心的人」。此為用詞偏好，不列作規則錯誤。 |

## 網站與 PDF 共用資料

`scripts/playbook_model.py` 只保存組合順序與段落參照，沒有另一份譯文。十種角色均包含五個專屬動作；所有創角選項、特色動作進階、成長與暗影內容都在角色頁直接顯示，不須另外查詢動作。既有條目與動作連結仍有效，動作連結會開啟完整扮演書並移至該動作。

兩份 PDF 共二十頁。逐區塊驗證 301 次內容出現，涵蓋共同規則在不同角色的重複出現；沒有遺漏。全頁已渲染檢查，另放大查看密集動作頁與成長欄，確認無溢欄、重疊及缺字。數值驗證與視覺檢查分開保存於 `playbook-pdf-check.json` 與 `playbook-pdf-build.json`。

字體沿用工作區「角色卡字型配置」：JasonHandwriting1-SemiBold 用於大標、1-Medium 用於區塊標題、2-SemiBold 用於小標與重點、2-Regular 用於內文。網站使用隨站託管的 WOFF2 子集，PDF 嵌入對應字體；原字體不修改，保留 SIL OFL 授權。

## 維護

安裝 `requirements-artifacts.txt`，提供含四個 TTF 與 OFL 檔的字體資料夾：

```text
python scripts/build-playbook-pdfs.py --font-directory <字體資料夾>
python scripts/register-playbook-pdfs.py --pdf-directory ../output/pdf
python scripts/verify-playbook-pdfs.py
python scripts/build-fonts.py --font-directory <字體資料夾>
python scripts/sync-data.py
python scripts/quality_check.py --report dist/translation-quality.json
python -m unittest discover -s tests -v
node scripts/validate.mjs
```

正文或組合順序改變後，舊 PDF 建置指紋會失效，發布檢查會阻擋。重製後仍須重新渲染檢查。此輪是原文初校的延伸，獨立第二輪語義複核仍待完成；精魂嚮導的條件範圍與孤龍進階等原文疑義繼續保留。

中文基本動作表不在本次角色卡重製範圍，仍保留舊版及已知的研讀他龍題數差異；其下載說明繼續明示。
