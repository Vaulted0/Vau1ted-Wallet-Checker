import requests
import time
from datetime import datetime, timedelta
import random
import json

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

def get_wallet_transactions(wallet_address, rpc_endpoint=None, max_retries=3):
    """Fetch recent transactions for a Solana wallet using a specific endpoint"""
    base_delay = 1  # Start with 1 second delay
    max_delay = 30  # Maximum delay between retries
    
    if rpc_endpoint is None:
        rpc_endpoint = get_random_rpc()
    
    attempt = 1
    while attempt <= max_retries:
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
    
    return None

def check_wallet_with_all_nodes(wallet_address):
    """Check a wallet's activity across all RPC nodes"""
    print(f"\nPerforming thorough check for wallet: {wallet_address}")
    two_weeks_ago = datetime.now() - timedelta(days=14)
    
    for endpoint in RPC_ENDPOINTS:
        print(f"\nTrying endpoint: {endpoint}")
        transactions = get_wallet_transactions(wallet_address, endpoint)
        if transactions is not None:  # If we got a valid response
            if transactions:  # If we found transactions
                # Check if any transaction is within the last 2 weeks
                for tx in transactions:
                    tx_time = datetime.fromtimestamp(tx['blockTime'])
                    if tx_time >= two_weeks_ago:
                        print(f"Found recent activity from {tx_time}")
                        return True  # Wallet is active
                print("Found transactions but none are recent")
            else:
                print("No transactions found")
        else:
            print("Failed to get response from endpoint")
    return False  # All nodes returned inactive or failed

def filter_active_wallets(wallet_list):
    """Filter wallets that have had activity in the last 2 weeks"""
    active_wallets = []
    inactive_wallets = []
    two_weeks_ago = datetime.now() - timedelta(days=14)
    total_wallets = len(wallet_list)
    
    for index, wallet in enumerate(wallet_list, 1):
        wallet_address = wallet['trackedWalletAddress']
        print(f"\nChecking wallet {index}/{total_wallets}: {wallet_address}")
        
        # Initial check with random endpoint
        transactions = get_wallet_transactions(wallet_address)
            
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
                # If initially marked as inactive, check with all nodes
                print("Initial check shows inactive, performing thorough check...")
                if check_wallet_with_all_nodes(wallet_address):
                    active_wallets.append(wallet)
                    print("Wallet is active after thorough check")
                else:
                    inactive_wallets.append(wallet)
                    print("Wallet confirmed inactive after checking all nodes")
        else:
            # If initially marked as inactive, check with all nodes
            print("Initial check shows inactive, performing thorough check...")
            if check_wallet_with_all_nodes(wallet_address):
                active_wallets.append(wallet)
                print("Wallet is active after thorough check")
            else:
                inactive_wallets.append(wallet)
                print("Wallet confirmed inactive after checking all nodes")
            
        # Be kind to the RPC server
        time.sleep(0.5)  # Base delay between wallets
        
        # Save progress after each wallet
        with open('active_wallets.json', 'w', encoding='utf-8') as f:
            json.dump(active_wallets, f, indent=2, ensure_ascii=False)
        with open('inactive_wallets.json', 'w', encoding='utf-8') as f:
            json.dump(inactive_wallets, f, indent=2, ensure_ascii=False)
    
    return active_wallets, inactive_wallets

if __name__ == "__main__":
    # Print banner
    print(BANNER)
    print("Solana Wallet Activity Checker")
    print("Twitter: @vaulted0")
    print("=" * 50)
    
    # Load wallet list from JSON file
    with open('wallets.json', 'r', encoding='utf-8') as f:
        wallets = json.load(f)
    
    print(f"Loaded {len(wallets)} wallets to check")
    active, inactive = filter_active_wallets(wallets)
    
    print("\nFinal Results:")
    print(f"Active wallets (last 2 weeks): {len(active)}")
    print(f"Inactive wallets: {len(inactive)}\n")
    print("Results saved to active_wallets.json and inactive_wallets.json")
