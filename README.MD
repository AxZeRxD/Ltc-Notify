# LTC Transaction Monitor

This Python script continuously monitors a specified Litecoin (LTC) wallet address for new transactions and sends a notification to a Discord webhook whenever a new transaction is detected. Notifications include details about the transaction and current market data for LTC.

## Features

- **LTC Transaction Monitoring**: Checks for incoming transactions to a specified LTC address.
- **Discord Notifications**: Sends transaction alerts to a Discord channel using a webhook.
- **Market Data**: Fetches the latest LTC price, 24-hour price change, and volume from CoinGecko.
- **Exchange Rate Conversion**: Converts the received amount to both USD and INR (using CoinGecko's exchange rates).
- **Enhanced Notifications**: Includes transaction details like sender address, confirmation status, timestamp, and market stats.

## Requirements

- Python 3.x
- `requests` library
- `pytz` library

You can install the necessary Python libraries by running:

```bash
pip install requests pytz
```

## Setup and Configuration

1. **Set Wallet Address**: Update the `ltcAddy` variable with your LTC address.
2. **Discord Webhook URL**: Set the `webhookURL` variable with your Discord webhook URL.
3. **Lodalassan Emoji Mappings**: Customize emojis for transaction status and alerts in the `Lodalassan` dictionary if desired.

## Usage

Run the script by executing:

```bash
python aizer.py
```

### Main Functions

- **`Main()`**: Starts the transaction monitoring loop.
- **`CheckTransactions()`**: Checks the latest transaction on the specified LTC address.
- **`S3NDTransactionNotification()`**: Formats transaction data and sends it to the Discord webhook.
- **`GetMarketData()`**: Fetches LTC market data, including price and market cap, from CoinGecko.
- **`FormatTimestamp()` and `GetTransactionAge()`**: Utility functions to format timestamps for Discord and calculate transaction age.

## Example Notification

When a new transaction is detected, the Discord notification will include:
- Transaction Hash and Link
- Time and Age of Transaction
- Amount in USD and LTC
- Sender Address
- LTC Market Price in USD and INR
- 24-hour Price Change and Volume
- Confirmation Status

### Customization

You can adjust the script to set:
- The frequency of checking transactions (`time.sleep(60)` can be adjusted in the `Main()` function).
- The threshold for “high-value” and “low-value” transactions by changing the conditional in the `S3NDTransactionNotification()` function.

## Error Handling

The script handles errors gracefully, with retry logic in the main loop. If the script encounters too many errors, it increases the wait time between checks to reduce API load and rate limiting.

## Notes

- Ensure the Litecoin address and webhook URL are correct.
- Be aware of the API rate limits for CoinGecko and BlockCypher, as they can affect the frequency of transaction checks.

## License

This project is open-source and free to use.
