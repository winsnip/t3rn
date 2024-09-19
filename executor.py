from web3 import Web3
from eth_abi import encode
import os
from dotenv import load_dotenv

load_dotenv()
blastrpc = os.getenv("BLAST_RPC")
baserpc = os.getenv("BASE_RPC")
arbrpc = os.getenv("ARB_RPC")
oprpc = os.getenv("OP_RPC")
privatekeys = os.getenv("PRIVATE_KEY")

web3op = Web3(Web3.HTTPProvider(oprpc))
web3blast = Web3(Web3.HTTPProvider(blastrpc))
web3_brn = Web3(Web3.HTTPProvider("https://brn.rpc.caldera.xyz/http"))
chainId_brn = web3_brn.eth.chain_id
web3base = Web3(Web3.HTTPProvider(baserpc))
web3arb = Web3(Web3.HTTPProvider(arbrpc))

#connecting web3
if  web3blast.is_connected() == True:
    print("Web3 Connected BLAST...\n")
else:
    print("Error Connecting Please Try Again Exit...")
    exit()

if  web3op.is_connected() == True:
    print("Web3 Connected OP...\n")
else:
    print("Error Connecting Please Try Again Exit...")
    exit()

if  web3arb.is_connected() == True:
    print("Web3 Connected ARB...\n")
else:
    print("Error Connecting Please Try Again Exit...")
    exit()

if  web3base.is_connected() == True:
    print("Web3 Connected BASE...\n")
else:
    print("Error Connecting Please Try Again Exit...")
    exit()
#connecting web3
if  web3_brn.is_connected() == True:
    print("Web3 Connected BRN...\n")
else:
    print("Error Connecting Please Try Again Exit...")
    exit()
        
def ClaimBRN(sender, key, amount, orderid, ordertime, txhash):
    try:
        gasPrice = web3_brn.eth.gas_price
        gasPricePlus = web3_brn.from_wei(gasPrice, 'gwei')
        nonce = web3_brn.eth.get_transaction_count(sender)
        claimaddr = web3blast.to_checksum_address('0x05C9e2dDfBa9120565c9588fd5d4464B85E77285') #for brn
        funcclaim = bytes.fromhex('5765d3c8')
        enc_claim = encode(['bytes32', 'address'], [orderid, sender])
        data = web3_brn.to_hex(funcclaim+enc_claim)

        gasAmount = web3_brn.eth.estimate_gas({
            'chainId': chainId_brn,
            'from': sender,
            'to': claimaddr,
            'value': 0,
            'data': data,
            'gasPrice': web3_brn.to_wei(gasPricePlus*2, 'gwei'),
            'nonce': nonce
        })

        claim_tx = {
            'chainId': chainId_brn,
            'from': sender,
            'to': claimaddr,
            'value': 0,
            'data': data,
            'gas': gasAmount,
            'gasPrice': web3_brn.to_wei(gasPricePlus*2, 'gwei'),
            'nonce': nonce
        }
        
        tx_hash = web3_brn.eth.send_raw_transaction(web3_brn.eth.account.sign_transaction(claim_tx, key).rawTransaction)
        print(f'Processing Claim Reward 1 BRN As Executor...')
        web3_brn.eth.wait_for_transaction_receipt(tx_hash)
        print(f'TX-ID : {str(web3_brn.to_hex(tx_hash))}')
        with open("lognya.txt", "r") as file:
            lines = file.readlines()
        with open("lognya.txt", "w") as file:
            found = False
        for line in lines:
            if line.strip().startswith(txhash):
                found = True
            else:
                file.write(line)
        if found:
            print("Success Delete Used TXhash and Claim Reward 1 BRN As Executor Success!")
        else:
            print("Txhash not found")
    except Exception as e:
        if "BD#16" in str(e):
            print('Reward BRN Still Not Ready For Claim!')
        elif "BD#15" in str(e):
            with open("lognya.txt", "r") as file:
                    lines = file.readlines()
            with open("lognya.txt", "w") as file:
                found = False
            for line in lines:
                if line.strip().startswith(txhash):
                    found = True
                else:
                    file.write(line)
            if found:
                print("Reward BRN Already Claimed!, Success Delete Used TXhash")
            else:
                print("Txhash not found")
        else:
            print(str(e))
        pass

def BLAST_BLAST(sender, key, web3, chainid):
    with open('lognya.txt', 'r') as file:
        local_data = file.read().splitlines()
        for txhash in local_data:
            try:
                txhashdat = txhash.split(":")
                if(txhashdat[1] == str(168587773)):
                    web3 = web3blast
                elif(txhashdat[1] == str(84532)):
                    web3 = web3base
                elif(txhashdat[1] == str(421614)):
                    web3 = web3arb
                else:
                    web3 = web3op
                tx = web3.eth.get_transaction(txhashdat[0])
                event = web3.eth.get_transaction_receipt(txhashdat[0])
                amount = tx["value"]
                log = event["logs"][0]
                topic = log["topics"][1]
                data = log["data"]
                orderid = topic
                getordertime = web3.to_hex(data)
                ordertime = int(getordertime[58:], 16)
                ClaimBRN(sender, key, amount, orderid, ordertime, txhashdat[0])
            except Exception as e:
                print(str(e))
  
while True:
    sender = web3blast.eth.account.from_key(privatekeys)
    BLAST_BLAST(sender.address, sender.key, web3blast, 168587773)