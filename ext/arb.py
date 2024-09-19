from web3 import Web3
from eth_abi import encode
import os
from dotenv import load_dotenv
import time
import sys
import random
import requests

load_dotenv()
blastrpc = os.getenv("ARB_RPC")
privatekeys = os.getenv("PRIVATE_KEY")

web3 = Web3(Web3.HTTPProvider(blastrpc))
chainId = web3.eth.chain_id
web3_brn = Web3(Web3.HTTPProvider("https://brn.rpc.caldera.xyz/http"))
chainId_brn = web3_brn.eth.chain_id

#connecting web3
if  web3.is_connected() == True:
    print("Web3 Connected ARB...\n")
else:
    print("Error Connecting Please Try Again Exit...")
    exit()
#connecting web3
if  web3_brn.is_connected() == True:
    print("Web3 Connected BRN...\n")
else:
    print("Error Connecting Please Try Again Exit...")
    exit()

def loading_message(message, duration):
    sys.stdout.write(message)
    sys.stdout.flush()
    for _ in range(duration):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1)  # Adjust speed of the loading effect
    sys.stdout.write('\n')

#log to txt file
def log(txt):
    f = open("lognya.txt", "a")
    f.write(txt+":"+str(chainId)+'\n')
    f.close()

def Executor(sender, key, amount, amountin, orderid, txhash):
    try:
        gasPrice = web3.eth.gas_price
        nonce = web3.eth.get_transaction_count(sender)
        bridgeaddr = web3.to_checksum_address('0x8D86c3573928CE125f9b2df59918c383aa2B514D') #for arb
        funcexcutor = bytes.fromhex('01a8f065')
        amountzero = 0
        bridgedmin = web3.from_wei(amountin, 'ether')
        
        enc_excutor = encode(['bytes32', 'address', 'uint256', 'uint256'], [orderid, sender, amountin, amountzero])
        data = web3.to_hex(funcexcutor+enc_excutor)

        gasAmount = web3.eth.estimate_gas({
            'chainId': chainId,
            'from': sender,
            'to': bridgeaddr,
            'value': amountin,
            'data': data,
            'gasPrice': gasPrice,
            'nonce': nonce
        })

        excutor_tx = {
            'chainId': chainId,
            'from': sender,
            'to': bridgeaddr,
            'value': amountin,
            'data': data,
            'gas': gasAmount,
            'gasPrice': gasPrice,
            'nonce': nonce
        }
        
        #sign & send the transaction
        tx_hash = web3.eth.send_raw_transaction(web3.eth.account.sign_transaction(excutor_tx, key).rawTransaction)
        #get transaction hash
        print(f'Processing Executor Bridge {bridgedmin} From ETH ARB TO ETH ARB')
        web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f'Executor Bridge {bridgedmin} From ETH ARB TO ETH ARB Success!')
        print(f'TX-ID : {str(web3.to_hex(tx_hash))}')
        print(f'')
        log(str(txhash))
    except Exception as e:
        print(f"Error: {e}")
        pass
        
