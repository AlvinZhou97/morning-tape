#!/usr/bin/env python3
"""
晨報爬蟲 v2 — 每天早上執行，輸出 晨報.html
安裝依賴：pip install feedparser deep-translator
執行方式：python3 scraper.py
排程（Mac/Linux）：crontab -e 加入 → 0 7 * * * /usr/bin/python3 /絕對路徑/scraper.py
排程（Windows）：工作排程器 → 每天 07:00 執行 python3 scraper.py
"""

import feedparser, json, time, re, sys
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
from pathlib import Path

try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("請先執行：pip install feedparser deep-translator"); sys.exit(1)

OUT_HTML = Path(__file__).parent / "晨報.html"  # 輸出到 repo 根目錄

# ════════════════════════════════════════════════════════════
#  股票清單
# ════════════════════════════════════════════════════════════
STOCKS = [
    {"sym":"RDW",     "name":"Redwire",       "market":"美股",   "source":"yahoo", "ticker":"RDW",  "q":"Redwire RDW"},
    {"sym":"ORCL",    "name":"Oracle",        "market":"美股",   "source":"yahoo", "ticker":"ORCL", "q":"Oracle ORCL"},
    {"sym":"BE",      "name":"Bloom Energy",  "market":"美股",   "source":"yahoo", "ticker":"BE",   "q":"Bloom Energy BE"},
    {"sym":"INTC",    "name":"Intel",         "market":"美股",   "source":"yahoo", "ticker":"INTC", "q":"Intel INTC semiconductor"},
    {"sym":"MU",      "name":"美光 Micron",   "market":"美股",   "source":"yahoo", "ticker":"MU",   "q":"Micron MU memory chip"},
    {"sym":"SNDK",    "name":"SanDisk",       "market":"美股",   "source":"yahoo", "ticker":"SNDK", "q":"SanDisk SNDK flash"},
    {"sym":"TSLA",    "name":"特斯拉 Tesla",  "market":"美股",   "source":"yahoo", "ticker":"TSLA", "q":"Tesla TSLA"},
    {"sym":"SPACEX",  "name":"SpaceX",        "market":"未上市", "source":"gnews", "ticker":"",     "q":"SpaceX launch rocket"},
    {"sym":"KIOXIA",  "name":"鎧俠 Kioxia",   "market":"日股",   "source":"gnews", "ticker":"",     "q":"Kioxia 285A NAND flash"},
    {"sym":"HYNIX",   "name":"SK海力士",      "market":"韓股",   "source":"gnews", "ticker":"",     "q":"SK Hynix HBM memory chip"},
    {"sym":"SAMSUNG", "name":"三星電子",      "market":"韓股",   "source":"gnews", "ticker":"",     "q":"Samsung Electronics semiconductor chip"},
    {"sym":"2344",    "name":"華邦電",        "market":"台股",   "source":"gnews_zh","ticker":"",   "q":"華邦電 2344 DRAM"},
    {"sym":"2408",    "name":"南亞科",        "market":"台股",   "source":"gnews_zh","ticker":"",   "q":"南亞科 2408 記憶體"},
    {"sym":"2337",    "name":"旺宏",          "market":"台股",   "source":"gnews_zh","ticker":"",   "q":"旺宏 2337 NOR Flash"},
    {"sym":"8299",    "name":"群聯",          "market":"台股",   "source":"gnews_zh","ticker":"",   "q":"群聯 8299 NAND控制器"},
    {"sym":"4172",    "name":"因華生技",      "market":"台股",   "source":"gnews_zh","ticker":"",   "q":"因華生技 4172"},
    {"sym":"6541",    "name":"泰福-KY",       "market":"台股",   "source":"gnews_zh","ticker":"",   "q":"泰福 6541 生技"},
    {"sym":"4726",    "name":"永昕生醫",      "market":"台股",   "source":"gnews_zh","ticker":"",   "q":"永昕生醫 4726"},
]

