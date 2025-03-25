# Vaulted's Activity Checker

A Python script that checks Solana wallet addresses for recent activity (within the last 2 weeks).

## Features

- Checks multiple Solana RPC endpoints for reliability
- Automatically retries failed requests with exponential backoff
- Saves progress continuously to prevent data loss
- Categorizes wallets as active or inactive
- Shows detailed progress and results
- Preserves wallet metadata (name, emoji, alerts status)

## Requirements

- Python 3.6 or higher
- Required Python packages:
  ```
  requests==2.31.0
  ```

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Create a `wallets.json` file in the same directory as the script
2. Add wallet data in JSON format (see example below, exporting from any major platform will work!)
3. Run the script:
   ```
   python "solana wallet checker.py"
   ```

## Output Files

The script will create two JSON files:
- `active_wallets.json`: Contains wallet data for addresses with activity in the last 2 weeks
- `inactive_wallets.json`: Contains wallet data for addresses with no recent activity

## Example wallets.json Format

```json
[
  {
    "trackedWalletAddress": "4jeg1JVXoKJUaPdTLYYXP9xq93buUk3AsfHy9KEcH8BE",
    "name": "Example Wallet",
    "emoji": "👻",
    "alertsOn": false
  }
]
```

## Notes

- The script uses multiple RPC endpoints to ensure reliable results
- Progress is saved after each wallet check
- If the script is interrupted, you can restart it and it will continue from where it left off
- A wallet is considered "active" if it has had any transaction in the last 2 weeks
- All original wallet metadata (name, emoji, alerts status) is preserved in the output files

## Credits

- Created by @vaulted0 
- If you would like to support me --> FGcKb4EQPNp12DoBfp12fwx1abBqQzqYBGuyRqVau1t
