import requests
import time
from datetime import datetime, timedelta
import random

# ASCII Art Banner
BANNER = """
 ██▒   █▓ ▄▄▄       █    ██  ██▓  ▄▄▄█████▓▓█████ ▓█████▄ 
▓██░   █▒▒████▄     ██  ▓██▒▓██▒  ▓  ██▒ ▓▒▓█   ▀ ▒██▀ ██▌
 ▓██  █▒░▒██  ▀█▄  ▓██  ▒██░▒██░  ▒ ▓██░ ▒░▒███   ░██   █▌
  ▒██ █░░░██▄▄▄▄██ ▓▓█  ░██░▒██░  ░ ▓██▓ ░ ▒▓█  ▄ ░▓█▄   ▌
   ▒▀█░   ▓█   ▓██▒▒▒█████▓ ░██████▒▒██▒ ░ ░▒████▒░▒████▓ 
   ░ ▐░   ▒▒   ▓▒█░░▒▓▒ ▒ ▒ ░ ▒░▓  ░▒ ░░   ░░ ▒░ ░ ▒▒▓  ▒ 
   ░ ░░    ▒   ▒▒ ░░░▒░ ░ ░ ░ ░ ▒  ░  ░     ░ ░  ░ ░ ▒  ▒ 
     ░░    ░   ▒    ░░░ ░ ░   ░ ░   ░         ░    ░ ░  ░ 
      ░        ░  ░   ░         ░  ░          ░  ░   ░    
     ░                                             ░      
"""

# List of RPC endpoints to try
RPC_ENDPOINTS = [
    "https://go.getblock.io/4136d34f90a6488b84214ae26f0ed5f4",
    "https://solana.leorpc.com/?api_key=FREE",
    "https://endpoints.omniatech.io/v1/sol/mainnet/public",
    "https://solana.api.onfinality.io/public",
    "https://api.mainnet-beta.solana.com"
]

def get_random_rpc():
    """Get a random RPC endpoint"""
    return random.choice(RPC_ENDPOINTS)

def get_wallet_transactions(wallet_address, max_endpoints=3):
    """Fetch recent transactions for a Solana wallet trying multiple endpoints"""
    base_delay = 1  # Start with 1 second delay
    max_delay = 30  # Maximum delay between retries
    
    # Try multiple endpoints
    for endpoint_attempt in range(max_endpoints):
        attempt = 1
        rpc_endpoint = get_random_rpc()
        
        while True:  # Keep trying current endpoint until success or max retries
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    wallet_address,
                    {"limit": 20}
                ]
            }
            
            try:
                print(f"Attempt {attempt} using {rpc_endpoint}")
                response = requests.post(rpc_endpoint, json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data:
                        if data['result']:
                            print("Success!")
                            return data['result']
                        return []  # Empty result is valid
                    elif 'error' in data:
                        print(f"RPC Error: {data['error']}")
                elif response.status_code == 429:  # Rate limit
                    print(f"Rate limited, waiting {base_delay} seconds...")
                else:
                    print(f"HTTP Error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print("Request timed out")
            except requests.exceptions.ConnectionError:
                print("Connection error")
            except Exception as e:
                print(f"Error on attempt {attempt}: {e}")
            
            # Calculate delay with exponential backoff
            delay = min(base_delay * (1.5 ** (attempt - 1)), max_delay)
            print(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)
            attempt += 1
            
            # If we've tried too many times with this endpoint, try another one
            if attempt > 3:
                print(f"Switching to different endpoint after {attempt} attempts")
                break
    
    return None

def filter_active_wallets(wallet_list):
    """Filter wallets that have had activity in the last 2 weeks"""
    active_wallets = []
    inactive_wallets = []
    two_weeks_ago = datetime.now() - timedelta(days=14)
    total_wallets = len(wallet_list)
    
    for index, wallet in enumerate(wallet_list, 1):
        wallet = wallet.strip()
        if not wallet:
            continue
            
        print(f"\nChecking wallet {index}/{total_wallets}: {wallet}")
        transactions = get_wallet_transactions(wallet)
            
        if transactions:
            # Check if any transaction is within the last 2 weeks
            recent_activity = False
            for tx in transactions:
                tx_time = datetime.fromtimestamp(tx['blockTime'])
                if tx_time >= two_weeks_ago:
                    recent_activity = True
                    print(f"Found recent activity from {tx_time}")
                    break
            
            if recent_activity:
                active_wallets.append(wallet)
                print("Wallet is active")
            else:
                inactive_wallets.append(wallet)
                print("No recent activity found - Wallet is inactive")
        else:
            inactive_wallets.append(wallet)
            print("No transactions found - Wallet is inactive")
            
        # Be kind to the RPC server
        time.sleep(0.5)  # Base delay between wallets
        
        # Save progress after each wallet
        with open('active_wallets.txt', 'w') as f:
            f.write("\n".join(active_wallets))
        with open('inactive_wallets.txt', 'w') as f:
            f.write("\n".join(inactive_wallets))
    
    return active_wallets, inactive_wallets

if __name__ == "__main__":
    # Print banner
    print(BANNER)
    print("Solana Wallet Activity Checker")
    print("Twitter: @vaulted0")
    print("=" * 50)
    
    # Load wallet list from file (one address per line)
    with open('wallets.txt', 'r') as f:
        wallets = f.readlines()
    
    print(f"Loaded {len(wallets)} wallets to check")
    active, inactive = filter_active_wallets(wallets)
    
    print("\nFinal Results:")
    print(f"Active wallets (last 2 weeks): {len(active)}")
    print(f"Inactive wallets: {len(inactive)}\n")
    print("Results saved to active_wallets.txt and inactive_wallets.txt")
