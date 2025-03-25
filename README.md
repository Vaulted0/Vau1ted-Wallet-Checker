# Solana Wallet Activity Checker

A Python script that checks Solana wallet addresses for recent activity (within the last 2 weeks).

## Features

- Checks multiple Solana RPC endpoints for reliability
- Automatically retries failed requests with exponential backoff
- Saves progress continuously to prevent data loss
- Categorizes wallets as active or inactive
- Shows detailed progress and results

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

1. Create a `wallets.txt` file in the same directory as the script
2. Add Solana wallet addresses to `wallets.txt`, one per line
3. Run the script:
   ```
   python "solana wallet checker.py"
   ```

## Output Files

The script will create two files:
- `active_wallets.txt`: Contains wallet addresses with activity in the last 2 weeks
- `inactive_wallets.txt`: Contains wallet addresses with no recent activity

## Example wallets.txt Format

```
4jeg1JVXoKJUaPdTLYYXP9xq93buUk3AsfHy9KEcH8BE
YOUR WALLETS HERE
```

## Notes

- The script uses multiple RPC endpoints to ensure reliable results
- Progress is saved after each wallet check
- If the script is interrupted, you can restart it and it will continue from where it left off
- A wallet is considered "active" if it has had any transaction in the last 2 weeks

## Credits

Created by @vaulted0 