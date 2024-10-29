import requests
import json
import time
from datetime import datetime
import pytz

lastHash = None
ltcAddy = 'Le15Q6dP4X2W2aCKAm3deC47FT9mwudTch'
webhookURL = "https://discord.com/api/webhooks/1300818347117772810/plTHxcIMmKmo6Dfu8SC3qfQ3R588Xevv2idR7l6drRMbrYO_fzAUwOhvco-6BqBRAfzZ"

Lodalassan = {
    "confirmed": "✅",
    "unconfirmed": "⏳",
    "highvalue": "💰",
    "lowvalue": "💸",
    "alert": "🚨",
    "clock": "⏰",
    "chart": "📊"
}

def FormatTimestamp(timestamp):
    return f"<t:{int(timestamp)}:F>"

def GetTransactionAge(timestamp):
    currentTime = time.time()
    return int((currentTime - timestamp) / 60)

def GetMarketData():
    try:
        response = requests.get('https://api.coingecko.com/api/v3/coins/litecoin')
        data = response.json()
        return {
            'priceusd': data['market_data']['current_price']['usd'],
            'pricechange24h': data['market_data']['price_change_percentage_24h'],
            'volume24h': data['market_data']['total_volume']['usd'],
            'marketcap': data['market_data']['market_cap']['usd']
        }
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None

def CheckTransactions():
    global lastHash
    try:
        response = requests.get(f'https://api.blockcypher.com/v1/ltc/main/addrs/{ltcAddy}/full').json()
        if 'txs' in response:
            latestTransaction = response['txs'][0]
            latestHash = latestTransaction['hash']
            
            if latestHash != lastHash:
                totalReceived = sum(output['value'] / 1e8 for output in latestTransaction['outputs'] 
                                  if 'addresses' in output and ltcAddy in output['addresses'])
                
                if totalReceived > 0:
                    marketData = GetMarketData()
                    if marketData:
                        totalReceivedUSD = totalReceived * marketData['priceusd']
                        S3NDTransactionNotification(latestTransaction, totalReceivedUSD, marketData)
                    
                lastHash = latestHash
    except Exception as e:
        print(f"Error checking transactions: {e}")

def S3NDTransactionNotification(transaction, amountUSD, marketData):
    inputAddress = transaction['inputs'][0]['addresses'][0] if 'inputs' in transaction else 'Unknown'
    confirmations = transaction.get('confirmations', 0)
    
    try:
        timestamp = int(datetime.fromisoformat(transaction['received'].replace("Z", "+00:00")).timestamp())
    except Exception:
        timestamp = int(time.time())
    
    try:
        exchangeRateResponse = requests.get("https://api.coingecko.com/api/v3/exchange_rates").json()
        usdToInrRate = exchangeRateResponse['rates']['inr']['value']
    except Exception as e:
        print(f"Error fetching INR exchange rate: {e}")
        usdToInrRate = 75.0

    statusEmoji = Lodalassan['confirmed'] if confirmations > 2 else Lodalassan['unconfirmed']
    valueEmoji = Lodalassan['highvalue'] if amountUSD > 1000 else Lodalassan['lowvalue']
    
    embed = {
        "title": f"{statusEmoji} New LTC Transaction Detected {valueEmoji}",
        "color": 0x808080,
        "fields": [
            {
                "name": "💼 Transaction Details",
                "value": f"Hash: [{transaction['hash']}](https://live.blockcypher.com/ltc/tx/{transaction['hash']})\n"
                        f"Time: {FormatTimestamp(timestamp)}\n"
                        f"Age: {GetTransactionAge(timestamp)} minutes",
                "inline": False
            },
            {
                "name": f"{Lodalassan['chart']} Amount",
                "value": f"USD: ${amountUSD:.2f} (LTC {amountUSD/marketData['priceusd']:.4f})\n",
                "inline": True
            },
            {
                "name": "👤 Sender",
                "value": f"`{inputAddress}`",
                "inline": True
            },
            {
                "name": "📊 Market Status",
                "value": f"Price: ${marketData['priceusd']:.2f} (₹{marketData['priceusd'] * usdToInrRate:.2f})\n"
                         f"24h Change: {marketData['pricechange24h']:.2f}%\n"
                         f"24h Volume: ${marketData['volume24h']:,.0f}",
                "inline": False
            }
        ],
        "footer": {
            "text": f"Confirmations: {confirmations} | Market Cap: ${marketData['marketcap']:,.0f} (₹{marketData['marketcap'] * usdToInrRate:,.0f})"
        },
        "timestamp": datetime.now(pytz.UTC).isoformat()
    }

    data = {
        "content": f"{Lodalassan['alert']} New transaction detected! Amount: ${amountUSD:.2f}",
        "embeds": [embed]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(webhookURL, data=json.dumps(data), headers=headers)
        if response.status_code != 204:
            print(f"Failed to send webhook: {response.status_code}")
    except Exception as e:
        print(f"Error sending notification: {e}")

def Main():
    alertEmoji = Lodalassan['alert']
    print(f"{alertEmoji} Starting LTC Transaction Monitor...".encode("ascii", errors="ignore").decode())
    errorCount = 0
    while True:
        try:
            CheckTransactions()
            errorCount = 0
            time.sleep(60)
        except Exception as e:
            errorCount += 1
            print(f"Error in main loop: {e}")
            if errorCount > 5:
                print("Too many errors, increasing wait time...")
                time.sleep(300)
            else:
                time.sleep(60)


if __name__ == "__main__":
    Main()
