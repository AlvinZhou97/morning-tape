#!/usr/bin/env python3
"""
國小一年級下學期數學練習
每天自動產生 20 題，累積歷史，有日期篩選
"""
import json, random, hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUT_HTML = Path(__file__).parent / "數學練習.html"
HIST_FILE = Path(__file__).parent / "math_history.json"
TZ_TW = timezone(timedelta(hours=8))

# ══════════════════════════════════════════════════════════════
#  數字轉中文（TTS 用）
# ══════════════════════════════════════════════════════════════
_D = ["零","一","二","三","四","五","六","七","八","九"]
def num_zh(n):
    if n == 0: return "零"
    if n <= 9: return _D[n]
    if n >= 100: return str(n)
    if n == 10: return "十"
    if 11 <= n <= 19: return "十" + _D[n-10]
    t, o = n//10, n%10
    r = (_D[t] if t < len(_D) else str(t)) + "十"
    if o: r += _D[o]
    return r

# ══════════════════════════════════════════════════════════════
#  生成 500 題題庫（固定種子，每次相同）
# ══════════════════════════════════════════════════════════════
def make_opts(ans, lo=0, hi=99, n=4, rng=None):
    rng = rng or random
    # 確保範圍合理，支援答案超過 99
    hi = max(hi, ans + 15)
    lo = min(lo, max(0, ans - 15))
    lo, hi = max(0, lo), hi
    pool = {ans}
    for d in [1,-1,2,-2,3,-3,5,-5,10,-10,11,-11,20,-20]:
        if len(pool) >= n: break
        w = ans + d
        if w >= 0 and w != ans: pool.add(w)
    attempts = 0
    while len(pool) < n and attempts < 100:
        attempts += 1
        spread = max(20, abs(ans // 4))
        w = ans + rng.randint(-spread, spread)
        if w >= 0 and w != ans: pool.add(w)
    opts = list(pool)[:n]; rng.shuffle(opts)
    return opts

def gen_pool():
    rng = random.Random(20240901)  # 固定種子讓題庫永遠一樣
    qs = []
    qid = 0

    def add(cat, lv, q, q_zh, ans, opts=None, exp=""):
        nonlocal qid; qid += 1
        qs.append({"id":qid,"cat":cat,"lv":lv,
                   "q":q,"q_zh":q_zh,"ans":ans,
                   "opts":opts or make_opts(ans,0,100,4,rng),"exp":exp})

    # ── 1. 一位數加法 (40) ──────────────────────────────────
    for _ in range(40):
        a,b = rng.randint(1,9), rng.randint(1,9)
        ans = a+b
        add("加法","基礎",
            f"{a} + {b} = ?",
            f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,1,18,4,rng))

    # ── 2. 一位數減法 (30) ──────────────────────────────────
    for _ in range(30):
        a = rng.randint(2,9); b = rng.randint(1,a)
        ans = a-b
        add("減法","基礎",
            f"{a} - {b} = ?",
            f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,0,8,4,rng))

    # ── 3. 10 加一位數 (20) ─────────────────────────────────
    for _ in range(20):
        b = rng.randint(1,9); ans=10+b
        add("加法","基礎",
            f"10 + {b} = ?",
            f"十 加 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,10,19,4,rng))

    # ── 4. 整十加減 (40) ────────────────────────────────────
    for _ in range(20):
        a = rng.randint(1,8)*10; b = rng.randint(1,9-a//10)*10
        ans = a+b
        add("加法","整十",
            f"{a} + {b} = ?",
            f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,10,90,4,rng))
    for _ in range(20):
        a = rng.randint(2,9)*10; b = rng.randint(1,a//10-1)*10
        ans = a-b
        add("減法","整十",
            f"{a} - {b} = ?",
            f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,10,90,4,rng))

    # ── 5. 兩位數加一位數（不進位）(50) ─────────────────────
    for _ in range(50):
        t = rng.randint(1,8)*10; o = rng.randint(0,8); b = rng.randint(1,9-o)
        a = t+o; ans = a+b
        add("加法","兩位數",
            f"{a} + {b} = ?",
            f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,max(0,ans-5),min(99,ans+5),4,rng))

    # ── 6. 兩位數減一位數（不借位）(50) ─────────────────────
    for _ in range(50):
        t = rng.randint(1,9)*10; o = rng.randint(1,9); b = rng.randint(1,o)
        a = t+o; ans = a-b
        add("減法","兩位數",
            f"{a} - {b} = ?",
            f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,max(0,ans-5),min(99,ans+5),4,rng))

    # ── 7. 兩位數加兩位數（不進位）(50) ─────────────────────
    for _ in range(50):
        a1,b1 = rng.randint(1,9), rng.randint(1,9)
        a2,b2 = rng.randint(1,9), rng.randint(0,9-b1)
        a = a1*10+a2; b = b1*10+b2; ans = a+b
        add("加法","進階",
            f"{a} + {b} = ?",
            f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,max(10,ans-10),min(99,ans+10),4,rng))

    # ── 8. 兩位數減兩位數（不借位）(50) ─────────────────────
    for _ in range(50):
        b1 = rng.randint(1,8); b2 = rng.randint(0,9)
        a1 = rng.randint(b1+1,9); a2 = rng.randint(b2,9)
        a = a1*10+a2; b = b1*10+b2; ans = a-b
        add("減法","進階",
            f"{a} - {b} = ?",
            f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,max(0,ans-10),min(89,ans+10),4,rng))

    # ── 9. 比大小（50）──────────────────────────────────────
    for _ in range(50):
        a = rng.randint(10,99); b = rng.randint(10,99)
        # 正確說法
        if a > b:   correct = f"{a} ＞ {b}"
        elif a < b: correct = f"{a} ＜ {b}"
        else:       correct = f"{a} ＝ {b}"
        # 3 個錯誤說法：反向、等號、反向等號
        wrongs = list({
            f"{b} ＞ {a}" if a<b else f"{a} ＞ {b}" if a==b else f"{b} ＞ {a}",
            f"{a} ＝ {b}" if a!=b else f"{a} ＞ {b}",
            f"{b} ＜ {a}" if a>b else f"{a} ＜ {b}" if a==b else f"{b} ＜ {a}",
        } - {correct})
        # 補到 3 個
        extras = [f"{a} ＝ {b+1}", f"{a+1} ＜ {b}", f"{b} ＝ {a+2}"]
        for e in extras:
            if len(wrongs) >= 3: break
            if e != correct: wrongs.append(e)
        opts = [correct] + list(wrongs)[:3]; rng.shuffle(opts)
        add("比大小","比較",
            f"{a}  和  {b}，哪個說法正確？",
            f"{num_zh(a)} 和 {num_zh(b)} 比較，哪個說法正確？",
            correct, opts,
            f"正確答案是 {correct}")

    # ── 10. 數序填空（50）──────────────────────────────────
    for _ in range(25):
        start = rng.randint(10,90); step = rng.choice([1,2,5,10])
        pos = rng.randint(0,3)
        nums = [start+step*i for i in range(5)]
        ans = nums[pos]
        display = [str(n) if i!=pos else "__" for i,n in enumerate(nums)]
        q = " , ".join(display)
        q_zh = "、".join([num_zh(n) if i!=pos else "空格" for i,n in enumerate(nums)]) + "，空格填什麼？"
        add("數序","數序",q,q_zh,ans,make_opts(ans,max(0,ans-step*2),min(99,ans+step*2),4,rng))
    for _ in range(25):
        end = rng.randint(20,99); step = rng.choice([1,2,5,10])
        start = end - step*4
        if start < 0: start = 0; end = start+step*4
        pos = rng.randint(0,4)
        nums = [start+step*i for i in range(5)]
        ans = nums[pos]
        display = [str(n) if i!=pos else "__" for i,n in enumerate(nums)]
        q = " , ".join(display)
        q_zh = "、".join([num_zh(n) if i!=pos else "空格" for i,n in enumerate(nums)]) + "，空格填什麼？"
        add("數序","數序",q,q_zh,ans,make_opts(ans,max(0,ans-step*2),min(99,ans+step*2),4,rng))

    # ── 11. 應用題（50）────────────────────────────────────
    templates_add = [
        ("籃子裡有 {a} 顆蘋果，又放入 {b} 顆，共幾顆？",
         "籃子裡有 {azh} 顆蘋果，又放入 {bzh} 顆，共幾顆？"),
        ("停車場有 {a} 輛車，開進來 {b} 輛，現在共有幾輛？",
         "停車場有 {azh} 輛車，開進來 {bzh} 輛，現在共有幾輛？"),
        ("小明有 {a} 元，媽媽又給他 {b} 元，他現在有幾元？",
         "小明有 {azh} 元，媽媽又給他 {bzh} 元，他現在有幾元？"),
        ("花園裡有 {a} 朵紅花和 {b} 朵黃花，共有幾朵花？",
         "花園裡有 {azh} 朵紅花和 {bzh} 朵黃花，共有幾朵花？"),
        ("書架上有 {a} 本書，又加上 {b} 本，一共有幾本？",
         "書架上有 {azh} 本書，又加上 {bzh} 本，一共有幾本？"),
    ]
    templates_sub = [
        ("冰箱裡有 {a} 顆雞蛋，用掉 {b} 顆，還剩幾顆？",
         "冰箱裡有 {azh} 顆雞蛋，用掉 {bzh} 顆，還剩幾顆？"),
        ("班上有 {a} 位同學，有 {b} 位請假，今天有幾位同學上課？",
         "班上有 {azh} 位同學，有 {bzh} 位請假，今天有幾位同學上課？"),
        ("小花有 {a} 元，買了 {b} 元的糖果，還剩幾元？",
         "小花有 {azh} 元，買了 {bzh} 元的糖果，還剩幾元？"),
        ("盒子裡有 {a} 顆糖，吃了 {b} 顆，還剩幾顆？",
         "盒子裡有 {azh} 顆糖，吃了 {bzh} 顆，還剩幾顆？"),
        ("樹上有 {a} 隻鳥，飛走了 {b} 隻，剩幾隻？",
         "樹上有 {azh} 隻鳥，飛走了 {bzh} 隻，剩幾隻？"),
    ]
    for _ in range(25):
        a = rng.randint(10,50); b = rng.randint(1,min(a-1,40))
        t1, t2 = rng.choice(templates_add)
        q = t1.format(a=a,b=b); q_zh = t2.format(azh=num_zh(a),bzh=num_zh(b))
        ans = a+b
        add("應用題","加法",q,q_zh,ans,make_opts(ans,max(0,ans-8),min(99,ans+8),4,rng))
    for _ in range(25):
        a = rng.randint(15,60); b = rng.randint(5,a-5)
        t1, t2 = rng.choice(templates_sub)
        q = t1.format(a=a,b=b); q_zh = t2.format(azh=num_zh(a),bzh=num_zh(b))
        ans = a-b
        add("應用題","減法",q,q_zh,ans,make_opts(ans,max(0,ans-8),min(99,ans+8),4,rng))

    # ── 12. 時間（20）──────────────────────────────────────
    for _ in range(20):
        h = rng.randint(1,12)
        m = rng.choice([0,30])
        suffix = "整" if m==0 else "30分"
        ans_text = f"{h}點{suffix}"
        other_hours = [hh for hh in range(1,13) if hh != h]
        rng.shuffle(other_hours)
        wrong_opts = [f"{hh}點{suffix}" for hh in other_hours[:3]]
        opts = [ans_text] + wrong_opts
        rng.shuffle(opts)
        qs.append({"id":qid,"cat":"時間","lv":"時間",
                   "q_hour":h,"q_minute":m,   # 讓 JS 畫時鐘用
                   "q":"時鐘顯示的是幾點？",
                   "q_zh":f"時鐘顯示 {num_zh(h)} 點{'整' if m==0 else '三十分'}，是幾點？",
                   "ans":ans_text,"opts":opts[:4],
                   "exp":f"答案是 {ans_text}"})
        qid += 1

    print(f"✓ 題庫共 {len(qs)} 題")
    return qs