# ════════════════════════════════════════════════════════════
#  產業動態來源（半導體 / AI / 科技 權威媒體）
# ════════════════════════════════════════════════════════════
INDUSTRY_FEEDS = [
    # 半導體 / 硬體
    {"name":"EE Times",               "cat":"半導體", "lang":"en",
     "url":"https://www.eetimes.com/feed/"},
    {"name":"Semiconductor Eng.",      "cat":"半導體", "lang":"en",
     "url":"https://semiengineering.com/feed/"},
    {"name":"IEEE Spectrum",           "cat":"半導體", "lang":"en",
     "url":"https://spectrum.ieee.org/feeds/feed.rss"},
    {"name":"Tom's Hardware",          "cat":"半導體", "lang":"en",
     "url":"https://www.tomshardware.com/feeds/all"},
    # AI / 科技
    {"name":"VentureBeat AI",         "cat":"AI",     "lang":"en",
     "url":"https://venturebeat.com/category/ai/feed/"},
    {"name":"MIT Tech Review",        "cat":"AI",     "lang":"en",
     "url":"https://www.technologyreview.com/feed/"},
    {"name":"Ars Technica",           "cat":"科技",   "lang":"en",
     "url":"https://feeds.arstechnica.com/arstechnica/technology-lab"},
    {"name":"TechCrunch",             "cat":"科技",   "lang":"en",
     "url":"https://techcrunch.com/feed/"},
    {"name":"The Verge",              "cat":"科技",   "lang":"en",
     "url":"https://www.theverge.com/rss/index.xml"},
    # 財經科技
    {"name":"Reuters Tech",           "cat":"財經",   "lang":"en",
     "url":"https://feeds.reuters.com/reuters/technologyNews"},
    {"name":"CNBC Tech",              "cat":"財經",   "lang":"en",
     "url":"https://www.cnbc.com/id/19854910/device/rss/rss.html"},
    # 台灣（已是中文，無需翻譯）
    {"name":"科技新報",               "cat":"台灣",   "lang":"zh",
     "url":"https://technews.tw/feed/"},
    {"name":"iThome",                 "cat":"台灣",   "lang":"zh",
     "url":"https://www.ithome.com.tw/rss"},
    {"name":"電子時報 Digitimes",     "cat":"台灣",   "lang":"zh",
     "url":"https://www.digitimes.com.tw/rss/rss.asp"},
]

MAX_STOCK_ITEMS    = 6   # 每檔個股最多幾則
MAX_INDUSTRY_ITEMS = 4   # 每個來源最多幾則
MAX_AGE_DAYS       = 14
TRANS_DELAY        = 0.4

# ════════════════════════════════════════════════════════════
#  工具函式
# ════════════════════════════════════════════════════════════
_tr = GoogleTranslator(source="auto", target="zh-TW")

def translate(text: str) -> str:
    if not text or not text.strip(): return text
    try:
        time.sleep(TRANS_DELAY)
        return _tr.translate(text[:4500]) or text
    except Exception as e:
        print(f"(翻譯失敗:{e})", end=" ")
        return text

def parse_date(entry) -> str:
    for f in ("published_parsed","updated_parsed"):
        t = getattr(entry, f, None)
        if t:
            try: return datetime(*t[:6], tzinfo=timezone.utc).strftime("%Y-%m-%d")
            except: pass
    return datetime.now().strftime("%Y-%m-%d")

def is_recent(date_str: str) -> bool:
    try:
        d = datetime.strptime(date_str,"%Y-%m-%d").replace(tzinfo=timezone.utc)
        return d >= datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    except: return True

def fetch_rss(url: str) -> list:
    for attempt in range(3):
        try:
            feed = feedparser.parse(url)
            return feed.entries or []
        except Exception as e:
            if attempt < 2: time.sleep(2)
            else: print(f"(RSS失敗:{e})", end=" "); return []

def clean(text: str) -> str:
    return re.sub(r"<[^>]+>","",text or "").strip()

POS = ["上漲","突破","創高","獲利","升評","買進","surge","beat","record","gain","win","upgrade","buy","strong"]
NEG = ["下跌","虧損","降評","裁員","警告","drop","fall","loss","miss","cut","downgrade","sell","layoff","warn"]

def sentiment(texts) -> str:
    s = " ".join(texts).lower()
    p = sum(1 for k in POS if k in s)
    n = sum(1 for k in NEG if k in s)
    return "positive" if p>n else ("negative" if n>p else "neutral")

