"""Daily fetch: Google News (positive headlines) + Yahoo volume -> data.json. No API key needed."""
import json, re, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# NSE F&O stocks: "SYMBOL": "name used for news search". Add or remove freely.
STOCKS = {
"ABB":"ABB India","ABCAPITAL":"Aditya Birla Capital","ACC":"ACC","ADANIENSOL":"Adani Energy Solutions","ADANIENT":"Adani Enterprises",
"ADANIGREEN":"Adani Green","ADANIPORTS":"Adani Ports","ALKEM":"Alkem Laboratories","AMBUJACEM":"Ambuja Cements","ANGELONE":"Angel One",
"APOLLOHOSP":"Apollo Hospitals","APLAPOLLO":"APL Apollo","ASHOKLEY":"Ashok Leyland","ASIANPAINT":"Asian Paints","ASTRAL":"Astral",
"AUBANK":"AU Small Finance Bank","AUROPHARMA":"Aurobindo Pharma","AXISBANK":"Axis Bank","BAJAJ-AUTO":"Bajaj Auto","BAJAJFINSV":"Bajaj Finserv",
"BAJFINANCE":"Bajaj Finance","BANDHANBNK":"Bandhan Bank","BANKBARODA":"Bank of Baroda","BANKINDIA":"Bank of India","BDL":"Bharat Dynamics",
"BEL":"Bharat Electronics","BHARATFORG":"Bharat Forge","BHARTIARTL":"Bharti Airtel","BHEL":"BHEL","BIOCON":"Biocon","BLUESTARCO":"Blue Star",
"BOSCHLTD":"Bosch","BPCL":"BPCL","BRITANNIA":"Britannia","BSE":"BSE Ltd","CAMS":"CAMS","CANBK":"Canara Bank","CDSL":"CDSL","CGPOWER":"CG Power",
"CHOLAFIN":"Cholamandalam Investment","CIPLA":"Cipla","COALINDIA":"Coal India","COFORGE":"Coforge","COLPAL":"Colgate-Palmolive",
"CONCOR":"Container Corporation","CROMPTON":"Crompton Greaves","CUMMINSIND":"Cummins India","DABUR":"Dabur","DALBHARAT":"Dalmia Bharat",
"DELHIVERY":"Delhivery","DIVISLAB":"Divi's Laboratories","DIXON":"Dixon Technologies","DLF":"DLF","DMART":"Avenue Supermarts","DRREDDY":"Dr Reddy's",
"EICHERMOT":"Eicher Motors","ETERNAL":"Eternal","EXIDEIND":"Exide Industries","FEDERALBNK":"Federal Bank","FORTIS":"Fortis Healthcare","GAIL":"GAIL",
"GLENMARK":"Glenmark","GMRAIRPORT":"GMR Airports","GODREJCP":"Godrej Consumer","GODREJPROP":"Godrej Properties","GRASIM":"Grasim","HAVELLS":"Havells",
"HAL":"Hindustan Aeronautics","HCLTECH":"HCL Technologies","HDFCAMC":"HDFC AMC","HDFCBANK":"HDFC Bank","HDFCLIFE":"HDFC Life","HEROMOTOCO":"Hero MotoCorp",
"HFCL":"HFCL","HINDALCO":"Hindalco","HINDPETRO":"HPCL","HINDUNILVR":"Hindustan Unilever","HINDZINC":"Hindustan Zinc","HUDCO":"HUDCO","ICICIBANK":"ICICI Bank",
"ICICIGI":"ICICI Lombard","ICICIPRULI":"ICICI Prudential Life","IDEA":"Vodafone Idea","IDFCFIRSTB":"IDFC First Bank","IEX":"Indian Energy Exchange",
"IGL":"Indraprastha Gas","INDHOTEL":"Indian Hotels","INDIGO":"InterGlobe Aviation","INDUSINDBK":"IndusInd Bank","INDUSTOWER":"Indus Towers","INFY":"Infosys",
"INOXWIND":"Inox Wind","IOC":"Indian Oil","IRCTC":"IRCTC","IREDA":"IREDA","IRFC":"IRFC","ITC":"ITC","JINDALSTEL":"Jindal Steel","JIOFIN":"Jio Financial",
"JSWENERGY":"JSW Energy","JSWSTEEL":"JSW Steel","JUBLFOOD":"Jubilant FoodWorks","KALYANKJIL":"Kalyan Jewellers","KEI":"KEI Industries","KOTAKBANK":"Kotak Mahindra Bank",
"KPITTECH":"KPIT Technologies","LAURUSLABS":"Laurus Labs","LICHSGFIN":"LIC Housing Finance","LICI":"LIC","LODHA":"Macrotech Developers","LT":"Larsen & Toubro",
"LTF":"L&T Finance","LTIM":"LTIMindtree","LUPIN":"Lupin","M&M":"Mahindra & Mahindra","MANAPPURAM":"Manappuram Finance","MANKIND":"Mankind Pharma","MARICO":"Marico",
"MARUTI":"Maruti Suzuki","MAXHEALTH":"Max Healthcare","MAZDOCK":"Mazagon Dock","MCX":"Multi Commodity Exchange","MFSL":"Max Financial","MOTHERSON":"Motherson Sumi",
"MPHASIS":"Mphasis","MUTHOOTFIN":"Muthoot Finance","NATIONALUM":"National Aluminium","NAUKRI":"Info Edge","NBCC":"NBCC","NCC":"NCC","NESTLEIND":"Nestle India",
"NHPC":"NHPC","NMDC":"NMDC","NTPC":"NTPC","NYKAA":"Nykaa","OBEROIRLTY":"Oberoi Realty","OFSS":"Oracle Financial Services","OIL":"Oil India","ONGC":"ONGC",
"PAGEIND":"Page Industries","PATANJALI":"Patanjali Foods","PAYTM":"Paytm","PERSISTENT":"Persistent Systems","PETRONET":"Petronet LNG","PFC":"Power Finance Corporation",
"PHOENIXLTD":"Phoenix Mills","PIDILITIND":"Pidilite","PIIND":"PI Industries","PNB":"Punjab National Bank","PNBHOUSING":"PNB Housing","POLICYBZR":"PB Fintech",
"POLYCAB":"Polycab","POWERGRID":"Power Grid","PRESTIGE":"Prestige Estates","RBLBANK":"RBL Bank","RECLTD":"REC Ltd","RELIANCE":"Reliance Industries","RVNL":"RVNL",
"SAIL":"SAIL","SBICARD":"SBI Cards","SBILIFE":"SBI Life","SBIN":"State Bank of India","SHREECEM":"Shree Cement","SHRIRAMFIN":"Shriram Finance","SIEMENS":"Siemens",
"SOLARINDS":"Solar Industries","SONACOMS":"Sona BLW","SRF":"SRF","SUNPHARMA":"Sun Pharma","SUPREMEIND":"Supreme Industries","SUZLON":"Suzlon","SYNGENE":"Syngene",
"TATACHEM":"Tata Chemicals","TATACONSUM":"Tata Consumer","TATAELXSI":"Tata Elxsi","TATAMOTORS":"Tata Motors","TATAPOWER":"Tata Power","TATASTEEL":"Tata Steel",
"TATATECH":"Tata Technologies","TCS":"TCS","TECHM":"Tech Mahindra","TIINDIA":"Tube Investments","TITAGARH":"Titagarh","TITAN":"Titan Company","TORNTPHARM":"Torrent Pharma",
"TORNTPOWER":"Torrent Power","TRENT":"Trent","TVSMOTOR":"TVS Motor","ULTRACEMCO":"UltraTech Cement","UNIONBANK":"Union Bank of India","UNITDSPR":"United Spirits",
"UNOMINDA":"Uno Minda","UPL":"UPL","VBL":"Varun Beverages","VEDL":"Vedanta","VOLTAS":"Voltas","WIPRO":"Wipro","YESBANK":"Yes Bank","ZYDUSLIFE":"Zydus Lifesciences",
}
ALIAS = {"LT":["l&t"],"SBIN":["sbi"],"IOC":["iocl"],"M&M":["m&m"],"EICHERMOT":["royal enfield"],"ETERNAL":["zomato"],
 "TATAMOTORS":["tmpv","tmcv"],"HINDUNILVR":["hul"],"DRREDDY":["dr reddy"],"NAUKRI":["naukri"],"HAL":["hal"],"BEL":["bel"],
 "HINDPETRO":["hindustan petroleum"],"MOTHERSON":["samvardhana motherson"],"NYKAA":["fsn e-commerce"],"PAYTM":["one97"]}
