import requests
import datetime
import pytz
import os

# GitHub Secrets에서 불러오기
ETHERSCAN_KEY = os.getenv("ETHERSCAN_KEY")   # Ethers API v2 키
TELEGRAM_BOT = os.getenv("TELEGRAM_BOT")     
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TOKEN = "0x83e137cf30dc28e5e6d28a63e841aa3bc6af1a99"  # SZPN
POOL_ADDRESS = "0xb3cf454ba8bd35134c14f7b5426d6d70585d0903"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})

def get_kst_range():
    kst = pytz.timezone("Asia/Seoul")
    now = datetime.datetime.now(kst)

    start_kst = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_kst   = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    start_utc = start_kst.astimezone(pytz.utc).timestamp()
    end_utc   = end_kst.astimezone(pytz.utc).timestamp()

    return int(start_utc), int(end_utc)

def check_liquidity():
    start_utc, end_utc = get_kst_range()

    # 🔥 Ethers API v2 (BscScan v2) endpoint
    url = (
        f"https://api.etherscan.io/v2/api?"
        f"chainid=56&"
        f"module=account&"
        f"action=tokentx&"
        f"address={POOL_ADDRESS}&"
        f"contractaddress={TOKEN}&"
        f"page=1&offset=3000&"
        f"sort=asc&"
        f"apikey={ETHERSCAN_KEY}"
    )

    data = requests.get(url).json()
    txs = data.get("result", [])

    count90 = count300 = count1500 = count3000 = 0

    for tx in txs:
        if tx["to"].lower() != POOL_ADDRESS.lower():
            continue

        ts = int(tx["timeStamp"])
        if ts < start_utc or ts > end_utc:
            continue

        value = int(tx["value"]) / 1e18  # SZPN Decimals 18

        if value == 90:
            count90 += 1
        elif value == 300:
            count300 += 1
        elif value == 1500:
            count1500 += 1
        elif value == 3000:
            count3000 += 1

    total = (90 * count90 +
             300 * count300 +
             1500 * count1500 +
             3000 * count3000)

    report = (
        f"📊 Hive3 유동성 — 오늘(KST)\n\n"
        f"90: {count90}회\n"
        f"300: {count300}회\n"
        f"1500: {count1500}회\n"
        f"3000: {count3000}회\n\n"
        f"총 유동성 참여: {total} SZPN"
    )

    send_msg(report)

if __name__ == "__main__":
    check_liquidity()
