#!/usr/bin/env python3
"""
英文單字日報 — 每天早上 7 點自動生成 30 個商業/科技/財經單字
執行：python3 vocab_scraper.py
不需要任何外部 API，完全離線生成
"""
import json, random, hashlib
from datetime import datetime
from pathlib import Path

OUT_HTML = Path(__file__).parent / "英文單字.html"

# ══════════════════════════════════════════════════════════════
#  單字庫  (240 個，涵蓋會議/商業/科技/財經/生活)
#  每個欄位：word 英文, ipa 音標, phonetic 發音提示, zh 中文意思,
#            category 類別, example 例句, example_zh 例句中文
# ══════════════════════════════════════════════════════════════
WORDS = [
  # ── 會議 Meeting ──────────────────────────────────────────
  {"word":"agenda","ipa":"/əˈdʒɛndə/","phonetic":"uh-JEN-duh","zh":"議程；待辦事項","category":"會議",
   "example":"Please review the agenda before the meeting starts.","example_zh":"請在會議開始前查閱議程。"},
  {"word":"adjourn","ipa":"/əˈdʒɜːrn/","phonetic":"uh-JURN","zh":"散會；休會","category":"會議",
   "example":"The meeting was adjourned until next Monday.","example_zh":"會議休會至下週一。"},
  {"word":"brainstorm","ipa":"/ˈbreɪnstɔːrm/","phonetic":"BRAYN-storm","zh":"腦力激盪；集思廣益","category":"會議",
   "example":"Let's brainstorm ideas for the new product launch.","example_zh":"我們來腦力激盪新產品上市的點子。"},
  {"word":"consensus","ipa":"/kənˈsɛnsəs/","phonetic":"kun-SEN-sus","zh":"共識；一致意見","category":"會議",
   "example":"We need to reach a consensus before moving forward.","example_zh":"我們需要在推進之前達成共識。"},
  {"word":"convene","ipa":"/kənˈviːn/","phonetic":"kun-VEEN","zh":"召開（會議）；集合","category":"會議",
   "example":"The board will convene an emergency meeting tomorrow.","example_zh":"董事會明天將召開緊急會議。"},
  {"word":"debrief","ipa":"/diːˈbriːf/","phonetic":"dee-BREEF","zh":"彙報；事後討論","category":"會議",
   "example":"Let's debrief after the client presentation.","example_zh":"客戶簡報後我們來做個彙報。"},
  {"word":"delegate","ipa":"/ˈdɛlɪɡeɪt/","phonetic":"DEL-uh-gayt","zh":"授權；委派；代表","category":"會議",
   "example":"A good manager knows how to delegate tasks effectively.","example_zh":"好的管理者知道如何有效授權。"},
  {"word":"facilitate","ipa":"/fəˈsɪlɪteɪt/","phonetic":"fuh-SIL-uh-tayt","zh":"促進；主持（會議）","category":"會議",
   "example":"She was asked to facilitate the workshop.","example_zh":"她被要求主持這場工作坊。"},
  {"word":"keynote","ipa":"/ˈkiːnoʊt/","phonetic":"KEE-note","zh":"主題演講","category":"會議",
   "example":"The CEO delivered the keynote at the conference.","example_zh":"執行長在大會發表了主題演講。"},
  {"word":"minutes","ipa":"/ˈmɪnɪts/","phonetic":"MIN-its","zh":"會議記錄","category":"會議",
   "example":"Who will take the minutes during today's meeting?","example_zh":"今天的會議記錄由誰負責？"},
  {"word":"moderator","ipa":"/ˈmɒdəreɪtər/","phonetic":"MOD-uh-ray-ter","zh":"主持人；協調人","category":"會議",
   "example":"The moderator kept the discussion on track.","example_zh":"主持人讓討論保持在正確方向。"},
  {"word":"negotiate","ipa":"/nɪˈɡoʊʃieɪt/","phonetic":"nuh-GO-shee-ayt","zh":"談判；協商","category":"會議",
   "example":"We will negotiate the contract terms next week.","example_zh":"我們下週將協商合約條款。"},
  {"word":"quorum","ipa":"/ˈkwɔːrəm/","phonetic":"KWOR-um","zh":"法定人數","category":"會議",
   "example":"We cannot vote until we have a quorum.","example_zh":"在達到法定人數之前我們無法投票。"},
  {"word":"resolution","ipa":"/ˌrɛzəˈluːʃən/","phonetic":"rez-uh-LOO-shun","zh":"決議；解決方案","category":"會議",
   "example":"The board passed a resolution to expand overseas.","example_zh":"董事會通過了海外擴張的決議。"},
  {"word":"unanimous","ipa":"/juːˈnænɪməs/","phonetic":"yoo-NAN-uh-mus","zh":"全體一致的","category":"會議",
   "example":"The vote was unanimous in favor of the proposal.","example_zh":"投票結果全體一致支持該提案。"},
  {"word":"escalate","ipa":"/ˈɛskəleɪt/","phonetic":"ES-kuh-layt","zh":"升級；呈報上級","category":"會議",
   "example":"Please escalate this issue to your manager immediately.","example_zh":"請立即將此問題呈報給你的主管。"},
  {"word":"milestone","ipa":"/ˈmaɪlstoʊn/","phonetic":"MYLE-stone","zh":"里程碑；重要節點","category":"會議",
   "example":"We hit a major milestone by completing the prototype.","example_zh":"完成原型機是我們達到的重要里程碑。"},
  {"word":"takeaway","ipa":"/ˈteɪkəweɪ/","phonetic":"TAYK-uh-way","zh":"重點結論；收穫","category":"會議",
   "example":"The key takeaway from today's meeting is to focus on quality.","example_zh":"今天會議的重點結論是專注於品質。"},
  {"word":"action item","ipa":"/ˈækʃən ˈaɪtəm/","phonetic":"AK-shun I-tem","zh":"待辦行動項目","category":"會議",
   "example":"Each action item must have an owner and a deadline.","example_zh":"每個待辦事項都必須有負責人和截止日期。"},
  {"word":"follow-up","ipa":"/ˈfɒloʊˌʌp/","phonetic":"FOL-oh-up","zh":"後續跟進；追蹤","category":"會議",
   "example":"I will send a follow-up email after the meeting.","example_zh":"會後我會發送一封跟進郵件。"},

  # ── 商業 Business ─────────────────────────────────────────
  {"word":"acquisition","ipa":"/ˌækwɪˈzɪʃən/","phonetic":"ak-wih-ZIH-shun","zh":"收購；購買","category":"商業",
   "example":"The company announced the acquisition of a startup.","example_zh":"公司宣布收購一家新創公司。"},
  {"word":"benchmark","ipa":"/ˈbɛntʃmɑːrk/","phonetic":"BENCH-mark","zh":"基準；標竿","category":"商業",
   "example":"Our performance is measured against industry benchmarks.","example_zh":"我們的表現以行業基準來衡量。"},
  {"word":"compliance","ipa":"/kəmˈplaɪəns/","phonetic":"kum-PLY-uns","zh":"合規；遵從","category":"商業",
   "example":"All employees must attend the compliance training.","example_zh":"所有員工必須參加合規培訓。"},
  {"word":"deliverable","ipa":"/dɪˈlɪvərəbəl/","phonetic":"duh-LIV-er-uh-bul","zh":"交付成果；交付物","category":"商業",
   "example":"Please list all deliverables in the project plan.","example_zh":"請在專案計畫中列出所有交付成果。"},
  {"word":"equity","ipa":"/ˈɛkwɪti/","phonetic":"EK-wuh-tee","zh":"股權；公平","category":"商業",
   "example":"They offered equity as part of the compensation package.","example_zh":"他們提供股權作為薪酬方案的一部分。"},
  {"word":"franchise","ipa":"/ˈfræntʃaɪz/","phonetic":"FRAN-chyz","zh":"特許經營；加盟","category":"商業",
   "example":"They expanded their business through a franchise model.","example_zh":"他們透過加盟模式擴展業務。"},
  {"word":"leverage","ipa":"/ˈlɛvərɪdʒ/","phonetic":"LEV-er-ij","zh":"槓桿；善用資源","category":"商業",
   "example":"We can leverage our existing network to enter new markets.","example_zh":"我們可以利用現有網絡進入新市場。"},
  {"word":"merger","ipa":"/ˈmɜːrdʒər/","phonetic":"MUR-jer","zh":"合併","category":"商業",
   "example":"The merger created the largest company in the sector.","example_zh":"這次合併創造了該行業最大的公司。"},
  {"word":"overhead","ipa":"/ˈoʊvərˌhɛd/","phonetic":"OH-ver-hed","zh":"管銷費用；間接成本","category":"商業",
   "example":"Reducing overhead costs is essential for profitability.","example_zh":"降低管銷費用對盈利能力至關重要。"},
  {"word":"procurement","ipa":"/prəˈkjʊərmənt/","phonetic":"pruh-KYOOR-ment","zh":"採購","category":"商業",
   "example":"The procurement team negotiated better prices with suppliers.","example_zh":"採購團隊與供應商談判了更好的價格。"},
  {"word":"revenue","ipa":"/ˈrɛvɪnjuː/","phonetic":"REV-uh-nyoo","zh":"收益；營業額","category":"商業",
   "example":"Annual revenue grew by 15% compared to last year.","example_zh":"年收益比去年增長了15%。"},
  {"word":"subsidiary","ipa":"/səbˈsɪdiɛri/","phonetic":"sub-SID-ee-air-ee","zh":"子公司","category":"商業",
   "example":"The subsidiary operates independently in the Asian market.","example_zh":"該子公司在亞洲市場獨立運營。"},
  {"word":"synergy","ipa":"/ˈsɪnərdʒi/","phonetic":"SIN-er-jee","zh":"協同效應","category":"商業",
   "example":"The merger created significant synergy between the two teams.","example_zh":"合併在兩個團隊之間創造了顯著的協同效應。"},
  {"word":"turnover","ipa":"/ˈtɜːrnoʊvər/","phonetic":"TURN-oh-ver","zh":"營業額；人員流動率","category":"商業",
   "example":"High employee turnover increases recruitment costs.","example_zh":"高員工流動率增加了招募成本。"},
  {"word":"incentive","ipa":"/ɪnˈsɛntɪv/","phonetic":"in-SEN-tiv","zh":"激勵；獎勵","category":"商業",
   "example":"Performance bonuses are a great incentive for employees.","example_zh":"績效獎金是員工的絕佳激勵。"},
  {"word":"outsource","ipa":"/ˈaʊtsɔːrs/","phonetic":"OWT-sors","zh":"外包","category":"商業",
   "example":"Many companies outsource IT support to reduce costs.","example_zh":"許多公司將IT支援外包以降低成本。"},
  {"word":"scalable","ipa":"/ˈskeɪləbəl/","phonetic":"SKAY-luh-bul","zh":"可擴展的；可規模化的","category":"商業",
   "example":"We need a scalable solution for our growing customer base.","example_zh":"我們需要一個可擴展的方案來應對不斷增長的客戶群。"},
  {"word":"stakeholder","ipa":"/ˈsteɪkhoʊldər/","phonetic":"STAYK-hol-der","zh":"利害關係人","category":"商業",
   "example":"All stakeholders must approve the project before launch.","example_zh":"所有利害關係人必須在啟動前批准該專案。"},
  {"word":"supply chain","ipa":"/ˈsʌplaɪ tʃeɪn/","phonetic":"SUP-ly CHAYN","zh":"供應鏈","category":"商業",
   "example":"The pandemic disrupted global supply chains significantly.","example_zh":"疫情嚴重擾亂了全球供應鏈。"},
  {"word":"venture","ipa":"/ˈvɛntʃər/","phonetic":"VEN-cher","zh":"冒險；合資企業","category":"商業",
   "example":"They launched a joint venture with a European partner.","example_zh":"他們與一家歐洲合作夥伴成立了合資企業。"},

  # ── 科技 Technology ────────────────────────────────────────
  {"word":"algorithm","ipa":"/ˈælɡərɪðəm/","phonetic":"AL-guh-rith-um","zh":"演算法","category":"科技",
   "example":"The algorithm recommends products based on your history.","example_zh":"演算法根據您的歷史記錄推薦產品。"},
  {"word":"automation","ipa":"/ˌɔːtəˈmeɪʃən/","phonetic":"aw-tuh-MAY-shun","zh":"自動化","category":"科技",
   "example":"Automation has transformed manufacturing processes worldwide.","example_zh":"自動化改變了全球的製造流程。"},
  {"word":"bandwidth","ipa":"/ˈbændwɪdθ/","phonetic":"BAND-width","zh":"頻寬；處理能力","category":"科技",
   "example":"We need more bandwidth to support video conferencing.","example_zh":"我們需要更多頻寬來支援視訊會議。"},
  {"word":"blockchain","ipa":"/ˈblɒktʃeɪn/","phonetic":"BLOK-chayn","zh":"區塊鏈","category":"科技",
   "example":"Blockchain technology ensures transparent and secure transactions.","example_zh":"區塊鏈技術確保交易透明且安全。"},
  {"word":"cybersecurity","ipa":"/ˌsaɪbərsɪˈkjʊərɪti/","phonetic":"SY-ber-sih-KYOOR-uh-tee","zh":"網路安全","category":"科技",
   "example":"Investing in cybersecurity is critical for every business.","example_zh":"投資網路安全對每個企業都至關重要。"},
  {"word":"encryption","ipa":"/ɪnˈkrɪpʃən/","phonetic":"in-KRIP-shun","zh":"加密","category":"科技",
   "example":"End-to-end encryption protects your private messages.","example_zh":"端對端加密保護您的私人訊息。"},
  {"word":"infrastructure","ipa":"/ˈɪnfrəˌstrʌktʃər/","phonetic":"IN-fruh-struk-cher","zh":"基礎設施；架構","category":"科技",
   "example":"Cloud infrastructure reduces the need for physical servers.","example_zh":"雲端基礎設施減少了對實體伺服器的需求。"},
  {"word":"integration","ipa":"/ˌɪntɪˈɡreɪʃən/","phonetic":"in-tuh-GRAY-shun","zh":"整合；集成","category":"科技",
   "example":"Seamless integration between apps improves user experience.","example_zh":"應用程式之間的無縫整合改善了用戶體驗。"},
  {"word":"iteration","ipa":"/ˌɪtəˈreɪʃən/","phonetic":"it-uh-RAY-shun","zh":"迭代；反覆修改","category":"科技",
   "example":"Each iteration of the product improves based on feedback.","example_zh":"產品的每次迭代都根據回饋進行改進。"},
  {"word":"latency","ipa":"/ˈleɪtənsi/","phonetic":"LAY-ten-see","zh":"延遲時間","category":"科技",
   "example":"Low latency is essential for real-time gaming applications.","example_zh":"低延遲對於即時遊戲應用至關重要。"},
  {"word":"machine learning","ipa":"/məˈʃiːn ˈlɜːrnɪŋ/","phonetic":"muh-SHEEN LUR-ning","zh":"機器學習","category":"科技",
   "example":"Machine learning enables computers to learn from data.","example_zh":"機器學習使電腦能夠從資料中學習。"},
  {"word":"optimization","ipa":"/ˌɒptɪmaɪˈzeɪʃən/","phonetic":"op-tuh-my-ZAY-shun","zh":"優化","category":"科技",
   "example":"Search engine optimization improves your website ranking.","example_zh":"搜尋引擎優化提升您的網站排名。"},
  {"word":"prototype","ipa":"/ˈproʊtətaɪp/","phonetic":"PRO-tuh-typ","zh":"原型；雛形","category":"科技",
   "example":"We built a prototype to test the concept with users.","example_zh":"我們建立了原型來與用戶測試概念。"},
  {"word":"repository","ipa":"/rɪˈpɒzɪtɔːri/","phonetic":"ruh-POZ-uh-tor-ee","zh":"程式庫；儲存庫","category":"科技",
   "example":"All code is stored in the GitHub repository.","example_zh":"所有程式碼都儲存在GitHub儲存庫中。"},
  {"word":"virtualization","ipa":"/ˌvɜːrtʃuəlaɪˈzeɪʃən/","phonetic":"vur-choo-uh-ly-ZAY-shun","zh":"虛擬化","category":"科技",
   "example":"Server virtualization reduces hardware costs significantly.","example_zh":"伺服器虛擬化大幅降低了硬體成本。"},
  {"word":"agile","ipa":"/ˈædʒaɪl/","phonetic":"AJ-ul","zh":"敏捷的；靈活的（開發方法）","category":"科技",
   "example":"The team uses agile methodology for software development.","example_zh":"團隊使用敏捷方法論進行軟體開發。"},
  {"word":"deployment","ipa":"/dɪˈplɔɪmənt/","phonetic":"duh-PLOY-ment","zh":"部署；發布","category":"科技",
   "example":"The deployment of the new system was completed overnight.","example_zh":"新系統的部署在一夜之間完成。"},
  {"word":"debugging","ipa":"/diːˈbʌɡɪŋ/","phonetic":"dee-BUG-ing","zh":"除錯；找出並修復錯誤","category":"科技",
   "example":"Debugging the code took longer than expected.","example_zh":"程式碼除錯花的時間比預期要長。"},
  {"word":"firewall","ipa":"/ˈfaɪərwɔːl/","phonetic":"FY-er-wall","zh":"防火牆","category":"科技",
   "example":"The firewall blocked the unauthorized access attempt.","example_zh":"防火牆阻擋了未授權的存取嘗試。"},
  {"word":"user experience","ipa":"/ˈjuːzər ɪkˈspɪriəns/","phonetic":"YOO-zer ik-SPEER-ee-uns","zh":"用戶體驗（UX）","category":"科技",
   "example":"A great user experience keeps customers coming back.","example_zh":"出色的用戶體驗讓客戶持續回訪。"},

  # ── 財經 Finance ───────────────────────────────────────────
  {"word":"amortization","ipa":"/əˌmɔːrtɪˈzeɪʃən/","phonetic":"uh-mor-tuh-ZAY-shun","zh":"攤銷；分期償還","category":"財經",
   "example":"The loan amortization schedule shows monthly payments.","example_zh":"貸款攤銷時間表顯示每月還款金額。"},
  {"word":"arbitrage","ipa":"/ˈɑːrbɪtrɑːʒ/","phonetic":"AR-buh-trazh","zh":"套利；仲裁","category":"財經",
   "example":"Traders use arbitrage to profit from price differences.","example_zh":"交易員利用套利從價格差異中獲利。"},
  {"word":"bear market","ipa":"/ˈbɛr ˈmɑːrkɪt/","phonetic":"BAIR MAR-kit","zh":"熊市（股市下跌）","category":"財經",
   "example":"Investors are cautious during a bear market.","example_zh":"在熊市期間投資者會保持謹慎。"},
  {"word":"bull market","ipa":"/ˈbʊl ˈmɑːrkɪt/","phonetic":"BOOL MAR-kit","zh":"牛市（股市上漲）","category":"財經",
   "example":"The tech sector thrived during the bull market.","example_zh":"科技板塊在牛市期間蓬勃發展。"},
  {"word":"cash flow","ipa":"/ˈkæʃ floʊ/","phonetic":"KASH floh","zh":"現金流","category":"財經",
   "example":"Positive cash flow is vital for business survival.","example_zh":"正向現金流對企業生存至關重要。"},
  {"word":"depreciation","ipa":"/dɪˌpriːʃɪˈeɪʃən/","phonetic":"duh-pree-shee-AY-shun","zh":"折舊；貶值","category":"財經",
   "example":"Equipment depreciation reduces taxable income.","example_zh":"設備折舊可減少應稅收入。"},
  {"word":"diversification","ipa":"/daɪˌvɜːrsɪfɪˈkeɪʃən/","phonetic":"dy-vur-suh-fuh-KAY-shun","zh":"多元化；分散投資","category":"財經",
   "example":"Portfolio diversification reduces investment risk.","example_zh":"投資組合多元化可降低投資風險。"},
  {"word":"dividend","ipa":"/ˈdɪvɪdɛnd/","phonetic":"DIV-uh-dend","zh":"股息；紅利","category":"財經",
   "example":"The company paid a dividend of two dollars per share.","example_zh":"公司支付了每股兩美元的股息。"},
  {"word":"fiscal","ipa":"/ˈfɪskəl/","phonetic":"FIS-kul","zh":"財政的；會計年度的","category":"財經",
   "example":"The fiscal year ends on December 31st.","example_zh":"財政年度於12月31日結束。"},
  {"word":"hedge fund","ipa":"/ˈhɛdʒ fʌnd/","phonetic":"HEJ fund","zh":"對沖基金","category":"財經",
   "example":"Hedge funds often use complex strategies to generate returns.","example_zh":"對沖基金常使用複雜策略來產生回報。"},
  {"word":"inflation","ipa":"/ɪnˈfleɪʃən/","phonetic":"in-FLAY-shun","zh":"通貨膨脹","category":"財經",
   "example":"Rising inflation erodes purchasing power over time.","example_zh":"通貨膨脹上升會隨時間侵蝕購買力。"},
  {"word":"liquidity","ipa":"/lɪˈkwɪdɪti/","phonetic":"luh-KWID-uh-tee","zh":"流動性；變現能力","category":"財經",
   "example":"High liquidity means assets can be quickly converted to cash.","example_zh":"高流動性意味著資產可以快速轉換為現金。"},
  {"word":"portfolio","ipa":"/pɔːrtˈfoʊlioʊ/","phonetic":"port-FOH-lee-oh","zh":"投資組合；作品集","category":"財經",
   "example":"A balanced portfolio includes stocks, bonds, and real estate.","example_zh":"均衡的投資組合包括股票、債券和房地產。"},
  {"word":"return on investment","ipa":"/rɪˈtɜːrn ɒn ɪnˈvɛstmənt/","phonetic":"ruh-TURN on in-VEST-ment","zh":"投資報酬率（ROI）","category":"財經",
   "example":"This marketing campaign had an excellent return on investment.","example_zh":"這次行銷活動有出色的投資報酬率。"},
  {"word":"securities","ipa":"/sɪˈkjʊərɪtiz/","phonetic":"suh-KYOOR-uh-teez","zh":"有價證券","category":"財經",
   "example":"Government securities are considered low-risk investments.","example_zh":"政府有價證券被視為低風險投資。"},
  {"word":"valuation","ipa":"/ˌvæljuˈeɪʃən/","phonetic":"val-yoo-AY-shun","zh":"估值；評估","category":"財經",
   "example":"The startup received a valuation of one billion dollars.","example_zh":"這家新創公司的估值達到了十億美元。"},
  {"word":"venture capital","ipa":"/ˈvɛntʃər ˈkæpɪtəl/","phonetic":"VEN-cher KAP-uh-tul","zh":"創投資金","category":"財經",
   "example":"Venture capital funds early-stage innovative companies.","example_zh":"創投資金資助早期創新公司。"},
  {"word":"yield","ipa":"/jiːld/","phonetic":"YEELD","zh":"收益率；產生","category":"財經",
   "example":"The bond yield increased to 4.5% this quarter.","example_zh":"本季債券收益率上升至4.5%。"},
  {"word":"balance sheet","ipa":"/ˈbæləns ʃiːt/","phonetic":"BAL-uns sheet","zh":"資產負債表","category":"財經",
   "example":"The balance sheet shows the company's financial position.","example_zh":"資產負債表顯示公司的財務狀況。"},
  {"word":"audit","ipa":"/ˈɔːdɪt/","phonetic":"AW-dit","zh":"審計；查帳","category":"財經",
   "example":"An external auditor conducts the annual financial audit.","example_zh":"外部審計師進行年度財務審計。"},

  # ── 生活職場 Daily Life / Soft Skills ──────────────────────
  {"word":"proactive","ipa":"/proʊˈæktɪv/","phonetic":"pro-AK-tiv","zh":"主動積極的","category":"生活",
   "example":"Being proactive helps you solve problems before they arise.","example_zh":"積極主動幫助你在問題發生前解決它。"},
  {"word":"transparent","ipa":"/trænsˈpærənt/","phonetic":"trans-PAIR-unt","zh":"透明的；坦誠的","category":"生活",
   "example":"Leaders should be transparent about company challenges.","example_zh":"領導者應該對公司挑戰保持透明。"},
  {"word":"resilient","ipa":"/rɪˈzɪliənt/","phonetic":"ruh-ZIL-ee-unt","zh":"有韌性的；恢復力強的","category":"生活",
   "example":"Resilient employees adapt quickly to change.","example_zh":"有韌性的員工能快速適應變化。"},
  {"word":"empathy","ipa":"/ˈɛmpəθi/","phonetic":"EM-puh-thee","zh":"同理心；設身處地","category":"生活",
   "example":"Empathy is a key skill for effective leadership.","example_zh":"同理心是有效領導的關鍵技能。"},
  {"word":"accountability","ipa":"/əˌkaʊntəˈbɪlɪti/","phonetic":"uh-kown-tuh-BIL-uh-tee","zh":"責任感；問責","category":"生活",
   "example":"Accountability means taking responsibility for your actions.","example_zh":"問責意味著為自己的行動承擔責任。"},
  {"word":"assertive","ipa":"/əˈsɜːrtɪv/","phonetic":"uh-SUR-tiv","zh":"果斷的；自信表達的","category":"生活",
   "example":"Being assertive helps you communicate your needs clearly.","example_zh":"果斷有助於你清楚地溝通自己的需求。"},
  {"word":"constructive","ipa":"/kənˈstrʌktɪv/","phonetic":"kun-STRUK-tiv","zh":"建設性的","category":"生活",
   "example":"Please provide constructive feedback on the report.","example_zh":"請對報告提供建設性的回饋。"},
  {"word":"adaptable","ipa":"/əˈdæptəbəl/","phonetic":"uh-DAP-tuh-bul","zh":"適應力強的；靈活的","category":"生活",
   "example":"Adaptable employees are valuable in a changing environment.","example_zh":"適應力強的員工在變化的環境中非常寶貴。"},
  {"word":"collaborate","ipa":"/kəˈlæbəreɪt/","phonetic":"kuh-LAB-uh-rayt","zh":"合作；協作","category":"生活",
   "example":"Teams that collaborate effectively achieve better results.","example_zh":"有效合作的團隊能取得更好的成果。"},
  {"word":"integrity","ipa":"/ɪnˈtɛɡrɪti/","phonetic":"in-TEG-ruh-tee","zh":"正直；誠信","category":"生活",
   "example":"Integrity is the foundation of a trustworthy business.","example_zh":"誠信是值得信賴企業的基礎。"},
  {"word":"initiative","ipa":"/ɪˈnɪʃɪətɪv/","phonetic":"ih-NISH-ee-uh-tiv","zh":"主動性；倡議","category":"生活",
   "example":"Take the initiative and suggest solutions to your manager.","example_zh":"主動出擊，向你的主管提出解決方案。"},
  {"word":"mentor","ipa":"/ˈmɛntɔːr/","phonetic":"MEN-tor","zh":"導師；指導者","category":"生活",
   "example":"Having a mentor can accelerate your career growth.","example_zh":"有一位導師可以加速你的職業發展。"},
  {"word":"networking","ipa":"/ˈnɛtwɜːrkɪŋ/","phonetic":"NET-wur-king","zh":"人脈建立；社交","category":"生活",
   "example":"Networking events are great for meeting industry peers.","example_zh":"社交活動非常適合結識行業同仁。"},
  {"word":"multitask","ipa":"/ˈmʌltiˌtæsk/","phonetic":"MUL-tee-task","zh":"同時處理多項工作","category":"生活",
   "example":"Effective professionals know how to multitask efficiently.","example_zh":"高效的專業人士知道如何高效地同時處理多項工作。"},
  {"word":"punctual","ipa":"/ˈpʌŋktʃuəl/","phonetic":"PUNK-choo-ul","zh":"準時的","category":"生活",
   "example":"Being punctual shows respect for others' time.","example_zh":"準時表現了對他人時間的尊重。"},
  {"word":"streamline","ipa":"/ˈstriːmlaɪn/","phonetic":"STREAM-lyn","zh":"簡化流程；精簡","category":"生活",
   "example":"We need to streamline the approval process.","example_zh":"我們需要簡化審批流程。"},
  {"word":"sustainable","ipa":"/səˈsteɪnəbəl/","phonetic":"suh-STAY-nuh-bul","zh":"可持續的；永續的","category":"生活",
   "example":"The company is committed to sustainable business practices.","example_zh":"公司致力於可持續的商業實踐。"},
  {"word":"versatile","ipa":"/ˈvɜːrsətaɪl/","phonetic":"VUR-suh-tyl","zh":"多才多藝的；多功能的","category":"生活",
   "example":"A versatile employee can handle a variety of tasks.","example_zh":"多才多藝的員工可以處理各種任務。"},
  {"word":"deadline","ipa":"/ˈdɛdlaɪn/","phonetic":"DED-lyn","zh":"截止日期","category":"生活",
   "example":"Always submit your work before the deadline.","example_zh":"始終在截止日期前提交你的工作。"},
  {"word":"feedback","ipa":"/ˈfiːdbæk/","phonetic":"FEED-bak","zh":"回饋；意見","category":"生活",
   "example":"Regular feedback helps employees grow and improve.","example_zh":"定期回饋有助於員工成長和進步。"},
]