# ════════════════════════════════════════════════════════════
#  個股抓取
# ════════════════════════════════════════════════════════════
def yahoo_url(ticker): return f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
def gnews_url(q, zh=False):
    eq = quote(q)
    if zh: return f"https://news.google.com/rss/search?q={eq}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    return f"https://news.google.com/rss/search?q={eq}&hl=en-US&gl=US&ceid=US:en"

def process_stock(stock: dict) -> dict:
    src  = stock["source"]
    need_tr = src != "gnews_zh"

    if src == "yahoo":
        entries = fetch_rss(yahoo_url(stock["ticker"]))
        # 若 Yahoo 不夠，補 Google News
        if len(entries) < 3:
            entries += fetch_rss(gnews_url(stock["q"]))
    elif src == "gnews":
        entries = fetch_rss(gnews_url(stock["q"]))
    else:  # gnews_zh
        entries = fetch_rss(gnews_url(stock["q"], zh=True))

    items, seen = [], set()
    for e in entries[:MAX_STOCK_ITEMS * 3]:
        date    = parse_date(e)
        if not is_recent(date): continue
        title   = clean(getattr(e,"title",""))
        if not title or title in seen: continue
        seen.add(title)
        summary = clean(getattr(e,"summary","") or getattr(e,"description",""))
        src_obj = getattr(e,"source",{})
        src_name= src_obj.get("title","") if isinstance(src_obj,dict) else str(src_obj)
        link    = getattr(e,"link","")
        items.append({
            "date":     date,
            "headline": translate(title) if need_tr else title,
            "detail":   translate(summary[:300]) if (need_tr and summary) else summary[:300],
            "source":   src_name,
            "link":     link,
        })
        if len(items) >= MAX_STOCK_ITEMS: break

    all_text = [i["headline"] for i in items] + [i["detail"] for i in items]
    return {
        "sym":       stock["sym"],
        "name":      stock["name"],
        "market":    stock["market"],
        "sentiment": sentiment(all_text) if items else "neutral",
        "summary":   items[0]["headline"] if items else "近期無重大消息",
        "items":     items,
    }

# ════════════════════════════════════════════════════════════
#  產業動態抓取
# ════════════════════════════════════════════════════════════
def fetch_industry() -> list:
    all_articles = []
    for feed_cfg in INDUSTRY_FEEDS:
        print(f"  [{feed_cfg['name']}]", end=" ", flush=True)
        entries = fetch_rss(feed_cfg["url"])
        need_tr = feed_cfg["lang"] != "zh"
        count = 0
        for e in entries[:MAX_INDUSTRY_ITEMS * 2]:
            date  = parse_date(e)
            if not is_recent(date): continue
            title = clean(getattr(e,"title",""))
            if not title: continue
            link  = getattr(e,"link","")
            all_articles.append({
                "date":    date,
                "source":  feed_cfg["name"],
                "cat":     feed_cfg["cat"],
                "headline": translate(title) if need_tr else title,
                "link":    link,
            })
            count += 1
            if count >= MAX_INDUSTRY_ITEMS: break
        print(f"✓ {count} 則")
    # 依日期排序，最新在前
    all_articles.sort(key=lambda x: x["date"], reverse=True)
    return all_articles

