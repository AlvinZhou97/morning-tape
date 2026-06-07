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
    if n == 100: return "一百"
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
CAT_NAMES = ["50以內的數","100內加法","100內減法","圖形","100以內的數","錢幣","二位數加減","日曆","時鐘","有多長","應用題","動畫"]

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

    # ── 2. 100以內加法（65題：整十15＋兩位數20＋進位15＋填空15）
    # A. 整十數加法 15題（10~90）
    for _ in range(15):
        a=rng.randint(1,8)*10; b=rng.randint(1,9-a//10)*10
        ans=a+b
        add("100內加法",f"{a} + {b} = ?",f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(10,ans-20),min(100,ans+20),4,rng),f"{a}+{b}={ans}")
    # B. 兩位數+兩位數（不進位）20題
    for _ in range(20):
        a1=rng.randint(1,5)*10; a2=rng.randint(1,8)
        b1=rng.randint(1,4)*10; b2=rng.randint(0,9-a2)
        a=a1+a2; b=b1+b2; ans=a+b
        if ans>99: continue
        add("100內加法",f"{a} + {b} = ?",f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(10,ans-15),min(99,ans+15),4,rng),f"{a}+{b}={ans}")
    # C. 兩位數+兩位數（進位，個位和>10）15題
    for _ in range(15):
        while True:
            a=rng.randint(15,65); b=rng.randint(15,65)
            if a%10+b%10>10 and a+b<=100: break
        ans=a+b
        add("100內加法",f"{a} + {b} = ?",f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(20,ans-15),min(100,ans+15),4,rng),f"{a}+{b}={ans}（進位）")
    # D. 填空題 15題（□ + b = sum，逆向思考）
    for _ in range(15):
        b=rng.choice([10,20,30,40,50]); a=rng.randint(10,50)
        total=a+b
        if total>100: continue
        add("100內加法",f"□ + {b} = {total}",
            f"空格加{num_zh(b)}等於{num_zh(total)}，空格是幾？",
            a,make_opts(a,max(5,a-15),min(90,a+15),4,rng),f"{total}-{b}={a}")

    # ── 3. 100以內減法（65題：整十15＋兩位數20＋借位15＋填空15）
    # A. 整十數減法 15題
    for _ in range(15):
        a=rng.randint(2,9)*10; b=rng.randint(1,a//10-1)*10
        ans=a-b
        add("100內減法",f"{a} - {b} = ?",f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(0,ans-20),min(90,ans+20),4,rng),f"{a}-{b}={ans}")
    # B. 兩位數-兩位數（不借位）20題
    for _ in range(20):
        b1=rng.randint(1,5)*10; b2=rng.randint(0,8)
        a1=rng.randint(b1//10+1,8)*10; a2=rng.randint(b2,9)
        a=a1+a2; b=b1+b2; ans=a-b
        if ans<=0: continue
        add("100內減法",f"{a} - {b} = ?",f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(1,ans-15),min(89,ans+15),4,rng),f"{a}-{b}={ans}")
    # C. 兩位數-兩位數（借位，個位不夠減）15題
    for _ in range(15):
        while True:
            a=rng.randint(30,90); b=rng.randint(15,a-5)
            if a%10<b%10 and a-b>0: break  # 個位不夠，需借位
        ans=a-b
        add("100內減法",f"{a} - {b} = ?",f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(1,ans-15),min(89,ans+15),4,rng),f"{a}-{b}={ans}（借位）")
    # D. 填空題 15題（a - □ = remain）
    for _ in range(15):
        a=rng.randint(30,90); ans_val=rng.randint(10,a-10); b=a-ans_val
        add("100內減法",f"{a} - □ = {ans_val}",
            f"{num_zh(a)}減空格等於{num_zh(ans_val)}，空格是幾？",
            b,make_opts(b,max(5,b-15),min(80,b+15),4,rng),f"{a}-{ans_val}={b}")

    # ── 4. 圖形與分類（60題）──────────────────────────────────
    shape_pool = [
        # ── 邊數 ────────────────────────────────────────────
        ("三角形有幾條邊？","3",["2","3","4","5"],"三角形有3條邊"),
        ("正方形有幾條邊？","4",["3","4","5","6"],"正方形有4條邊"),
        ("長方形有幾條邊？","4",["3","4","5","6"],"長方形有4條邊"),
        ("圓形有幾條邊？","0",["0","1","2","3"],"圓形沒有邊（0條）"),
        # ── 角數 ────────────────────────────────────────────
        ("三角形有幾個角？","3",["2","3","4","5"],"三角形有3個角"),
        ("正方形有幾個角？","4",["3","4","5","6"],"正方形有4個角"),
        ("長方形有幾個角？","4",["3","4","5","6"],"長方形有4個角"),
        ("圓形有幾個角？","0",["0","1","2","3"],"圓形沒有角（0個）"),
        # ── 形狀識別 ────────────────────────────────────────
        ("有3條邊的圖形叫什麼？","三角形",["三角形","正方形","長方形","圓形"],"3條邊的是三角形"),
        ("4條邊都一樣長的圖形叫什麼？","正方形",["三角形","正方形","長方形","圓形"],"正方形4邊等長"),
        ("沒有角也沒有邊的圖形叫什麼？","圓形",["三角形","正方形","長方形","圓形"],"圓形沒有角也沒有邊"),
        ("4條邊但不一定等長的圖形叫什麼？","長方形",["三角形","正方形","長方形","圓形"],"長方形對邊等長但相鄰邊不同"),
        ("3個角、3條邊的圖形是？","三角形",["三角形","正方形","長方形","圓形"],"三角形3邊3角"),
        ("4個角、4條邊且4邊等長的是？","正方形",["三角形","正方形","長方形","圓形"],"正方形4邊等長"),
        # ── 生活中的形狀 ────────────────────────────────────
        ("時鐘的外形最像哪種圖形？","圓形",["三角形","正方形","長方形","圓形"],"時鐘是圓形"),
        ("硬幣的外形最像哪種圖形？","圓形",["三角形","正方形","長方形","圓形"],"硬幣是圓形"),
        ("書本封面最像哪種圖形？","長方形",["三角形","正方形","長方形","圓形"],"書本是長方形"),
        ("門的形狀最像哪種圖形？","長方形",["三角形","正方形","長方形","圓形"],"門是長方形"),
        ("窗戶的形狀最像哪種圖形？","長方形",["三角形","正方形","長方形","圓形"],"窗戶通常是長方形"),
        ("骰子的每一面是什麼形狀？","正方形",["三角形","正方形","長方形","圓形"],"骰子每面是正方形"),
        ("砰的一聲吹起來的是哪種圖形？","圓形",["三角形","正方形","長方形","圓形"],"氣球是圓形"),
        ("三角板的形狀是哪種圖形？","三角形",["三角形","正方形","長方形","圓形"],"三角板是三角形"),
        ("披薩切成三角形後，尖尖的頂點有幾個？","3",["2","3","4","5"],"三角形有3個角"),
        ("手帕通常是什麼形狀？","正方形",["三角形","正方形","長方形","圓形"],"手帕通常是正方形"),
        # ── 比較 ────────────────────────────────────────────
        ("三角形和正方形，哪個角比較多？","正方形",["三角形","正方形","一樣多","圓形"],"正方形4角>三角形3角"),
        ("哪種圖形可以一直滾不停下來？","圓形",["三角形","正方形","長方形","圓形"],"圓形可以滾"),
        ("正方形和長方形，邊的數量一樣嗎？","一樣，都是4條",["不一樣","一樣，都是3條","一樣，都是4條","一樣，都是5條"],"都是4條邊"),
        ("三角形和圓形，哪個沒有角？","圓形",["三角形","圓形","都沒有","都有"],"圓形沒有角"),
        ("哪兩種圖形邊數一樣？","正方形和長方形",["三角形和正方形","三角形和長方形","正方形和長方形","都不一樣"],"正方形和長方形都有4條邊"),
        # ── 計算 ────────────────────────────────────────────
        ("一個三角形和一個正方形，共有幾個角？","7",["5","6","7","8"],"3+4=7個角"),
        ("兩個三角形共有幾條邊？","6",["4","5","6","8"],"3+3=6條邊"),
        ("兩個正方形共有幾個角？","8",["6","7","8","9"],"4+4=8個角"),
        ("一個長方形和一個三角形，共有幾個角？","7",["5","6","7","8"],"4+3=7個角"),
        ("三個三角形共有幾條邊？","9",["6","8","9","12"],"3×3=9條邊"),
        ("兩個圓形和一個正方形，共有幾個角？","4",["0","4","8","6"],"圓形0角+正方形4角=4個角"),
        # ── 分類特徵 ────────────────────────────────────────
        ("下列哪個圖形有直角？","正方形",["三角形（等邊）","正方形","圓形","以上都沒有"],"正方形有直角"),
        ("哪種圖形所有的角都一樣大？","正方形",["三角形","正方形","長方形","圓形"],"正方形4角相等都是直角"),
        ("下列哪個圖形可以完全蓋住另一個同樣大小的自己（沿邊對齊）？","正方形",["正方形","長方形","三角形","都不行"],"正方形對稱性最好"),
        ("哪種圖形不管怎麼放都找得到對稱軸？","圓形",["三角形","正方形","長方形","圓形"],"圓形有無數條對稱軸"),
        # ── 數圖形 ────────────────────────────────────────
        ("一個正方形可以切成幾個三角形（沿對角線切）？","2",["1","2","3","4"],"沿對角線切成2個三角形"),
        ("四個三角形拼在一起可以組成哪種圖形？","正方形",["圓形","正方形","長方形","三角形"],"4個等腰直角三角形→正方形"),
        ("圓形有幾條對稱軸？","很多條",["0條","2條","4條","很多條"],"圓形有無數條對稱軸"),
        ("正方形有幾條對稱軸？","4條",["1條","2條","4條","8條"],"正方形有4條對稱軸"),
        ("長方形有幾條對稱軸？","2條",["1條","2條","4條","8條"],"長方形有2條對稱軸"),
        # ── 全等圖形 ────────────────────────────────────────
        ("大小和形狀完全一樣的兩個圖形叫做什麼？","全等圖形",["相似圖形","全等圖形","對稱圖形","平行圖形"],"大小形狀完全相同叫全等圖形"),
        ("兩個一樣大的正方形是什麼關係？","全等圖形",["相似圖形","全等圖形","不同圖形","對稱圖形"],"大小相同叫全等"),
        # ── 積木情境 ────────────────────────────────────────
        ("用正方形積木拼一個長方形，最少需要幾個？","2",["1","2","3","4"],"2個正方形可拼成長方形"),
        ("三角形積木的角是幾個？","3",["2","3","4","5"],"三角形3個角"),
        ("圓形積木能不能像正方形那樣疊起來不滑落？","不能",["能","不能","有時能","要看大小"],"圓形會滾，較難疊"),
    ]
    # 60種不重複，隨機排列
    rng.shuffle(shape_pool)
    for q_text,ans,opts,exp in shape_pool[:60]:
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
    # 錢幣（一年級下：認識、計算合計，不做找零）
    coins_q = []
    # A. X個10元和Y個1元（主力題型）
    for _ in range(25):
        t=rng.randint(1,5); o=rng.randint(0,9)
        ans=t*10+o
        if o==0:
            q=f"{t}個10元是多少元？"
        else:
            q=f"{t}個10元和{o}個1元，一共幾元？"
        coins_q.append((q,q,ans,make_opts(ans,max(1,ans-12),min(59,ans+12),4,rng),
                        f"{t}×10={t*10}，加{o}個1元＝{ans}元"))
    # B. X個10元和Y個5元
    for _ in range(15):
        a=rng.randint(1,4); b=rng.randint(1,4)
        ans=a*10+b*5
        q=f"{a}個10元和{b}個5元，一共幾元？"
        coins_q.append((q,q,ans,make_opts(ans,max(5,ans-15),min(65,ans+15),4,rng),
                        f"{a}×10+{b}×5={ans}元"))
    # C. 50元銅板計算
    for _ in range(10):
        n50=rng.randint(1,2); n10=rng.randint(0,4)
        ans=n50*50+n10*10
        if n10==0:
            q=f"{n50}個50元，共幾元？"
        else:
            q=f"{n50}個50元和{n10}個10元，共幾元？"
        coins_q.append((q,q,ans,make_opts(ans,max(10,ans-20),min(99,ans+20),4,rng),
                        f"{n50}×50+{n10}×10={ans}元"))
    # D. 哪些錢幣組合等於？（逆向推理）
    targets = [10,20,30,15,25,35,40,45]
    rng.shuffle(targets)
    for tgt in targets[:10]:
        combos = []
        if tgt%10==0: combos.append(f"{tgt//10}個10元")
        if tgt>=5 and (tgt-5)%10==0: combos.append(f"1個5元和{(tgt-5)//10}個10元" if tgt>5 else "1個5元")
        combos.append(f"{tgt}個1元")
        correct = combos[0] if combos else f"{tgt}個1元"
        # 干擾選項
        wrong1 = f"{tgt+5}個1元"; wrong2 = f"{tgt//10+1}個10元"; wrong3 = f"{max(1,tgt-5)}個1元"
        opts = [correct,wrong1,wrong2,wrong3]; rng.shuffle(opts)
        if correct not in opts: opts[0]=correct
        coins_q.append((f"哪個組合等於{tgt}元？",
                        f"哪個組合合計是{tgt}元？",
                        correct,opts[:4],f"{tgt}元最簡單是{correct}"))
    rng.shuffle(coins_q)
    for q,q_zh,ans,opts,exp in coins_q[:60]:
        add("錢幣",q,q_zh,ans,opts,exp)

    # ── 7. 二位數的加減（65題，加入兩位數±兩位數）────────────
    # A. 二位數+一位數（不進位）12題
    for _ in range(12):
        t=rng.randint(1,8)*10; o=rng.randint(0,7)
        b=rng.randint(1,9-o); a=t+o; ans=a+b
        add("二位數加減",f"{a} + {b} = ?",
            f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(10,ans-8),min(99,ans+8),4,rng),f"{a}+{b}={ans}")
    # B. 二位數-一位數（不借位）12題
    for _ in range(12):
        t=rng.randint(1,9)*10; o=rng.randint(2,9); b=rng.randint(1,o)
        a=t+o; ans=a-b
        add("二位數加減",f"{a} - {b} = ?",
            f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(10,ans-8),min(99,ans+8),4,rng),f"{a}-{b}={ans}")
    # C. 二位數+整十數 10題
    for _ in range(10):
        a=rng.randint(11,55); b=rng.choice([10,20,30,40])
        ans=a+b
        if ans>99: continue
        add("二位數加減",f"{a} + {b} = ?",
            f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(10,ans-12),min(99,ans+12),4,rng),f"{a}+{b}={ans}")
    # D. 二位數-整十數 10題
    for _ in range(10):
        a=rng.randint(40,90); b=rng.choice([10,20,30,40])
        ans=a-b
        if ans<0: continue
        add("二位數加減",f"{a} - {b} = ?",
            f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(0,ans-12),min(89,ans+12),4,rng),f"{a}-{b}={ans}")
    # E. ★新增★ 二位數+二位數（不進位）11題
    for _ in range(11):
        t1=rng.randint(1,6)*10; o1=rng.randint(1,8)
        t2=rng.randint(1,3)*10; o2=rng.randint(0,9-o1)
        a=t1+o1; b=t2+o2; ans=a+b
        if ans>99: continue
        add("二位數加減",f"{a} + {b} = ?",
            f"{num_zh(a)} 加 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(10,ans-12),min(99,ans+12),4,rng),f"{a}+{b}={ans}（兩位數加兩位數）")
    # F. ★新增★ 二位數-二位數（不借位）10題
    for _ in range(10):
        t1=rng.randint(3,9)*10; o1=rng.randint(3,9)
        t2=rng.randint(1,t1//10-1)*10; o2=rng.randint(0,o1)
        a=t1+o1; b=t2+o2; ans=a-b
        if ans<=0: continue
        add("二位數加減",f"{a} - {b} = ?",
            f"{num_zh(a)} 減 {num_zh(b)} 等於多少？",
            ans,make_opts(ans,max(1,ans-12),min(89,ans+12),4,rng),f"{a}-{b}={ans}（兩位數減兩位數）")

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
    def add_len(q, q_zh, ans, opts, exp, a, b, la, lb, unit):
        nonlocal qid; qid+=1
        qs.append({"id":qid,"cat":"有多長","q":q,"q_zh":q_zh,
                   "q_a":a,"q_b":b,"q_la":la,"q_lb":lb,"q_unit":unit,
                   "ans":str(ans),"opts":[str(o) for o in opts],"exp":exp})
    # 比較長短 25 題
    for _ in range(25):
        a,b = rng.sample(objs,2)
        la = rng.randint(3,12); lb = rng.randint(3,12)
        while la==lb: lb=rng.randint(3,12)
        unit = rng.choice(units)
        q_type = rng.choice(["長","短"])
        ans = (a if la>lb else b) if q_type=="長" else (b if la>lb else a)
        # 題目不寫數字，讓小孩自己數圖案
        q = f"數一數，{a}和{b}，哪個比較{q_type}？"
        q_zh = q
        opts = [a, b, "一樣長", "無法比較"]; rng.shuffle(opts)
        if ans not in opts: opts[0]=ans
        add_len(q,q_zh,ans,opts[:4],
            f"{a}有{la}個，{b}有{lb}個，{'>' if la>lb else '<'}，所以{ans}比較長",
            a,b,la,lb,unit)
    # 相差幾格 15 題
    for _ in range(15):
        a,b = rng.sample(objs,2)
        la = rng.randint(4,12); lb = rng.randint(2,la-1)
        unit = rng.choice(units)
        diff = la-lb
        q = f"數一數，{a}比{b}多幾個{unit}？"
        add_len(q,q,diff,make_opts(diff,1,10,4,rng),
            f"{a}有{la}個，{b}有{lb}個，{la}-{lb}={diff}",a,b,la,lb,unit)
    # 加在一起 10 題
    for _ in range(10):
        a,b = rng.sample(objs,2)
        la = rng.randint(3,8); lb = rng.randint(3,8)
        unit = rng.choice(units)
        total = la+lb
        q = f"數一數，{a}和{b}加在一起共有幾個{unit}？"
        add_len(q,q,total,make_opts(total,4,20,4,rng),
            f"{a}有{la}個，{b}有{lb}個，{la}+{lb}={total}",a,b,la,lb,unit)

    # ── 11. 應用題（80題，7種類型）────────────────────────────
    # 場景物件池
    FOOD   = ["糖果","餅乾","蘋果","香蕉","橘子","草莓","葡萄","包子","饅頭","湯圓"]
    ANIMAL = ["小雞","小鴨","兔子","小魚","小鳥","蝴蝶","螢火蟲","青蛙","烏龜","蝸牛"]
    # 分類：飛行動物 vs 非飛行動物
    FLY_ANIMAL  = ["小鴨","小鳥","蝴蝶","螢火蟲"]   # 只有這些會飛
    WALK_ANIMAL = ["兔子","青蛙","小狗","小貓","松鼠"] # 在地面跑跳
    STATY  = ["鉛筆","橡皮擦","貼紙","彩色筆","本子","書本","剪刀","蠟筆","迴紋針","磁鐵"]
    PERSON = ["同學","小朋友","男生","女生","小孩","姊姊","弟弟","同班同學","隊員","朋友"]
    NATURE = ["花朵","葉子","石頭","貝殼","松果","氣球","星星","雲朵","水滴","落葉"]
    ALL_OBJ = FOOD+ANIMAL+STATY+PERSON+NATURE

    def robj(): return rng.choice(ALL_OBJ)
    def rsmall(lo=2,hi=9): return rng.randint(lo,hi)
    def rbig(lo=10,hi=18): return rng.randint(lo,hi)
    def rmed(lo=5,hi=15): return rng.randint(lo,hi)

    # ── A. 合併型（兩組合在一起）──────────────────────────────
    A_tmpl = [
        lambda a,b,o: (f"花園裡有{a}朵紅花和{b}朵黃花，一共有幾朵花？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"籃子裡有{a}個{o}，旁邊又有{b}個{o}，合起來共有幾個{o}？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"操場上有{a}位男生和{b}位女生在玩，一共有幾位小朋友？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"桌上有{a}本書，地板上有{b}本書，合起來共有幾本書？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"左邊有{a}隻{rng.choice(ANIMAL)}，右邊有{b}隻，一共有幾隻？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"小明有{a}張貼紙，小花有{b}張貼紙，兩人共有幾張貼紙？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"袋子裡有{a}顆{rng.choice(FOOD)}，又加入{b}顆，共有幾顆？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"一班有{a}人，二班有{b}人，兩班合計有幾人？", a+b, f"{a}+{b}={a+b}"),
    ]
    for _ in range(12):
        a,b=rsmall(),rsmall(); o=robj()
        q_fn=rng.choice(A_tmpl); q,ans,exp=q_fn(a,b,o)
        add("應用題",q,q,ans,make_opts(ans,1,18,4,rng),exp)

    # ── B. 添加型（原來+再來）──────────────────────────────────
    B_tmpl = [
        lambda a,b,o: (f"樹上有{a}隻{rng.choice(FLY_ANIMAL)}，又飛來{b}隻，現在樹上有幾隻？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"停車場有{a}輛車，又開進來{b}輛，現在共有幾輛車？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"小明有{a}顆{rng.choice(FOOD)}，媽媽又給了他{b}顆，他現在有幾顆？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"書架上有{a}本書，老師再放上{b}本，現在共有幾本書？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"花瓶裡有{a}朵花，又插入{b}朵，現在花瓶裡有幾朵花？", a+b, f"{a}+{b}={a+b}"),
    ]
    for _ in range(10):
        a,b=rsmall(),rsmall(); o=robj()
        q_fn=rng.choice(B_tmpl); q,ans,exp=q_fn(a,b,o)
        add("應用題",q,q,ans,make_opts(ans,1,18,4,rng),exp)

    # ── C. 拿走型（原來-拿走）──────────────────────────────────
    C_tmpl = [
        lambda a,b,o: (f"盤子裡有{a}顆{rng.choice(FOOD)}，吃掉{b}顆，還剩幾顆？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"停車場有{a}輛車，開走{b}輛，剩下幾輛？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"班上有{a}位同學，有{b}位請假，今天來了幾位？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"樹上有{a}隻{rng.choice(FLY_ANIMAL)}，飛走{b}隻，還剩幾隻？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"小花有{a}張{rng.choice(STATY)}，送給朋友{b}張，還剩幾張？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"架子上有{a}本書，借走{b}本，還剩幾本？", a-b, f"{a}-{b}={a-b}"),
    ]
    for _ in range(12):
        a=rng.randint(6,18); b=rng.randint(1,a-1)
        o=robj(); q_fn=rng.choice(C_tmpl); q,ans,exp=q_fn(a,b,o)
        add("應用題",q,q,ans,make_opts(ans,0,17,4,rng),exp)

    # ── D. 比多型（A比B多幾個，B有X，求A）────────────────────
    D_tmpl = [
        lambda a,d,o: (f"小明有{a}顆{rng.choice(FOOD)}，小花比小明多{d}顆，小花有幾顆？", a+d, f"{a}+{d}={a+d}"),
        lambda a,d,o: (f"哥哥有{a}張貼紙，弟弟比哥哥多{d}張，弟弟有幾張貼紙？", a+d, f"{a}+{d}={a+d}"),
        lambda a,d,o: (f"籃子裡有{a}個{rng.choice(FOOD)}，盒子裡比籃子多{d}個，盒子裡有幾個？", a+d, f"{a}+{d}={a+d}"),
        lambda a,d,o: (f"小紅有{a}本書，小藍比小紅多{d}本，小藍有幾本書？", a+d, f"{a}+{d}={a+d}"),
    ]
    for _ in range(10):
        a=rsmall(3,9); d=rsmall(1,5)
        o=robj(); q_fn=rng.choice(D_tmpl); q,ans,exp=q_fn(a,d,o)
        add("應用題",q,q,ans,make_opts(ans,2,18,4,rng),exp)

    # ── E. 比少型（A比B少幾個，A有X，求B）────────────────────
    E_tmpl = [
        lambda a,d,o: (f"小花有{a}顆{rng.choice(FOOD)}，小明比小花少{d}顆，小明有幾顆？", a-d, f"{a}-{d}={a-d}"),
        lambda a,d,o: (f"姊姊有{a}張貼紙，妹妹比姊姊少{d}張，妹妹有幾張貼紙？", a-d, f"{a}-{d}={a-d}"),
        lambda a,d,o: (f"大盒有{a}個{rng.choice(FOOD)}，小盒比大盒少{d}個，小盒有幾個？", a-d, f"{a}-{d}={a-d}"),
    ]
    for _ in range(9):
        d=rsmall(1,4); a=rsmall(d+2,9)
        o=robj(); q_fn=rng.choice(E_tmpl); q,ans,exp=q_fn(a,d,o)
        add("應用題",q,q,ans,make_opts(ans,1,15,4,rng),exp)

    # ── F. 求原來（知道剩下或結果，求原來）────────────────────
    F_tmpl = [
        lambda r,b,o: (f"箱子裡有一些{rng.choice(FOOD)}，拿出{b}個後還剩{r}個，原來有幾個？", r+b, f"{r}+{b}={r+b}"),
        lambda r,b,o: (f"小明有一些{rng.choice(STATY)}，用掉{b}個後還剩{r}個，他原來有幾個？", r+b, f"{r}+{b}={r+b}"),
        lambda r,b,o: (f"草地上有一些{rng.choice(WALK_ANIMAL)}，跑走{b}隻後剩下{r}隻，草地上原來有幾隻？", r+b, f"{r}+{b}={r+b}"),
    ]
    for _ in range(9):
        r=rsmall(2,8); b=rsmall(1,6)
        o=robj(); q_fn=rng.choice(F_tmpl); q,ans,exp=q_fn(r,b,o)
        add("應用題",q,q,ans,make_opts(ans,4,18,4,rng),exp)

    # ── G. 相差型（兩個比較，問相差幾個）─────────────────────
    G_tmpl = [
        lambda a,b,o: (f"小明有{a}顆{rng.choice(FOOD)}，小花有{b}顆，小明比小花多幾顆？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"哥哥有{a}張貼紙，弟弟有{b}張，哥哥比弟弟多幾張貼紙？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"左邊有{a}個{rng.choice(FOOD)}，右邊有{b}個，左邊比右邊多幾個？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"甲班有{a}人，乙班有{b}人，甲班比乙班多幾人？", a-b, f"{a}-{b}={a-b}"),
    ]
    for _ in range(10):
        b=rsmall(2,7); a=rsmall(b+1,b+7)
        o=robj(); q_fn=rng.choice(G_tmpl); q,ans,exp=q_fn(a,b,o)
        add("應用題",q,q,ans,make_opts(ans,1,10,4,rng),exp)

    # ── H. 二位數應用題（大數字，數字範圍提升）────────────────
    H_tmpl = [
        lambda a,b,o: (f"停車場有{a}輛車，又來了{b}輛，現在共有幾輛？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"學校有{a}位學生，轉來{b}位新生，現在共有幾位？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"圖書館有{a}本書，又買了{b}本，共有幾本？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"操場有{a}人，又跑來{b}人，現在有幾人？", a+b, f"{a}+{b}={a+b}"),
        lambda a,b,o: (f"工廠生產{a}件商品，賣掉{b}件，還剩幾件？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"遊樂場有{a}人，離開{b}人，還剩幾人？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"農場有{a}隻動物，賣掉{b}隻，還剩幾隻？", a-b, f"{a}-{b}={a-b}"),
        lambda a,b,o: (f"倉庫有{a}箱貨物，搬走{b}箱，還剩幾箱？", a-b, f"{a}-{b}={a-b}"),
    ]
    for _ in range(5):  # 大數加法
        q_fn=rng.choice(H_tmpl[:4])
        a=rng.randint(30,70); b=rng.randint(10,30)
        while a+b>99: b=rng.randint(5,20)
        o=robj(); q,ans,exp=q_fn(a,b,o)
        add("應用題",q,q,ans,make_opts(ans,max(10,ans-15),min(99,ans+15),4,rng),exp)
    for _ in range(5):  # 大數減法
        q_fn=rng.choice(H_tmpl[4:])
        a=rng.randint(40,90); b=rng.randint(10,a-10)
        o=robj(); q,ans,exp=q_fn(a,b,o)
        add("應用題",q,q,ans,make_opts(ans,max(5,ans-15),min(85,ans+15),4,rng),exp)

    # ── 12. 動畫題（5種題型，60題，每天6題）──────────────────
    AE = ["🍎","🌸","⭐","🐱","🐶","🦋","🎈","🐥","🍓","🎵",
          "🐢","🌈","🍭","🦊","🌻","🍩","🐸","💎","🏀","🚗",
          "🐠","🦄","🍦","🎯","🌺","🐨","🍇","🎪","🐻","🦉"]
    AE2= ["🌙","🔴","🌿","🎀","🧡","🔵","🌞","🎵","🍋","🧸"]

    # ── 12. 動畫題（5種題型，難度提升，60題，每天6題）──────────
    AE = ["🍎","🌸","⭐","🐱","🐶","🦋","🎈","🐥","🍓","🎵",
          "🐢","🌈","🍭","🦊","🌻","🍩","🐸","💎","🏀","🚗",
          "🐠","🦄","🍦","🎯","🌺","🐨","🍇","🎪","🐻","🦉"]
    AE2= ["🌙","🔴","🌿","🎀","🧡","🔵","🌞","🎵","🍋","🧸"]

    # A. 計數型（8~18個，超過10需進位思考）15題
    for _ in range(15):
        n=rng.randint(8,18); e=rng.choice(AE)
        qs.append({"id":qid,"cat":"動畫","anim":"count",
                   "anim_emoji":e,"anim_n1":n,"anim_n2":0,
                   "q":"數一數，共有幾個？","q_zh":"數一數，共有幾個？",
                   "ans":str(n),"opts":[str(o) for o in make_opts(n,max(5,n-4),min(20,n+4),4,rng)],
                   "exp":f"一個一個數，共有{n}個"}); qid+=1

    # B. 加法合併型（進位加法，和 10~18）12題
    for _ in range(12):
        while True:
            n1=rng.randint(4,9); n2=rng.randint(4,9)
            if 10<=n1+n2<=18: break
        e=rng.choice(AE); ans=n1+n2
        qs.append({"id":qid,"cat":"動畫","anim":"add",
                   "anim_emoji":e,"anim_n1":n1,"anim_n2":n2,
                   "q":f"左邊和右邊合起來共有幾個？（超過10要進位喔！）",
                   "q_zh":f"左邊{num_zh(n1)}個加右邊{num_zh(n2)}個，合起來共有幾個？",
                   "ans":str(ans),"opts":[str(o) for o in make_opts(ans,max(8,ans-3),min(18,ans+3),4,rng)],
                   "exp":f"{n1}+{n2}={ans}（進位）"}); qid+=1

    # C. 減法（10~18範圍）12題 — 依emoji選合適動詞
    EMOJI_VERB = {
        # 飛走的
        "🦋":"飛走","🎈":"飛走","🐥":"飛走","🎵":"飄走","🌸":"飄走",
        "⭐":"消失","🌻":"飄走","🌈":"消失","🦉":"飛走",
        # 跑走的
        "🐱":"跑走","🐶":"跑走","🦊":"跑走","🐸":"跳走","🐨":"走掉",
        "🐻":"走掉","🦄":"跑走","🐢":"爬走","🚗":"開走",
        # 游走的
        "🐠":"游走",
        # 被吃掉的
        "🍎":"被吃掉","🍓":"被吃掉","🍭":"被吃掉","🍩":"被吃掉",
        "🍦":"被吃掉","🍇":"被吃掉","🎪":"消失",
        # 其他
        "💎":"消失","🏀":"滾走","🎯":"消失","🌺":"飄走","🐠":"游走",
    }
    SUB_EMOJI = list(EMOJI_VERB.keys())
    for _ in range(12):
        n1=rng.randint(10,18); n2=rng.randint(3,n1-3)
        e=rng.choice(SUB_EMOJI)
        verb=EMOJI_VERB.get(e,"不見")
        ans=n1-n2
        # 隨機決定哪些位置是「消失」的（交錯排列）
        positions=list(range(n1)); rng.shuffle(positions)
        gone_pos=sorted(positions[:n2])
        q=f"灰色的{verb}了，還剩幾個？"
        q_zh=f"原本{num_zh(n1)}個，有{num_zh(n2)}個{verb}了，還剩幾個？"
        qs.append({"id":qid,"cat":"動畫","anim":"sub",
                   "anim_emoji":e,"anim_n1":n1,"anim_n2":n2,
                   "anim_gone_pos":gone_pos,
                   "q":q,"q_zh":q_zh,
                   "ans":str(ans),"opts":[str(o) for o in make_opts(ans,max(1,ans-4),min(15,ans+4),4,rng)],
                   "exp":f"{n1}-{n2}={ans}"}); qid+=1

    # D. 數序型（100以內，步距2/5/10，有回推）11題
    for _ in range(11):
        step=rng.choice([2,5,10,10,2])      # 10較常見（百以內）
        start=rng.randint(5,80)
        seq=[start+step*i for i in range(5)]
        while any(n>100 for n in seq):
            start=max(1,start-step*3)
            seq=[start+step*i for i in range(5)]
        # 挖掉1或2個空格
        n_holes=rng.choice([1,1,2])
        poses=rng.sample(range(5),n_holes)
        ans_val=seq[poses[0]]
        seq_disp=[str(n) if i not in poses else "?" for i,n in enumerate(seq)]
        q_zh="、".join([num_zh(n) if i not in poses else "空格" for i,n in enumerate(seq)])+"，第一個空格填幾？"
        qs.append({"id":qid,"cat":"動畫","anim":"seq",
                   "anim_seq":seq_disp,
                   "q":"空格填哪個數？","q_zh":q_zh,
                   "ans":str(ans_val),"opts":[str(o) for o in make_opts(ans_val,max(1,ans_val-step*2),min(100,ans_val+step*2),4,rng)],
                   "exp":f"每次加{step}，空格是{ans_val}"}); qid+=1

    # E. 比多少型（問相差幾個，而非只問哪個多）10題
    for _ in range(10):
        n1=rng.randint(5,15); n2=rng.randint(4,14)
        while n1==n2: n2=rng.randint(4,14)
        e1=rng.choice(AE); e2=rng.choice(AE2)
        diff=abs(n1-n2)
        bigger="第一排" if n1>n2 else "第二排"
        q_type=rng.choice(["哪排多","哪排少","相差多少"])
        if q_type=="哪排多":
            ans=bigger
            opts=["第一排","第二排","一樣多"]; rng.shuffle(opts)
            if ans not in opts: opts[0]=ans
            exp=f"第一排{n1}個，第二排{n2}個，{bigger}比較多"
        elif q_type=="哪排少":
            ans="第二排" if bigger=="第一排" else "第一排"
            opts=["第一排","第二排","一樣少"]; rng.shuffle(opts)
            if ans not in opts: opts[0]=ans
            exp=f"第一排{n1}個，第二排{n2}個，{ans}比較少"
        else:  # 相差多少
            ans=str(diff)
            opts=[str(o) for o in make_opts(diff,max(1,diff-3),min(12,diff+3),4,rng)]
            exp=f"|{n1}-{n2}|={diff}個"
            q_type="相差幾個"
        qs.append({"id":qid,"cat":"動畫","anim":"cmp",
                   "anim_emoji":e1,"anim_emoji2":e2,"anim_n1":n1,"anim_n2":n2,
                   "q":f"{q_type}？","q_zh":f"數一數，{q_type}？",
                   "ans":ans,"opts":opts[:4] if len(opts)>=4 else opts+["無法比較"],
                   "exp":exp}); qid+=1

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
        if cat=='動畫':
            # 確保5種類型各出現1題，再補1題湊6題
            ANIM_TYPES=['count','add','sub','seq','cmp']
            anim_picked=[]
            for atype in ANIM_TYPES:
                t_pool=[q for q in pool if q.get('anim')==atype]
                rng.shuffle(t_pool)
                if t_pool: anim_picked.append(t_pool[0])
            # 從剩餘未選的補1題（任意類型）
            used_ids={q['id'] for q in anim_picked}
            extras=[q for q in pool if q['id'] not in used_ids]
            rng.shuffle(extras)
            if extras: anim_picked.append(extras[0])
            rng.shuffle(anim_picked)
            picked.extend(anim_picked)
        else:
            picked.extend(pool[:4])  # 其餘各4題
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
  --correct:#16A34A;--wrong:#DC2626;--add:#3B82F6;--app:#10B981;--maxw:640px}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);font-family:"Noto Sans TC","Nunito",sans-serif;
  min-height:100vh;padding-bottom:80px}
/* 寬螢幕置中：全頁限制在 640px，左右置中 */
@media(min-width:680px){
  body{background:#D1D5DB;display:flex;flex-direction:column;align-items:center}
  .header,.progress-wrap,.filters{width:var(--maxw)!important;
    border-left:1px solid var(--border);border-right:1px solid var(--border)}
  .feed{width:var(--maxw)}
  .submit-bar{width:var(--maxw);left:50%;transform:translateX(-50%);
    border-left:1px solid var(--border);border-right:1px solid var(--border);
    border-radius:0 0 12px 12px}
  .result-banner{border-radius:12px}
}

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

/* 動畫題 */
.anim-box{background:#FFFBEB;border:2px solid #FDE68A;border-radius:16px;
  padding:14px 10px 10px;margin:4px 0 10px;text-align:center;min-height:80px}
.anim-row{display:flex;flex-wrap:wrap;gap:5px;justify-content:center;align-items:center}
.anim-group{display:flex;flex-wrap:wrap;gap:5px;justify-content:center}
/* 預設隱藏，按按鈕才播放 */
.anim-item{display:inline-block;font-size:30px;opacity:0}
.anim-num{display:inline-block;font-size:24px;font-weight:900;
  background:#fff;border:2px solid #E5E7EB;border-radius:10px;
  padding:4px 10px;margin:2px;opacity:0}
.anim-num.blank{background:#FEF3C7;border-color:#F59E0B;color:#B45309}
.anim-op{font-size:26px;font-weight:900;color:#3B82F6;opacity:0}
.anim-hint{font-size:11.5px;color:var(--soft);margin-top:7px}
/* 播放中 */
.anim-box.playing .anim-item{animation:popIn 0.4s ease-out both}
.anim-box.playing .anim-item.gone{animation:popIn 0.4s ease-out both;
  filter:grayscale(1);opacity:.28!important}
.anim-box.playing .anim-num{animation:bounceNum 0.4s ease-out both}
.anim-box.playing .anim-op{animation:bounceNum 0.35s ease-out both}
@keyframes popIn{
  from{opacity:0;transform:scale(0) rotate(-15deg)}
  65%{transform:scale(1.25) rotate(5deg)}
  to{opacity:1;transform:scale(1) rotate(0)}
}
@keyframes bounceNum{
  from{opacity:0;transform:translateY(12px) scale(.7)}
  to{opacity:1;transform:translateY(0) scale(1)}
}
.play-btn{background:var(--add);color:#fff;border:none;border-radius:20px;
  padding:7px 20px;font-family:"Nunito";font-size:14px;font-weight:800;
  cursor:pointer;display:flex;align-items:center;gap:6px;margin:0 auto 10px;transition:opacity .15s}
.play-btn:hover{opacity:.85}
.cat-badge.c10{background:#F3E8FF;color:#6D28D9}
.cat-badge.c11{background:#ECFDF5;color:#065F46}
.cat-badge.c_anim{background:#FEF3C7;color:#B45309}
.submit-bar{position:fixed;bottom:0;left:0;right:0;background:rgba(255,249,240,.96);
  backdrop-filter:blur(12px);border-top:2px solid var(--border);padding:12px 16px 16px;z-index:30}
.submit-btn{display:flex;align-items:center;justify-content:center;gap:10px;
  width:100%;max-width:560px;margin:0 auto;
  background:linear-gradient(135deg,#10B981,#059669);color:#fff;border:none;
  border-radius:28px;padding:17px 24px;font-family:"Nunito";font-size:20px;
  font-weight:900;letter-spacing:.03em;cursor:pointer;
  box-shadow:0 6px 24px rgba(16,185,129,.45);transition:transform .15s,box-shadow .15s}
.submit-btn:hover{transform:translateY(-2px);box-shadow:0 10px 32px rgba(16,185,129,.5)}
.submit-btn:active{transform:translateY(1px);box-shadow:0 3px 12px rgba(16,185,129,.35)}
.sub-count{font-size:13px;font-weight:700;opacity:.85;
  background:rgba(255,255,255,.2);border-radius:20px;padding:2px 10px}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.45);
  z-index:200;display:none;align-items:center;justify-content:center;padding:20px}
.modal-overlay.show{display:flex}
.modal-card{background:#fff;border-radius:24px;padding:28px 22px;max-width:320px;
  width:100%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.2);
  animation:modalIn .25s ease-out}
@keyframes modalIn{from{opacity:0;transform:scale(.85) translateY(20px)}to{opacity:1;transform:none}}
.modal-emoji{font-size:48px;margin-bottom:10px}
.modal-title{font-family:"Nunito";font-size:20px;font-weight:900;color:var(--ink);margin-bottom:8px}
.modal-body{font-size:14px;color:var(--soft);line-height:1.65;margin-bottom:22px}
.modal-date{font-weight:800;color:var(--add)}
.modal-btns{display:flex;gap:10px}
.modal-btn{flex:1;padding:14px 8px;border-radius:16px;border:none;
  font-family:"Nunito";font-size:15px;font-weight:800;cursor:pointer;transition:.15s}
.modal-btn.no{background:#F3F4F6;color:var(--soft)}
.modal-btn.no:hover{background:#E5E7EB}
.modal-btn.yes{background:linear-gradient(135deg,#3B82F6,#2563EB);color:#fff;
  box-shadow:0 4px 16px rgba(59,130,246,.4)}

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

<!-- 更新提示 Modal -->
<div class="modal-overlay" id="updateModal">
  <div class="modal-card">
    <div class="modal-emoji">🆕</div>
    <div class="modal-title">有新題目！</div>
    <div class="modal-body">今天（<span class="modal-date" id="newDateLabel"></span>）的題目已更新，要切換到最新題目嗎？</div>
    <div class="modal-btns">
      <button class="modal-btn no" id="btnNo">先不要</button>
      <button class="modal-btn yes" id="btnYes">✅ 好，換新題！</button>
    </div>
  </div>
</div>

<!-- 送出按鈕 -->
<div class="submit-bar" id="submitBar">
  <button class="submit-btn" onclick="submitAnswers()">
    📝 送出答案
    <span class="sub-count" id="subCount"></span>
  </button>
</div>
<script>
const ALL_DATA=__ALL_DATA_JSON__;
const ALL_DATES=Object.keys(ALL_DATA).sort((a,b)=>b.localeCompare(a));
const CAT_NAMES=["50以內的數","18內加法","18內減法","圖形","100以內的數","錢幣","二位數加減","日曆","時鐘","有多長","應用題","動畫"];
const CAT_CLS={
  "50以內的數":"c0","18內加法":"c1","18內減法":"c2","圖形":"c3",
  "100以內的數":"c4","錢幣":"c5","二位數加減":"c6","日曆":"c7",
  "時鐘":"c8","有多長":"c9","應用題":"c1","動畫":"c_anim"};

function playAnim(qid){
  const box=document.getElementById('anim-'+qid);
  if(!box) return;
  box.classList.remove('playing');
  void box.offsetWidth; // force reflow
  box.classList.add('playing');
}

function animWidget(q){
  if(!q.anim) return '';
  const e=q.anim_emoji||'⭐';
  const e2=q.anim_emoji2||'🌸';
  const n1=q.anim_n1||5, n2=q.anim_n2||0;
  const item=(i,cls='')=>
    `<span class="anim-item ${cls}" style="animation-delay:${(i*0.28).toFixed(2)}s">${e}</span>`;

  // A. 計數型
  if(q.anim==='count'){
    return `<div class="anim-box" id="anim-${q.id}">
      <div class="anim-row">${Array.from({length:n1},(_,i)=>item(i)).join('')}</div>
    </div>`;
  }
  // B. 加法合併型
  if(q.anim==='add'){
    const d2=n1*0.28+0.4;
    const opD=(n1*0.28+0.05).toFixed(2);
    const item2=(i)=>
      `<span class="anim-item" style="animation-delay:${(d2+i*0.28).toFixed(2)}s">${e}</span>`;
    return `<div class="anim-box" id="anim-${q.id}">
      <div class="anim-row">
        <span class="anim-group">${Array.from({length:n1},(_,i)=>item(i)).join('')}</span>
        <span class="anim-op" style="animation-delay:${opD}s">＋</span>
        <span class="anim-group">${Array.from({length:n2},(_,i)=>item2(i)).join('')}</span>
      </div>
    </div>`;
  }
  // C. 減法飛走型
  if(q.anim==='sub'){
    const goneSet=new Set(q.anim_gone_pos||[]);
    const items=Array.from({length:n1},(_,i)=>
      item(i, goneSet.has(i)?'gone':'')).join('');
    const hint=q.q||'灰色的不見了';
    return `<div class="anim-box" id="anim-${q.id}">
      <div class="anim-row">${items}</div>
      <div class="anim-hint">（灰色的${hint.includes('飛')||hint.includes('飄')?'飛走':'不見'}了）</div>
    </div>`;
  }
  // D. 數序型
  if(q.anim==='seq'&&q.anim_seq){
    const nums=q.anim_seq;
    const seqHTML=nums.map((n,i)=>
      `<span class="anim-num ${n==='?'?'blank':''}" style="animation-delay:${(i*0.35).toFixed(2)}s">${n==='?'?'？':n}</span>`
    ).join('');
    return `<div class="anim-box" id="anim-${q.id}">
      <div class="anim-row" style="gap:6px">${seqHTML}</div>
    </div>`;
  }
  // E. 比多少型（兩排）
  if(q.anim==='cmp'){
    const d2=n1*0.22+0.35;
    const row1=Array.from({length:n1},(_,i)=>
      `<span class="anim-item" style="animation-delay:${(i*0.22).toFixed(2)}s">${e}</span>`).join('');
    const row2=Array.from({length:n2},(_,i)=>
      `<span class="anim-item" style="animation-delay:${(d2+i*0.22).toFixed(2)}s">${e2}</span>`).join('');
    return `<div class="anim-box" id="anim-${q.id}">
      <div style="display:flex;flex-direction:column;gap:8px;width:100%">
        <div class="anim-row"><span style="font-size:12px;font-weight:700;color:#6B7280;width:46px;text-align:left;flex-shrink:0">第一排</span>${row1}</div>
        <div class="anim-row"><span style="font-size:12px;font-weight:700;color:#6B7280;width:46px;text-align:left;flex-shrink:0">第二排</span>${row2}</div>
      </div>
    </div>`;
  }
  return '';
}
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
  const sc=document.getElementById("subCount");
  if(sc) sc.textContent=submitted?'':`${done}/${total}`;
}
function clockSVG(hour, minute, qid){
  // 使用 rotate(deg, cx, cy) 支援動畫：12點方向=0°，順時針增加
  const hDeg=(hour%12)*30+minute*0.5;  // 0=12點，順時針
  const mDeg=minute*6;
  const animated=qid!=null;
  const hRot=animated?0:hDeg, mRot=animated?0:mDeg;
  const hId=qid?`id="h-hand-${qid}"`:'';
  const mId=qid?`id="m-hand-${qid}"`:'';
  const cx=100,cy=100,rad=a=>a*Math.PI/180;
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
    <g ${hId} transform="rotate(${hRot},100,100)">
      <line x1="100" y1="100" x2="100" y2="55" stroke="#1F2937" stroke-width="6" stroke-linecap="round"/>
    </g>
    <g ${mId} transform="rotate(${mRot},100,100)">
      <line x1="100" y1="100" x2="100" y2="34" stroke="#3B82F6" stroke-width="3.5" stroke-linecap="round"/>
    </g>
    <circle cx="100" cy="100" r="5" fill="#1F2937"/></svg>`;
}

function animateClock(qid, hDeg, mDeg){
  const hEl=document.getElementById('h-hand-'+qid);
  const mEl=document.getElementById('m-hand-'+qid);
  if(!hEl||!mEl) return;
  // 先歸零到12點
  hEl.setAttribute('transform','rotate(0,100,100)');
  mEl.setAttribute('transform','rotate(0,100,100)');
  const duration=1800;
  const ease=t=>1-Math.pow(1-t,3);
  const start=performance.now();
  function tick(now){
    const t=Math.min((now-start)/duration,1);
    const e=ease(t);
    hEl.setAttribute('transform',`rotate(${(hDeg*e).toFixed(2)},100,100)`);
    mEl.setAttribute('transform',`rotate(${(mDeg*e).toFixed(2)},100,100)`);
    if(t<1) requestAnimationFrame(tick);
  }
  setTimeout(()=>requestAnimationFrame(tick),150);
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
function lengthSVG(a, la, b, lb, unit){
  const EMOJI={
    "鉛筆":"✏️","橡皮擦":"🧽","剪刀":"✂️","書本":"📚",
    "文具盒":"🗃️","繩子":"🪢","緞帶":"🎀","毛線":"🧶",
    "尺":"📏","布條":"🎗️"
  };
  const ea=EMOJI[a]||"📦", eb=EMOJI[b]||"📦";
  const sz=26;
  const lw=62;
  const maxN=Math.max(la,lb);
  const sw=lw+maxN*sz+10;
  const rowH=32; const gap=10;
  const sh=rowH*2+gap+28;
  const em=(x,y,e,n)=>Array.from({length:n},(_,i)=>
    `<text x="${(x+i*sz+sz/2).toFixed(1)}" y="${y}"
      font-size="20" text-anchor="middle">${e}</text>`).join('');
  const ya=28, yb=ya+rowH+gap;
  return `<svg width="${sw}" height="${sh}" viewBox="0 0 ${sw} ${sh}" style="max-width:100%;display:block;margin:0 auto">
    <text x="0" y="${ya}" font-size="13" font-weight="700" fill="#374151" font-family="Noto Sans TC,sans-serif">${a}</text>
    ${em(lw,ya,ea,la)}
    <text x="0" y="${yb}" font-size="13" font-weight="700" fill="#374151" font-family="Noto Sans TC,sans-serif">${b}</text>
    ${em(lw,yb,eb,lb)}
    <text x="${lw}" y="${sh-4}" font-size="11" fill="#9CA3AF" font-family="Noto Sans TC,sans-serif">（單位：${unit}）</text>
  </svg>`;
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
    const isLen=q.cat==="有多長"&&q.q_a!=null;
    const isAnim=q.cat==="動畫"&&q.anim!=null;
    const isWide=q.cat==="圖形"||q.cat==="日曆"||q.cat==="錢幣"||q.cat==="應用題";
    const isCmp=(q.cat==="50以內的數"||q.cat==="100以內的數")&&q.q.includes("○");
    const qClass=isWide?"qtext word":"qtext";
    const optsClass=isCmp?"opts cmp":"opts";
    const optClass="opt";
    const sayText=isClock?"時鐘顯示的是幾點幾分？":q.q_zh||q.q;
    const hDeg_=q.q_hour!=null?(q.q_hour%12)*30+q.q_minute*0.5:0;
    const mDeg_=q.q_minute!=null?q.q_minute*6:0;
    const qDisplay = isAnim
      ? `${animWidget(q)}<div class="qtext" style="text-align:center;margin-top:4px">${q.q}</div>`
      : isClock
      ? `<div class="clock-wrap">${clockSVG(q.q_hour,q.q_minute,q.id)}</div>
         <div style="text-align:center;font-size:13px;color:var(--soft);margin-bottom:8px">時鐘顯示的是幾點幾分？</div>`
      : isLen
      ? `<div style="margin:8px 0 4px;overflow-x:auto;text-align:center">${lengthSVG(q.q_a,q.q_la,q.q_b,q.q_lb,q.q_unit)}</div>
         <div class="qtext word" style="margin-top:6px">${q.q}</div>`
      : `<div class="${qClass}">${q.q}</div>`;
    const opts=q.opts.map((o,j)=>`<button class="${optClass}" id="opt-${q.id}-${j}" onclick="selectOpt(${q.id},${j})">${o}</button>`).join("");
    html+=`
    <div class="qcard" id="qcard-${q.id}">
      <div class="qtop">
        <span class="qnum">第 ${i+1} 題</span>
        <span class="cat-badge ${CAT_CLS[q.cat]||'c0'}">${q.cat}</span>
      </div>
      ${qDisplay}
      ${isAnim
        ? `<button class="play-btn" onclick="playAnim(${q.id});sayQ('${sayText.replace(/'/g,"\\'")}')">▶ 開始動畫 / 聽題目</button>`
        : isClock
        ? `<button class="play-btn" onclick="animateClock(${q.id},${hDeg_.toFixed(1)},${mDeg_.toFixed(1)});sayQ('時鐘顯示的是幾點幾分？')">▶ 開始動畫 / 聽題目</button>`
        : `<button class="say-btn" onclick="sayQ('${sayText.replace(/'/g,"\\'")}')">🔊 聽題目</button>`
      }
      <div class="${optsClass}" id="opts-${q.id}">${opts}</div>
      <div class="feedback" id="fb-${q.id}"></div>
    </div>`;
  });
  feed.innerHTML=html;
  Object.entries(selections).forEach(([qidStr,chosen])=>{
    const qid=parseInt(qidStr);
    const q=qs.find(x=>x.id===qid); if(!q)return;
    const isCorrect=answered[qid];
    q.opts.forEach((o,j)=>{
      const btn=document.getElementById("opt-"+qid+"-"+j);
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
function selectOpt(qid, optIdx){
  if(submitted)return;
  if(selections[qid]!==undefined)return;
  const qs=filteredQs();
  const q=qs.find(x=>x.id===qid); if(!q)return;
  const chosen=String(q.opts[optIdx]);
  selections[qid]=chosen;
  const isCorrect=String(chosen)===String(q.ans);
  answered[qid]=isCorrect;
  q.opts.forEach((o,j)=>{
    const btn=document.getElementById("opt-"+qid+"-"+j);
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
      q.opts.forEach((o,j)=>{const btn=document.getElementById("opt-"+q.id+"-"+j);if(!btn)return;btn.disabled=true;if(String(o)===String(q.ans))btn.classList.add("correct");});
      const fb=document.getElementById("fb-"+q.id);const card=document.getElementById("qcard-"+q.id);
      if(fb){fb.className="feedback ng show";fb.textContent=`⚠️ 未作答。正確答案是 ${q.ans}`;}if(card)card.className="qcard answered-wrong";
    }
  });
  const correct=Object.values(answered).filter(Boolean).length;
  const wrong=qs.length-correct;
  const pct=Math.round(correct/qs.length*100);
  const emoji=pct>=90?"🏆":pct>=70?"🎉":pct>=50?"💪":"📚";
  const msg=pct>=90?"太厲害了！":pct>=70?"做得很好！":pct>=50?"繼續加油！":"再練習看看！";
  const wrongQs=qs.filter(q=>!answered[q.id]).map(q=>({q, chosen:selections[q.id]}));
  let reviewHTML=wrongQs.length?`
    <div class="review-section">
      <div class="review-title">📚 錯題複習（${wrongQs.length} 題）</div>
      ${wrongQs.map(({q,chosen},idx)=>{
        const isWide=q.cat==="圖形"||q.cat==="日曆"||q.cat==="錢幣";
        const qd=`<div class="review-q-text ${isWide?'word':''}">${q.q}</div>`;
        return `<div class="review-card">
          <div class="review-num">${idx+1}. ${q.cat}</div>${qd}
          <div class="review-wrong-row">❌ 你選了：<span class="review-wrong-val">${chosen||'未作答'}</span></div>
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
function checkNewContent(){
  try{
    const KEY='math_seen_v3';
    const seen=new Set(JSON.parse(localStorage.getItem(KEY)||'[]'));
    const isFirst=seen.size===0;
    const newDates=ALL_DATES.filter(d=>!seen.has(d));
    ALL_DATES.forEach(d=>seen.add(d));
    localStorage.setItem(KEY,JSON.stringify([...seen]));
    if(!isFirst&&newDates.length>0){
      const newest=newDates.sort((a,b)=>b.localeCompare(a))[0];
      document.getElementById('newDateLabel').textContent=fmtDate(newest);
      const modal=document.getElementById('updateModal');
      modal.classList.add('show');
      document.getElementById('btnYes').onclick=()=>{modal.classList.remove('show');setDate(newest);};
      document.getElementById('btnNo').onclick=()=>modal.classList.remove('show');
    }
  }catch(e){}
}
setTimeout(checkNewContent,600);
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
