# 晨報 Morning Tape

自動爬取 18 檔股票 + 14 個科技媒體的每日晨報，每天早上 07:00（台灣時間）自動更新。

## 查看晨報

**網址**：`https://YOUR_USERNAME.github.io/morning-tape/晨報.html`  
（把 YOUR_USERNAME 換成你的 GitHub 帳號）

## 包含股票

美股：RDW、ORCL、BE、INTC、MU、SNDK、TSLA、SpaceX  
日股：鎧俠 Kioxia  
韓股：SK海力士、三星電子  
台股：華邦電、南亞科、旺宏、群聯、因華、泰福、永昕

## 產業新聞來源

EE Times、Semiconductor Eng.、IEEE Spectrum、Tom's Hardware、VentureBeat AI、MIT Tech Review、Ars Technica、TechCrunch、Reuters Tech、CNBC Tech、科技新報、iThome、Digitimes

## 本地執行

```bash
pip install feedparser deep-translator
python scraper.py
```
