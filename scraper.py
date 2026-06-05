#!/usr/bin/env python3
"""
晨報爬蟲 v3 — 每天早上執行，輸出 晨報.html
安裝依賴：pip install feedparser deep-translator requests
"""

import feedparser, json, time, re, sys, requests
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
from pathlib import Path

try:
    from deep_translator import GoogleTranslator
    _HAS_TRANSLATOR = True
except ImportError:
    print("⚠️  deep-translator 未安裝，翻譯將跳過（英文標題直接顯示）")
    _HAS_TRANSLATOR = False

OUT_HTML = Path(__file__).parent / "晨報.html"

# ════════════════════════════════════════════════════════════
#  股票清單
# ════════════════════════════════════════════════════════════
STOCKS = [
    # ── 美股 US Stocks ──────────────────────────────────────────
    {"sym":"RDW",     "name":"Redwire",       "market":"美股", "source":"yahoo",    "ticker":"RDW",  "q":"Redwire RDW space"},
    {"sym":"ORCL",    "name":"Oracle",        "market":"美股", "source":"yahoo",    "ticker":"ORCL", "q":"Oracle ORCL earnings cloud AI database"},
    {"sym":"BE",      "name":"Bloom Energy",  "market":"美股", "source":"yahoo",    "ticker":"BE",   "q":"Bloom Energy BE fuel cell hydrogen power"},
    {"sym":"INTC",    "name":"Intel",         "market":"美股", "source":"yahoo",    "ticker":"INTC", "q":"Intel INTC chip semiconductor foundry"},
    {"sym":"MU",      "name":"美光 Micron",   "market":"美股", "source":"yahoo",    "ticker":"MU",   "q":"Micron MU DRAM HBM memory earnings"},
    {"sym":"SNDK",    "name":"SanDisk",       "market":"美股", "source":"yahoo",    "ticker":"SNDK", "q":"SanDisk SNDK Western Digital flash storage"},
    {"sym":"TSLA",    "name":"特斯拉 Tesla",  "market":"美股", "source":"yahoo",    "ticker":"TSLA", "q":"Tesla TSLA EV earnings deliveries"},
    # ── 台股 Taiwan Stocks ──────────────────────────────────────
    {"sym":"2344",    "name":"華邦電",        "market":"台股", "source":"gnews_zh", "ticker":"",     "q":"華邦電 2344 DRAM"},
    {"sym":"2408",    "name":"南亞科",        "market":"台股", "source":"gnews_zh", "ticker":"",     "q":"南亞科 2408 記憶體"},
    {"sym":"2409",    "name":"友達光電",       "market":"台股", "source":"gnews_zh", "ticker":"",     "q":"友達光電 2409 面板"},
    {"sym":"2337",    "name":"旺宏",          "market":"台股", "source":"gnews_zh", "ticker":"",     "q":"旺宏 2337 NOR Flash"},
    {"sym":"8299",    "name":"群聯",          "market":"台股", "source":"gnews_zh", "ticker":"",     "q":"群聯 8299 NAND控制器"},
    {"sym":"4172",    "name":"因華生技",      "market":"台股", "source":"gnews_zh", "ticker":"",     "q":"因華生技 4172"},
    {"sym":"6541",    "name":"泰福-KY",       "market":"台股", "source":"gnews_zh", "ticker":"",     "q":"泰福 6541 生技"},
    {"sym":"4726",    "name":"永昕生醫",      "market":"台股", "source":"gnews_zh", "ticker":"",     "q":"永昕生醫 4726"},
    # ── 韓股 Korean Stocks ─────────────────────────────────────
    {"sym":"SAMSUNG", "name":"三星電子",      "market":"韓股", "source":"gnews",    "ticker":"005930.KS", "q":"Samsung Electronics semiconductor chip"},
    {"sym":"HYNIX",   "name":"SK海力士",      "market":"韓股", "source":"gnews",    "ticker":"000660.KS", "q":"SK Hynix HBM memory chip"},
]

