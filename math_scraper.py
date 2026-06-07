#!/usr/bin/env python3
"""
翰林版一年級下學期數學練習
8大類型 × 5題 = 每天40題
"""
import json, random, hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUT_HTML  = Path(__file__).parent / "數學練習.html"
HIST_FILE = Path(__file__).parent / "math_history.json"
TZ_TW     = timezone(timedelta(hours=8))

_D = ["零","一","二","三","四","五","六","七","八","九"]
def num_zh(n):
    if n == 0: return "零"
    if n <= 9: return _D[n]
    if n == 10: return "十"
    if 11 <= n <= 19: return "十" + _D[n-10]
    t, o = n//10, n%10
    r = _D[t] + "十"
    if o: r += _D[o]
    return r

def make_opts(ans, lo=0, hi=99, n=4, rng=None):
    rng = rng or random
    hi = max(hi, ans+15); lo = min(lo, max(0,ans-15))
    pool = {ans}
    for d in [1,-1,2,-2,3,-3,5,-5,10,-10]:
        if len(pool)>=n: break
        w=ans+d
        if w>=0 and w!=ans: pool.add(w)
    att=0
    while len(pool)<n and att<100:
        att+=1
        w=ans+rng.randint(-max(10,ans//4), max(10,ans//4))
        if w>=0 and w!=ans: pool.add(w)
    opts=list(pool)[:n]; rng.shuffle(opts)
    return opts

# ═══════════════════════════════════════════════════════════════
#  題庫（固定種子，500 題）
# ═══════════════════════════════════════════════════════════════
CAT_NAMES = ["50以內的數","18內加法","18內減法","圖形","100以內的數","錢幣","二位數加減","日曆","時鐘","有多長"]

def gen_pool():
    rng = random.Random(20240901)
    qs  = []
    qid = 0

    def add(cat, q, q_zh, ans, opts, exp=""):
        nonlocal qid; qid+=1
        qs.append({"id":qid,"cat":cat,"q":q,"q_zh":q_zh,
                   "ans":str(ans),"opts":[str(o) for o in opts],"exp":exp})

    # ── 1. 50以內的數（比大小＋數序）─────────────────────────
    # 比大小 33題
    for _ in range(33):
        a=rng.randint(1,50); b=rng.randint(1,50)
        if a>b:   ans="大於"
        elif a<b: ans="小於"
        else:     ans="等於"
        add("50以內的數",f"{a}  ○  {b}",
            f"{num_zh(a)} 和 {num_zh(b)}，中間填什麼？",
            ans, ["大於","小於","等於"],
            f"{a}{'>'if a>b else('='if a==b else'<')}{b}，所以填{ans}")
    # 數序 32題
    for _ in range(32):
        start=rng.randint(1,40); step=rng.choice([1,2,5])
        nums=[start+step*i for i in range(5)]
        if any(n>50 for n in nums): nums=[n-step*5 for n in nums]; nums=[max(1,n) for n in nums]
        pos=rng.randint(0,4); ans=nums[pos]
        display=[str(n) if i!=pos else "__" for i,n in enumerate(nums)]
        q=", ".join(display)
        q_zh="、".join([num_zh(n) if i!=pos else "空格" for i,n in enumerate(nums)])+"，空格是幾？"
        add("50以內的數",q,q_zh,ans,make_opts(ans,max(1,ans-10),min(50,ans+10),4,rng),
            f"每次增加{step}，空格是{ans}")

    # ── 2. 18以內加法（65題）──────────────────────────────────
    for _ in range(65):
        a=rng.randint(1,9); b=rng.randint(1,min(9,18-a))
        ans=a+b
        add("18內加法",f"{a} + {b} = ?",
            f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,1,18,4,rng), f"{a}+{b}={ans}")

    # ── 3. 18以內減法（65題）──────────────────────────────────
    for _ in range(65):
        a=rng.randint(2,18); b=rng.randint(1,min(a-1,9))
        ans=a-b
        add("18內減法",f"{a} - {b} = ?",
            f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans, make_opts(ans,0,17,4,rng), f"{a}-{b}={ans}")

    # ── 4. 圖形與分類（60題）──────────────────────────────────
    shape_pool = [
        # 邊數
        ("三角形有幾條邊？","3",["2","3","4","5"],"三角形有3條邊"),
        ("正方形有幾條邊？","4",["3","4","5","6"],"正方形有4條邊"),
        ("長方形有幾條邊？","4",["3","4","5","6"],"長方形有4條邊"),
        ("圓形有幾條邊？","0",["0","1","2","3"],"圓形沒有邊（0條）"),
        # 角數
        ("三角形有幾個角？","3",["2","3","4","5"],"三角形有3個角"),
        ("正方形有幾個角？","4",["3","4","5","6"],"正方形有4個角"),
        ("長方形有幾個角？","4",["3","4","5","6"],"長方形有4個角"),
        ("圓形有幾個角？","0",["0","1","2","3"],"圓形沒有角（0個）"),
        # 圖形識別
        ("有3條邊的圖形是哪一種？","三角形",["三角形","正方形","長方形","圓形"],"三角形有3條邊"),
        ("4條邊都一樣長的是哪種圖形？","正方形",["三角形","正方形","長方形","圓形"],"正方形4邊等長"),
        ("沒有角的圖形是哪一種？","圓形",["三角形","正方形","長方形","圓形"],"圓形沒有角"),
        ("4條邊但長短可能不同的是哪種圖形？","長方形",["三角形","正方形","長方形","圓形"],"長方形對邊等長但相鄰邊不同"),
        # 比較
        ("三角形和長方形，哪個角比較多？","一樣多",["三角形","長方形","一樣多","圓形"],"三角形和長方形都有3或4個角→長方形較多...等等→長方形4角>三角形3角"),
        ("哪種圖形有4個角？","正方形",["三角形","正方形","圓形","五邊形"],"正方形有4個角"),
        ("正方形和長方形，哪個邊數一樣？","一樣多",["正方形","長方形","一樣多","不一樣"],"都有4條邊"),
        # 辨認
        ("下面哪個是有3個角的圖形？","三角形",["三角形","正方形","長方形","圓形"],"三角形有3個角"),
        ("骰子的每一面是什麼形狀？","正方形",["三角形","正方形","長方形","圓形"],"骰子每面是正方形"),
        ("硬幣的形狀最像哪種圖形？","圓形",["三角形","正方形","長方形","圓形"],"硬幣是圓形"),
        ("門的形狀最像哪種圖形？","長方形",["三角形","正方形","長方形","圓形"],"門通常是長方形"),
        ("下面哪個圖形可以沿中間折成左右一樣大？","正方形",["正方形","三角形（直角）","都可以","都不可以"],"正方形左右對稱"),
        # 分類
        ("三角形、正方形、長方形都有的特徵是？","有角",["有邊","有角","是圓的","沒有邊"],"這三種圖形都有角"),
        ("哪種圖形可以一直滾不停下來？","圓形",["三角形","正方形","長方形","圓形"],"圓形可以滾"),
        ("有4條邊的圖形有哪些？","正方形和長方形",["只有正方形","只有長方形","正方形和長方形","三角形和圓形"],"正方形和長方形都有4條邊"),
        # 數量
        ("教室裡的窗戶通常是什麼形狀？","長方形",["三角形","正方形","長方形","圓形"],"窗戶通常是長方形"),
        ("積木中的三角形積木有幾個角？","3",["2","3","4","5"],"三角形積木有3個角"),
        ("積木中的正方形積木有幾條邊？","4",["3","4","5","6"],"正方形積木有4條邊"),
        ("一個三角形和一個正方形，加起來共有幾個角？","7",["5","6","7","8"],"三角形3角+正方形4角=7角"),
        ("兩個三角形加起來共有幾條邊？","6",["4","5","6","8"],"3+3=6條邊"),
        ("一個正方形有幾條邊和幾個角？","各4個",["各2個","各3個","各4個","各5個"],"正方形4邊4角"),
        ("哪種圖形沒有直角？","圓形",["三角形（等邊）","正方形","長方形","圓形"],"圓形沒有角也沒有直角"),
    ]
    used = []; [used.extend([s]*2) for s in shape_pool]  # 每題用2次 = 60題
    rng.shuffle(used)
    for q_text,ans,opts,exp in used[:60]:
        opts2=opts.copy(); rng.shuffle(opts2)
        add("圖形",q_text,q_text,ans,opts2,exp)

    # ── 5. 100以內的數（65題）─────────────────────────────────
    # 數的組成 30題
    for _ in range(30):
        tens=rng.randint(1,9); ones=rng.randint(0,9)
        ans=tens*10+ones
        if ones==0:
            q=f"{tens}個十是多少？"
            q_zh=f"{num_zh(tens)} 個十是多少？"
        else:
            q=f"{tens}個十和{ones}個一是多少？"
            q_zh=f"{num_zh(tens)} 個十和 {num_zh(ones)} 個一是多少？"
        add("100以內的數",q,q_zh,ans,make_opts(ans,max(10,ans-15),min(99,ans+15),4,rng),
            f"{tens}個十={tens*10}，加{ones}個一={ans}")
    # 比大小 20題
    for _ in range(20):
        a=rng.randint(10,99); b=rng.randint(10,99)
        if a>b: ans="大於"
        elif a<b: ans="小於"
        else: ans="等於"
        add("100以內的數",f"{a}  ○  {b}",
            f"{num_zh(a)} 和 {num_zh(b)}，中間填什麼？",
            ans,["大於","小於","等於"],f"{a}{'>'if a>b else('='if a==b else'<')}{b}")
    # 數序 15題
    for _ in range(15):
        start=rng.randint(10,85); step=rng.choice([1,2,5,10])
        nums=[start+step*i for i in range(5)]
        if any(n>100 for n in nums): continue
        pos=rng.randint(0,4); ans=nums[pos]
        display=[str(n) if i!=pos else "__" for i,n in enumerate(nums)]
        add("100以內的數",", ".join(display),
            "、".join([num_zh(n) if i!=pos else "空格" for i,n in enumerate(nums)])+"，空格是幾？",
            ans,make_opts(ans,max(1,ans-15),min(100,ans+15),4,rng),
            f"每次加{step}，空格是{ans}")

    # ── 6. 認識錢幣（60題）────────────────────────────────────
    coins_q = []
    # 硬幣組合
    coin_vals = [1,5,10,50]
    for _ in range(25):
        t=rng.randint(1,5); o=rng.randint(0,9)
        ans=t*10+o
        q=f"{t}個10元和{o}個1元，共幾元？"
        q_zh=q
        coins_q.append((q,q_zh,ans,make_opts(ans,max(0,ans-15),ans+15,4,rng),
                        f"{t}×10={t*10}，加{o}個1元={ans}元"))
    for _ in range(20):
        buy=rng.randint(5,45); pay=rng.choice([i for i in [10,20,30,50] if i>buy])
        ans=pay-buy
        q=f"買了{buy}元的東西，付了{pay}元，找回幾元？"
        coins_q.append((q,q,ans,make_opts(ans,0,50,4,rng),f"{pay}-{buy}={ans}元"))
    for _ in range(15):
        a=rng.randint(1,4); b=rng.randint(1,4)
        ans=a*10+b*5
        q=f"{a}個10元和{b}個5元，共幾元？"
        coins_q.append((q,q,ans,make_opts(ans,0,70,4,rng),f"{a}×10+{b}×5={ans}元"))
    rng.shuffle(coins_q)
    for q,q_zh,ans,opts,exp in coins_q[:60]:
        add("錢幣",q,q_zh,ans,opts,exp)

    # ── 7. 二位數的加減（65題）────────────────────────────────
    # 二位數+一位數（不進位）20題
    for _ in range(20):
        t=rng.randint(1,9)*10; o=rng.randint(0,8)
        b=rng.randint(1,9-o)
        a=t+o; ans=a+b
        add("二位數加減",f"{a} + {b} = ?",
            f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(0,ans-8),min(99,ans+8),4,rng),f"{a}+{b}={ans}")
    # 二位數+整十數 15題
    for _ in range(15):
        a=rng.randint(11,60); b=rng.choice([10,20,30])
        ans=a+b
        if ans>99: continue
        add("二位數加減",f"{a} + {b} = ?",
            f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(0,ans-15),min(99,ans+15),4,rng),f"{a}+{b}={ans}")
    # 二位數-一位數（不借位）20題
    for _ in range(20):
        t=rng.randint(1,9)*10; o=rng.randint(1,9); b=rng.randint(1,o)
        a=t+o; ans=a-b
        add("二位數加減",f"{a} - {b} = ?",
            f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(0,ans-8),min(99,ans+8),4,rng),f"{a}-{b}={ans}")
    # 二位數-整十數 10題
    for _ in range(10):
        a=rng.randint(30,90); b=rng.choice([10,20,30])
        ans=a-b
        if ans<0: continue
        add("二位數加減",f"{a} - {b} = ?",
            f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(0,ans-15),min(99,ans+15),4,rng),f"{a}-{b}={ans}")

    # ── 8. 幾月幾日星期幾（60題）────────────────────────────────
    month_days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    month_zh   = ["","一","二","三","四","五","六","七","八","九","十","十一","十二"]
    week_zh    = ["星期日","星期一","星期二","星期三","星期四","星期五","星期六"]
    cal_pool   = []
    # 月份天數
    for m,d in month_days.items():
        cal_pool.append((f"{m}月有幾天？",f"{month_zh[m]}月有幾天？",str(d),
                         sorted({str(d),str(d-1),str(d+1),"28" if d!=28 else "30"}),
                         f"{m}月有{d}天"))
    # 一週/一年
    cal_pool += [
        ("一週有幾天？","一週有幾天？","7",["5","6","7","8"],"一週7天"),
        ("一年有幾個月？","一年有幾個月？","12",["10","11","12","13"],"一年12個月"),
        ("一年有幾天？","一年有幾天？","365",["360","365","366","367"],"一年365天"),
        ("一個月最多有幾天？","一個月最多有幾天？","31",["28","29","30","31"],"最多31天"),
        ("一個月最少有幾天？","一個月最少有幾天？","28",["28","29","30","31"],"二月最少28天"),
        ("哪個月份天數最少？","哪個月份天數最少？","2月",["1月","2月","3月","4月"],"二月最少"),
        ("有30天的月份有幾個？","有30天的月份有幾個？","4",["3","4","5","6"],"4、6、9、11月共4個"),
        ("有31天的月份有幾個？","有31天的月份有幾個？","7",["6","7","8","9"],"1,3,5,7,8,10,12月共7個"),
    ]
    # 星期計算
    for day_i,day_name in enumerate(week_zh):
        next_d = week_zh[(day_i+1)%7]
        prev_d = week_zh[(day_i-1)%7]
        after2 = week_zh[(day_i+2)%7]
        before2= week_zh[(day_i-2)%7]
        cal_pool.append((f"{day_name}的隔天是？",f"{day_name}的後一天是？",next_d,
                         list({next_d,prev_d,after2,week_zh[(day_i+3)%7]}),
                         f"{day_name}後一天是{next_d}"))
        cal_pool.append((f"{day_name}的前一天是？",f"{day_name}的前一天是？",prev_d,
                         list({prev_d,next_d,before2,week_zh[(day_i-3)%7]}),
                         f"{day_name}前一天是{prev_d}"))
    # 月份前後
    for m in range(1,13):
        nm=(m%12)+1; pm=(m-2)%12+1
        cal_pool.append((f"{m}月的下一個月是幾月？",f"{month_zh[m]}月的下一個月？",
                         f"{nm}月",sorted({f"{nm}月",f"{pm}月",f"{(m+2)%12+1}月"}|({f"1月"} if nm!=1 else {f"12月"})),
                         f"{m}月後是{nm}月"))
    rng.shuffle(cal_pool)
    for item in cal_pool[:60]:
        q,q_zh,ans,opts,exp=item[0],item[1],item[2],list(item[3])[:4],item[4]
        while len(opts)<4: opts.append(opts[0]+"？")
        rng.shuffle(opts)
        if ans not in opts: opts[0]=ans
        add("日曆",q,q_zh,ans,opts,exp)

    # ── 9. 時鐘（50題）────────────────────────────────────────
    # 整點 25 題
    for _ in range(25):
        h = rng.randint(1,12); m = 0
        ans = f"{h}點整"
        others = [hh for hh in range(1,13) if hh != h]; rng.shuffle(others)
        opts = [ans] + [f"{hh}點整" for hh in others[:3]]; rng.shuffle(opts)
        qs.append({"id":qid,"cat":"時鐘","q":"時鐘顯示的是幾點？",
                   "q_zh":f"時鐘顯示{num_zh(h)}點整，是幾點？",
                   "q_hour":h,"q_minute":0,"ans":ans,"opts":opts[:4],
                   "exp":f"短針（時針）指向{h}，長針（分針）指向12，是{ans}"})
        qid+=1
    # 半點 25 題
    for _ in range(25):
        h = rng.randint(1,12); m = 30
        ans = f"{h}點30分"
        others = [hh for hh in range(1,13) if hh != h]; rng.shuffle(others)
        opts = [ans] + [f"{hh}點30分" for hh in others[:3]]; rng.shuffle(opts)
        nxt = h%12+1
        qs.append({"id":qid,"cat":"時鐘","q":"時鐘顯示的是幾點幾分？",
                   "q_zh":f"時鐘顯示{num_zh(h)}點三十分，是幾點幾分？",
                   "q_hour":h,"q_minute":30,"ans":ans,"opts":opts[:4],
                   "exp":f"短針在{h}和{nxt}之間，長針指向6，是{ans}"})
        qid+=1

    # ── 10. 有多長（50題）──────────────────────────────────────
    objs = ["鉛筆","橡皮擦","剪刀","書本","文具盒","繩子","緞帶","毛線","尺","布條"]
    units = ["個迴紋針","個積木","格","個方塊"]
    # 比較長短 25 題
    for _ in range(25):
        a,b = rng.sample(objs,2)
        la = rng.randint(3,12); lb = rng.randint(3,12)
        while la==lb: lb=rng.randint(3,12)
        unit = rng.choice(units)
        q_type = rng.choice(["長","短"])
        ans = (a if la>lb else b) if q_type=="長" else (b if la>lb else a)
        q = f"{a}有{la}{unit}，{b}有{lb}{unit}，哪個比較{q_type}？"
        opts = [a, b, "一樣長", "無法比較"]; rng.shuffle(opts)
        if ans not in opts: opts[0]=ans
        add("有多長",q,q,ans,opts[:4],
            f"{'>' if la>lb else '<'}代表{'左邊' if la>lb else '右邊'}比較長，答案是{ans}")
    # 相差幾格 15 題
    for _ in range(15):
        a,b = rng.sample(objs,2)
        la = rng.randint(4,12); lb = rng.randint(2,la-1)
        unit = rng.choice(units)
        diff = la-lb
        q = f"{a}有{la}{unit}，{b}有{lb}{unit}，{a}比{b}長幾{unit}？"
        add("有多長",q,q,diff,make_opts(diff,1,10,4,rng),f"{la}-{lb}={diff}")
    # 加在一起 10 題
    for _ in range(10):
        a,b = rng.sample(objs,2)
        la = rng.randint(3,8); lb = rng.randint(3,8)
        unit = rng.choice(units)
        total = la+lb
        q = f"{a}有{la}{unit}，{b}有{lb}{unit}，加在一起共有幾{unit}？"
        add("有多長",q,q,total,make_opts(total,4,20,4,rng),f"{la}+{lb}={total}")

    total_q = len(qs)
    print(f"✓ 題庫共 {total_q} 題")
    for cat in CAT_NAMES:
        n = sum(1 for q in qs if q['cat']==cat)
        print(f"  {cat}: {n} 題")
    return qs