# ══════════════════════════════════════════════════════════════
#  文法庫（商務英文核心文法 60 點）
# ══════════════════════════════════════════════════════════════
GRAMMAR = [
  # ── 情態動詞 Modal Verbs ───────────────────────────────────
  {"title":"Could — 委婉請求與可能性","category":"情態動詞",
   "rule":"比 can 更禮貌；用於請求、建議、可能性。商務場合常用。",
   "pattern":"Could you [動詞原形]... ?  /  We could [動詞原形]...",
   "examples":[
     {"en":"Could you send me the report by Friday?","zh":"您能在週五前把報告發給我嗎？"},
     {"en":"We could schedule a follow-up meeting next week.","zh":"我們可以安排下週的後續會議。"},
     {"en":"Could you elaborate on that point?","zh":"您能詳細說明那個觀點嗎？"},
   ],"wrong":"Can you elaborate that point?","right":"Could you elaborate on that point?",
   "tip":"在正式會議中用 could 比 can 更有禮貌，也更專業。"},

  {"title":"Would — 條件與禮貌表達","category":"情態動詞",
   "rule":"表示假設、禮貌請求、過去習慣。商務中常用於提案與回應。",
   "pattern":"I would [動詞]... / Would you like to...?",
   "examples":[
     {"en":"I would suggest moving the deadline to next Friday.","zh":"我建議將截止日期移到下週五。"},
     {"en":"Would you like to review the contract together?","zh":"您願意一起審閱合約嗎？"},
     {"en":"That would be a great opportunity for both companies.","zh":"這對兩家公司來說都是一個很好的機會。"},
   ],"wrong":"I will suggest to move the deadline.","right":"I would suggest moving the deadline.",
   "tip":"I would suggest + V-ing，不是 to V。"},

  {"title":"Should — 建議與責任","category":"情態動詞",
   "rule":"表示應該做某事（建議、義務）。比 must 柔和，比 could 更明確。",
   "pattern":"We should [動詞原形] / You should consider [V-ing]",
   "examples":[
     {"en":"We should review the budget before the Q3 planning.","zh":"我們應該在Q3規劃前審查預算。"},
     {"en":"You should consider the risks before making a decision.","zh":"您應該在做決定前考慮風險。"},
     {"en":"This issue should be escalated to management.","zh":"這個問題應該呈報給管理層。"},
   ],"wrong":"We should to review the budget.","right":"We should review the budget.",
   "tip":"情態動詞後面直接接動詞原形，不加 to。"},

  {"title":"Might — 不確定的可能性","category":"情態動詞",
   "rule":"表示不太確定的可能性（比 may 更不確定）。會議中表達不確定時使用。",
   "pattern":"We might [動詞] / This might [動詞]",
   "examples":[
     {"en":"We might need to revise our projections for Q4.","zh":"我們可能需要修訂Q4的預測。"},
     {"en":"This might affect our timeline significantly.","zh":"這可能會顯著影響我們的時間表。"},
     {"en":"The client might request additional changes.","zh":"客戶可能會要求額外的修改。"},
   ],"wrong":"We might to revise our projections.","right":"We might need to revise our projections.",
   "tip":"might 後面也是動詞原形，不加 to。"},

  {"title":"Must vs. Have to — 強制與義務","category":"情態動詞",
   "rule":"must = 說話者認為必須（主觀）；have to = 外部規定必須（客觀）。",
   "pattern":"We must [動詞] / We have to [動詞]",
   "examples":[
     {"en":"We must deliver this project on time — it's non-negotiable.","zh":"我們必須準時交付這個專案——這是不可協商的。"},
     {"en":"All employees have to complete the compliance training.","zh":"所有員工都必須完成合規培訓。"},
     {"en":"You must not share confidential information externally.","zh":"您絕對不能對外分享機密信息。"},
   ],"wrong":"We must to deliver this project on time.","right":"We must deliver this project on time.",
   "tip":"must 和 have to 後面都接動詞原形，不加 to。"},

  # ── 條件句 Conditionals ────────────────────────────────────
  {"title":"第一條件句 — 可能發生的情況","category":"條件句",
   "rule":"If + 現在式, will/can + 動詞原形。用於討論可能發生的結果。",
   "pattern":"If we [現在式動詞], we will [動詞原形].",
   "examples":[
     {"en":"If we close this deal, we will exceed our quarterly target.","zh":"如果我們完成這筆交易，我們將超過季度目標。"},
     {"en":"If the budget is approved, we can start next month.","zh":"如果預算獲批，我們可以下個月開始。"},
     {"en":"If you have any concerns, please raise them now.","zh":"如果您有任何顧慮，請現在提出。"},
   ],"wrong":"If we will close this deal, we will exceed our target.","right":"If we close this deal, we will exceed our target.",
   "tip":"if 子句用現在式，不用 will（這是最常見的錯誤！）"},

  {"title":"第二條件句 — 假設情況","category":"條件句",
   "rule":"If + 過去式, would + 動詞原形。用於假設或不太可能的情況。",
   "pattern":"If we [過去式], we would [動詞原形].",
   "examples":[
     {"en":"If we had more resources, we would launch the product sooner.","zh":"如果我們有更多資源，我們會更早推出產品。"},
     {"en":"If I were in your position, I would negotiate the terms.","zh":"如果我在您的立場，我會談判條款。"},
     {"en":"If we reduced headcount, it would impact productivity.","zh":"如果我們裁員，將會影響生產力。"},
   ],"wrong":"If we would have more resources, we would launch sooner.","right":"If we had more resources, we would launch sooner.",
   "tip":"if 子句用過去式（be 動詞用 were，不用 was），主句用 would。"},

  # ── 被動語態 Passive Voice ─────────────────────────────────
  {"title":"被動語態 — 商務報告常用","category":"被動語態",
   "rule":"be + 過去分詞。強調動作的對象而非執行者，商務書信和報告很常見。",
   "pattern":"[主詞] + is/was/will be + [過去分詞] (+ by [執行者])",
   "examples":[
     {"en":"The proposal was approved by the board last week.","zh":"提案上週獲得董事會批准。"},
     {"en":"The meeting has been rescheduled to Thursday.","zh":"會議已改期至週四。"},
     {"en":"All contracts must be reviewed by the legal team.","zh":"所有合約必須由法務團隊審查。"},
   ],"wrong":"The proposal was approve by the board.","right":"The proposal was approved by the board.",
   "tip":"被動語態一定是 be + 過去分詞（approved、reviewed 等）。"},

  # ── 連接詞與轉折 Connectors ────────────────────────────────
  {"title":"表示對比：However / Although","category":"連接詞",
   "rule":"However 放句首加逗號；Although 放在子句前面。表示轉折或對比。",
   "pattern":"However, [句子]. / Although [子句], [主句].",
   "examples":[
     {"en":"The project is on schedule. However, the budget is running low.","zh":"專案進展順利。然而，預算正在減少。"},
     {"en":"Although the market is challenging, we remain optimistic.","zh":"雖然市場充滿挑戰，我們仍然保持樂觀。"},
     {"en":"The results are promising. However, we need more data.","zh":"結果很有希望。然而，我們需要更多數據。"},
   ],"wrong":"However the project is on schedule, the budget is low.","right":"The project is on schedule. However, the budget is running low.",
   "tip":"However 是副詞，後面加逗號，不能像 although 一樣連接兩個子句。"},

  {"title":"表示原因：Because / Due to","category":"連接詞",
   "rule":"Because 後接完整子句；due to 後接名詞或名詞片語。",
   "pattern":"Because [子句] / Due to [名詞片語]",
   "examples":[
     {"en":"We postponed the launch because the product needed more testing.","zh":"我們推遲了發布，因為產品需要更多測試。"},
     {"en":"Due to budget constraints, we cannot proceed with the original plan.","zh":"由於預算限制，我們無法繼續原計畫。"},
     {"en":"Sales declined because of the global economic slowdown.","zh":"由於全球經濟放緩，銷售額下降。"},
   ],"wrong":"Due to we don't have enough budget, we cannot proceed.","right":"Due to budget constraints, we cannot proceed.",
   "tip":"due to 後面接名詞，不接子句！要接子句就用 because。"},

  {"title":"表示結果：Therefore / As a result","category":"連接詞",
   "rule":"兩者都表示因此、所以，放在結果句的句首或句中。",
   "pattern":"Therefore, [結果句]. / As a result, [結果句].",
   "examples":[
     {"en":"Sales exceeded expectations. Therefore, we will expand the team.","zh":"銷售超出預期。因此，我們將擴充團隊。"},
     {"en":"The supplier delayed delivery. As a result, production was affected.","zh":"供應商延誤交貨。結果，生產受到影響。"},
     {"en":"The market shifted rapidly; therefore, we had to adapt our strategy.","zh":"市場迅速變化；因此，我們不得不調整策略。"},
   ],"wrong":"Therefore we will expand the team.","right":"Therefore, we will expand the team.",
   "tip":"Therefore 和 As a result 後面要加逗號。"},

  {"title":"表示補充：In addition / Furthermore","category":"連接詞",
   "rule":"表示「另外、此外」，用來補充前面說的內容，使論點更強。",
   "pattern":"In addition, [補充內容]. / Furthermore, [更進一步的內容].",
   "examples":[
     {"en":"The new system reduces costs. In addition, it improves efficiency.","zh":"新系統降低了成本。此外，它還提高了效率。"},
     {"en":"We need to improve quality. Furthermore, we must reduce delivery time.","zh":"我們需要提高品質。而且，我們還必須縮短交貨時間。"},
     {"en":"The candidate has relevant experience. In addition, she speaks three languages.","zh":"該候選人有相關經驗。此外，她會說三種語言。"},
   ],"wrong":"In addition we need to improve quality.","right":"In addition, we need to improve quality.",
   "tip":"In addition 和 Furthermore 後面一定要加逗號。"},

  # ── 表達意見 Expressing Opinions ──────────────────────────
  {"title":"表達意見：In my opinion / I believe","category":"表達意見",
   "rule":"提出個人看法時使用，讓對方知道這是你的觀點，不是事實。",
   "pattern":"In my opinion, [觀點]. / I believe [that] [觀點].",
   "examples":[
     {"en":"In my opinion, we should prioritize customer satisfaction over cost-cutting.","zh":"在我看來，我們應該把客戶滿意度放在降低成本之上。"},
     {"en":"I believe this partnership will benefit both companies significantly.","zh":"我相信這次合作將對兩家公司都大有裨益。"},
     {"en":"In my view, the timeline is too aggressive.","zh":"在我看來，這個時間表太緊迫了。"},
   ],"wrong":"In my opinion is that we should prioritize customers.","right":"In my opinion, we should prioritize customers.",
   "tip":"In my opinion 後面直接接句子，不加 is that。"},

  {"title":"委婉不同意：I understand, however...","category":"表達意見",
   "rule":"先認可對方觀點，再提出不同意見。這是商務英文中非常重要的禮貌技巧。",
   "pattern":"I understand your point, however [你的觀點]. / I see what you mean, but [補充].",
   "examples":[
     {"en":"I understand your concern, however, the data supports a different approach.","zh":"我理解您的顧慮，然而，數據支持不同的方法。"},
     {"en":"I see what you mean, but I think we should consider the long-term impact.","zh":"我明白您的意思，但我認為我們應該考慮長期影響。"},
     {"en":"That's a valid point. However, we also need to consider the budget constraints.","zh":"這是一個有效的觀點。然而，我們還需要考慮預算限制。"},
   ],"wrong":"I don't agree. The data is different.","right":"I understand your point, however, the data suggests a different approach.",
   "tip":"直接說「I don't agree」在商務場合太強硬，先認可再反駁更專業。"},

  {"title":"提出建議：I suggest / I recommend","category":"表達意見",
   "rule":"正式提出建議的句型。suggest/recommend 後面接 V-ing 或 that 子句。",
   "pattern":"I suggest [V-ing] / I recommend [V-ing] / I suggest that we [動詞原形]",
   "examples":[
     {"en":"I suggest scheduling a follow-up meeting next week.","zh":"我建議安排下週的後續會議。"},
     {"en":"I recommend reviewing the contract before signing.","zh":"我建議在簽署前審查合約。"},
     {"en":"I suggest that we postpone the launch until Q2.","zh":"我建議我們將發布推遲到第二季。"},
   ],"wrong":"I suggest to schedule a follow-up meeting.","right":"I suggest scheduling a follow-up meeting.",
   "tip":"suggest 後面接 V-ing，不接 to V！（recommend 也一樣）"},

  # ── 澄清與確認 Clarification ───────────────────────────────
  {"title":"請求澄清：Could you clarify...","category":"澄清確認",
   "rule":"聽不懂或需要更多說明時，禮貌請求對方澄清的句型。",
   "pattern":"Could you clarify [what/how/why]...? / Could you elaborate on...?",
   "examples":[
     {"en":"Could you clarify what you mean by 'revised timeline'?","zh":"您能澄清「修訂後的時間表」是什麼意思嗎？"},
     {"en":"Could you elaborate on the proposed budget allocation?","zh":"您能詳細說明提議的預算分配嗎？"},
     {"en":"I'm not quite sure I understand. Could you give an example?","zh":"我不太確定我理解了。您能舉個例子嗎？"},
   ],"wrong":"What you mean?","right":"Could you clarify what you mean?",
   "tip":"直接問 'What you mean?' 不夠禮貌，加 Could you 讓語氣更委婉。"},

  {"title":"確認理解：If I understand correctly...","category":"澄清確認",
   "rule":"重述對方的意思以確認自己理解正確，商務溝通中避免誤解的關鍵技巧。",
   "pattern":"If I understand correctly, [重述]. / So what you're saying is [重述]?",
   "examples":[
     {"en":"If I understand correctly, you want to delay the project by two weeks?","zh":"如果我理解正確，您想將專案延遲兩週？"},
     {"en":"So what you're saying is that the budget needs to be approved first?","zh":"所以您的意思是預算需要先獲得批准？"},
     {"en":"Let me confirm — you need the report by Monday morning, correct?","zh":"讓我確認一下——您需要在週一早上前收到報告，對嗎？"},
   ],"wrong":"You mean delay two weeks?","right":"If I understand correctly, you want to delay the project by two weeks?",
   "tip":"用完整句型重述，讓對方確認，可以避免很多誤解。"},

  # ── 時態 Tenses ────────────────────────────────────────────
  {"title":"現在完成式 — 與現在相關的過去","category":"時態",
   "rule":"Have/has + 過去分詞。強調過去的動作對現在的影響，不說明具體時間。",
   "pattern":"We have [過去分詞] / The team has [過去分詞]",
   "examples":[
     {"en":"We have completed the initial review of the proposal.","zh":"我們已完成提案的初步審查。"},
     {"en":"The team has made significant progress this quarter.","zh":"本季度團隊取得了重大進展。"},
     {"en":"I have already sent the contract to the client.","zh":"我已經將合約發給客戶了。"},
   ],"wrong":"We already complete the review.","right":"We have already completed the review.",
   "tip":"already、just、yet 這些詞通常配合現在完成式使用。"},

  {"title":"過去進行式 vs. 簡單過去式","category":"時態",
   "rule":"過去進行式（was/were + V-ing）強調過去某時正在進行的動作。簡單過去式強調完成的動作。",
   "pattern":"We were [V-ing] when [事件發生] / We [過去式動詞] [時間]",
   "examples":[
     {"en":"We were reviewing the budget when the client called.","zh":"我們正在審查預算時客戶打電話來了。"},
     {"en":"The team was preparing the presentation all morning.","zh":"整個上午團隊都在準備簡報。"},
     {"en":"While I was attending the conference, the deal was finalized.","zh":"當我在參加會議時，交易已經敲定。"},
   ],"wrong":"We reviewed the budget when the client was called.","right":"We were reviewing the budget when the client called.",
   "tip":"「當...的時候」背景動作用進行式，發生的事件用簡單過去式。"},

  # ── 介系詞搭配 Prepositions ────────────────────────────────
  {"title":"常用介系詞搭配（商務）","category":"介系詞",
   "rule":"英文動詞+介系詞的固定搭配，必須整組記憶，不能用中文邏輯翻譯。",
   "pattern":"[動詞] + [固定介系詞]",
   "examples":[
     {"en":"I am responsible for managing the project timeline.","zh":"我負責管理專案時間表。（responsible for）"},
     {"en":"We need to focus on the key deliverables this week.","zh":"本週我們需要專注於關鍵交付成果。（focus on）"},
     {"en":"This plan depends on the budget approval.","zh":"這個計畫取決於預算批准。（depend on）"},
   ],"wrong":"I am responsible of managing the project.","right":"I am responsible for managing the project.",
   "tip":"responsible for / focus on / depend on / agree with / result in — 這些固定搭配要整組背。"},

  {"title":"in / on / at — 時間介系詞","category":"介系詞",
   "rule":"at 用於具體時刻；on 用於日期和星期；in 用於月份、年份、時段。",
   "pattern":"at [時刻] / on [日期/星期] / in [月/年/時段]",
   "examples":[
     {"en":"The meeting starts at 9 AM on Monday.","zh":"會議在週一上午9點開始。"},
     {"en":"We will launch the product in Q3.","zh":"我們將在第三季推出產品。"},
     {"en":"The report is due on Friday, March 15th.","zh":"報告的截止日期是3月15日（週五）。"},
   ],"wrong":"The meeting starts in Monday at morning.","right":"The meeting starts at 9 AM on Monday.",
   "tip":"at + 時刻、on + 日期/星期、in + 月份/季度/年份，不要混用。"},

  # ── 動名詞 vs. 不定式 Gerund vs. Infinitive ────────────────
  {"title":"動名詞 vs. 不定式 — 常見動詞","category":"句型結構",
   "rule":"有些動詞後接 V-ing（動名詞），有些接 to V（不定式），意思可能不同。",
   "pattern":"[動詞] + V-ing 或 [動詞] + to V",
   "examples":[
     {"en":"I recommend starting the project next week. (recommend + V-ing)","zh":"我建議下週開始這個專案。"},
     {"en":"We decided to postpone the launch. (decide + to V)","zh":"我們決定推遲發布。"},
     {"en":"Please avoid scheduling meetings on Friday afternoon. (avoid + V-ing)","zh":"請避免在週五下午安排會議。"},
   ],"wrong":"I recommend to start the project.","right":"I recommend starting the project.",
   "tip":"接 V-ing：suggest, recommend, avoid, consider, finish。接 to V：decide, plan, agree, need, want。"},

  {"title":"問接問句 — 禮貌問法","category":"句型結構",
   "rule":"直接問句在商務場合可能太唐突，改用間接問句更有禮貌。",
   "pattern":"Could you tell me [what/when/how] + [直敘句語序]?",
   "examples":[
     {"en":"Could you tell me when the report will be ready?","zh":"您能告訴我報告什麼時候會準備好嗎？"},
     {"en":"Do you know how many people will attend the conference?","zh":"您知道有多少人會參加會議嗎？"},
     {"en":"I was wondering if you have reviewed the proposal yet.","zh":"我想知道您是否已經審查過提案了。"},
   ],"wrong":"Could you tell me when will the report be ready?","right":"Could you tell me when the report will be ready?",
   "tip":"間接問句用直敘句語序（主詞在前），不用疑問句語序（助動詞不提前）。"},
]