POOL = gen_pool()

# ══════════════════════════════════════════════════════════════
#  每日選題
# ══════════════════════════════════════════════════════════════
def daily_questions():
    today = datetime.now(TZ_TW).strftime("%Y-%m-%d")
    seed = int(hashlib.md5(today.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)

    # 每個類別各抽固定題數，確保均勻分佈
    categories = {
        "加法":   4,
        "減法":   4,
        "比大小": 4,
        "數序":   4,
        "時間":   4,
        "應用題": 10,
    }

    picked = []
    for cat, count in categories.items():
        pool = [q for q in POOL if q["cat"] == cat]
        rng.shuffle(pool)
        picked.extend(pool[:count])

    # 依題號排序，混合顯示
    picked.sort(key=lambda q: q["id"])
    return picked

# ══════════════════════════════════════════════════════════════
#  HTML 樣板
# ══════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>數學練習 🔢</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Nunito:wght@700;800;900&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#FFF9F0; --card:#fff; --ink:#1a1a2e;
  --soft:#6b7280; --border:#e5e7eb;
  --add:#3B82F6; --sub:#EF4444; --cmp:#F59E0B;
  --seq:#8B5CF6; --app:#10B981; --time:#EC4899;
  --correct:#16A34A; --wrong:#DC2626;
}
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{background:var(--bg);font-family:"Noto Sans TC","Nunito",sans-serif;
  min-height:100vh;padding-bottom:100px}