# ════════════════════════════════════════════════════════════
#  產業動態來源（半導體 / AI / 科技 權威媒體）
# ════════════════════════════════════════════════════════════
INDUSTRY_FEEDS = [
    # 半導體 / 硬體
    # ── 美國：半導體 / 硬體 ──────────────────────────────────────
    {"name":"EE Times",               "cat":"半導體", "lang":"en",
     "url":"https://www.eetimes.com/feed/"},
    {"name":"Semiconductor Eng.",      "cat":"半導體", "lang":"en",
     "url":"https://semiengineering.com/feed/"},
    {"name":"IEEE Spectrum",           "cat":"半導體", "lang":"en",
     "url":"https://spectrum.ieee.org/feeds/feed.rss"},
    {"name":"Tom's Hardware",          "cat":"半導體", "lang":"en",
     "url":"https://www.tomshardware.com/feeds/all"},
    {"name":"AnandTech (THW)",         "cat":"半導體", "lang":"en",
     "url":"https://www.tomshardware.com/feeds/all"},
    {"name":"EE Journal",              "cat":"半導體", "lang":"en",
     "url":"https://www.eejournal.com/feed/"},
    {"name":"Electronic Design",       "cat":"半導體", "lang":"en",
     "url":"https://www.electronicdesign.com/rss"},
    # ── 美國：AI / 科技 ───────────────────────────────────────
    {"name":"VentureBeat AI",          "cat":"AI",     "lang":"en",
     "url":"https://venturebeat.com/category/ai/feed/"},
    {"name":"MIT Tech Review",         "cat":"AI",     "lang":"en",
     "url":"https://www.technologyreview.com/feed/"},
    {"name":"Wired Business",          "cat":"AI",     "lang":"en",
     "url":"https://www.wired.com/feed/category/business/latest/rss"},
    {"name":"Ars Technica",            "cat":"科技",   "lang":"en",
     "url":"https://feeds.arstechnica.com/arstechnica/technology-lab"},
    {"name":"TechCrunch",              "cat":"科技",   "lang":"en",
     "url":"https://techcrunch.com/feed/"},
    {"name":"The Verge",               "cat":"科技",   "lang":"en",
     "url":"https://www.theverge.com/rss/index.xml"},
    {"name":"ZDNet",                   "cat":"科技",   "lang":"en",
     "url":"https://www.zdnet.com/news/rss.xml"},
    # ── 美國：財經 ────────────────────────────────────────────
    {"name":"Reuters Business",        "cat":"美國財經","lang":"en",
     "url":"https://feeds.reuters.com/reuters/businessNews"},
    {"name":"Reuters Tech",            "cat":"美國財經","lang":"en",
     "url":"https://feeds.reuters.com/reuters/technologyNews"},
    {"name":"CNBC Tech",               "cat":"美國財經","lang":"en",
     "url":"https://www.cnbc.com/id/19854910/device/rss/rss.html"},
    {"name":"CNBC Finance",            "cat":"美國財經","lang":"en",
     "url":"https://www.cnbc.com/id/10001147/device/rss/rss.html"},
    {"name":"MarketWatch Top",         "cat":"美國財經","lang":"en",
     "url":"https://feeds.marketwatch.com/marketwatch/topstories/"},
    {"name":"Forbes Tech",             "cat":"美國財經","lang":"en",
     "url":"https://www.forbes.com/technology/feed2/"},
    {"name":"Bloomberg Markets",       "cat":"美國財經","lang":"en",
     "url":"https://feeds.bloomberg.com/markets/news.rss"},
    # ── 韓國：科技 / 財經 ─────────────────────────────────────
    {"name":"Korea Herald Tech",       "cat":"韓國",   "lang":"en",
     "url":"https://www.koreaherald.com/feed/technology.xml"},
    {"name":"Korea Herald Business",   "cat":"韓國",   "lang":"en",
     "url":"https://www.koreaherald.com/feed/finance.xml"},
    {"name":"Business Korea",          "cat":"韓國",   "lang":"en",
     "url":"https://www.businesskorea.co.kr/rss/allArticles.xml"},
    {"name":"Korea JoongAng Daily",    "cat":"韓國",   "lang":"en",
     "url":"https://koreajoongangdaily.joins.com/api/rss/feed"},
    {"name":"Korea Times Biz",         "cat":"韓國",   "lang":"en",
     "url":"https://www.koreatimes.co.kr/www/rss/rss.xml"},
    {"name":"ET News Korea",           "cat":"韓國",   "lang":"en",
     "url":"https://english.etnews.com/rss/allArticles.xml"},
    # ── 日本：科技 / 財經 ─────────────────────────────────────
    {"name":"Nikkei Asia",             "cat":"日本",   "lang":"en",
     "url":"https://asia.nikkei.com/rss/feed/nar"},
    {"name":"Japan Times Tech",        "cat":"日本",   "lang":"en",
     "url":"https://www.japantimes.co.jp/feed/"},
    {"name":"NHK World Business",      "cat":"日本",   "lang":"en",
     "url":"https://www3.nhk.or.jp/rss/news/cat3.xml"},
    {"name":"The Register",            "cat":"日本",   "lang":"en",
     "url":"https://www.theregister.com/headlines.atom"},
    # ── 亞洲：半導體 / 科技 ───────────────────────────────────
    {"name":"DigiTimes (EN)",          "cat":"亞洲半導體","lang":"en",
     "url":"https://www.digitimes.com/rss/daily.xml"},
    {"name":"Asia Nikkei Semi",        "cat":"亞洲半導體","lang":"en",
     "url":"https://asia.nikkei.com/rss/feed/nar"},
    # ── 台灣 ─────────────────────────────────────────────────
    {"name":"科技新報",                "cat":"台灣",   "lang":"zh",
     "url":"https://technews.tw/feed/"},
    {"name":"iThome",                  "cat":"台灣",   "lang":"zh",
     "url":"https://www.ithome.com.tw/rss"},
    {"name":"Digitimes 電子時報",      "cat":"台灣",   "lang":"zh",
     "url":"https://www.digitimes.com.tw/rss/rss.asp"},
    {"name":"MoneyDJ 科技",            "cat":"台灣",   "lang":"zh",
     "url":"https://www.moneydj.com/KMDJ/News/NewsRSS.aspx?SectionId=t"},
    {"name":"鉅亨網科技",              "cat":"台灣",   "lang":"zh",
     "url":"https://news.cnyes.com/api/v3/news/category/tech?hasImage=0&limit=20"},
]

MAX_STOCK_ITEMS    = 6   # 每檔個股最多幾則
MAX_INDUSTRY_ITEMS = 4   # 每個來源最多幾則
MAX_AGE_DAYS       = 14
TRANS_DELAY        = 0.4

# ════════════════════════════════════════════════════════════
#  工具函式
# ════════════════════════════════════════════════════════════
_tr = GoogleTranslator(source="auto", target="zh-TW") if _HAS_TRANSLATOR else None

def translate(text: str) -> str:
    if not text or not text.strip(): return text
    if not _tr: return text          # 沒有翻譯器就直接回傳原文
    for attempt in range(2):
        try:
            time.sleep(TRANS_DELAY)
            result = _tr.translate(text[:4500])
            return result if result else text
        except Exception as e:
            if attempt == 0:
                time.sleep(2)        # 第一次失敗等2秒再試
            else:
                print(f"(翻譯略過:{type(e).__name__})", end=" ")
                return text          # 第二次失敗就回傳原文，不中斷
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
    """用瀏覽器 User-Agent 抓取 RSS，避免被封鎖"""
    AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Googlebot/2.1 (+http://www.google.com/bot.html)",
    ]
    headers_base = {"Accept": "application/rss+xml, application/xml, text/xml, */*",
                    "Accept-Language": "en-US,en;q=0.9"}
    for attempt, agent in enumerate(AGENTS):
        try:
            hdrs = {**headers_base, "User-Agent": agent}
            r = requests.get(url, headers=hdrs, timeout=12)
            if r.status_code == 200 and r.content:
                feed = feedparser.parse(r.content)
                if feed.entries:
                    return feed.entries
            # 若 requests 抓到空，退回 feedparser 直連
            feed = feedparser.parse(url)
            if feed.entries:
                return feed.entries
        except Exception as e:
            if attempt == len(AGENTS)-1:
                print(f"(RSS失敗:{e})", end=" ")
            else:
                time.sleep(1.5)
    return []

def yahoo_url(ticker):
    return f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"

def gnews_url(q, zh=False):
    eq = quote(q)
    if zh:
        return f"https://news.google.com/rss/search?q={eq}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    return f"https://news.google.com/rss/search?q={eq}&hl=en-US&gl=US&ceid=US:en"