# ══════════════════════════════════════════════════════════════
#  每日選字（以日期為種子，固定同一天的30個單字）
# ══════════════════════════════════════════════════════════════
def daily_words():
    today = datetime.now().strftime("%Y-%m-%d")
    seed  = int(hashlib.md5(today.encode()).hexdigest(), 16) % (2**32)
    rng   = random.Random(seed)
    pool  = WORDS.copy()
    rng.shuffle(pool)
    return pool[:30]

def daily_grammar():
    today = datetime.now().strftime("%Y-%m-%d")
    seed  = int(hashlib.md5(("g"+today).encode()).hexdigest(), 16) % (2**32)
    rng   = random.Random(seed)
    pool  = GRAMMAR.copy()
    rng.shuffle(pool)
    return pool[:4]

# ══════════════════════════════════════════════════════════════
#  HTML 樣板
# ══════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>英文單字日報</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@300;400;500;700&family=Noto+Serif+TC:wght@600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#f0f4f8;--card:#fff;--ink:#191b1f;--soft:#5a6270;--line:#e2e6ea;
  --up:#1f7a4d;--accent:#1a56c4;--orange:#c45f1a;--red:#c2402d}
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--ink);font-family:"Noto Sans TC","Hanken Grotesk",sans-serif;min-height:100vh}