def Get_Estimate(sender, key, amount):
    url = f"https://pricer.t1rn.io/estimate"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Origin": "https://bridge.t1rn.io",
        "Referer": "https://bridge.t1rn.io/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    
    data = {
        "fromAsset": "eth",
        "toAsset": "eth",
        "fromChain": "arbt",
        "toChain": "arbt", #arbt (arb) | bssp (base) | blss (blast) | opsp (op)
        "amountWei": str(amount),
        "executorTipUSD": 0,
        "overpayOptionPercentage": 0,
        "spreadOptionPercentage": 0
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    data = result.get('estimatedReceivedAmountWei', {})
    amounthex = data.get('hex')
    amountin = int(amounthex, 16)
    BLAST_BLAST(sender, key, amount, amountin)

def BidExecute(sender, key, amount, amountin, orderid, txhash):
    try:
        gasPrice = web3_brn.eth.gas_price
        gasPricePlus = web3_brn.from_wei(gasPrice, 'gwei')
        nonce = web3_brn.eth.get_transaction_count(sender)
        bidaddr = web3_brn.to_checksum_address('0x05C9e2dDfBa9120565c9588fd5d4464B85E77285') #for brn
        funcbid = bytes.fromhex('95627628')
        amountzero = 0
        bridgedmin = web3_brn.from_wei(amountin, 'ether')
        
        enc_bid = encode(['bytes32', 'uint256', 'address'], [orderid, amount, sender])
        data = web3_brn.to_hex(funcbid+enc_bid)

        gasAmount = web3_brn.eth.estimate_gas({
            'chainId': chainId_brn,
            'from': sender,
            'to': bidaddr,
            'value': 0,
            'data': data,
            'gasPrice': web3_brn.to_wei(gasPricePlus*2, 'gwei'),
            'nonce': nonce
        })

        bid_tx = {
            'chainId': chainId_brn,
            'from': sender,
            'to': bidaddr,
            'value': 0,
            'data': data,
            'gas': gasAmount,
            'gasPrice': web3_brn.to_wei(gasPricePlus*2, 'gwei'),
            'nonce': nonce
        }
        
        tx_hash = web3_brn.eth.send_raw_transaction(web3_brn.eth.account.sign_transaction(bid_tx, key).rawTransaction)
        print(f'Processing Bid Executor Bridge {bridgedmin} From ETH ARB TO ETH ARB')
        web3_brn.eth.wait_for_transaction_receipt(tx_hash)
        print(f'Executor Bid Bridge {bridgedmin} From ETH ARB TO ETH ARB Success!')
        print(f'TX-ID : {str(web3_brn.to_hex(tx_hash))}')
        time.sleep(2)
        Executor(sender, key, amount, amountin, orderid, txhash)
    except Exception as e:
        if "BD#3" in str(e):
            loading_message('Please wait',12)
            BidExecute(sender, key, amount, amountin, orderid, txhash)
        elif "BD#8" in str(e):
            loading_message('Please wait',12)
            Get_Estimate(sender, key, amount)
        elif "nonce" in str(e):
            loading_message('Please wait',2)
            BidExecute(sender, key, amount, amountin, orderid, txhash)
        else:
            print(f"Error: {e}")
            print('')
            time.sleep(2)
        time.sleep(2)
        pass
    
def BLAST_BLAST(sender, key, amount, amountin):
    try:
        gasPrice = web3.eth.gas_price
        nonce = web3.eth.get_transaction_count(sender)
        bridgeaddr = web3.to_checksum_address('0x8D86c3573928CE125f9b2df59918c383aa2B514D') #for arb
        funcbridge = bytes.fromhex('56591d59')
        codebridge = bytes.fromhex('61726274') #arb>arb
        amountzero = 0
        totalbridge = amount
        bridgedmin = web3.from_wei(amountin, 'ether')
        
        enc_bridge = encode(['bytes4', 'uint256', 'address', 'uint256', 'uint256', 'uint256', 'uint256'], [codebridge, amountzero, sender, amountin, amountzero, amountzero, totalbridge])
        data = web3.to_hex(funcbridge+enc_bridge)

        gasAmount = web3.eth.estimate_gas({
            'chainId': chainId,
            'from': sender,
            'to': bridgeaddr,
            'value': totalbridge,
            'data': data,
            'gasPrice': gasPrice,
            'nonce': nonce
        })

        bridge_tx = {
            'chainId': chainId,
            'from': sender,
            'to': bridgeaddr,
            'value': totalbridge,
            'data': data,
            'gas': gasAmount,
            'gasPrice': gasPrice,
            'nonce': nonce
        }
        
        tx_hash = web3.eth.send_raw_transaction(web3.eth.account.sign_transaction(bridge_tx, key).rawTransaction)
        print(f'For Wallet Address {sender}')
        print(f'Processing Bridge {bridgedmin} ETH ARB TO ETH ARB')
        web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f'Bridge {bridgedmin} ETH ARB TO ETH ARB Success!')
        print(f'TX-ID : {str(web3.to_hex(tx_hash))}')
        event = web3.eth.get_transaction_receipt(web3.to_hex(tx_hash))
        log = event["logs"][1]
        topic = log["topics"][1]
        orderid = topic
        BidExecute(sender, key, amount, amountin, orderid, web3.to_hex(tx_hash))
    except Exception as e:
        print(f"Error: {e}")
        pass

amountmin = float(0.01)
amountmax = float(0.0101)  
sender = web3.eth.account.from_key(privatekeys)
amountrandom = random.uniform(amountmin, amountmax)
amount = web3.to_wei(amountrandom, 'ether')
calcamountmin = (amountrandom*99.995) / 100
amountin = web3.to_wei(calcamountmin, 'ether')
BLAST_BLAST(sender.address, sender.key, amount, amountin)