POOL = gen_pool()

# ═══════════════════════════════════════════════════════════════
#  每日選題：每類 5 題 × 8 = 40 題
# ═══════════════════════════════════════════════════════════════
def daily_questions():
    today=datetime.now(TZ_TW).strftime("%Y-%m-%d")
    seed=int(hashlib.md5(today.encode()).hexdigest(),16)%(2**32)
    rng=random.Random(seed)
    picked=[]
    for cat in CAT_NAMES:
        pool=[q for q in POOL if q['cat']==cat]
        rng.shuffle(pool)
        picked.extend(pool[:4])          # 每類 4 題 × 10 類 = 40 題
    picked.sort(key=lambda q:q['id'])
    return picked

# ═══════════════════════════════════════════════════════════════
#  HTML
# ═══════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>數學練習 🔢</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&family=Nunito:wght@700;800;900&display=swap" rel="stylesheet">
<style>
:root{--bg:#FFF9F0;--card:#fff;--ink:#1a1a2e;--soft:#6b7280;--border:#e5e7eb;
  --correct:#16A34A;--wrong:#DC2626;--add:#3B82F6;--app:#10B981}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);font-family:"Noto Sans TC","Nunito",sans-serif;
  min-height:100vh;padding-bottom:80px}

.header{background:#fff;border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:20;padding:0 16px}
.hinner{max-width:600px;margin:0 auto;height:52px;display:flex;align-items:center;gap:10px}
.logo{font-family:"Nunito";font-weight:900;font-size:20px;color:var(--ink)}
.logo span{color:var(--add)}
.hdate{margin-left:auto;font-size:12px;font-weight:700;color:var(--soft)}

.progress-wrap{background:#fff;border-bottom:1px solid var(--border);padding:7px 16px}
.progress-inner{max-width:600px;margin:0 auto;display:flex;align-items:center;gap:10px}
.prog-bar-bg{flex:1;height:10px;background:#E5E7EB;border-radius:8px;overflow:hidden}
.prog-bar{height:100%;background:linear-gradient(90deg,#3B82F6,#8B5CF6);border-radius:8px;transition:width .4s}
.prog-label{font-family:"Nunito";font-size:12px;font-weight:800;color:var(--soft);white-space:nowrap}
.score-badge{font-family:"Nunito";font-size:12px;font-weight:800;
  background:#FEF3C7;color:#92400E;border-radius:16px;padding:2px 10px;white-space:nowrap}

.filters{background:#fff;border-bottom:1px solid var(--border);padding:7px 16px}
.filter-row{max-width:600px;margin:0 auto;display:flex;align-items:center;gap:8px}
.filter-label{font-size:11px;font-weight:800;color:var(--soft);letter-spacing:.06em;white-space:nowrap}
.chips{display:flex;gap:5px;overflow-x:auto;scrollbar-width:none;flex:1}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;font-size:12px;font-weight:700;padding:4px 11px;border-radius:20px;
  border:1.5px solid var(--border);background:#fff;color:var(--soft);cursor:pointer;transition:.15s}
.chip.on{background:var(--add);color:#fff;border-color:var(--add)}

.feed{max-width:600px;margin:0 auto;padding:14px}
.date-hdr{font-size:11px;font-weight:800;letter-spacing:.1em;color:var(--soft);
  padding:14px 4px 7px;border-bottom:2px solid var(--border);margin-bottom:4px}

/* 類型徽章顏色 */
.cat-badge{font-size:10px;font-weight:800;border-radius:8px;padding:2px 8px;letter-spacing:.04em}
.cat-badge.c0{background:#DBEAFE;color:#1D4ED8}
.cat-badge.c1{background:#D1FAE5;color:#065F46}
.cat-badge.c2{background:#FEE2E2;color:#B91C1C}
.cat-badge.c3{background:#EDE9FE;color:#6D28D9}
.cat-badge.c4{background:#FEF3C7;color:#92400E}
.cat-badge.c5{background:#FCE7F3;color:#9D174D}
.cat-badge.c6{background:#CCFBF1;color:#065F46}
.cat-badge.c7{background:#F1F5F9;color:#475569}
.cat-badge.c8{background:#FFF7ED;color:#C2410C}
.cat-badge.c9{background:#ECFDF5;color:#047857}

.qcard{background:var(--card);border-radius:20px;padding:18px;margin-bottom:11px;
  border:2px solid var(--border);transition:border-color .2s;scroll-margin-top:120px}
.qcard.answered-correct{border-color:var(--correct);background:#F0FDF4}
.qcard.answered-wrong{border-color:var(--wrong);background:#FFF5F5}

.qtop{display:flex;align-items:center;gap:8px;margin-bottom:11px}
.qnum{font-family:"Nunito";font-size:11px;font-weight:800;color:var(--soft)}

.qtext{font-family:"Nunito";font-weight:900;font-size:30px;text-align:center;
  margin:12px 0;color:var(--ink);line-height:1.3}
.qtext.word{font-family:"Noto Sans TC";font-size:16px;font-weight:700;
  text-align:left;line-height:1.8}
.clock-wrap{text-align:center;margin:4px 0 10px}

.say-btn{background:none;border:1.5px solid var(--border);border-radius:20px;
  padding:5px 14px;font-size:12px;font-weight:700;cursor:pointer;color:var(--soft);
  transition:.15s;display:flex;align-items:center;gap:5px;margin:0 auto 12px}
.say-btn:hover{border-color:var(--add);color:var(--add)}

.opts{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.opts.cmp{grid-template-columns:1fr 1fr 1fr}
.opts.wide{grid-template-columns:1fr}
.opt{border:2.5px solid var(--border);border-radius:14px;padding:14px 8px;
  font-family:"Nunito";font-size:20px;font-weight:900;text-align:center;
  cursor:pointer;background:#fff;transition:all .2s;color:var(--ink)}
.opt.wide-opt{font-size:15px;text-align:left;padding:12px 14px}
.opt:hover:not(:disabled){border-color:var(--add);background:#EFF6FF;transform:scale(1.02)}
.opt.correct{border-color:var(--correct)!important;background:#F0FDF4!important;color:var(--correct)!important}
.opt.wrong{border-color:var(--wrong)!important;background:#FFF5F5!important;color:var(--wrong)!important}
.opt:disabled{cursor:default;opacity:.85}
.opts.cmp .opt{font-size:15px;padding:14px 4px;font-weight:900}

.feedback{margin-top:10px;padding:9px 13px;border-radius:11px;font-size:13.5px;font-weight:700;display:none}
.feedback.show{display:block}
.feedback.ok{background:#DCFCE7;color:#166534}
.feedback.ng{background:#FEE2E2;color:#991B1B}

/* 送出列 */
.submit-bar{position:fixed;bottom:0;left:0;right:0;background:rgba(255,249,240,.95);
  backdrop-filter:blur(10px);border-top:2px solid var(--border);padding:11px 16px;z-index:30}
.submit-btn{display:block;width:100%;max-width:600px;margin:0 auto;
  background:var(--app);color:#fff;border:none;border-radius:20px;padding:13px;
  font-family:"Nunito";font-size:17px;font-weight:900;cursor:pointer;transition:opacity .15s}
.submit-btn:hover{opacity:.85}

/* 結果橫幅 */
.result-banner{background:linear-gradient(135deg,#D1FAE5,#A7F3D0);border-radius:20px;
  padding:22px 16px;text-align:center;margin-bottom:14px;border:2px solid #6EE7B7;display:none}
.result-banner.show{display:block}
.result-emoji{font-size:38px;margin-bottom:5px}
.result-score{font-family:"Nunito";font-size:52px;font-weight:900;color:#065F46}
.result-label{font-size:14px;font-weight:700;color:#065F46;margin-top:3px;margin-bottom:2px}

/* 錯題複習 */
.review-section{margin-top:14px;text-align:left}
.review-title{font-family:"Nunito";font-size:14px;font-weight:900;color:#7C2D12;
  background:#FEF3C7;border-radius:11px;padding:9px 13px;margin-bottom:9px;border:1.5px solid #FDE68A}
.review-card{background:#fff;border-radius:14px;padding:13px;margin-bottom:8px;border:2px solid #FCA5A5}
.review-num{font-size:11px;font-weight:800;color:var(--soft);margin-bottom:6px;letter-spacing:.05em}
.review-q-text{font-family:"Nunito";font-size:20px;font-weight:900;color:var(--ink);
  text-align:center;margin:6px 0 9px;padding:8px;background:#F9FAFB;border-radius:9px}
.review-q-text.word{font-size:14px;text-align:left;line-height:1.7}
.review-wrong-row{font-size:13px;color:#B91C1C;font-weight:700;margin-bottom:4px}
.review-wrong-val{background:#FEE2E2;border-radius:5px;padding:1px 7px}
.review-correct-row{font-size:13px;color:#065F46;font-weight:700;margin-bottom:7px}
.review-correct-val{background:#D1FAE5;border-radius:5px;padding:1px 7px;font-size:14px}
.review-teach{font-size:12.5px;color:#374151;line-height:1.65;
  background:#FFFBEB;border-radius:9px;padding:8px 11px;border-left:3px solid #F59E0B}
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
    <div class="prog-label" id="progLabel">0 / 40</div>
    <div class="score-badge" id="scoreBadge">📝 已答 0 題</div>
  </div>
</div>
<div class="filters">
  <div class="filter-row">
    <span class="filter-label">日期</span>
    <div class="chips" id="dateBar"></div>
  </div>
</div>
<div class="feed" id="feed"></div>
<div class="submit-bar" id="submitBar">
  <button class="submit-btn" onclick="submitAnswers()">📝 送出答案</button>
</div>
<script>
const ALL_DATA=__ALL_DATA_JSON__;
const ALL_DATES=Object.keys(ALL_DATA).sort((a,b)=>b.localeCompare(a));
const CAT_NAMES=["50以內的數","18內加法","18內減法","圖形","100以內的數","錢幣","二位數加減","日曆","時鐘","有多長"];
const CAT_CLS={
  "50以內的數":"c0","18內加法":"c1","18內減法":"c2","圖形":"c3",
  "100以內的數":"c4","錢幣":"c5","二位數加減":"c6","日曆":"c7",
  "時鐘":"c8","有多長":"c9"};
let curDate="全部",selections={},answered={},submitted=false;

function fmtDate(iso){
  const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(iso||""); if(!m)return iso;
  const d=new Date(+m[1],+m[2]-1,+m[3]),w=["日","一","二","三","四","五","六"];
  return `${m[2]}/${m[3]} 週${w[d.getDay()]}`;
}
function buildDateBar(){
  const btns=[{k:"全部",l:`全部（${ALL_DATES.length}天）`},...ALL_DATES.map(d=>({k:d,l:fmtDate(d)}))];
  document.getElementById("dateBar").innerHTML=btns.map(b=>
    `<button class="chip${b.k===curDate?" on":""}" onclick="setDate('${b.k}')">${b.l}</button>`).join("");
}
function setDate(d){
  curDate=d;selections={};answered={};submitted=false;
  document.getElementById("submitBar").style.display="";
  document.getElementById("resultBanner")?.classList.remove("show");
  buildDateBar();buildFeed();updateProgress();
}
function filteredQs(){
  if(curDate==="全部"){
    const all=[];
    ALL_DATES.forEach(d=>(ALL_DATA[d]||[]).forEach(q=>all.push({...q,_date:d})));
    return all;
  }
  return (ALL_DATA[curDate]||[]).map(q=>({...q,_date:curDate}));
}
function updateProgress(){
  const qs=filteredQs(),total=qs.length;
  const done=Object.keys(selections).length;
  const correct=Object.values(answered).filter(Boolean).length;
  const pct=total?Math.round(done/total*100):0;
  document.getElementById("progBar").style.width=pct+"%";
  document.getElementById("progLabel").textContent=`${done} / ${total}`;
  document.getElementById("scoreBadge").textContent=
    submitted?`⭐ ${correct} 分`:`📝 已答 ${done} 題`;
}
function clockSVG(hour,minute){
  const cx=100,cy=100,rad=a=>a*Math.PI/180;
  const hDeg=(hour%12)*30+minute*0.5-90,mDeg=minute*6-90;
  const hx=cx+48*Math.cos(rad(hDeg)),hy=cy+48*Math.sin(rad(hDeg));
  const mx=cx+68*Math.cos(rad(mDeg)),my=cy+68*Math.sin(rad(mDeg));
  const ticks=Array.from({length:60},(_,i)=>{
    const a=rad(i*6-90),r1=i%5===0?76:82,r2=88;
    return `<line x1="${(cx+r1*Math.cos(a)).toFixed(1)}" y1="${(cy+r1*Math.sin(a)).toFixed(1)}"
      x2="${(cx+r2*Math.cos(a)).toFixed(1)}" y2="${(cy+r2*Math.sin(a)).toFixed(1)}"
      stroke="${i%5===0?'#9CA3AF':'#E5E7EB'}" stroke-width="${i%5===0?2:1}"/>`;
  }).join('');
  const nums=Array.from({length:12},(_,i)=>{
    const a=rad((i+1)*30-90),x=cx+74*Math.cos(a),y=cy+74*Math.sin(a);
    return `<text x="${x.toFixed(1)}" y="${(y+5).toFixed(1)}"
      text-anchor="middle" font-size="13" font-weight="bold" fill="#374151" font-family="Nunito">${i+1}</text>`;
  }).join('');
  return `<svg width="180" height="180" viewBox="0 0 200 200" style="filter:drop-shadow(0 3px 8px rgba(0,0,0,.1))">
    <circle cx="100" cy="100" r="95" fill="#FFF9F0" stroke="#E5E7EB" stroke-width="3"/>
    ${ticks}${nums}
    <line x1="100" y1="100" x2="${hx.toFixed(1)}" y2="${hy.toFixed(1)}" stroke="#1F2937" stroke-width="6" stroke-linecap="round"/>
    <line x1="100" y1="100" x2="${mx.toFixed(1)}" y2="${my.toFixed(1)}" stroke="#3B82F6" stroke-width="3.5" stroke-linecap="round"/>
    <circle cx="100" cy="100" r="5" fill="#1F2937"/></svg>`;
}
function sayQ(text){
  if(!window.speechSynthesis)return;
  speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.lang="zh-TW";u.rate=0.85;
  const v=speechSynthesis.getVoices().find(v=>/zh-TW|zh_TW/i.test(v.lang));
  if(v)u.voice=v;
  speechSynthesis.speak(u);
}
function sayResult(text){
  if(!window.speechSynthesis)return;
  setTimeout(()=>{
    const u=new SpeechSynthesisUtterance(text);
    u.lang="zh-TW";u.rate=1;
    const v=speechSynthesis.getVoices().find(v=>/zh-TW|zh_TW/i.test(v.lang));
    if(v)u.voice=v;
    speechSynthesis.speak(u);
  },200);
}
function buildFeed(){
  const qs=filteredQs();
  const feed=document.getElementById("feed");
  if(!qs.length){feed.innerHTML=`<div style="text-align:center;padding:40px;color:var(--soft)">此日期無題目</div>`;return;}
  let html="",lastDate="";
  qs.forEach((q,i)=>{
    if(curDate==="全部"&&q._date!==lastDate){
      lastDate=q._date;
      html+=`<div class="date-hdr">${fmtDate(q._date)} · ${(ALL_DATA[q._date]||[]).length} 題</div>`;
    }
    const isClock=q.cat==="時鐘"&&q.q_hour!=null;
    const isWide=q.cat==="圖形"||q.cat==="日曆"||q.cat==="錢幣"||q.cat==="有多長";
    const isCmp=(q.cat==="50以內的數"||q.cat==="100以內的數")&&q.q.includes("○");
    const qClass=isWide?"qtext word":"qtext";
    const optsClass=isCmp?"opts cmp":isWide?"opts wide":"opts";
    const optClass=isWide?"opt wide-opt":"opt";
    const sayText=isClock
      ? `時鐘顯示${q.q_hour}點${q.q_minute===0?'整':q.q_minute+'分'}`
      : q.q_zh||q.q;
    const qDisplay = isClock
      ? `<div class="clock-wrap">${clockSVG(q.q_hour,q.q_minute)}</div>
         <div style="text-align:center;font-size:13px;color:var(--soft);margin-bottom:8px">時鐘顯示的是幾點？</div>`
      : `<div class="${qClass}">${q.q}</div>`;
      onclick="selectOpt(${q.id},'${String(o).replace(/'/g,"\\'")}')"> ${o} </button>`).join("");
    html+=`
    <div class="qcard" id="qcard-${q.id}">
      <div class="qtop">
        <span class="qnum">第 ${i+1} 題</span>
        <span class="cat-badge ${CAT_CLS[q.cat]||'c0'}">${q.cat}</span>
      </div>
      ${qDisplay}
      <button class="say-btn" onclick="sayQ('${sayText.replace(/'/g,"\\'")}')">🔊 聽題目</button>
      <div class="${optsClass}" id="opts-${q.id}">${opts}</div>
      <div class="feedback" id="fb-${q.id}"></div>
    </div>`;
  });
  feed.innerHTML=html;
  Object.entries(selections).forEach(([qidStr,chosen])=>{
    const qid=parseInt(qidStr);
    const q=qs.find(x=>x.id===qid); if(!q)return;
    const isCorrect=answered[qid];
    q.opts.forEach(o=>{
      const btn=document.getElementById("opt-"+qid+"-"+encodeURIComponent(String(o)));
      if(!btn)return; btn.disabled=true;
      if(isCorrect&&String(o)===String(q.ans))btn.classList.add("correct");
      else if(!isCorrect&&String(o)===String(chosen))btn.classList.add("wrong");
    });
    const fb=document.getElementById("fb-"+qid);
    const card=document.getElementById("qcard-"+qid);
    if(isCorrect){if(fb)fb.className="feedback ok show",fb.textContent="✅ 答對了！真棒！";if(card)card.className="qcard answered-correct";}
    else{if(fb)fb.className="feedback ng show",fb.textContent="❌ 答錯了！";if(card)card.className="qcard answered-wrong";}
  });
}
function selectOpt(qid,chosen){
  if(submitted)return;
  if(selections[qid]!==undefined)return;
  selections[qid]=String(chosen);
  const qs=filteredQs();
  const q=qs.find(x=>x.id===qid); if(!q)return;
  const isCorrect=String(chosen)===String(q.ans);
  answered[qid]=isCorrect;
  q.opts.forEach(o=>{
    const btn=document.getElementById("opt-"+qid+"-"+encodeURIComponent(String(o)));
    if(!btn)return; btn.disabled=true;
    if(isCorrect&&String(o)===String(q.ans))btn.classList.add("correct");
    else if(!isCorrect&&String(o)===String(chosen))btn.classList.add("wrong");
  });
  const fb=document.getElementById("fb-"+qid);
  const card=document.getElementById("qcard-"+qid);
  if(isCorrect){if(fb){fb.className="feedback ok show";fb.textContent="✅ 答對了！真棒！";}if(card)card.className="qcard answered-correct";sayResult("答對了！");}
  else{if(fb){fb.className="feedback ng show";fb.textContent="❌ 答錯了！";}if(card)card.className="qcard answered-wrong";sayResult("答錯了！");}
  updateProgress();
}
function makeTeaching(q){
  if(q.cat.includes("加法")||q.cat==="18內加法"||q.cat==="二位數加減"){
    const m=q.q.match(/(\d+)\s*\+\s*(\d+)/);
    if(m)return `💡 ${m[1]} + ${m[2]} = <b>${parseInt(m[1])+parseInt(m[2])}</b>`;}
  if(q.cat.includes("減法")||q.cat==="18內減法"){
    const m=q.q.match(/(\d+)\s*-\s*(\d+)/);
    if(m)return `💡 ${m[1]} - ${m[2]} = <b>${parseInt(m[1])-parseInt(m[2])}</b>`;}
  if(q.cat.includes("的數")){
    if(q.q.includes("○"))return `💡 正確答案是 <b>${q.ans}</b>`;
    if(q.q.includes("個十"))return `💡 ${q.exp||''}，答案是 <b>${q.ans}</b>`;}
  return `💡 ${q.exp?q.exp+'，':''}正確答案是 <b>${q.ans}</b>`;
}
function submitAnswers(){
  if(submitted)return; submitted=true;
  const qs=filteredQs();
  qs.forEach(q=>{
    if(selections[q.id]===undefined){
      answered[q.id]=false;
      q.opts.forEach(o=>{const btn=document.getElementById("opt-"+q.id+"-"+encodeURIComponent(String(o)));if(!btn)return;btn.disabled=true;if(String(o)===String(q.ans))btn.classList.add("correct");});
      const fb=document.getElementById("fb-"+q.id);const card=document.getElementById("qcard-"+q.id);
      if(fb){fb.className="feedback ng show";fb.textContent=`⚠️ 未作答。正確答案是 ${q.ans}`;}if(card)card.className="qcard answered-wrong";
    }
  });
  const correct=Object.values(answered).filter(Boolean).length;
  const wrong=qs.length-correct;
  const pct=Math.round(correct/qs.length*100);
  const emoji=pct>=90?"🏆":pct>=70?"🎉":pct>=50?"💪":"📚";
  const msg=pct>=90?"太厲害了！":pct>=70?"做得很好！":pct>=50?"繼續加油！":"再練習看看！";
  const wrongQs=qs.filter(q=>!answered[q.id]);
  let reviewHTML=wrongQs.length?`
    <div class="review-section">
      <div class="review-title">📚 錯題複習（${wrongQs.length} 題）</div>
      ${wrongQs.map(({q,chosen,id},idx)=>{
        const c=selections[id];
        const isWide=q.cat==="圖形"||q.cat==="日曆"||q.cat==="錢幣";
        const qd=`<div class="review-q-text ${isWide?'word':''}">${q.q}</div>`;
        return `<div class="review-card">
          <div class="review-num">${idx+1}. ${q.cat}</div>${qd}
          <div class="review-wrong-row">❌ 你選了：<span class="review-wrong-val">${c||'未作答'}</span></div>
          <div class="review-correct-row">✅ 正確答案：<span class="review-correct-val">${q.ans}</span></div>
          <div class="review-teach">${makeTeaching(q)}</div></div>`;}).join("")}
    </div>`:`<div style="margin-top:12px;font-size:15px">🎊 全部答對！超棒的！</div>`;
  const banner=document.getElementById("resultBanner");
  if(banner){
    banner.innerHTML=`<div class="result-emoji">${emoji}</div>
      <div class="result-score">${correct}<span style="font-size:26px"> / ${qs.length}</span></div>
      <div class="result-label">${msg}（答對${correct}題，答錯${wrong}題）</div>${reviewHTML}`;
    banner.classList.add("show");banner.scrollIntoView({behavior:"smooth",block:"start"});}
  document.getElementById("submitBar").style.display="none";
  updateProgress();
}
if(window.speechSynthesis){speechSynthesis.getVoices();speechSynthesis.onvoiceschanged=()=>{};}
document.getElementById("feed").insertAdjacentHTML("beforebegin",'<div class="result-banner" id="resultBanner"></div>');
buildDateBar();buildFeed();updateProgress();
</script>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════════
def main():
    today=datetime.now(TZ_TW).strftime("%Y-%m-%d")
    gen_date=datetime.now(TZ_TW).strftime("%Y/%m/%d")
    history=json.loads(HIST_FILE.read_text(encoding="utf-8")) if HIST_FILE.exists() else {}
    print(f"✓ 歷史 {len(history)} 天")
    if today not in history:
        history[today]=daily_questions()
        print(f"✓ 新增 {today} 的 40 題")
    else:
        print(f"✓ {today} 已有記錄")
    HIST_FILE.write_text(json.dumps(history,ensure_ascii=False,indent=2),encoding="utf-8")
    html=HTML.replace("__ALL_DATA_JSON__",json.dumps(history,ensure_ascii=False))
    html=html.replace("__DATE__",gen_date)
    OUT_HTML.write_text(html,encoding="utf-8")
    print(f"✅ 完成 → {OUT_HTML}")

if __name__=="__main__":
    main()