/* header */
.header{background:var(--accent);color:#fff;padding:14px 16px 0;position:sticky;top:0;z-index:20}
.header-top{display:flex;align-items:center;gap:10px;max-width:600px;margin:0 auto;padding-bottom:10px}
.logo-text{font-family:"Hanken Grotesk";font-weight:800;font-size:16px;letter-spacing:.04em}
.logo-sub{font-size:11px;opacity:.8;margin-top:1px}
.date-badge{margin-left:auto;font-family:"Hanken Grotesk";font-size:11.5px;opacity:.85}
/* 主分頁 */
.main-tabs{display:flex;max-width:600px;margin:0 auto;border-top:1px solid rgba(255,255,255,.2)}
.mtab{flex:1;background:none;border:none;color:rgba(255,255,255,.7);font-family:inherit;
  font-size:14px;font-weight:700;padding:10px 0;cursor:pointer;position:relative;transition:.15s}
.mtab:hover{color:#fff}
.mtab.on{color:#fff}
.mtab.on::after{content:"";position:absolute;left:20%;right:20%;bottom:0;height:3px;
  background:#fff;border-radius:2px}
/* grammar */
.grammar-card{border-left:3px solid var(--orange)}
.gcat-tag{display:inline-block;font-family:"Hanken Grotesk";font-size:10.5px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;background:#fef3e8;color:var(--orange);
  border-radius:6px;padding:2px 8px}
.g-title{font-family:"Noto Serif TC",serif;font-weight:700;font-size:19px;margin-bottom:6px}
.g-rule{font-size:14px;color:#2c2f36;line-height:1.65;margin-bottom:8px;
  background:#f8f9fa;border-radius:8px;padding:8px 10px}
.g-pattern{font-size:13px;color:var(--accent);font-weight:600;margin-bottom:10px}
.g-pattern code{background:#e8f0fe;border-radius:6px;padding:2px 8px;font-family:monospace}
.g-examples-label{font-family:"Hanken Grotesk";font-size:10.5px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:var(--soft);margin-bottom:5px}
.g-example{margin-bottom:8px;padding:8px 10px;background:var(--bg);border-radius:8px}
.g-en{font-size:14.5px;color:var(--ink);line-height:1.55;display:flex;align-items:flex-start;gap:6px}
.g-zh{font-size:13px;color:var(--soft);margin-top:2px;margin-left:26px}
.g-compare{background:#fff5f5;border-radius:10px;padding:10px 12px;margin:10px 0;font-size:13px}
.g-wrong{color:var(--red);margin-bottom:4px}
.g-right{color:var(--up);font-weight:600}
.g-tip{font-size:13px;background:#fffbea;border-radius:8px;padding:8px 10px;
  color:#7a5800;font-weight:500;line-height:1.6}

/* progress */
.progress-bar-wrap{max-width:600px;margin:10px auto 0;background:rgba(255,255,255,.25);border-radius:8px;height:5px;overflow:hidden}
.progress-bar{height:100%;background:#fff;border-radius:8px;transition:width .4s}
.progress-text{font-family:"Hanken Grotesk";font-size:12px;opacity:.85;margin-top:5px;text-align:center;max-width:600px;margin-left:auto;margin-right:auto}

/* controls */
.controls{background:#fff;border-bottom:1px solid var(--line);padding:10px 16px}
.controls-inner{max-width:600px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.btn{border:none;cursor:pointer;font-family:inherit;font-weight:600;font-size:13px;border-radius:20px;padding:8px 16px;transition:.15s}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:active{opacity:.8}
.btn-outline{background:none;border:1.5px solid var(--line);color:var(--ink)}
.btn-outline:active{background:var(--bg)}
.btn-outline.active{border-color:var(--accent);color:var(--accent)}
.speed-wrap{display:flex;align-items:center;gap:6px;font-family:"Hanken Grotesk";font-size:12px;color:var(--soft);margin-left:auto}
.speed-wrap input{width:70px;accent-color:var(--accent)}
.auto-wrap{display:flex;align-items:center;gap:5px;font-family:"Hanken Grotesk";font-size:12.5px;font-weight:600;color:var(--soft)}
.auto-wrap input{width:16px;height:16px;cursor:pointer;accent-color:var(--accent)}

/* 篩選列 */
.filter-bar{background:#fff;border-bottom:1px solid var(--line);padding:8px 16px;display:flex;flex-direction:column;gap:6px}
.filter-inner{max-width:600px;margin:0 auto;width:100%;display:flex;align-items:center;gap:8px}
.filter-label{font-family:"Hanken Grotesk";font-size:11px;font-weight:800;color:var(--soft);
  letter-spacing:.06em;white-space:nowrap;text-transform:uppercase;min-width:30px}
.filter-chips{display:flex;gap:5px;overflow-x:auto;scrollbar-width:none;flex:1}
.filter-chips::-webkit-scrollbar{display:none}
.cat-btn,.date-btn{flex:0 0 auto;background:none;border:1.5px solid var(--line);border-radius:16px;
  cursor:pointer;font-family:"Hanken Grotesk";font-size:12px;font-weight:600;color:var(--soft);
  padding:4px 11px;white-space:nowrap;transition:.15s}
.cat-btn:hover,.date-btn:hover{border-color:var(--accent);color:var(--accent)}
.cat-btn.on,.date-btn.on{background:var(--accent);color:#fff;border-color:var(--accent)}
/* 日期區塊標題 */
.date-header{font-family:"Hanken Grotesk";font-weight:800;font-size:13px;
  letter-spacing:.06em;color:var(--soft);padding:18px 4px 8px;
  border-bottom:2px solid var(--line);margin-bottom:2px}

/* word cards */
.wrap{max-width:600px;margin:0 auto;padding:14px 14px 60px}
.card{background:var(--card);border-radius:18px;padding:20px;margin-bottom:12px;border:1px solid var(--line);transition:box-shadow .2s,border-color .2s;scroll-margin-top:170px}
.card.active{border-color:var(--accent);box-shadow:0 0 0 2px rgba(26,86,196,.18)}
.card.done{opacity:.55}

/* word display */
.cat-tag{display:inline-block;font-family:"Hanken Grotesk";font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;border-radius:6px;padding:2px 8px;margin-bottom:8px}
.cat-tag.會議{background:#e8f0fe;color:#1a56c4}
.cat-tag.商業{background:#fef3e8;color:#c45f1a}
.cat-tag.科技{background:#e8fef3;color:#1f7a4d}
.cat-tag.財經{background:#fde8e8;color:#c2402d}
.cat-tag.生活{background:#f3e8fe;color:#7c3aed}

.word-num{font-family:"Hanken Grotesk";font-size:12px;font-weight:700;color:var(--soft);margin-bottom:4px}
.word-en{font-family:"Hanken Grotesk";font-weight:800;font-size:32px;letter-spacing:-.01em;line-height:1.1;margin-bottom:4px;display:flex;align-items:center;gap:10px}
.word-en .say-btn{font-size:20px;background:none;border:none;cursor:pointer;opacity:.5;padding:0;transition:opacity .15s}
.word-en .say-btn:hover{opacity:1}
.ipa{font-family:"Hanken Grotesk";font-size:14px;color:var(--soft);margin-bottom:2px}
.phonetic{font-family:"Hanken Grotesk";font-size:13px;color:var(--accent);font-weight:600;background:#e8f0fe;border-radius:8px;padding:3px 10px;display:inline-block;margin-bottom:10px}
.zh-meaning{font-family:"Noto Serif TC",serif;font-size:19px;font-weight:700;margin-bottom:12px;border-left:3px solid var(--accent);padding-left:10px}
.example-label{font-family:"Hanken Grotesk";font-size:10.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--soft);margin-bottom:4px}
.example-en{font-size:14.5px;color:#2c2f36;line-height:1.6;margin-bottom:3px;display:flex;align-items:flex-start;gap:8px}
.example-en .say-btn{font-size:15px;flex:0 0 auto;margin-top:2px;background:none;border:none;cursor:pointer;opacity:.45;transition:opacity .15s}
.example-en .say-btn:hover{opacity:.9}
.example-zh{font-size:13px;color:var(--soft);line-height:1.55}
.rep-dots{display:flex;gap:5px;margin-top:8px}
.rep-dot{width:8px;height:8px;border-radius:50%;background:var(--line);transition:.2s}
.rep-dot.done{background:var(--accent)}

.foot{text-align:center;font-size:11px;color:var(--soft);padding:10px 0}
.play-status{margin-top:10px;background:#e8f0fe;border-radius:10px;padding:7px 12px;
  font-family:"Hanken Grotesk";font-size:13px;font-weight:600;color:var(--accent);
  display:flex;align-items:center;gap:8px}
.play-status.hidden{display:none}
/* 發音練習 */
.mic-btn{background:none;border:1.5px solid var(--line);border-radius:16px;cursor:pointer;
  font-size:13px;padding:2px 9px;color:var(--soft);font-family:inherit;font-weight:600;
  transition:.15s;margin-left:4px;vertical-align:middle}
.mic-btn:hover{border-color:var(--accent);color:var(--accent)}
.mic-btn:disabled{opacity:.4;cursor:default}
.rec-result{margin:5px 0 8px}
.rec-box{background:var(--bg);border-radius:12px;padding:10px 13px;font-size:13px;line-height:1.6}
.rec-listening{animation:pulse 1s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
.rec-score{font-weight:700;font-size:14px;margin-bottom:5px}
.rec-row{display:flex;gap:6px;margin-top:3px;flex-wrap:wrap}
.rec-lbl{font-weight:600;color:var(--soft);white-space:nowrap}
</style>
</head>
<body>

<div class="header">
  <div class="header-top">
    <div><div class="logo-text">📚 英文學習日報</div><div class="logo-sub">單字 · 文法 · 商務英文</div></div>
    <div class="date-badge" id="dateBadge"></div>
  </div>
  <!-- 主分頁 -->
  <div class="main-tabs" id="mainTabs"></div>
</div>

<div id="playControls">
<div class="controls">
  <div class="controls-inner">
    <button class="btn btn-primary" id="playBtn" onclick="togglePlay()">▶ 開始播報</button>
    <button class="btn btn-outline" onclick="prevWord()">‹ 上一個</button>
    <button class="btn btn-outline" onclick="nextWord()">下一個 ›</button>
    <div class="speed-wrap">
      <span>語速</span>
      <input type="range" min="0.6" max="1.6" step="0.2" value="0.9" oninput="setRate(this.value)">
      <span id="rateLabel">0.9x</span>
    </div>
    <label class="auto-wrap" title="開啟後進入頁面自動播報">
      <input type="checkbox" id="autoToggle"> 自動播報
    </label>
  </div>
</div>
</div>

<div id="subBars">
<div class="filter-bar">
  <div class="filter-inner">
    <span class="filter-label">主題</span>
    <div class="filter-chips" id="catBar"></div>
  </div>
  <div class="filter-inner">
    <span class="filter-label">日期</span>
    <div class="filter-chips" id="dateBar"></div>
  </div>
</div>
</div>

<div class="wrap" id="feed"></div>
<div class="foot">每段各重複 3 次：英文單字 → 發音拼音 → 中文意思 → 英文例句 → 中文例句<br>生成：__DATE__</div>

<script>
const ALL_DATA = __ALL_DATA_JSON__;   // {date: {words:[...], grammar:[...]}, ...}
const CATS  = ["全部","會議","商業","科技","財經","生活"];
const REPS  = 3;
let curCat="全部", curDate="全部", curTab="單字", curIdx=0, rate=0.9, playing=false, cancelled=false;

// 所有日期，由新到舊
const ALL_DATES = Object.keys(ALL_DATA).sort((a,b)=>b.localeCompare(a));

// 取某日的單字（相容舊格式）
function getWords(d){ const v=ALL_DATA[d]; return Array.isArray(v)?v:(v?.words||[]); }
function getGrammar(d){ const v=ALL_DATA[d]; return Array.isArray(v)?[]:(v?.grammar||[]); }

// 初始化
document.getElementById("dateBadge").textContent = "__DATE__";
buildMainTabs();
buildCatBar();
buildDateBar();
buildCards();
updateProgress(0);

// 自動播報設定
const autoToggle = document.getElementById("autoToggle");
autoToggle.checked = localStorage.getItem("vocabAuto")==="1";
autoToggle.addEventListener("change",()=>localStorage.setItem("vocabAuto",autoToggle.checked?"1":"0"));
if(localStorage.getItem("vocabAuto")==="1") setTimeout(()=>startPlay(), 1200);

// ── 主分頁（單字 / 文法） ────────────────────────────────────
function buildMainTabs(){
  document.getElementById("mainTabs").innerHTML=
    ["單字","文法"].map(t=>
      `<button class="mtab${t===curTab?" on":""}" onclick="setTab('${t}')">${t==="單字"?"📚 單字":"📐 文法"}</button>`
    ).join("");
}
function setTab(t){
  curTab=t; stopPlay(); curIdx=0;
  buildMainTabs();
  const subBars=document.getElementById("subBars");
  subBars.style.display=t==="單字"?"":"none";
  document.getElementById("playControls").style.display=t==="單字"?"":"none";
  if(t==="單字") buildCards();
  else buildGrammarCards();
}

// ── 日期篩選 ─────────────────────────────────────────────────
function fmtDate(iso){
  const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(iso||"");
  if(!m) return iso;
  const d=new Date(+m[1],+m[2]-1,+m[3]);
  const days=["日","一","二","三","四","五","六"];
  return `${m[2]}/${m[3]} 週${days[d.getDay()]}`;
}
function buildDateBar(){
  const bar=document.getElementById("dateBar");
  const btns=[{k:"全部",l:`全部（${ALL_DATES.length}天）`},...ALL_DATES.map(d=>({k:d,l:fmtDate(d)}))];
  bar.innerHTML = btns.map(b=>
    `<button class="date-btn${b.k===curDate?" on":""}" onclick="setDate('${b.k}')">${b.l}</button>`
  ).join("");
}
function setDate(d){
  curDate=d; curIdx=0; stopPlay();
  document.querySelectorAll(".date-btn").forEach(b=>b.classList.toggle("on",b.dataset?.d===d||b.textContent.startsWith(d==="全部"?"全部":fmtDate(d))));
  buildDateBar();
  buildCards();
  updateProgress(0);
}

// ── 類別篩選 ─────────────────────────────────────────────────
function buildCatBar(){
  const all=filteredWords();
  const cnt={}; all.forEach(w=>{cnt[w.category]=(cnt[w.category]||0)+1;});
  document.getElementById("catBar").innerHTML = CATS.map(c=>{
    const n=c==="全部"?all.length:(cnt[c]||0);
    return `<button class="cat-btn${c===curCat?" on":""}" onclick="setCat('${c}')">${c}<span style="font-size:10px;opacity:.7;margin-left:3px">${n}</span></button>`;
  }).join("");
}
function buildDateBar(){
  const btns=[{k:"全部",l:`全部（${ALL_DATES.length}天）`},...ALL_DATES.map(d=>({k:d,l:fmtDate(d)}))];
  document.getElementById("dateBar").innerHTML = btns.map(b=>
    `<button class="date-btn${b.k===curDate?" on":""}" onclick="setDate('${b.k}')">${b.l}</button>`
  ).join("");
}
function setCat(cat){
  curCat=cat; curIdx=0; stopPlay();
  document.querySelectorAll(".cat-btn").forEach(b=>b.classList.toggle("on",b.textContent.startsWith(cat)));
  buildCards(); updateProgress(0);
}

// 依日期+類別篩選出單字（含日期欄位）
function filteredWords(){
  let dates = curDate==="全部" ? ALL_DATES : [curDate];
  let words = [];
  dates.forEach(d=> getWords(d).forEach(w=>words.push({...w, _date:d})));
  if(curCat!=="全部") words=words.filter(w=>w.category===curCat);
  return words;
}

// ── 文法卡片 ─────────────────────────────────────────────────
function buildGrammarCards(){
  const feed=document.getElementById("feed");
  // 蒐集所有日期的文法（去重）
  const seen=new Set(); const all=[];
  ALL_DATES.forEach(d=>{
    getGrammar(d).forEach(g=>{
      if(!seen.has(g.title)){ seen.add(g.title); all.push({...g,_date:d}); }
    });
  });
  // 今天的排前面
  const todayG = getGrammar(ALL_DATES[0]);
  const todayTitles = new Set(todayG.map(g=>g.title));
  const sorted = [...all.filter(g=>todayTitles.has(g.title)), ...all.filter(g=>!todayTitles.has(g.title))];

  feed.innerHTML = sorted.map((g,i)=>{
    const isToday = todayTitles.has(g.title);
    return `
    <div class="card grammar-card" id="gcard-${i}">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap">
        <span class="gcat-tag">${g.category}</span>
        ${isToday?'<span style="font-size:11px;font-weight:700;color:var(--accent);background:#e8f0fe;padding:2px 8px;border-radius:6px">今日重點</span>':''}
      </div>
      <div class="g-title">${g.title}</div>
      <div class="g-rule">${g.rule}</div>
      <div class="g-pattern">📋 句型：<code>${g.pattern}</code></div>
      <div class="g-examples-label">例句（各可點 🔊 聆聽）</div>
      ${g.examples.map((ex,j)=>`
        <div class="g-example">
          <div class="g-en">
            <button class="say-btn" onclick="sayText('${encodeURIComponent(ex.en)}','en-US')" title="聆聽">🔊</button>
            ${ex.en}
          </div>
          <div class="g-zh">${ex.zh}</div>
        </div>`).join("")}
      <div class="g-compare">
        <div class="g-wrong">❌ 常見錯誤：<span>${g.wrong}</span></div>
        <div class="g-right">✅ 正確說法：<span>${g.right}</span></div>
      </div>
      <div class="g-tip">💡 ${g.tip}</div>
    </div>`;
  }).join("");
}

function sayText(enc, lang){
  const text=decodeURIComponent(enc);
  speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.lang=lang; const v=lang.startsWith("zh")?zhVoice():enVoice(); if(v)u.voice=v;
  try{speechSynthesis.resume();}catch(_){}
  speechSynthesis.speak(u);
}
function filteredWords(){return curCat==="全部"?WORDS:WORDS.filter(w=>w.category===curCat);}

// ── 建立卡片 ─────────────────────────────────────────────────
function buildCards(){
  const feed=document.getElementById("feed");
  const words=filteredWords();
  buildCatBar();
  if(!words.length){ feed.innerHTML=`<div style="text-align:center;padding:40px;color:var(--soft)">此條件下無單字</div>`; return; }

  let html="", lastDate="";
  words.forEach((w,i)=>{
    if(curDate==="全部" && w._date!==lastDate){
      lastDate=w._date;
      html+=`<div class="date-header">${fmtDate(w._date)} · ${ALL_DATA[w._date]?.length||0} 個單字</div>`;
    }
    // 用 data 屬性存文字，避免引號轉義問題
    const wEnc = encodeURIComponent(w.word);
    const eEnc = encodeURIComponent(w.example);
    html+=`
    <div class="card" id="card-${i}">
      <span class="cat-tag ${w.category}">${w.category}</span>
      <div class="word-num">第 ${i+1} 個</div>
      <div class="word-en">
        ${w.word}
        <button class="say-btn" onclick="sayWord(${i})" title="聆聽">🔊</button>
        <button class="mic-btn" data-enc="${wEnc}" data-rid="wr-${i}" onclick="startRec(this)" title="練習發音">🎤</button>
      </div>
      <div class="ipa">${w.ipa}</div>
      <div class="phonetic">🗣 ${w.phonetic}</div>
      <div id="wr-${i}" class="rec-result"></div>
      <div class="zh-meaning">${w.zh}</div>
      <div class="example-label">例句 <button class="say-btn" style="font-size:13px" onclick="sayExample(${i})" title="聆聽例句">🔊</button>
        <button class="mic-btn" data-enc="${eEnc}" data-rid="er-${i}" onclick="startRec(this)" title="練習例句">🎤 練例句</button>
      </div>
      <div class="example-en"><span>${w.example}</span></div>
      <div class="example-zh">${w.example_zh}</div>
      <div id="er-${i}" class="rec-result"></div>
      <div class="rep-dots" id="dots-${i}">
        ${Array(REPS).fill('<span class="rep-dot"></span>').join("")}
      </div>
      <div class="play-status hidden" id="status-${i}"></div>
    </div>`;
  });
  feed.innerHTML=html;
}

// ── 進度 ─────────────────────────────────────────────────────
function updateProgress(idx){
  const total=filteredWords().length;
  const pct = total ? Math.round((idx/total)*100) : 0;
  document.getElementById("progressBar").style.width=pct+"%";
  document.getElementById("progressText").textContent=`第 ${Math.min(idx+1,total)} / ${total} 個單字`;
}
function setActive(idx){
  document.querySelectorAll(".card").forEach((c,i)=>{
    c.classList.toggle("active",i===idx);
    if(i<idx) c.classList.add("done"); else c.classList.remove("done");
  });
  const card=document.getElementById("card-"+idx);
  if(card) card.scrollIntoView({behavior:"smooth",block:"center"});
  updateProgress(idx);
  curIdx=idx;
}
function setDot(idx,rep){
  const dots=document.querySelectorAll(`#dots-${idx} .rep-dot`);
  dots.forEach((d,i)=>d.classList.toggle("done",i<=rep));
}
function clearDots(idx){
  document.querySelectorAll(`#dots-${idx} .rep-dot`).forEach(d=>d.classList.remove("done"));
}

// ── TTS 語音 ─────────────────────────────────────────────────
function enVoice(){const vs=speechSynthesis.getVoices();return vs.find(v=>v.lang==="en-US")||vs.find(v=>/en/i.test(v.lang));}
function zhVoice(){const vs=speechSynthesis.getVoices();return vs.find(v=>/zh-TW|zh_TW/i.test(v.lang))||vs.find(v=>/zh/i.test(v.lang));}

function speak(text,lang,r){
  return new Promise(res=>{
    if(!playing&&lang!=="direct"){res();return;}
    const u=new SpeechSynthesisUtterance(text);
    u.lang=lang; u.rate=r||rate;
    const v=lang.startsWith("zh")?zhVoice():enVoice();
    if(v)u.voice=v;
    u.onend=res; u.onerror=res;
    try{speechSynthesis.resume();}catch(_){}
    speechSynthesis.speak(u);
  });
}
function pause(ms){return new Promise(r=>setTimeout(r,ms));}

// 單字與例句個別朗讀按鈕
async function sayWord(i){
  speechSynthesis.cancel();
  const w=filteredWords()[i];
  await speak(w.word,"en-US","direct");
}
async function sayExample(i){
  speechSynthesis.cancel();
  const w=filteredWords()[i];
  await speak(w.example,"en-US","direct");
}

// ── 播報控制 ─────────────────────────────────────────────────
function togglePlay(){if(playing)stopPlay();else startPlay();}
function startPlay(){
  if(!window.speechSynthesis){alert("此瀏覽器不支援語音功能");return;}
  playing=true; cancelled=false;
  document.getElementById("playBtn").textContent="⏹ 停止播報";
  playFrom(curIdx);
}
function stopPlay(){
  playing=false; cancelled=true;
  speechSynthesis.cancel();
  document.getElementById("playBtn").textContent="▶ 開始播報";
}
function prevWord(){stopPlay();if(curIdx>0){curIdx--;setActive(curIdx);}}
function nextWord(){stopPlay();if(curIdx<filteredWords().length-1){curIdx++;setActive(curIdx);}}
function setRate(v){rate=parseFloat(v);document.getElementById("rateLabel").textContent=v+"x";}

async function playFrom(startIdx){
  const words=filteredWords();
  const SECTIONS=[
    {label:"🔤 英文單字",  fn:(w)=>speak(w.word,"en-US"),       gap:400},
    {label:"🗣 發音拼音",  fn:(w)=>speak(w.phonetic,"en-US"),   gap:350},
    {label:"🇹🇼 中文意思", fn:(w)=>speak(w.zh,"zh-TW"),         gap:350},
    {label:"📖 英文例句",  fn:(w)=>speak(w.example,"en-US"),    gap:450},
    {label:"📝 中文例句",  fn:(w)=>speak(w.example_zh,"zh-TW"), gap:500},
  ];
  for(let i=startIdx; i<words.length; i++){
    if(!playing||cancelled) return;
    const w=words[i];
    setActive(i);

    for(let s=0;s<SECTIONS.length;s++){
      const sec=SECTIONS[s];
      for(let rep=0;rep<REPS;rep++){
        if(!playing||cancelled)return;
        setStatus(i, sec.label, rep+1);
        await sec.fn(w);
        await pause(sec.gap);
      }
    }
    setStatus(i,"✅ 完成","");
    await pause(600);
  }
  if(playing) stopPlay();
}

function setStatus(idx, section, rep){
  const el=document.getElementById("status-"+idx);
  if(!el)return;
  el.classList.remove("hidden");
  el.innerHTML=`<span>${section}</span><span style="margin-left:auto;opacity:.7">${rep?rep+"/"+REPS:""}</span>`;
}
function clearStatus(idx){
  const el=document.getElementById("status-"+idx);
  if(el)el.classList.add("hidden");
}

if(window.speechSynthesis){speechSynthesis.getVoices();speechSynthesis.onvoiceschanged=()=>{};}

// ── 發音練習（語音辨識） ──────────────────────────────────────
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

function levenshtein(s,t){
  const m=s.length,n=t.length;
  const dp=Array.from({length:m+1},(_,i)=>Array.from({length:n+1},(_,j)=>i?j?0:i:j));
  for(let i=1;i<=m;i++) for(let j=1;j<=n;j++)
    dp[i][j]=s[i-1]===t[j-1]?dp[i-1][j-1]:1+Math.min(dp[i-1][j],dp[i][j-1],dp[i-1][j-1]);
  return dp[m][n];
}
function similarity(a,b){
  a=a.toLowerCase().replace(/[^a-z\s']/g,"").trim();
  b=b.toLowerCase().replace(/[^a-z\s']/g,"").trim();
  if(a===b) return 100;
  if(!a||!b) return 0;
  return Math.max(0, Math.round((1-levenshtein(a,b)/Math.max(a.length,b.length))*100));
}
function showRecResult(rid, target, heard, score){
  const el=document.getElementById(rid);
  if(!el) return;
  const [emoji,label,color] = score>=90?["🌟","非常準確！","var(--up)"]:
    score>=70?["👍","不錯，再練幾次","var(--accent)"]:
    score>=50?["📝","有些出入，慢慢說","var(--orange)"]:
    ["🔄","差異較大，先多聽幾遍","var(--red)"];
  // 標出差異（詞級）
  const tWords=target.toLowerCase().split(/\s+/);
  const hWords=heard.toLowerCase().split(/\s+/);
  const diffHtml=hWords.map(w=>tWords.includes(w)?
    `<span style="color:var(--up);font-weight:600">${w}</span>`:
    `<span style="color:var(--red);text-decoration:underline">${w}</span>`
  ).join(" ");
  el.innerHTML=`
    <div class="rec-box">
      <div class="rec-score" style="color:${color}">${emoji} ${score}% ${label}</div>
      <div class="rec-row"><span class="rec-lbl">你說：</span><span>${diffHtml}</span></div>
      <div class="rec-row"><span class="rec-lbl">目標：</span><span style="color:var(--soft)">${target}</span></div>
      <div style="font-size:11px;color:var(--soft);margin-top:4px">✅ 綠色=正確 🔴 紅色+底線=有出入</div>
    </div>`;
}
function startRec(btn){
  if(!SR){ alert("請用 Chrome 瀏覽器開啟此頁面，才能使用語音辨識功能。"); return; }
  const target = decodeURIComponent(btn.dataset.enc);
  const rid    = btn.dataset.rid;
  const el     = document.getElementById(rid);
  if(el) el.innerHTML=`<div class="rec-box rec-listening">🔴 請說：<b>${target}</b></div>`;
  btn.textContent="⏳"; btn.disabled=true;

  const rec = new SR();
  rec.lang="en-US"; rec.interimResults=false; rec.maxAlternatives=3;
  rec.onresult=(e)=>{
    const heard=e.results[0][0].transcript;
    showRecResult(rid, target, heard, similarity(heard, target));
    btn.textContent="🎤"; btn.disabled=false;
  };
  rec.onerror=(e)=>{
    const msg={
      "no-speech":"沒有偵測到聲音，請再試一次",
      "not-allowed":"麥克風權限被拒絕，請在瀏覽器設定中允許",
      "network":"網路連線問題",
    }[e.error]||`錯誤：${e.error}`;
    if(el) el.innerHTML=`<div class="rec-box" style="color:var(--red)">⚠️ ${msg}</div>`;
    btn.textContent="🎤"; btn.disabled=false;
  };
  rec.onend=()=>{ btn.textContent="🎤"; btn.disabled=false; };
  try{ rec.start(); }catch(e){ btn.textContent="🎤"; btn.disabled=false; }
  setTimeout(()=>{ try{rec.stop();}catch(_){} }, 9000);
}
</script>
</body>
</html>"""

# ══════════════════════════════════════════════════════════════
#  生成 HTML
# ══════════════════════════════════════════════════════════════
def main():
    today    = datetime.now().strftime("%Y-%m-%d")
    gen_date = datetime.now().strftime("%Y/%m/%d")

    # 讀取歷史記錄
    history_file = Path(__file__).parent / "vocab_history.json"
    if history_file.exists():
        history = json.loads(history_file.read_text(encoding="utf-8"))
        print(f"✓ 讀取歷史：共 {len(history)} 天的記錄")
    else:
        history = {}
        print("✓ 首次執行，建立新的歷史記錄")

    # 加入今天的單字（若今天尚未執行）
    if today not in history:
        history[today] = {"words": daily_words(), "grammar": daily_grammar()}
        print(f"✓ 新增今天 ({today}) 的 30 個單字 + 4 個文法重點")
    else:
        # 向舊格式相容：若舊格式只有 list（單字），轉換為新格式
        if isinstance(history[today], list):
            history[today] = {"words": history[today], "grammar": daily_grammar()}
        print(f"✓ 今天 ({today}) 已有記錄，沿用")

    # 儲存歷史
    history_file.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 歷史已儲存 → {history_file}")

    # 生成 HTML（含所有歷史資料）
    html = HTML.replace("__ALL_DATA_JSON__", json.dumps(history, ensure_ascii=False))
    html = html.replace("__DATE__", gen_date)
    OUT_HTML.write_text(html, encoding="utf-8")

    total_words = sum(len(v) for v in history.values())
    print(f"✓ HTML 生成完成 → {OUT_HTML}")
    print(f"  累積 {len(history)} 天，共 {total_words} 個單字")

if __name__ == "__main__":
    main()