def cnyes_url(stock_id):
    """鉅亨網台股新聞 RSS（比 Google News 更穩定）"""
    return f"https://news.cnyes.com/api/v3/news/category/tw_stock?hasImage=0&limit=30&startAt=0"

def moneydj_url(stock_id):
    """MoneyDJ 台股新聞 RSS"""
    return f"https://www.moneydj.com/KMDJ/News/NewsRSS.aspx?StockSymbol={stock_id}"

def tw_stock_news_urls(stock_id, stock_name):
    """台股多來源 RSS 清單，按可靠度排序"""
    q_tw = quote(f"{stock_name} {stock_id}")
    q_en = quote(f"{stock_id} stock Taiwan")
    return [
        moneydj_url(stock_id),
        f"https://news.google.com/rss/search?q={q_tw}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        f"https://news.google.com/rss/search?q={q_en}&hl=en-US&gl=US&ceid=US:en",
    ]

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
def extract_content(entry) -> str:
    """從 RSS entry 取得最完整的文章內容"""
    parts = []
    content = getattr(entry, 'content', [])
    if content:
        c = content[0]
        val = c.get('value', '') if isinstance(c, dict) else str(c)
        t = clean(val)
        if t: parts.append(t)
    for field in ('summary', 'description', 'subtitle'):
        t = clean(getattr(entry, field, '') or '')
        if t and t not in ' '.join(parts):
            parts.append(t)
    combined = ' '.join(parts)
    combined = re.sub(r'\s{2,}', ' ', combined).strip()
    return combined


def build_detail(entry, need_tr: bool) -> str:
    """組合文章內容，翻譯並格式化成可讀段落"""
    text = extract_content(entry)
    if not text:
        return ''
    text = text[:1200]
    if need_tr:
        text = translate(text)
    sentences = re.split(r'(?<=[。.!?！？])\s*', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) >= 5:
        mid = len(sentences) // 2
        return '　　' + ''.join(sentences[:mid]) + '\n　　' + ''.join(sentences[mid:])
    return '　　' + ''.join(sentences)