# ════════════════════════════════════════════════════════════
#  HTML 樣板
# ════════════════════════════════════════════════════════════
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>晨報 · Morning Tape</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@300;400;500;700&family=Noto+Serif+TC:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#f5f4ef;--card:#fff;--ink:#191b1f;--soft:#71757c;--line:#e8e5dc;--up:#1f7a4d;--down:#c2402d;--flat:#9a7b2e}
*{margin:0;padding:0;box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--ink);font-family:"Noto Sans TC","Hanken Grotesk",sans-serif;line-height:1.6}
.topbar{position:sticky;top:0;z-index:20;background:rgba(245,244,239,.93);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.topbar .inner{max-width:780px;margin:0 auto;padding:11px 16px 0}
.head-row{display:flex;align-items:center;gap:10px}
.logo{font-family:"Noto Serif TC",serif;font-weight:700;font-size:23px}
.logo small{font-family:"Hanken Grotesk";font-weight:700;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--soft);margin-left:7px;vertical-align:middle}
.gentime{margin-left:auto;font-family:"Hanken Grotesk";font-size:11.5px;color:var(--soft)}
.cats{display:flex;gap:2px;overflow-x:auto;padding:9px 0 0;border-bottom:1px solid var(--line);scrollbar-width:none}
.cats::-webkit-scrollbar{display:none}
.cat{flex:0 0 auto;background:none;border:none;cursor:pointer;font-family:inherit;font-size:13.5px;font-weight:600;color:var(--soft);padding:6px 10px 9px;position:relative;white-space:nowrap;transition:color .15s}
.cat:hover{color:var(--ink)}.cat.on{color:var(--ink)}
.cat.on::after{content:"";position:absolute;left:10px;right:10px;bottom:-1px;height:2.5px;background:var(--ink);border-radius:2px}
.cat .cn{font-family:"Hanken Grotesk";font-size:10px;font-weight:700;color:var(--soft);margin-left:2px}
.chips{display:flex;gap:6px;overflow-x:auto;padding:9px 0 10px;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;background:#fff;border:1px solid var(--line);border-radius:18px;padding:4px 12px;cursor:pointer;font-size:12px;font-weight:500;color:var(--ink);transition:.15s;display:flex;align-items:center;gap:5px}
.chip:hover{border-color:var(--ink)}
.cdot{width:6px;height:6px;border-radius:50%;background:var(--soft);flex:0 0 auto}
.cdot.up{background:var(--up)}.cdot.down{background:var(--down)}.cdot.flat{background:var(--flat)}
.csym{font-family:"Hanken Grotesk";font-weight:700;font-size:12px}
.wrap{max-width:780px;margin:0 auto;padding:14px 16px 100px}
.lead{font-size:12.5px;color:var(--soft);margin-bottom:12px}
/* overview */
.overview{background:var(--ink);color:#f3f2ee;border-radius:16px;padding:15px 17px;margin-bottom:14px}
.ov-title{font-family:"Hanken Grotesk";font-weight:800;font-size:10.5px;letter-spacing:.24em;text-transform:uppercase;color:#a9adb4;margin-bottom:4px}
.ov-mood{font-family:"Noto Serif TC",serif;font-size:15.5px;font-weight:600;line-height:1.55;margin-bottom:9px}
.ov-item{display:flex;gap:9px;padding:8px 0;border-top:1px solid rgba(255,255,255,.12)}
.ov-sym{flex:0 0 auto;font-family:"Hanken Grotesk";font-weight:700;font-size:11px;background:#f3f2ee;color:var(--ink);border-radius:5px;padding:2px 7px;height:fit-content;margin-top:2px}
.ov-point{font-size:13.5px;line-height:1.55;color:#e8e8e5}
/* date filter */
.dfilter{display:flex;gap:7px;align-items:center;flex-wrap:wrap;margin:0 0 12px}
.dlabel{font-size:12px;color:var(--soft);font-weight:600}
.dpill{background:#fff;border:1px solid var(--line);border-radius:16px;padding:4px 12px;font-size:12px;font-weight:500;color:var(--ink);cursor:pointer;font-family:inherit;transition:.15s}
.dpill:hover{border-color:var(--ink)}.dpill.on{background:var(--ink);color:#fff;border-color:var(--ink)}
/* 產業動態 */
.industry-box{background:#fff;border:1px solid var(--line);border-radius:16px;margin-bottom:14px;overflow:hidden}
.industry-head{display:flex;align-items:center;gap:10px;padding:13px 16px 10px;border-bottom:1px solid var(--line);cursor:pointer}
.industry-head h2{font-family:"Hanken Grotesk";font-weight:800;font-size:13px;letter-spacing:.12em;text-transform:uppercase}
.industry-head .itab-row{display:flex;gap:6px;overflow-x:auto;flex:1;scrollbar-width:none}
.industry-head .itab-row::-webkit-scrollbar{display:none}
.itab{background:none;border:1px solid var(--line);border-radius:14px;padding:3px 11px;font-size:11.5px;font-weight:600;cursor:pointer;font-family:inherit;white-space:nowrap;transition:.15s}
.itab:hover{border-color:var(--ink)}.itab.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.industry-list{max-height:420px;overflow-y:auto}
.iitem{display:flex;gap:10px;padding:10px 16px;border-top:1px solid var(--line)}
.iitem:first-child{border-top:none}
.isrc{flex:0 0 auto;font-family:"Hanken Grotesk";font-size:10px;font-weight:700;color:var(--soft);white-space:nowrap;margin-top:3px;max-width:72px;overflow:hidden;text-overflow:ellipsis}
.iright{flex:1;min-width:0}
.iright a{font-family:"Noto Serif TC",serif;font-size:14px;font-weight:600;color:var(--ink);text-decoration:none;line-height:1.4;display:block}
.iright a:hover{text-decoration:underline}
.idate{font-family:"Hanken Grotesk";font-size:10.5px;color:var(--soft);margin-top:3px}
.catdot{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:4px;vertical-align:middle}
.catdot.半導體{background:#3b6abf}.catdot.AI{background:#9b3bde}.catdot.科技{background:#2d9b6a}.catdot.財經{background:#c87c1a}.catdot.台灣{background:#c2402d}
/* cards */
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 15px 8px;margin-bottom:11px;scroll-margin-top:128px;transition:box-shadow .2s}
.card.reading{box-shadow:0 0 0 2.5px var(--ink);background:#fffdf7}
.card-head{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:2px}
.badge{font-family:"Hanken Grotesk";font-weight:700;font-size:11.5px;background:var(--ink);color:#fff;border-radius:6px;padding:2px 8px}
.cname{font-weight:700;font-size:16px}
.mktag{font-size:10.5px;color:var(--soft);border:1px solid var(--line);border-radius:5px;padding:1px 5px;font-weight:500}
.pill{margin-left:auto;font-family:"Hanken Grotesk";font-size:11px;font-weight:700;border-radius:14px;padding:2px 9px}
.pill.up{color:var(--up);background:rgba(31,122,77,.1)}
.pill.down{color:var(--down);background:rgba(194,64,45,.1)}
.pill.flat{color:var(--flat);background:rgba(154,123,46,.12)}
.saybtn{background:none;border:none;cursor:pointer;font-size:15px;padding:2px 3px;opacity:.45;transition:opacity .15s;margin-left:3px}
.saybtn:hover{opacity:1}
.summary{font-family:"Noto Serif TC",serif;font-size:14.5px;color:#2c2f34;margin:7px 0 10px;line-height:1.68}
.item{padding:10px 0;border-top:1px solid var(--line)}
.idate-s{font-family:"Hanken Grotesk";font-size:10.5px;font-weight:700;color:var(--soft);margin-bottom:3px}
.item h3{font-family:"Noto Serif TC",serif;font-weight:600;font-size:15px;line-height:1.42;margin-bottom:3px}
.item h3 a{color:inherit;text-decoration:none}.item h3 a:hover{text-decoration:underline}
.item p{font-size:13.5px;font-weight:300;color:#41454b;line-height:1.65}
.src{font-family:"Hanken Grotesk";font-size:10.5px;color:var(--soft);margin-top:3px}
.none{font-family:"Noto Serif TC",serif;font-style:italic;color:var(--soft);padding:5px 0 10px;font-size:13.5px}
/* play */
.playbar{position:fixed;bottom:14px;right:14px;z-index:30}
.playbtn{background:var(--ink);color:#fff;border:none;border-radius:22px;padding:10px 17px;font-size:12.5px;font-weight:600;font-family:inherit;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.28)}
.foot{text-align:center;font-size:11px;color:var(--soft);margin-top:18px;line-height:1.7}
</style>
</head>
<body>
<div class="topbar">
  <div class="inner">
    <div class="head-row">
      <div class="logo">晨報<small>Morning Tape</small></div>
      <span class="gentime">__GENTIME__</span>
    </div>
    <div class="cats" id="cats"></div>
    <div class="chips" id="chips"></div>
  </div>
</div>
<div class="wrap">
  <div class="lead">個股 __TOTAL__ 檔 · 近 14 天 · 依日期排序 · 自動翻譯繁體中文</div>
  <section class="overview" id="overview"></section>
  <div class="dfilter" id="dfilter"></div>
  <div class="industry-box" id="industryBox">
    <div class="industry-head" onclick="toggleIndustry()">
      <h2>📡 產業動態</h2>
      <div class="itab-row" id="itabs" onclick="event.stopPropagation()"></div>
      <span id="industryToggle" style="font-size:12px;color:var(--soft);margin-left:8px;white-space:nowrap">▾ 展開</span>
    </div>
    <div class="industry-list" id="industryList" style="display:none"></div>
  </div>
  <main id="feed"></main>
  <div class="foot">由 Python 爬蟲自動擷取並翻譯 · 僅供參考，非投資建議<br>來源：EE Times · Semiconductor Eng. · IEEE Spectrum · Tom's Hardware · VentureBeat · MIT Tech Review · Ars Technica · TechCrunch · Reuters · CNBC · 科技新報 · iThome</div>
</div>
<div class="playbar"><button class="playbtn" id="playBtn" onclick="speakAll()">▶ 播報</button></div>
<script>
const STOCKS_DATA=__STOCKS_JSON__;
const INDUSTRY_DATA=__INDUSTRY_JSON__;
const MK={"美股":"us","台股":"tw","日股":"jp","韓股":"kr","未上市":"pv"};
const CATS=[{k:"all",l:"全部"},{k:"us",l:"美股"},{k:"tw",l:"台股"},{k:"jp",l:"日股"},{k:"kr",l:"韓股"},{k:"pv",l:"未上市"}];
const SENT={positive:["up","偏多 ▲"],negative:["down","偏空 ▼"],neutral:["flat","中性 ●"]};
const DRANGES=[{d:0,l:"全部"},{d:1,l:"今天"},{d:3,l:"近3天"},{d:7,l:"近7天"},{d:14,l:"近14天"}];
const CATS_I=["全部","半導體","AI","科技","財經","台灣"];
let curF="all",dateDays=0,curICat="全部",industryOpen=false,speaking=false;

function fmtD(iso){const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(iso||"");if(!m)return iso||"";const d=new Date(+m[1],+m[2]-1,+m[3]),w=["日","一","二","三","四","五","六"];return m[1]+"/"+m[2]+"/"+m[3]+" 週"+w[d.getDay()]}
function inRange(iso){if(!dateDays)return true;const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(iso||"");if(!m)return true;const d=new Date(+m[1],+m[2]-1,+m[3]),cut=new Date();cut.setHours(0,0,0,0);cut.setDate(cut.getDate()-(dateDays-1));return d>=cut}

// ── 建立 UI ────────────────────────────────────────────────
function buildCats(){
  const cnt={};STOCKS_DATA.forEach(s=>{const k=MK[s.market]||"o";cnt[k]=(cnt[k]||0)+1;});
  document.getElementById("cats").innerHTML=CATS.filter(c=>c.k==="all"||cnt[c.k])
    .map(c=>`<button class="cat${c.k===curF?" on":""}" onclick="setF('${c.k}')">${c.l}<span class="cn">${c.k==="all"?STOCKS_DATA.length:cnt[c.k]}</span></button>`).join("");
}
function buildChips(){
  document.getElementById("chips").innerHTML=STOCKS_DATA.map((s,i)=>{const[cls]=SENT[s.sentiment]||SENT.neutral;return`<div class="chip" id="chip-${i}" onclick="document.getElementById('card-${i}').scrollIntoView({behavior:'smooth',block:'start'})"><span class="cdot ${cls}"></span><span class="csym">${s.sym}</span></div>`;}).join("");
}
function setF(k){
  curF=k;
  document.querySelectorAll(".cat").forEach(b=>{const label=CATS.find(c=>c.k===k)?.l||"";b.classList.toggle("on",b.textContent.trimStart().startsWith(label));});
  STOCKS_DATA.forEach((_,i)=>{const show=k==="all"||MK[STOCKS_DATA[i].market]===k;const c=document.getElementById("card-"+i),ch=document.getElementById("chip-"+i);if(c)c.style.display=show?"":"none";if(ch)ch.style.display=show?"":"none";});
  window.scrollTo({top:0,behavior:"smooth"});
}
function setDateRange(d){
  dateDays=d;
  document.querySelectorAll(".dpill").forEach(b=>b.classList.toggle("on",+b.dataset.d===d));
  buildFeed();
}

// ── 今日總覽 ────────────────────────────────────────────────
function buildOverview(){
  const ov=document.getElementById("overview");
  let pos=0,neg=0;const cands=[];
  STOCKS_DATA.forEach((s,i)=>{
    if(s.sentiment==="positive")pos++;else if(s.sentiment==="negative")neg++;
    (s.items||[]).forEach(it=>cands.push({sym:s.sym,h:it.headline||"",link:it.link||"",score:(s.sentiment!=="neutral"?1:0)}));
  });
  cands.sort((a,b)=>b.score-a.score);
  const mood=`${STOCKS_DATA.length} 檔完整資料　·　偏多 ${pos}　偏空 ${neg}`;
  ov.innerHTML=`<div class="ov-title">今日總覽 · Today</div><div class="ov-mood">${mood}</div>`+
    cands.slice(0,3).map(h=>`<div class="ov-item"><span class="ov-sym">${h.sym}</span><span class="ov-point">${h.h}</span></div>`).join("");
}

// ── 產業動態 ────────────────────────────────────────────────
function buildITabs(){
  document.getElementById("itabs").innerHTML=CATS_I.map(c=>`<button class="itab${c===curICat?" on":""}" onclick="filterIndustry('${c}')">${c}</button>`).join("");
}
function filterIndustry(cat){
  curICat=cat;
  document.querySelectorAll(".itab").forEach(b=>b.classList.toggle("on",b.textContent===cat));
  renderIndustry();
}
function renderIndustry(){
  const list=document.getElementById("industryList");
  const filtered=curICat==="全部"?INDUSTRY_DATA:INDUSTRY_DATA.filter(a=>a.cat===curICat);
  list.innerHTML=filtered.slice(0,50).map(a=>
    `<div class="iitem">
      <div class="isrc"><span class="catdot ${a.cat}"></span>${a.source}</div>
      <div class="iright">
        <a href="${a.link}" target="_blank" rel="noopener">${a.headline}</a>
        <div class="idate">${fmtD(a.date)}</div>
      </div>
     </div>`).join("");
}
function toggleIndustry(){
  industryOpen=!industryOpen;
  document.getElementById("industryList").style.display=industryOpen?"block":"none";
  document.getElementById("industryToggle").textContent=industryOpen?"▴ 收起":"▾ 展開";
}

// ── 個股卡片 ────────────────────────────────────────────────
function buildFeed(){
  document.getElementById("feed").innerHTML=STOCKS_DATA.map((s,i)=>{
    const[cls,label]=SENT[s.sentiment]||SENT.neutral;
    const sorted=(s.items||[]).slice().sort((a,b)=>(b.date||"").localeCompare(a.date||""));
    const items=sorted.filter(it=>inRange(it.date));
    let body=`<div class="summary">${s.summary||""}</div>`;
    if(!sorted.length) body+=`<p class="none">— 近期無重大消息 —</p>`;
    else if(!items.length) body+=`<p class="none">— 此期間無消息（共 ${sorted.length} 則較早消息）—</p>`;
    else body+=items.map(it=>
      `<div class="item">
        <div class="idate-s">${fmtD(it.date)}</div>
        <h3>${it.link?`<a href="${it.link}" target="_blank" rel="noopener">${it.headline||""}</a>`:it.headline||""}</h3>
        <p>${it.detail||""}</p>
        ${it.source?`<div class="src">— ${it.source}</div>`:""}
       </div>`).join("");
    return`<article class="card" id="card-${i}"><div class="card-head"><span class="badge">${s.sym}</span><span class="cname">${s.name}</span><span class="mktag">${s.market}</span><span class="pill ${cls}">${label}</span><button class="saybtn" onclick="speakCard(${i})">🔊</button></div>${body}</article>`;
  }).join("");
}
function buildDateFilter(){
  document.getElementById("dfilter").innerHTML=`<span class="dlabel">期間</span>`+DRANGES.map(r=>`<button class="dpill${r.d===dateDays?" on":""}" data-d="${r.d}" onclick="setDateRange(${r.d})">${r.l}</button>`).join("");
}

// ── TTS ─────────────────────────────────────────────────────
function pickV(){const vs=window.speechSynthesis?speechSynthesis.getVoices():[];return vs.find(v=>/zh|cmn|chinese|mandarin/i.test((v.lang||"")+(v.name||"")));}
function clearR(){document.querySelectorAll(".card.reading").forEach(c=>c.classList.remove("reading"));}
function stopSpeak(){speaking=false;if(window.speechSynthesis)speechSynthesis.cancel();clearR();const b=document.getElementById("playBtn");if(b)b.textContent="▶ 播報";}
function buildSpeech(idxs){const seq=[];idxs.forEach(i=>{const s=STOCKS_DATA[i];if(!s)return;seq.push({idx:i,text:`${s.name}。${s.summary}。`});(s.items||[]).filter(it=>inRange(it.date)).forEach(it=>seq.push({idx:i,text:`${it.headline}。${it.detail}。`}));});return seq;}
function visibleIdx(){return STOCKS_DATA.map((_,i)=>i).filter(i=>{const c=document.getElementById("card-"+i);return c&&c.style.display!=="none";});}
function speakSeq(seq){
  if(!window.speechSynthesis){alert("不支援語音");return;}
  if(!seq.length){alert("無可朗讀內容");return;}
  speechSynthesis.cancel();speaking=true;
  const btn=document.getElementById("playBtn");
  let p=0,cur=-1;
  function next(){if(!speaking||p>=seq.length){stopSpeak();return;}const{idx,text}=seq[p++];if(idx!==cur){clearR();cur=idx;const c=document.getElementById("card-"+idx);if(c){c.classList.add("reading");c.scrollIntoView({behavior:"smooth",block:"center"});}if(btn)btn.textContent=`⏹ ${STOCKS_DATA[idx]?.sym||""}`;}const u=new SpeechSynthesisUtterance(text);u.lang="zh-TW";const v=pickV();if(v)u.voice=v;u.onend=next;u.onerror=next;try{speechSynthesis.resume();}catch(_){}speechSynthesis.speak(u);}
  next();
  setTimeout(()=>{if(!speaking)return;if(!speechSynthesis.speaking&&!speechSynthesis.pending){stopSpeak();alert("語音啟動失敗。請確認手機音量已開，或安裝中文語音。");}},2000);
}
function speakAll(){if(speaking){stopSpeak();return;}speakSeq(buildSpeech(visibleIdx()));}
function speakCard(i){stopSpeak();speakSeq(buildSpeech([i]));}

// ── 初始化 ───────────────────────────────────────────────────
if(window.speechSynthesis){speechSynthesis.getVoices();speechSynthesis.onvoiceschanged=()=>{};}
buildCats();buildChips();buildOverview();buildDateFilter();
buildITabs();renderIndustry();
buildFeed();
document.querySelector(".cat")?.classList.add("on");
</script>
</body>
</html>
"""

def generate_html(stocks_data, industry_data, gen_time):
    html = HTML_TEMPLATE
    html = html.replace("__STOCKS_JSON__",   json.dumps(stocks_data,   ensure_ascii=False))
    html = html.replace("__INDUSTRY_JSON__", json.dumps(industry_data, ensure_ascii=False))
    html = html.replace("__TOTAL__",         str(len(stocks_data)))
    html = html.replace("__GENTIME__",       gen_time)
    return html

# ════════════════════════════════════════════════════════════
#  主程式
# ════════════════════════════════════════════════════════════
def main():
    gen_time = datetime.now().strftime("%Y/%m/%d %H:%M")
    print(f"\n🗞  晨報爬蟲 v2 — {gen_time}")
    print(f"   個股 {len(STOCKS)} 檔 + 產業來源 {len(INDUSTRY_FEEDS)} 個\n")

    print("【個股新聞】")
    stocks_data = []
    for i, s in enumerate(STOCKS, 1):
        print(f"[{i:2d}/{len(STOCKS)}]", end=" ")
        stocks_data.append(process_stock(s))

    print("\n【產業動態】")
    industry_data = fetch_industry()

    print(f"\n✅ 完成！共 {len(industry_data)} 則產業動態，生成 HTML...")
    OUT_HTML.write_text(generate_html(stocks_data, industry_data, gen_time), encoding="utf-8")
    print(f"📄 輸出：{OUT_HTML}\n   用 Chrome 開啟即可閱覽\n")

if __name__ == "__main__":
    main()