/* ── 頁首 ── */
.header{background:#fff;border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:20;padding:0 16px}
.hinner{max-width:600px;margin:0 auto;height:54px;
  display:flex;align-items:center;gap:10px}
.logo{font-family:"Nunito";font-weight:900;font-size:20px;color:var(--ink)}
.logo span{color:var(--add)}
.hdate{margin-left:auto;font-size:12px;font-weight:700;color:var(--soft)}

/* ── 進度 ── */
.progress-wrap{background:#fff;border-bottom:1px solid var(--border);padding:8px 16px}
.progress-inner{max-width:600px;margin:0 auto;display:flex;align-items:center;gap:10px}
.prog-bar-bg{flex:1;height:10px;background:#E5E7EB;border-radius:8px;overflow:hidden}
.prog-bar{height:100%;background:linear-gradient(90deg,#3B82F6,#8B5CF6);
  border-radius:8px;transition:width .4s}
.prog-label{font-family:"Nunito";font-size:13px;font-weight:800;color:var(--soft);white-space:nowrap}
.score-badge{font-family:"Nunito";font-size:13px;font-weight:800;
  background:#FEF3C7;color:#92400E;border-radius:16px;padding:2px 10px;white-space:nowrap}

/* ── 篩選 ── */
.filters{background:#fff;border-bottom:1px solid var(--border);padding:8px 16px}
.filter-row{max-width:600px;margin:0 auto;width:100%;
  display:flex;align-items:center;gap:8px}
.filter-label{font-size:11px;font-weight:800;color:var(--soft);
  letter-spacing:.08em;text-transform:uppercase;white-space:nowrap;min-width:28px}
.chips{display:flex;gap:5px;overflow-x:auto;scrollbar-width:none;flex:1}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;font-size:12px;font-weight:700;
  padding:4px 12px;border-radius:20px;border:1.5px solid var(--border);
  background:#fff;color:var(--soft);cursor:pointer;transition:.15s;white-space:nowrap}
.chip:hover{border-color:var(--add);color:var(--add)}
.chip.on{background:var(--add);color:#fff;border-color:var(--add)}

/* ── 題目卡 ── */
.feed{max-width:600px;margin:0 auto;padding:16px}
.date-hdr{font-size:12px;font-weight:800;letter-spacing:.1em;
  text-transform:uppercase;color:var(--soft);
  padding:16px 4px 8px;border-bottom:2px solid var(--border);margin-bottom:4px}

.qcard{background:var(--card);border-radius:20px;padding:20px;
  margin-bottom:12px;border:2px solid var(--border);
  transition:border-color .2s,box-shadow .2s;scroll-margin-top:130px}
.qcard.answered-correct{border-color:var(--correct);background:#F0FDF4}
.qcard.answered-wrong{border-color:var(--wrong);background:#FFF5F5}

.qtop{display:flex;align-items:center;gap:8px;margin-bottom:12px}
.qnum{font-family:"Nunito";font-size:12px;font-weight:800;color:var(--soft)}
.cat-badge{font-size:10px;font-weight:800;letter-spacing:.06em;
  text-transform:uppercase;border-radius:8px;padding:2px 8px}
.cat-badge.加法{background:#DBEAFE;color:#1D4ED8}
.cat-badge.減法{background:#FEE2E2;color:#B91C1C}
.cat-badge.比大小{background:#FEF3C7;color:#92400E}
.cat-badge.數序{background:#EDE9FE;color:#6D28D9}
.cat-badge.應用題{background:#D1FAE5;color:#065F46}
.cat-badge.時間{background:#FCE7F3;color:#9D174D}

.qtext{font-family:"Nunito";font-weight:900;font-size:32px;
  text-align:center;margin:16px 0;color:var(--ink);line-height:1.3;
  word-break:break-all}
.qtext.word-problem{font-family:"Noto Sans TC";font-size:17px;font-weight:700;
  text-align:left;line-height:1.7;color:#1e293b}

.say-btn{background:none;border:1.5px solid var(--border);border-radius:20px;
  padding:5px 14px;font-size:13px;font-weight:700;cursor:pointer;
  color:var(--soft);transition:.15s;display:flex;align-items:center;gap:5px;margin:0 auto 14px}
.say-btn:hover{border-color:var(--add);color:var(--add)}
.say-btn:active{opacity:.7}

/* ── 選項 ── */
.opts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px}
.opt{border:2.5px solid var(--border);border-radius:16px;
  padding:14px 10px;font-family:"Nunito";font-size:22px;font-weight:900;
  text-align:center;cursor:pointer;background:#fff;
  transition:all .2s;color:var(--ink)}
.opt:hover:not(:disabled){border-color:var(--add);background:#EFF6FF;transform:scale(1.02)}
.opt:active:not(:disabled){transform:scale(.97)}
.opt.correct{border-color:var(--correct)!important;background:#F0FDF4!important;color:var(--correct)!important}
.opt.wrong{border-color:var(--wrong)!important;background:#FFF5F5!important;color:var(--wrong)!important}
.opt:disabled{cursor:default;opacity:.8}

/* 比大小選項字體調整（選項是完整算式） */
.opts.cmp .opt{font-size:18px;padding:14px 8px;font-weight:800}

/* ── 結果回饋 ── */
.feedback{margin-top:12px;padding:10px 14px;border-radius:12px;
  font-size:14px;font-weight:700;display:none}
.feedback.show{display:block}
.feedback.ok{background:#DCFCE7;color:#166534}
.feedback.ng{background:#FEE2E2;color:#991B1B}


/* ── 時鐘 SVG ── */
.clock-wrap{text-align:center;margin:4px 0 10px}
/* 選擇後（送出前）的狀態 */
.opt.selected{border-color:var(--add)!important;background:#EFF6FF!important;color:var(--add)!important}
/* 送出按鈕列 */
.submit-bar{position:fixed;bottom:0;left:0;right:0;background:rgba(255,249,240,.95);
  backdrop-filter:blur(10px);border-top:2px solid var(--border);padding:12px 16px;z-index:30}
.submit-btn{display:block;width:100%;max-width:600px;margin:0 auto;
  background:var(--app);color:#fff;border:none;border-radius:20px;
  padding:14px;font-family:"Nunito";font-size:18px;font-weight:900;
  cursor:pointer;transition:opacity .15s}
.submit-btn:hover{opacity:.85}
.submit-btn:disabled{background:#9CA3AF;cursor:default}
/* 分數結果橫幅 */
.result-banner{background:linear-gradient(135deg,#D1FAE5,#A7F3D0);
  border-radius:20px;padding:24px 16px;text-align:center;margin-bottom:16px;
  border:2px solid #6EE7B7;display:none}
.result-banner.show{display:block}
.result-emoji{font-size:40px;margin-bottom:6px}
.result-score{font-family:"Nunito";font-size:56px;font-weight:900;color:#065F46}
.result-label{font-size:15px;font-weight:700;color:#065F46;margin-top:4px;margin-bottom:4px}
/* 錯題複習 */
.review-section{margin-top:16px;text-align:left}
.review-title{font-family:"Nunito";font-size:15px;font-weight:900;
  color:#7C2D12;background:#FEF3C7;border-radius:12px;
  padding:10px 14px;margin-bottom:10px;border:1.5px solid #FDE68A}
.review-card{background:#fff;border-radius:16px;padding:14px;margin-bottom:8px;
  border:2px solid #FCA5A5}
.review-num{font-family:"Nunito";font-size:11px;font-weight:800;
  color:var(--soft);margin-bottom:6px;letter-spacing:.06em;text-transform:uppercase}
.review-q-text{font-family:"Nunito";font-size:22px;font-weight:900;
  color:var(--ink);text-align:center;margin:6px 0 10px;padding:8px;
  background:#F9FAFB;border-radius:10px}
.review-wrong-row{font-size:13.5px;color:#B91C1C;font-weight:700;margin-bottom:5px}
.review-wrong-val{background:#FEE2E2;border-radius:6px;padding:1px 8px}
.review-correct-row{font-size:13.5px;color:#065F46;font-weight:700;margin-bottom:8px}
.review-correct-val{background:#D1FAE5;border-radius:6px;padding:1px 8px;font-size:15px}
.review-teach{font-size:13px;color:#374151;line-height:1.65;
  background:#FFFBEB;border-radius:10px;padding:9px 12px;
  border-left:3px solid #F59E0B}
</style>
</head>
<body>

<div class="header">
  <div class="hinner">
    <div class="logo">🔢 <span>數學</span>練習</div>
    <div class="hdate">__DATE__</div>
  </div>
</div>

<div class="progress-wrap">
  <div class="progress-inner">
    <div class="prog-bar-bg"><div class="prog-bar" id="progBar" style="width:0%"></div></div>
    <div class="prog-label" id="progLabel">0 / 30</div>
    <div class="score-badge" id="scoreBadge">⭐ 0 分</div>
  </div>
</div>

<div class="filters">
  <div class="filter-row">
    <span class="filter-label">日期</span>
    <div class="chips" id="dateBar"></div>
  </div>
</div>

<div class="feed" id="feed"></div>

<!-- 送出按鈕 -->
<div class="submit-bar" id="submitBar">
  <button class="submit-btn" id="submitBtn" onclick="submitAnswers()">📝 送出答案</button>
</div>

<script>
const ALL_DATA = __ALL_DATA_JSON__;
const ALL_DATES = Object.keys(ALL_DATA).sort((a,b)=>b.localeCompare(a));
let curDate = "全部";
let selections = {};  // {qid: 選擇的選項}
let submitted  = false;
let answered   = {};  // {qid: true/false} — 送出後才填

// ── 時鐘 SVG ──────────────────────────────────────────────
function clockSVG(hour, minute){
  const cx=100,cy=100;
  const rad=a=>a*Math.PI/180;
  // 時針角度（12點=0°，順時針）
  const hDeg=(hour%12)*30 + minute*0.5 - 90;
  const mDeg=minute*6 - 90;
  const hx=cx+48*Math.cos(rad(hDeg)), hy=cy+48*Math.sin(rad(hDeg));
  const mx=cx+68*Math.cos(rad(mDeg)), my=cy+68*Math.sin(rad(mDeg));
  // 刻度
  const ticks=Array.from({length:60},(_,i)=>{
    const a=rad(i*6-90), r1=i%5===0?76:82, r2=88;
    return `<line x1="${(cx+r1*Math.cos(a)).toFixed(1)}" y1="${(cy+r1*Math.sin(a)).toFixed(1)}" x2="${(cx+r2*Math.cos(a)).toFixed(1)}" y2="${(cy+r2*Math.sin(a)).toFixed(1)}" stroke="${i%5===0?'#9CA3AF':'#E5E7EB'}" stroke-width="${i%5===0?2:1}"/>`;
  }).join('');
  // 數字
  const nums=Array.from({length:12},(_,i)=>{
    const a=rad((i+1)*30-90), x=cx+74*Math.cos(a), y=cy+74*Math.sin(a);
    return `<text x="${x.toFixed(1)}" y="${(y+5).toFixed(1)}" text-anchor="middle" font-size="13" font-weight="bold" fill="#374151" font-family="Nunito">${i+1}</text>`;
  }).join('');
  return `<svg width="200" height="200" viewBox="0 0 200 200" style="filter:drop-shadow(0 4px 12px rgba(0,0,0,.12))">
    <circle cx="100" cy="100" r="95" fill="#FFF9F0" stroke="#E5E7EB" stroke-width="3"/>
    <circle cx="100" cy="100" r="88" fill="none" stroke="#F3F4F6" stroke-width="1"/>
    ${ticks}${nums}
    <line x1="100" y1="100" x2="${hx.toFixed(1)}" y2="${hy.toFixed(1)}" stroke="#1F2937" stroke-width="6" stroke-linecap="round"/>
    <line x1="100" y1="100" x2="${mx.toFixed(1)}" y2="${my.toFixed(1)}" stroke="#3B82F6" stroke-width="3.5" stroke-linecap="round"/>
    <circle cx="100" cy="100" r="5" fill="#1F2937"/>
  </svg>`;
}

function fmtDate(iso){
  const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(iso||"");
  if(!m)return iso;
  const d=new Date(+m[1],+m[2]-1,+m[3]),w=["日","一","二","三","四","五","六"];
  return `${m[2]}/${m[3]} 週${w[d.getDay()]}`;
}

// ── 日期篩選 ──────────────────────────────────────────────
function buildDateBar(){
  const btns=[{k:"全部",l:`全部（${ALL_DATES.length}天）`},
              ...ALL_DATES.map(d=>({k:d,l:fmtDate(d)}))];
  document.getElementById("dateBar").innerHTML=btns.map(b=>
    `<button class="chip${b.k===curDate?" on":""}" onclick="setDate('${b.k}')">${b.l}</button>`
  ).join("");
}
function setDate(d){
  curDate=d; selections={}; answered={}; submitted=false;
  const bar=document.getElementById("submitBar");
  if(bar) bar.style.display="";
  const banner=document.getElementById("resultBanner");
  if(banner) banner.classList.remove("show");
  buildDateBar(); buildFeed(); updateProgress();
}

// ── 篩選後的題目 ─────────────────────────────────────────
function filteredQs(){
  if(curDate==="全部"){
    const all=[];
    ALL_DATES.forEach(d=>(ALL_DATA[d]||[]).forEach(q=>all.push({...q,_date:d})));
    return all;
  }
  return (ALL_DATA[curDate]||[]).map(q=>({...q,_date:curDate}));
}

// ── 進度更新 ─────────────────────────────────────────────
function updateProgress(){
  const qs=filteredQs();
  const total=qs.length;
  const done=Object.keys(selections).length;
  const correct=Object.values(answered).filter(Boolean).length;
  const pct=total?Math.round((done/total)*100):0;
  document.getElementById("progBar").style.width=pct+"%";
  document.getElementById("progLabel").textContent=`${done} / ${total}`;
  document.getElementById("scoreBadge").textContent=submitted?`⭐ ${correct} 分`:`📝 已答 ${done} 題`;
}

// ── TTS ──────────────────────────────────────────────────
function sayQ(text){
  if(!window.speechSynthesis)return;
  speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.lang="zh-TW"; u.rate=0.85;
  const vs=speechSynthesis.getVoices();
  const v=vs.find(v=>/zh-TW|zh_TW/i.test(v.lang))||vs.find(v=>/zh/i.test(v.lang));
  if(v)u.voice=v;
  speechSynthesis.speak(u);
}

// ── 建立題目卡 ────────────────────────────────────────────
function buildFeed(){
  const qs=filteredQs();
  const feed=document.getElementById("feed");
  if(!qs.length){feed.innerHTML=`<div style="text-align:center;padding:40px;color:var(--soft)">此日期無題目</div>`;return;}

  let html="",lastDate="";
  qs.forEach((q,i)=>{
    if(curDate==="全部"&&q._date!==lastDate){
      lastDate=q._date;
      const cnt=(ALL_DATA[q._date]||[]).length;
      html+=`<div class="date-hdr">${fmtDate(q._date)} · ${cnt} 題</div>`;
    }
    const isWP=q.cat==="應用題";
    const isCmp=q.cat==="比大小";
    const isClock=q.cat==="時間" && q.q_hour!=null;
    const optsClass=isCmp?"opts cmp":"opts";
    const qtextClass=isWP?"qtext word-problem":"qtext";
    // 時間題：顯示 SVG 時鐘；其他：顯示文字
    const qDisplay = isClock
      ? `<div class="clock-wrap">${clockSVG(q.q_hour, q.q_minute)}</div>
         <div style="text-align:center;font-size:14px;color:var(--soft);margin-bottom:10px">時鐘顯示的是幾點？</div>`
      : `<div class="${qtextClass}" id="qtext-${q.id}">${q.q}</div>`;
    const sayText = isClock ? q.q_zh : q.q_zh||q.q;
    const opts=q.opts.map(o=>`<button class="opt" id="opt-${q.id}-${encodeURIComponent(String(o))}"
      onclick="selectOpt(${q.id},'${String(o).replace(/'/g,"\\'")}')">${o}</button>`).join("");
    // 所有題目都顯示聽題目按鈕
    const sayBtnHtml = `<button class="say-btn" onclick="sayQ('${sayText.replace(/'/g,"\\'")}')">🔊 聽題目</button>`;
    html+=`
    <div class="qcard" id="qcard-${q.id}">
      <div class="qtop">
        <span class="qnum">第 ${i+1} 題</span>
        <span class="cat-badge ${q.cat}">${q.cat}</span>
      </div>
      ${qDisplay}
      ${sayBtnHtml}
      <div class="${optsClass}" id="opts-${q.id}">${opts}</div>
      <div class="feedback" id="fb-${q.id}"></div>
    </div>`;
  });
  feed.innerHTML=html;
  // 還原已作答狀態
  Object.entries(answered).forEach(([qidStr,correct])=>{
    const qid=parseInt(qidStr);
    const q=qs.find(x=>x.id===qid);
    if(q) restoreAnswer(qid, q.ans, correct);
  });
}

// ── 選擇選項（送出前只標記，不顯示對錯） ──────────────────
function selectOpt(qid, chosen){
  if(submitted) return;
  if(selections[qid] !== undefined) return; // 已選過，不能更改
  selections[qid] = String(chosen);
  // 清除同題其他選項的 selected
  const qs=filteredQs();
  const q=qs.find(x=>x.id===qid); if(!q) return;
  q.opts.forEach(o=>{
    const btn=document.getElementById("opt-"+qid+"-"+encodeURIComponent(String(o)));
    if(btn) btn.classList.remove("selected");
  });
  const btn=document.getElementById("opt-"+qid+"-"+encodeURIComponent(String(chosen)));
  if(btn) btn.classList.add("selected");
  updateProgress();
}

// ── 送出答案，顯示全部對錯 + 總分 + 錯題教學 ────────────────────────
function submitAnswers(){
  if(submitted) return;
  submitted=true;
  const qs=filteredQs();
  let correct=0;
  const wrongQs=[];

  qs.forEach(q=>{
    const chosen=selections[q.id];
    const isCorrect = chosen!==undefined && String(chosen)===String(q.ans);
    answered[q.id]=isCorrect;
    if(isCorrect) correct++;
    else wrongQs.push({q, chosen});

    // 標記選項顏色
    q.opts.forEach(o=>{
      const btn=document.getElementById("opt-"+q.id+"-"+encodeURIComponent(String(o)));
      if(!btn) return;
      btn.disabled=true; btn.classList.remove("selected");
      if(String(o)===String(q.ans)) btn.classList.add("correct");
      else if(String(o)===String(chosen)&&!isCorrect) btn.classList.add("wrong");
    });

    // 回饋訊息
    const fb=document.getElementById("fb-"+q.id);
    const card=document.getElementById("qcard-"+q.id);
    if(isCorrect){
      if(fb){fb.className="feedback ok show";fb.textContent="✅ 答對了！真棒！";}
      if(card) card.className="qcard answered-correct";
    } else if(chosen!==undefined) {
      if(fb){fb.className="feedback ng show";fb.textContent=`❌ 答錯了。正確答案是 ${q.ans}`;}
      if(card) card.className="qcard answered-wrong";
    } else {
      if(fb){fb.className="feedback ng show";fb.textContent=`⚠️ 未作答。正確答案是 ${q.ans}`;}
      if(card) card.className="qcard answered-wrong";
    }
  });

  // ── 分數橫幅 ──────────────────────────────────────────
  const total=qs.length;
  const wrong=total-correct;
  const pct=Math.round(correct/total*100);
  const emoji=pct>=90?"🏆":pct>=70?"🎉":pct>=50?"💪":"📚";
  const msg=pct>=90?"太厲害了！":pct>=70?"做得很好！":pct>=50?"繼續加油！":"再練習看看！";

  // ── 錯題教學區 ────────────────────────────────────────
  let reviewHTML="";
  if(wrongQs.length>0){
    reviewHTML=`
    <div class="review-section">
      <div class="review-title">📚 錯題複習（${wrongQs.length} 題需要加強）</div>
      ${wrongQs.map(({q,chosen},idx)=>{
        // 顯示時鐘圖 or 題目文字
        const qDisp = (q.cat==="時間"&&q.q_hour!=null)
          ? `<div style="text-align:center;margin:6px 0">${clockSVG(q.q_hour,q.q_minute)}</div>`
          : `<div class="review-q-text">${q.q}</div>`;
        // 教學說明
        const teaching = makeTeaching(q);
        return `
        <div class="review-card">
          <div class="review-num">${idx+1}. ${q.cat}</div>
          ${qDisp}
          <div class="review-wrong-row">
            ❌ 你選了：<span class="review-wrong-val">${chosen||'未作答'}</span>
          </div>
          <div class="review-correct-row">
            ✅ 正確答案：<span class="review-correct-val">${q.ans}</span>
          </div>
          <div class="review-teach">${teaching}</div>
        </div>`;
      }).join("")}
    </div>`;
  } else {
    reviewHTML=`<div class="review-section" style="text-align:center;padding:16px">
      🎊 全部答對！超棒的！</div>`;
  }

  const banner=document.getElementById("resultBanner");
  if(banner){
    banner.innerHTML=`
      <div class="result-emoji">${emoji}</div>
      <div class="result-score">${correct} <span style="font-size:28px">/ ${total}</span></div>
      <div class="result-label">${msg}（答對 ${correct} 題，答錯 ${wrong} 題）</div>
      ${reviewHTML}`;
    banner.classList.add("show");
    banner.scrollIntoView({behavior:"smooth",block:"start"});
  }

  const bar=document.getElementById("submitBar");
  if(bar) bar.style.display="none";
  updateProgress();
}

// ── 教學說明生成 ──────────────────────────────────────────
function makeTeaching(q){
  if(q.cat==="加法"){
    const m=q.q.match(/(\d+)\s*\+\s*(\d+)/);
    if(m){const a=+m[1],b=+m[2];
      return `💡 計算方法：${a} + ${b} = ${a+b}<br>
        ${a}的個位是${a%10}，${b}的個位是${b%10}，個位相加 ${a%10}+${b%10}=${(a%10+b%10)}，
        十位 ${Math.floor(a/10)}+${Math.floor(b/10)}=${Math.floor(a/10)+Math.floor(b/10)}，
        合起來是 <b>${a+b}</b>`;}
  }
  if(q.cat==="減法"){
    const m=q.q.match(/(\d+)\s*-\s*(\d+)/);
    if(m){const a=+m[1],b=+m[2];
      return `💡 計算方法：${a} - ${b} = ${a-b}<br>
        從 ${a} 裡面拿掉 ${b}，剩下 <b>${a-b}</b>`;}
  }
  if(q.cat==="比大小"){
    const m=q.ans.match(/(\d+)\s*([＞＜＝])\s*(\d+)/);
    if(m){const a=+m[1],sym=m[2],b=+m[3];
      const word=sym==="＞"?"大於":sym==="＜"?"小於":"等於";
      return `💡 ${a} ${word} ${b}，所以填 <b>${sym}</b>`;}
  }
  if(q.cat==="數序"){
    return `💡 先找出規律：相鄰兩個數相差多少，再填入空格。答案是 <b>${q.ans}</b>`;
  }
  if(q.cat==="時間"){
    return `💡 短的指針（時針）指向幾，就是幾點。答案是 <b>${q.ans}</b>`;
  }
  if(q.cat==="應用題"){
    const m=q.q.match(/(\d+)[^\d]+(\d+)/);
    if(m) return `💡 解題：從題目找數字和運算，正確答案是 <b>${q.ans}</b>`;
  }
  return `💡 正確答案是 <b>${q.ans}</b>`;
}

function answer(){} // 保留舊函式名避免錯誤

function restoreAnswer(qid, correctAns, correct){
  const optsDiv=document.getElementById("opts-"+qid);
  if(!optsDiv)return;
  optsDiv.querySelectorAll(".opt").forEach(btn=>{
    btn.disabled=true;
    const val=btn.id.replace("opt-"+qid+"-","");
    if(val===String(correctAns)) btn.classList.add("correct");
  });
  const fb=document.getElementById("fb-"+qid);
  const card=document.getElementById("qcard-"+qid);
  if(fb&&card){
    if(correct){fb.className="feedback ok show";fb.textContent="✅ 答對了！真棒！";card.className="qcard answered-correct";}
    else{fb.className="feedback ng show";fb.textContent=`❌ 答錯了。正確答案是 ${correctAns}`;card.className="qcard answered-wrong";}
  }
}

function sayResult(t){
  if(!window.speechSynthesis)return;
  setTimeout(()=>{
    const u=new SpeechSynthesisUtterance(t);
    u.lang="zh-TW";u.rate=1;
    speechSynthesis.speak(u);
  },300);
}

// ── 初始化 ───────────────────────────────────────────────
if(window.speechSynthesis){speechSynthesis.getVoices();speechSynthesis.onvoiceschanged=()=>{};}
// 在 feed 前插入分數橫幅
document.getElementById("feed").insertAdjacentHTML("beforebegin",
  '<div class="result-banner" id="resultBanner"></div>');
buildDateBar();
buildFeed();
updateProgress();
</script>
</body>
</html>"""

# ══════════════════════════════════════════════════════════════
#  主程式
# ══════════════════════════════════════════════════════════════
def main():
    today = datetime.now(TZ_TW).strftime("%Y-%m-%d")
    gen_date = datetime.now(TZ_TW).strftime("%Y/%m/%d")

    # 讀取歷史
    if HIST_FILE.exists():
        history = json.loads(HIST_FILE.read_text(encoding="utf-8"))
        print(f"✓ 讀取歷史：共 {len(history)} 天")
    else:
        history = {}; print("✓ 首次執行，建立歷史")

    # 加入今天的題目
    if today not in history:
        history[today] = daily_questions()
        print(f"✓ 新增 {today} 的 20 題")
    else:
        print(f"✓ {today} 已有記錄")

    # 儲存
    HIST_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

    # 生成 HTML
    html = HTML.replace("__ALL_DATA_JSON__", json.dumps(history, ensure_ascii=False))
    html = html.replace("__DATE__", gen_date)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"✅ 完成！共 {len(history)} 天，HTML → {OUT_HTML}")

if __name__ == "__main__":
    main()
