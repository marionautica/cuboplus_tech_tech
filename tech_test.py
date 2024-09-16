import requests
from datetime import datetime, timedelta

# Base URL for the mempool.space API 
base_url = "https://mempool.space/api"

# Bitcoin address
address = "32ixEdVJWo3kmvJGMTZq5jAQVZZeuwnqzo"

# Function to get on-chain balance
def get_onchain_balance():
    endpoint = f"/address/{address}"
    response = requests.get(base_url + endpoint)
    
    if response.status_code == 200:
        data = response.json()
        # On-chain balance = total received - total spent (in sats)
        onchain_balance = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
        return onchain_balance / 1e8  # Convert sats to BTC
    else:
        print("Error fetching on-chain balance:", response.status_code, response.text)
        return None

# Function to get mempool balance (
def get_mempool_balance():
    endpoint = f"/address/{address}/txs/mempool"
    response = requests.get(base_url + endpoint)
    
    if response.status_code == 200:
        data = response.json()
        # Sum the outputs of unconfirmed transactions in mempool (in sats)
        mempool_balance = sum(tx['vout'][0]['value'] for tx in data)
        return mempool_balance / 1e8  # Convert sats to BTC
    else:
        print("Error fetching mempool balance:", response.status_code, response.text)
        return None

# Function to calculate balance variation over a specific period 
def get_balance_variation(days):
    endpoint = f"/address/{address}/txs"
    response = requests.get(base_url + endpoint)
    
    if response.status_code == 200:
        data = response.json()
        cutoff_time = datetime.now() - timedelta(days=days)
        balance_variation = 0
        
        for tx in data:
            # Ensure the transaction has a 'block_time' and is confirmed
            if tx['status']['confirmed'] and 'block_time' in tx['status']:
                tx_time = datetime.utcfromtimestamp(tx['status']['block_time'])
                
                if tx_time >= cutoff_time:
                    # Sum the values of received and spent transactions
                    received = sum(vout['value'] for vout in tx['vout'] if address in vout.get('scriptpubkey_address', ''))
                    spent = sum(vin['prevout']['value'] for vin in tx['vin'] if vin['prevout'].get('scriptpubkey_address', '') == address)
                    balance_variation += (received - spent)  # Variation in sats
        
        return balance_variation / 1e8  # Convert sats to BTC
    else:
        print("Error fetching transaction history:", response.status_code, response.text)
        return None

# Fetch and print the data
onchain_balance = get_onchain_balance()
mempool_balance = get_mempool_balance()
balance_variation_30_days = get_balance_variation(30)
balance_variation_7_days = get_balance_variation(7)

# Print results
print(f"On-chain Balance: {onchain_balance} BTC")
print(f"Mempool Balance: {mempool_balance} BTC")
print(f"Balance variation in the last 30 days: {balance_variation_30_days} BTC")
print(f"Balance variation in the last 7 days: {balance_variation_7_days} BTC")