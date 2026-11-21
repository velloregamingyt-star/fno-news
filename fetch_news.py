"""Daily fetch: Google News RSS -> positive-news F&O stocks -> data.json (no API key, stdlib only)."""
import json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# Add more F&O stocks here: "SYMBOL": "search name"
STOCKS = {
 "RELIANCE":"Reliance Industries","TCS":"TCS","INFY":"Infosys","HDFCBANK":"HDFC Bank","ICICIBANK":"ICICI Bank",
 "SBIN":"State Bank of India","AXISBANK":"Axis Bank","KOTAKBANK":"Kotak Mahindra Bank","LT":"Larsen & Toubro",
 "ITC":"ITC","HAL":"Hindustan Aeronautics","BEL":"Bharat Electronics","TITAN":"Titan Company","EICHERMOT":"Eicher Motors",
 "NTPC":"NTPC","IOC":"Indian Oil","ONGC":"ONGC","BPCL":"BPCL","TATAMOTORS":"Tata Motors","MARUTI":"Maruti Suzuki",
 "M&M":"Mahindra & Mahindra","BAJFINANCE":"Bajaj Finance","SUNPHARMA":"Sun Pharma","CIPLA":"Cipla","DRREDDY":"Dr Reddys",
 "TATASTEEL":"Tata Steel","JSWSTEEL":"JSW Steel","HINDALCO":"Hindalco","ADANIPORTS":"Adani Ports","POWERGRID":"Power Grid",
 "COALINDIA":"Coal India","BHARTIARTL":"Bharti Airtel","HCLTECH":"HCL Technologies","WIPRO":"Wipro","TECHM":"Tech Mahindra",
 "DIXON":"Dixon Technologies","BHEL":"BHEL","RVNL":"RVNL","IRCTC":"IRCTC","MAZDOCK":"Mazagon Dock","BDL":"Bharat Dynamics",
 "TRENT":"Trent","ZOMATO":"Eternal Zomato","DLF":"DLF","HINDUNILVR":"Hindustan Unilever","NESTLEIND":"Nestle India",
 "ASIANPAINT":"Asian Paints","ULTRACEMCO":"UltraTech Cement","GRASIM":"Grasim","VEDL":"Vedanta","SAIL":"SAIL",
}
POS = ["record profit","profit jumps","profit rises","profit surges","net profit up","profit up","bags order","wins order",
 "order win","secures order","order worth","upgrade","buy rating","target price raised","raises target","beats estimates",
 "strong q","dividend","bonus issue","acquisition","approval","surges","rallies","record high","jumps","gains","stake buy"]
NEG = ["falls","slumps","loss","downgrade","probe","fraud","penalty","cuts target","misses","plunges","resigns","raid",
 "ban","default","tumbles","drops","sell rating","decline","fine"]

def headlines(name):
    q = urllib.parse.quote(f'"{name}" stock when:1d')
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=20).read())
    out = []
    for it in root.iter("item"):
        out.append({"title": it.findtext("title", ""), "link": it.findtext("link", ""),
                    "source": it.findtext("source", ""), "date": it.findtext("pubDate", "")})
    return out[:10]

def score(title):
    t = title.lower()
    return sum(k in t for k in POS) - sum(k in t for k in NEG)

results = []
for sym, name in STOCKS.items():
    try:
        hs = headlines(name)
    except Exception as e:
        print("skip", sym, e); continue
    scored = [(score(h["title"]), h) for h in hs]
    pos = [h for s, h in scored if s > 0]
    net = sum(s for s, _ in scored)
    if pos and net > 0:
        results.append({"symbol": sym, "name": name, "score": min(100, 50 + net * 10),
                        "news": pos[:3]})
    time.sleep(1)

results.sort(key=lambda r: -r["score"])
ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
json.dump({"updated": ist.strftime("%Y-%m-%d %H:%M IST"), "date": ist.strftime("%Y-%m-%d"), "stocks": results},
          open("data.json", "w"), indent=1, ensure_ascii=False)
print(len(results), "stocks with positive news")
