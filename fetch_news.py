"""Daily fetch: Google News -> positive news F&O stocks + Yahoo volume -> data.json"""
import json, re, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

STOCKS = {
 "RELIANCE":"Reliance Industries","TCS":"TCS","INFY":"Infosys","HDFCBANK":"HDFC Bank","ICICIBANK":"ICICI Bank",
 "SBIN":"State Bank of India","AXISBANK":"Axis Bank","KOTAKBANK":"Kotak Mahindra Bank","LT":"Larsen & Toubro",
 "ITC":"ITC","HAL":"Hindustan Aeronautics","BEL":"Bharat Electronics","TITAN":"Titan Company","EICHERMOT":"Eicher Motors",
 "NTPC":"NTPC","IOC":"Indian Oil","ONGC":"ONGC","BPCL":"BPCL","TATAMOTORS":"Tata Motors","MARUTI":"Maruti Suzuki",
 "M&M":"Mahindra & Mahindra","BAJFINANCE":"Bajaj Finance","SUNPHARMA":"Sun Pharma","CIPLA":"Cipla","DRREDDY":"Dr Reddys",
 "TATASTEEL":"Tata Steel","JSWSTEEL":"JSW Steel","HINDALCO":"Hindalco","ADANIPORTS":"Adani Ports","POWERGRID":"Power Grid",
 "COALINDIA":"Coal India","BHARTIARTL":"Bharti Airtel","HCLTECH":"HCL Technologies","WIPRO":"Wipro","TECHM":"Tech Mahindra",
 "DIXON":"Dixon Technologies","BHEL":"BHEL","RVNL":"RVNL","IRCTC":"IRCTC","MAZDOCK":"Mazagon Dock","BDL":"Bharat Dynamics",
 "TRENT":"Trent","ZOMATO":"Eternal","DLF":"DLF","HINDUNILVR":"Hindustan Unilever","NESTLEIND":"Nestle India",
 "ASIANPAINT":"Asian Paints","ULTRACEMCO":"UltraTech Cement","GRASIM":"Grasim","VEDL":"Vedanta","SAIL":"SAIL",
}
# Extra names used in headlines
ALIAS = {"LT":["l&t","larsen"],"SBIN":["sbi"],"IOC":["iocl","indian oil corporation"],"M&M":["m&m"],
 "HAL":["hal"],"BEL":["bel"],"TITAN":["titan"],"EICHERMOT":["royal enfield"],"ZOMATO":["zomato"],
 "TATAMOTORS":["tmpv","tmcv"],"HINDUNILVR":["hul"],"DRREDDY":["dr reddy's","dr reddy"],"BAJFINANCE":["bajaj finserv"] and ["bajaj finance"]}
# Yahoo ticker fixes
YAHOO = {"M&M":"M%26M.NS","ZOMATO":"ETERNAL.NS","TATAMOTORS":"TMPV.NS"}

POS = ["record profit","profit jumps","profit rises","profit surges","net profit up","profit up","bags order","wins order",
 "order win","secures order","order worth","upgrade","buy rating","target price raised","raises target","beats estimates",
 "strong q","dividend","bonus issue","acquisition","approval","surges","rallies","record high","jumps","gains","stake buy"]
NEG = ["falls","slumps","loss","downgrade","probe","fraud","penalty","cuts target","misses","plunges","resigns","raid",
 "ban","default","tumbles","drops","sell rating","decline","fine"]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=20).read()

def about(title, sym, name):
    t = title.lower()
    keys = [name.lower(), sym.lower()] + ALIAS.get(sym, [])
    return any(re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", t) for k in keys)

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
    """Latest daily volume vs previous 20-day average (Yahoo Finance, no key)."""
    try:
        tk = YAHOO.get(sym, sym + ".NS")
        j = json.loads(get(f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}?range=2mo&interval=1d"))
        r = j["chart"]["result"][0]
        ts, q = r["timestamp"], r["indicators"]["quote"][0]
        rows = [(t, c, v) for t, c, v in zip(ts, q["close"], q["volume"]) if c and v]
        if len(rows) < 12:
            return None
        last = rows[-1]
        prev = [v for _, _, v in rows[-21:-1]]
        avg = sum(prev) / len(prev)
        chg = (last[1] / rows[-2][1] - 1) * 100
        d = datetime.fromtimestamp(last[0], timezone(timedelta(hours=5, minutes=30))).strftime("%d %b")
        return {"ratio": round(last[2] / avg, 2), "vol": int(last[2]), "avg": int(avg),
                "chg": round(chg, 2), "asof": d}
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
                        "news": pos[:3], "vol": volume(sym)})
        time.sleep(1)
    time.sleep(1)

results.sort(key=lambda r: -r["score"])
ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
json.dump({"updated": ist.strftime("%Y-%m-%d %H:%M IST"), "date": ist.strftime("%Y-%m-%d"), "stocks": results},
          open("data.json", "w"), indent=1, ensure_ascii=False)
print(len(results), "stocks with positive news")