def process_stock(stock: dict) -> dict:
    src     = stock["source"]
    sym     = stock["sym"]
    need_tr = src != "gnews_zh"
    entries = []

    if src == "yahoo":
        entries = fetch_rss(yahoo_url(stock["ticker"]))
        if len(entries) < 3:
            entries += fetch_rss(gnews_url(stock["q"]))
        if len(entries) < 3:
            entries += fetch_rss(f"https://www.bing.com/news/search?q={quote(stock['q'])}&format=rss")
    elif src == "gnews_zh":
        name = stock.get("name","").replace("-KY","")
        for url in tw_stock_news_urls(sym, name):
            entries += fetch_rss(url)
            if len(entries) >= 3:
                break
    else:
        entries = fetch_rss(gnews_url(stock["q"]))
        if len(entries) < 3:
            entries += fetch_rss(gnews_url(stock["q"].split()[0]))

    items, seen = [], set()
    for e in entries[:MAX_STOCK_ITEMS * 3]:
        date    = parse_date(e)
        if not is_recent(date): continue
        title   = clean(getattr(e,"title",""))
        if not title or title in seen: continue
        seen.add(title)
        src_obj = getattr(e,"source",{})
        src_name= src_obj.get("title","") if isinstance(src_obj,dict) else str(src_obj)
        link    = getattr(e,"link","")
        items.append({
            "date":     date,
            "headline": translate(title) if need_tr else title,
            "detail":   build_detail(e, need_tr),
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
    all_articles, seen_titles = [], set()
    success, failed = 0, 0
    for feed_cfg in INDUSTRY_FEEDS:
        try:
            entries = fetch_rss(feed_cfg["url"])
            need_tr = feed_cfg["lang"] != "zh"
            count = 0
            for e in entries[:MAX_INDUSTRY_ITEMS * 2]:
                date  = parse_date(e)
                if not is_recent(date): continue
                title = clean(getattr(e,"title",""))
                if not title or title in seen_titles: continue
                seen_titles.add(title)
                link  = getattr(e,"link","")
                all_articles.append({
                    "date":     date,
                    "source":   feed_cfg["name"],
                    "cat":      feed_cfg["cat"],
                    "headline": translate(title) if need_tr else title,
                    "detail":   build_detail(e, need_tr),
                    "link":     link,
                })
                count += 1
                if count >= MAX_INDUSTRY_ITEMS: break
            if count > 0:
                print(f"    ✓ {feed_cfg['name']}: {count} 則")
                success += 1
            else:
                print(f"    ○ {feed_cfg['name']}: 0 則（無最新文章）")
        except Exception as e:
            print(f"    ✗ {feed_cfg['name']}: 失敗 ({e})")
            failed += 1
    print(f"\n  產業動態：{success} 個來源成功，{failed} 個失敗，共 {len(all_articles)} 則")
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
<title>晨報</title>
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
/* 播報控制列 */
.tts-bar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:#fff;border:1px solid var(--line);border-radius:14px;padding:10px 14px;margin-bottom:14px}
.tts-controls{display:flex;align-items:center;gap:6px;font-family:"Hanken Grotesk";font-size:12.5px;color:var(--soft)}
.tts-label{font-weight:600;white-space:nowrap}
.auto-label{display:flex;align-items:center;gap:5px;font-family:"Hanken Grotesk";font-size:12.5px;font-weight:600;color:var(--soft);cursor:pointer;margin-left:auto;white-space:nowrap}
.auto-label input{cursor:pointer;width:15px;height:15px}
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
.idetail{font-size:12.5px;color:#4a4d54;line-height:1.72;margin-top:5px;white-space:pre-line}
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
.item p{font-size:13.5px;font-weight:300;color:#41454b;line-height:1.75;white-space:pre-line}
.src{font-family:"Hanken Grotesk";font-size:10.5px;color:var(--soft);margin-top:3px}
.none{font-family:"Noto Serif TC",serif;font-style:italic;color:var(--soft);padding:5px 0 10px;font-size:13.5px;display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.show-older{background:none;border:1.5px solid var(--line);border-radius:16px;
  padding:3px 10px;font-size:12px;font-weight:700;color:var(--soft);cursor:pointer;
  font-family:"Hanken Grotesk",sans-serif;transition:.15s;font-style:normal}
.show-older:hover{border-color:var(--ink);color:var(--ink)}
/* 管理股票抽屜 */
.manage-btn{background:none;border:1.5px solid var(--line);border-radius:20px;
  padding:5px 12px;font-family:inherit;font-size:12px;font-weight:700;
  color:var(--soft);cursor:pointer;transition:.15s;white-space:nowrap}
.manage-btn:hover{border-color:var(--ink);color:var(--ink)}
.mgr-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:50}
.mgr-overlay.open{display:block}
.mgr-drawer{position:fixed;top:0;right:-340px;width:320px;height:100vh;
  background:#fff;z-index:51;transition:right .3s cubic-bezier(.32,.72,0,1);
  display:flex;flex-direction:column;box-shadow:-4px 0 24px rgba(0,0,0,.12)}
.mgr-drawer.open{right:0}
.mgr-head{padding:16px 16px 12px;border-bottom:1px solid var(--line);
  display:flex;align-items:center;gap:8px}
.mgr-head h3{font-size:15px;font-weight:800;flex:1}
.mgr-close{background:none;border:none;font-size:18px;cursor:pointer;color:var(--soft);padding:2px 6px}
.mgr-tabs{display:flex;border-bottom:1px solid var(--line)}
.mgr-tab{flex:1;background:none;border:none;cursor:pointer;font-family:inherit;
  font-size:13px;font-weight:700;color:var(--soft);padding:10px 0;position:relative;transition:.15s}
.mgr-tab.on{color:var(--ink)}
.mgr-tab.on::after{content:"";position:absolute;left:20%;right:20%;bottom:0;
  height:2px;background:var(--ink);border-radius:2px}
.mgr-body{flex:1;overflow-y:auto;padding:12px 16px}
.mgr-section{font-family:"Hanken Grotesk";font-size:11px;font-weight:800;
  letter-spacing:.12em;text-transform:uppercase;color:var(--soft);
  margin:12px 0 6px}
.mgr-row{display:flex;align-items:center;gap:10px;padding:8px 0;
  border-bottom:1px solid var(--line)}
.mgr-row:last-child{border-bottom:none}
.mgr-sym{font-family:"Hanken Grotesk";font-weight:800;font-size:13px;min-width:48px}
.mgr-name{font-size:13px;flex:1;color:var(--soft)}
.mgr-mkt{font-size:11px;font-weight:700;padding:2px 7px;border-radius:6px}
.mgr-mkt.美股{background:#EEF2FF;color:#3730A3}
.mgr-mkt.台股{background:#F0FDF4;color:#166534}
.mgr-toggle{width:36px;height:20px;border-radius:10px;border:none;cursor:pointer;
  position:relative;transition:.2s;flex:0 0 auto}
.mgr-toggle.on{background:#4F46E5}
.mgr-toggle.off{background:#D1D5DB}
.mgr-toggle::after{content:"";position:absolute;width:16px;height:16px;
  background:#fff;border-radius:50%;top:2px;transition:.2s;box-shadow:0 1px 3px rgba(0,0,0,.2)}
.mgr-toggle.on::after{left:18px}
.mgr-toggle.off::after{left:2px}
.mgr-del{background:none;border:none;cursor:pointer;color:#DC2626;font-size:15px;padding:2px 5px}
/* 新增表單 */
.mgr-field{width:100%;border:1.5px solid var(--line);border-radius:10px;
  padding:9px 12px;font-family:inherit;font-size:14px;margin-bottom:8px;
  outline:none;transition:.15s}
.mgr-field:focus{border-color:#4F46E5}
.mgr-select{width:100%;border:1.5px solid var(--line);border-radius:10px;
  padding:9px 12px;font-family:inherit;font-size:14px;margin-bottom:8px;
  background:#fff;cursor:pointer}
.mgr-validate{width:100%;border:1.5px solid var(--line);border-radius:10px;
  padding:9px;font-family:inherit;font-size:13.5px;font-weight:700;
  cursor:pointer;transition:.15s;margin-bottom:6px}
.mgr-validate:hover{border-color:#4F46E5;color:#4F46E5}
.mgr-add-btn{width:100%;background:#4F46E5;color:#fff;border:none;border-radius:10px;
  padding:10px;font-family:inherit;font-size:14px;font-weight:800;cursor:pointer;
  transition:opacity .15s}
.mgr-add-btn:active{opacity:.8}
.mgr-add-btn:disabled{opacity:.4;cursor:default}
.mgr-msg{font-size:12.5px;padding:7px 10px;border-radius:8px;margin-bottom:8px}
.mgr-msg.ok{background:#F0FDF4;color:#166534}
.mgr-msg.err{background:#FFF5F5;color:#DC2626}
.mgr-hint{font-size:12px;color:var(--soft);line-height:1.55;
  background:#F9FAFB;border-radius:8px;padding:8px 10px;margin-top:6px}
/* 股價列 */
.price-row{display:flex;align-items:center;gap:8px;padding:8px 0 4px;
  border-top:1px solid var(--line);margin-top:8px;flex-wrap:wrap}
.price-val{font-family:"Hanken Grotesk";font-weight:800;font-size:18px;color:var(--ink)}
.price-chg{font-family:"Hanken Grotesk";font-size:12.5px;font-weight:700}
.price-chg.up{color:var(--up)}.price-chg.down{color:var(--down)}.price-chg.flat{color:var(--flat)}
.price-time{font-size:11px;color:var(--soft);margin-left:auto}
.price-refresh{background:none;border:1.5px solid var(--line);border-radius:20px;
  padding:3px 10px;font-size:11px;font-weight:700;cursor:pointer;color:var(--soft);transition:.15s}
.price-refresh:hover{border-color:var(--ink);color:var(--ink)}
.price-skeleton{font-size:12px;color:var(--soft);font-style:italic}
.playbtn{background:var(--ink);color:#fff;border:none;border-radius:20px;padding:9px 18px;font-size:13px;font-weight:600;font-family:inherit;cursor:pointer;white-space:nowrap;transition:opacity .15s}
.playbtn:active{opacity:.75}
.refresh-all-btn{background:none;border:1.5px solid var(--line);border-radius:20px;
  padding:7px 13px;font-family:inherit;font-size:12px;font-weight:700;
  color:var(--soft);cursor:pointer;transition:.15s;white-space:nowrap}
.refresh-all-btn:hover{border-color:var(--ink);color:var(--ink)}
.refresh-all-btn:disabled{opacity:.45;cursor:default}
.foot{text-align:center;font-size:11px;color:var(--soft);margin-top:18px;line-height:1.8}</style>
</head>
<body>
<div class="topbar">
  <div class="inner">
    <div class="head-row">
      <div class="logo">晨報<small>Morning Tape</small></div>
      <button class="manage-btn" onclick="openMgr()">⚙️ 管理股票</button>
      <span class="gentime">__GENTIME__</span>
    </div>
    <div class="cats" id="cats"></div>
    <div class="chips" id="chips"></div>
  </div>
</div>

<!-- 管理股票抽屜 -->
<div class="mgr-overlay" id="mgrOverlay" onclick="closeMgr()"></div>
<div class="mgr-drawer" id="mgrDrawer">
  <div class="mgr-head">
    <h3>⚙️ 管理股票</h3>
    <button class="mgr-close" onclick="closeMgr()">✕</button>
  </div>
  <div class="mgr-tabs">
    <button class="mgr-tab on" id="mgrTab1" onclick="switchMgrTab('list')">目前清單</button>
    <button class="mgr-tab" id="mgrTab2" onclick="switchMgrTab('add')">＋ 新增</button>
  </div>
  <div class="mgr-body" id="mgrList"><!-- 清單由 JS 建立 --></div>
  <div class="mgr-body" id="mgrAdd" style="display:none">
    <div class="mgr-hint" style="margin-bottom:14px;background:#EEF2FF;border:1px solid #C7D2FE">
      📋 <b>說明：</b>爬蟲清單（上方）的股票每天自動更新新聞。<br>
      這裡新增的是<b>額外的自訂股票</b>，儲存在您的手機瀏覽器，<b>不會有新聞資料</b>，只顯示股價。<br>
      如需新聞，請告知我把它加進爬蟲清單。
    </div>
    <div class="mgr-section">市場</div>
    <select class="mgr-select" id="addMkt">
      <option value="美股">🇺🇸 美股（NYSE / NASDAQ）</option>
      <option value="台股">🇹🇼 台股（TWSE / OTC）</option>
      <option value="韓股">🇰🇷 韓股（KRW）</option>
    </select>
    <div class="mgr-section">股票代號</div>
    <input class="mgr-field" id="addSym" placeholder="美股：AAPL　台股：2330"
           oninput="resetAddMsg()" autocapitalize="characters" autocorrect="off">
    <div class="mgr-section">公司名稱（可選）</div>
    <input class="mgr-field" id="addName" placeholder="留空會用代號代替">
    <button class="mgr-validate" onclick="doValidate()">🔍 驗證代號格式</button>
    <div id="addMsg"></div>
    <button class="mgr-add-btn" id="addBtn" onclick="doAdd()" disabled>＋ 加入自訂清單</button>
    <div class="mgr-hint">
      ✅ 美股代號：1-5 個英文字母，如 AAPL、NVDA、TSM<br>
      ✅ 台股代號：4 位數字，如 2330、0050<br>
      ✅ 韓股代號：6 位數字，如 005930（三星）、000660（海力士）
    </div>
  </div>
</div>
<div class="wrap">
  <div class="lead">共 __TOTAL__ 檔 · 近 14 天 · 依日期排序 · 自動翻譯繁體中文　生成：__GENTIME__</div>
  <!-- 播報控制列 -->
  <div class="tts-bar">
    <button class="playbtn" id="playBtn" onclick="speakAll()">▶ 全部播報</button>
    <button class="refresh-all-btn" id="refreshAllBtn" onclick="refreshAllPrices()">🔄 更新股價</button>
    <div class="tts-controls">
      <span class="tts-label">語速</span>
      <input type="range" min="0.6" max="1.8" step="0.2" value="1.0"
             oninput="setRate(this.value)" style="width:80px;vertical-align:middle">
      <span id="rateLabel" style="font-size:12px;min-width:26px">1x</span>
    </div>
    <label class="auto-label" title="開啟後每次進入頁面自動播報">
      <input type="checkbox" id="autoToggle"> 自動播報
    </label>
  </div>
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
  <div class="foot">資料來源：Yahoo Finance · Google News · EE Times · IEEE Spectrum · VentureBeat · MIT Tech Review · Ars Technica · TechCrunch · Reuters · CNBC · 科技新報 · iThome<br>由 Python 爬蟲每日自動擷取翻譯 · 僅供參考，非投資建議</div>
</div>
<script>
const STOCKS_DATA=__STOCKS_JSON__;
const INDUSTRY_DATA=__INDUSTRY_JSON__;
const MK={"美股":"us","台股":"tw","韓股":"kr"};
const CATS=[{k:"all",l:"全部"},{k:"us",l:"美股"},{k:"tw",l:"台股"},{k:"kr",l:"韓股"}];
const SENT={positive:["up","偏多 ▲"],negative:["down","偏空 ▼"],neutral:["flat","中性 ●"]};
const DRANGES=[{d:0,l:"全部"},{d:1,l:"今天"},{d:3,l:"近3天"},{d:7,l:"近7天"},{d:14,l:"近14天"}];
const CATS_I=["全部","半導體","AI","科技","美國財經","韓國","日本","亞洲半導體","台灣"];
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
        ${a.detail?`<div class="idetail">${a.detail}</div>`:''}
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
  const hidden=typeof getHidden==='function'?getHidden():[];
  document.getElementById("feed").innerHTML=STOCKS_DATA.filter(s=>!hidden.includes(s.sym)).map((s,i)=>{
    const[cls,label]=SENT[s.sentiment]||SENT.neutral;
    const sorted=(s.items||[]).slice().sort((a,b)=>(b.date||"").localeCompare(a.date||""));
    const items=sorted.filter(it=>inRange(it.date));
    let body=`<div class="summary">${s.summary||""}</div>`;
    if(!sorted.length){
      body+=`<p class="none">— 近期無重大消息 —</p>`;
    } else if(!items.length){
      // 有舊消息但被日期過濾，提供展開按鈕
      body+=`<p class="none">— 目前期間無新消息 —
        <button class="show-older" onclick="toggleOlder(this,'older-${i}')">
          顯示 ${sorted.length} 則較早消息 ▾
        </button></p>
        <div id="older-${i}" style="display:none">
          ${sorted.map(it=>`<div class="item">
            <div class="idate-s">${fmtD(it.date)}</div>
            <h3>${it.link?`<a href="${it.link}" target="_blank" rel="noopener">${it.headline||""}</a>`:it.headline||""}</h3>
            <p>${it.detail||""}</p>
            ${it.source?`<div class="src">— ${it.source}</div>`:""}
          </div>`).join("")}
        </div>`;
    } else {
      body+=items.map(it=>
        `<div class="item">
          <div class="idate-s">${fmtD(it.date)}</div>
          <h3>${it.link?`<a href="${it.link}" target="_blank" rel="noopener">${it.headline||""}</a>`:it.headline||""}</h3>
          <p>${it.detail||""}</p>
          ${it.source?`<div class="src">— ${it.source}</div>`:""}
         </div>`).join("");
    }
    const priceRow=`<div class="price-row" id="price-${s.sym}"><span class="price-skeleton">股價載入中...</span></div>`;
    return`<article class="card" id="card-${i}"><div class="card-head"><span class="badge">${s.sym}</span><span class="cname">${s.name}</span><span class="mktag">${s.market}</span><span class="pill ${cls}">${label}</span><button class="saybtn" onclick="speakCard(${i})">🔊</button></div>${priceRow}${body}</article>`;
  }).join("");
}
function buildDateFilter(){
  document.getElementById("dfilter").innerHTML=`<span class="dlabel">期間</span>`+DRANGES.map(r=>`<button class="dpill${r.d===dateDays?" on":""}" data-d="${r.d}" onclick="setDateRange(${r.d})">${r.l}</button>`).join("");
}

// ── TTS ─────────────────────────────────────────────────────
let ttsRate=1.0;
function pickV(){const vs=window.speechSynthesis?speechSynthesis.getVoices():[];return vs.find(v=>/zh|cmn|chinese|mandarin/i.test((v.lang||"")+(v.name||"")));}
function clearR(){document.querySelectorAll(".card.reading").forEach(c=>c.classList.remove("reading"));}
function updatePlayBtn(){const b=document.getElementById("playBtn");if(b)b.textContent=speaking?"⏹ 停止":"▶ 全部播報";}
function stopSpeak(){speaking=false;if(window.speechSynthesis)speechSynthesis.cancel();clearR();updatePlayBtn();}
function buildSpeech(idxs){const seq=[];idxs.forEach(i=>{const s=STOCKS_DATA[i];if(!s)return;seq.push({idx:i,text:`${s.name}。${s.summary}。`});(s.items||[]).filter(it=>inRange(it.date)).forEach(it=>seq.push({idx:i,text:`${it.headline}。${it.detail}。`}));});return seq;}
function visibleIdx(){
  const hidden=typeof getHidden==='function'?getHidden():[];
  return STOCKS_DATA.map((_,i)=>i).filter(i=>{
    const s=STOCKS_DATA[i];
    if(hidden.includes(s?.sym)) return false;
    const c=document.getElementById("card-"+i);
    return c&&c.style.display!=="none";
  });
}
function toggleOlder(btn,id){
  const el=document.getElementById(id);
  if(!el)return;
  const open=el.style.display==='none';
  el.style.display=open?'':'none';
  btn.textContent=open?`收起 ▴`:`顯示 ${el.querySelectorAll('.item').length} 則較早消息 ▾`;
}
function speakSeq(seq){
  if(!window.speechSynthesis){alert("此瀏覽器不支援語音功能");return;}
  if(!seq.length){alert("目前無可朗讀內容");return;}
  speechSynthesis.cancel();speaking=true;updatePlayBtn();
  const btn=document.getElementById("playBtn");
  let p=0,cur=-1;
  function next(){
    if(!speaking||p>=seq.length){stopSpeak();return;}
    const{idx,text}=seq[p++];
    if(idx!==cur){clearR();cur=idx;const c=document.getElementById("card-"+idx);if(c){c.classList.add("reading");c.scrollIntoView({behavior:"smooth",block:"center"});}if(btn)btn.textContent=`⏹ ${STOCKS_DATA[idx]?.sym||""}`;}
    const u=new SpeechSynthesisUtterance(text);
    u.lang="zh-TW";u.rate=ttsRate;const v=pickV();if(v)u.voice=v;
    u.onend=next;u.onerror=next;
    try{speechSynthesis.resume();}catch(_){}
    speechSynthesis.speak(u);
  }
  next();
  setTimeout(()=>{if(!speaking)return;if(!speechSynthesis.speaking&&!speechSynthesis.pending){stopSpeak();alert("語音啟動失敗。\n請確認：\n1. 手機音量是否開啟\n2. 是否安裝中文語音（設定 › 無障礙 › 文字轉語音）");}},2000);
}
function speakAll(){if(speaking){stopSpeak();return;}speakSeq(buildSpeech(visibleIdx()));}
function speakCard(i){stopSpeak();speakSeq(buildSpeech([i]));}
function setRate(v){ttsRate=parseFloat(v);document.getElementById("rateLabel").textContent=v+"x";}

// ── 初始化 ───────────────────────────────────────────────────
if(window.speechSynthesis){speechSynthesis.getVoices();speechSynthesis.onvoiceschanged=()=>{};}
buildCats();buildChips();buildOverview();buildDateFilter();
buildITabs();renderIndustry();
buildFeed();
document.querySelector(".cat")?.classList.add("on");
setTimeout(refreshAllPrices, 500); // 頁面載入後自動取得股價

const autoKey="morningAutoPlay";
const autoToggle=document.getElementById("autoToggle");
if(autoToggle){
  autoToggle.checked = localStorage.getItem(autoKey)==="1";
  autoToggle.addEventListener("change",()=>localStorage.setItem(autoKey,autoToggle.checked?"1":"0"));
}
if(localStorage.getItem(autoKey)==="1"){
  setTimeout(()=>{ if(!speaking) speakAll(); }, 1500);
}

// ── 股價即時更新 ──────────────────────────────────────────────
const priceCache={};

function yfSym(sym,market){
  if(market==='台股') return sym+'.TW';
  if(market==='韓股'){
    const kr={SAMSUNG:'005930.KS',HYNIX:'000660.KS'};
    return kr[sym]||sym+'.KS';
  }
  return sym;
}

function fmtCurrency(price,currency){
  if(price==null||isNaN(price)) return '—';
  if(currency==='USD') return '$'+price.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
  if(currency==='TWD') return 'NT$'+Math.round(price).toLocaleString('zh-TW');
  if(currency==='KRW') return '₩'+Math.round(price).toLocaleString('ko-KR');
  return price.toFixed(2)+' '+(currency||'');
}

async function fetchYF(ticker){
  const base=`https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=1d`;
  // 先試直連，再試 CORS proxy
  const urls=[
    base,
    `https://corsproxy.io/?${encodeURIComponent(base)}`,
    `https://api.allorigins.win/raw?url=${encodeURIComponent(base)}`,
  ];
  for(const url of urls){
    try{
      const r=await Promise.race([
        fetch(url,{headers:{Accept:'application/json'}}),
        new Promise((_,rej)=>setTimeout(()=>rej(new Error('timeout')),6000))
      ]);
      if(!r.ok) continue;
      const d=await r.json();
      const meta=d?.chart?.result?.[0]?.meta;
      if(meta?.regularMarketPrice) return meta;
    }catch{continue;}
  }
  return null;
}

async function fetchPrice(sym,market){
  const el=document.getElementById('price-'+sym);
  if(!el) return;
  el.innerHTML='<span class="price-skeleton">更新中...</span>';
  const meta=await fetchYF(yfSym(sym,market));
  if(!meta){
    el.innerHTML=`<span class="price-skeleton">⚠️ 無法取得</span> <button class="price-refresh" onclick="fetchPrice('${sym}','${market}')">重試</button>`;
    return;
  }
  const price=meta.regularMarketPrice;
  const prev=meta.chartPreviousClose||meta.regularMarketPreviousClose||price;
  const chg=price-prev, pct=prev?(chg/prev)*100:0;
  priceCache[sym]={price,chg,pct,cur:meta.currency||'USD',time:new Date()};
  renderPrice(sym,market);
}

function renderPrice(sym,market){
  const el=document.getElementById('price-'+sym);
  if(!el) return;
  const d=priceCache[sym]; if(!d) return;
  const cls=d.chg>0?'up':d.chg<0?'down':'flat';
  const sign=d.chg>=0?'+':'';
  const t=d.time.toLocaleTimeString('zh-TW',{hour:'2-digit',minute:'2-digit'});
  el.innerHTML=`
    <span class="price-val">${fmtCurrency(d.price,d.cur)}</span>
    <span class="price-chg ${cls}">${sign}${fmtCurrency(d.chg,d.cur)} (${sign}${d.pct.toFixed(2)}%)</span>
    <span class="price-time">${t} 更新</span>
    <button class="price-refresh" onclick="fetchPrice('${sym}','${market}')">🔄</button>`;
}

async function refreshAllPrices(){
  const btn=document.getElementById('refreshAllBtn');
  if(btn){btn.textContent='更新中...';btn.disabled=true;}
  const hidden=typeof getHidden==='function'?getHidden():[];
  await Promise.allSettled(
    STOCKS_DATA.filter(s=>!hidden.includes(s.sym)).map(s=>fetchPrice(s.sym,s.market))
  );
  if(btn){btn.textContent='🔄 更新股價';btn.disabled=false;}
}

// ── 股票管理 ──────────────────────────────────────────────────
const HIDDEN_KEY='morningHidden'; // 隱藏的代號 array
const CUSTOM_KEY='morningCustom'; // 自訂新增的股票 array

function getHidden(){try{return JSON.parse(localStorage.getItem(HIDDEN_KEY)||'[]');}catch{return[];}}
function getCustom(){try{return JSON.parse(localStorage.getItem(CUSTOM_KEY)||'[]');}catch{return[];}}
function saveHidden(a){localStorage.setItem(HIDDEN_KEY,JSON.stringify(a));}
function saveCustom(a){localStorage.setItem(CUSTOM_KEY,JSON.stringify(a));}

// 開關抽屜
function openMgr(){
  document.getElementById('mgrOverlay').classList.add('open');
  document.getElementById('mgrDrawer').classList.add('open');
  buildMgrList();
}
function closeMgr(){
  document.getElementById('mgrOverlay').classList.remove('open');
  document.getElementById('mgrDrawer').classList.remove('open');
}
function switchMgrTab(t){
  document.getElementById('mgrList').style.display=t==='list'?'':'none';
  document.getElementById('mgrAdd').style.display=t==='add'?'':'none';
  document.getElementById('mgrTab1').classList.toggle('on',t==='list');
  document.getElementById('mgrTab2').classList.toggle('on',t==='add');
  if(t==='list') buildMgrList();
}

// 建立管理清單
function buildMgrList(){
  const hidden=getHidden();
  const custom=getCustom();
  const el=document.getElementById('mgrList');
  const badge=(t,c)=>`<span style="font-size:10px;color:${c==='g'?'#166534':'#9A3412'};background:${c==='g'?'#D1FAE5':'#FFF7ED'};border-radius:5px;padding:1px 6px;white-space:nowrap">${t}</span>`;
  let html='';

  html+=`<div class="mgr-hint" style="margin-bottom:12px;background:#F0FDF4;border:1px solid #BBF7D0">
    📰 <b>爬蟲清單</b>：每天自動抓取新聞，可開關顯示<br>
    ⭐ <b>自訂清單</b>：只存在您的手機，只顯示股價，無新聞
  </div>`;

  // 美股
  const us=STOCKS_DATA.filter(s=>s.market==='美股');
  html+=`<div class="mgr-section">📰 爬蟲清單 — 🇺🇸 美股（${us.length} 檔，每日自動更新新聞）</div>`;
  us.forEach(s=>{
    const on=!hidden.includes(s.sym);
    html+=`<div class="mgr-row"><span class="mgr-sym">${s.sym}</span><span class="mgr-name">${s.name}</span>${badge('有新聞','g')}<button class="mgr-toggle ${on?'on':'off'}" onclick="toggleStock('${s.sym}')"></button></div>`;
  });

  // 台股
  const tw=STOCKS_DATA.filter(s=>s.market==='台股');
  html+=`<div class="mgr-section" style="margin-top:14px">📰 爬蟲清單 — 🇹🇼 台股（${tw.length} 檔，每日自動更新新聞）</div>`;
  tw.forEach(s=>{
    const on=!hidden.includes(s.sym);
    html+=`<div class="mgr-row"><span class="mgr-sym">${s.sym}</span><span class="mgr-name">${s.name}</span>${badge('有新聞','g')}<button class="mgr-toggle ${on?'on':'off'}" onclick="toggleStock('${s.sym}')"></button></div>`;
  });

  // 韓股
  const kr=STOCKS_DATA.filter(s=>s.market==='韓股');
  if(kr.length){
    html+=`<div class="mgr-section" style="margin-top:14px">📰 爬蟲清單 — 🇰🇷 韓股（${kr.length} 檔，每日自動更新新聞）</div>`;
    kr.forEach(s=>{
      const on=!hidden.includes(s.sym);
      html+=`<div class="mgr-row"><span class="mgr-sym">${s.sym}</span><span class="mgr-name">${s.name}</span>${badge('有新聞','g')}<button class="mgr-toggle ${on?'on':'off'}" onclick="toggleStock('${s.sym}')"></button></div>`;
    });
  }

  // 自訂清單
  html+=`<div class="mgr-section" style="margin-top:16px;padding-top:14px;border-top:2px solid var(--line)">⭐ 自訂清單（${custom.length} 檔）— 永久儲存於本機，按 ✕ 才會刪除</div>`;
  if(custom.length){
    custom.forEach(s=>{
      html+=`<div class="mgr-row"><span class="mgr-sym">${s.sym}</span><span class="mgr-name">${s.name}</span><span class="mgr-mkt ${s.market}">${s.market}</span>${badge('僅股價','r')}<button class="mgr-del" onclick="removeCustom('${s.sym}')" title="永久刪除">✕</button></div>`;
    });
  } else {
    html+=`<div style="font-size:12.5px;color:var(--soft);padding:8px 0 4px">目前沒有自訂股票。點上方「＋ 新增」分頁加入。</div>`;
  }

  el.innerHTML=html;
}

function toggleStock(sym){
  const hidden=getHidden();
  const idx=hidden.indexOf(sym);
  if(idx>=0) hidden.splice(idx,1); else hidden.push(sym);
  saveHidden(hidden);
  buildFeed();
  buildChips();
  buildMgrList();
}

function removeCustom(sym){
  const custom=getCustom().filter(s=>s.sym!==sym);
  saveCustom(custom);
  buildMgrList();
}

// 驗證代號
function validateTicker(sym,mkt){
  if(!sym) return {ok:false,msg:'請輸入代號'};
  if(mkt==='美股'){
    if(/^[A-Z]{1,5}$/.test(sym)) return {ok:true};
    if(/^[A-Z]{1,4}[-\.][A-Z]$/.test(sym)) return {ok:true};
    return {ok:false,msg:'❌ 美股代號格式錯誤：應為 1-5 個大寫英文字母（如 AAPL、NVDA）'};
  }
  if(mkt==='台股'){
    if(/^\d{4,5}$/.test(sym)) return {ok:true};
    return {ok:false,msg:'❌ 台股代號格式錯誤：應為 4 位數字（如 2330、0050）'};
  }
  if(mkt==='韓股'){
    if(/^\d{6}$/.test(sym)) return {ok:true};
    return {ok:false,msg:'❌ 韓股代號格式錯誤：應為 6 位數字（如 005930）'};
  }
  return {ok:false,msg:'請選擇市場'};
}

function showMsg(html,type){
  const el=document.getElementById('addMsg');
  el.innerHTML=`<div class="mgr-msg ${type}">${html}</div>`;
}
function resetAddMsg(){
  document.getElementById('addMsg').innerHTML='';
  document.getElementById('addBtn').disabled=true;
}

function doValidate(){
  const sym=document.getElementById('addSym').value.trim().toUpperCase();
  const mkt=document.getElementById('addMkt').value;
  document.getElementById('addSym').value=sym;

  // 檢查是否已存在
  const allSyms=[...STOCKS_DATA.map(s=>s.sym),...getCustom().map(s=>s.sym)];
  if(allSyms.includes(sym)){
    showMsg(`⚠️ ${sym} 已在清單中`,'err');
    document.getElementById('addBtn').disabled=true;
    return;
  }

  const v=validateTicker(sym,mkt);
  if(v.ok){
    showMsg(`✅ 代號格式正確！可以加入清單`,'ok');
    document.getElementById('addBtn').disabled=false;
  } else {
    showMsg(v.msg,'err');
    document.getElementById('addBtn').disabled=true;
  }
}

function doAdd(){
  const sym=document.getElementById('addSym').value.trim().toUpperCase();
  const name=document.getElementById('addName').value.trim()||sym;
  const mkt=document.getElementById('addMkt').value;

  const v=validateTicker(sym,mkt);
  if(!v.ok){showMsg(v.msg,'err');return;}

  const custom=getCustom();
  custom.push({sym,name,market:mkt});
  saveCustom(custom);

  // 重置表單
  document.getElementById('addSym').value='';
  document.getElementById('addName').value='';
  document.getElementById('addMsg').innerHTML='';
  document.getElementById('addBtn').disabled=true;

  showMsg(`✅ ${sym}（${name}）已加入自訂清單！下次執行爬蟲後即可看到新聞。`,'ok');
  buildMgrList();
}
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
    print(f"\n🗞  晨報爬蟲 v3 — {gen_time}")
    print(f"   個股 {len(STOCKS)} 檔 + 產業來源 {len(INDUSTRY_FEEDS)} 個")
    print(f"   翻譯：{'✓ 啟用' if _HAS_TRANSLATOR else '✗ 停用（英文直顯）'}\n")

    print("【個股新聞】")
    stocks_data = []
    for i, s in enumerate(STOCKS, 1):
        try:
            print(f"[{i:2d}/{len(STOCKS)}] {s['sym']}", end=" ")
            stocks_data.append(process_stock(s))
            print()
        except Exception as e:
            print(f"⚠️ 失敗({e})，跳過")
            stocks_data.append({**s, "items":[], "summary":"（暫無資料）", "sentiment":"neutral"})

    print("\n【產業動態】")
    try:
        industry_data = fetch_industry()
    except Exception as e:
        print(f"⚠️ 產業動態抓取失敗：{e}")
        industry_data = []

    print(f"\n✅ 完成！共 {len(industry_data)} 則產業動態，生成 HTML...")
    OUT_HTML.write_text(generate_html(stocks_data, industry_data, gen_time), encoding="utf-8")
    print(f"📄 輸出：{OUT_HTML}\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"\n❌ 爬蟲發生未預期錯誤：{e}")
        traceback.print_exc()
        sys.exit(1)