YAHOO = {"M&M":"M%26M.NS","ETERNAL":"ETERNAL.NS","TATAMOTORS":"TMPV.NS","LTF":"LTF.NS","IDEA":"IDEA.NS"}

POS = ["record profit","profit jumps","profit rises","profit surges","net profit up","profit up","bags order","wins order","order win",
 "secures order","order worth","upgrade","buy rating","target price raised","raises target","beats estimates","strong q","dividend",
 "bonus issue","acquisition","approval","surges","rallies","record high","jumps","gains","stake buy"]
NEG = ["falls","slumps","loss","downgrade","probe","fraud","penalty","cuts target","misses","plunges","resigns","raid","ban",
 "default","tumbles","drops","sell rating","decline","fine"]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=20).read()

def about(title, sym, name):
    """Headline must mention the company (name/alias, any case) or its SYMBOL in capitals."""
    t = title.lower()
    for k in [name.lower()] + ALIAS.get(sym, []):
        if re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", t):
            return True
    return bool(re.search(r"(?<![A-Za-z0-9])" + re.escape(sym) + r"(?![A-Za-z0-9])", title))

def headlines(sym, name):
    q = urllib.parse.quote(f'"{name}" stock when:1d')
    root = ET.fromstring(get(f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"))
    out = []
    for it in root.iter("item"):
        h = {"title": it.findtext("title", ""), "link": it.findtext("link", ""),
             "source": it.findtext("source", ""), "date": it.findtext("pubDate", "")}
        if about(h["title"], sym, name):
            out.append(h)
    return out[:10]

def score(title):
    t = title.lower()
    return sum(k in t for k in POS) - sum(k in t for k in NEG)

def volume(sym):
    """Last trading day's volume vs previous 20-day average (Yahoo Finance, end of day)."""
    try:
        tk = YAHOO.get(sym, urllib.parse.quote(sym, safe="-") + ".NS")
        j = json.loads(get(f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}?range=2mo&interval=1d"))
        r = j["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        rows = [(t, c, v) for t, c, v in zip(r["timestamp"], q["close"], q["volume"]) if c and v]
        if len(rows) < 12:
            return None
        last = rows[-1]
        prev = [v for _, _, v in rows[-21:-1]]
        avg = sum(prev) / len(prev)
        d = datetime.fromtimestamp(last[0], timezone(timedelta(hours=5, minutes=30))).strftime("%d %b")
        return {"ratio": round(last[2] / avg, 2), "vol": int(last[2]), "avg": int(avg),
                "price": round(last[1], 2), "chg": round((last[1] / rows[-2][1] - 1) * 100, 2), "asof": d}
    except Exception as e:
        print("no volume", sym, e)
        return None

results = []
for sym, name in STOCKS.items():
    try:
        hs = headlines(sym, name)
    except Exception as e:
        print("skip", sym, e); continue
    scored = [(score(h["title"]), h) for h in hs]
    pos = [h for s, h in scored if s > 0]
    net = sum(s for s, _ in scored)
    if pos and net > 0:
        results.append({"symbol": sym, "name": name, "score": min(100, 50 + net * 10),
                        "news": pos[:4], "vol": volume(sym)})
        time.sleep(0.5)
    time.sleep(0.7)

results.sort(key=lambda r: -r["score"])
ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
json.dump({"updated": ist.strftime("%Y-%m-%d %H:%M IST"), "date": ist.strftime("%Y-%m-%d"),
           "scanned": len(STOCKS), "stocks": results}, open("data.json", "w"), indent=1, ensure_ascii=False)
print(len(results), "of", len(STOCKS), "stocks have positive news")
