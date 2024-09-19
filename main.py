import curses
from web3 import Web3
import time
import subprocess
import shutil
import os
from dotenv import load_dotenv
load_dotenv()

privatekeys = os.getenv("PRIVATE_KEY")

python_executables = ['python', 'python3', 'py']

rpc_urls = {
    'sepolia': 'https://ethereum-sepolia-rpc.publicnode.com',
    'arb-sepolia': os.getenv("ARB_RPC"),
    'base-sepolia': os.getenv("BASE_RPC"),
    'opt-sepolia': os.getenv("OP_RPC"),
    'blast-sepolia': os.getenv("BLAST_RPC"),
    'brn': 'https://brn.rpc.caldera.xyz/http'
}

web3_instances = {name: Web3(Web3.HTTPProvider(url)) for name, url in rpc_urls.items()}
for name, web3 in web3_instances.items():
    if not web3.is_connected():
        print(f"Warning: Cannot connect to the {name} network")
        web3_instances[name] = None 

addresses = {
    'MDP': web3.eth.account.from_key(privatekeys).address
}

def get_balance(web3, address):
    if web3 is None:
        return 0
    balance_wei = web3.eth.get_balance(address)
    balance_ether = web3.from_wei(balance_wei, 'ether')
    print(f"Debug: Balance for {address}: {balance_ether}")  
    return balance_ether

def calculate_change(new_balance, old_balance):
    return new_balance - old_balance

def draw_large_number(stdscr, number, row, col):
    large_numbers = {
        '0': [" 000 ", "0   0", "0   0", "0   0", " 000 "],
        '1': ["  1  ", " 11  ", "  1  ", "  1  ", " 111 "],
        '2': [" 222 ", "2   2", "   2 ", "  2  ", " 2222"],
        '3': [" 333 ", "    3", "  33 ", "    3", " 333 "],
        '4': ["4  4 ", "4  4 ", " 4444", "   4 ", "   4 "],
        '5': [" 5555", "5    ", " 555 ", "    5", " 555 "],
        '6': [" 666 ", "6    ", " 666 ", "6   6", " 666 "],
        '7': [" 7777", "    7", "   7 ", "  7  ", " 7   "],
        '8': [" 888 ", "8   8", " 888 ", "8   8", " 888 "],
        '9': [" 999 ", "9   9", " 9999", "    9", " 999 "]
    }
    max_y, max_x = stdscr.getmaxyx()
    for i, line in enumerate(large_numbers[number]):
        if row + i < max_y and col + len(line) < max_x:
            try:
                stdscr.addstr(row + i, col, line, curses.color_pair(3))
            except curses.error:
                pass 

def main(stdscr):
    curses.curs_set(0)  
    stdscr.nodelay(1) 
    stdscr.timeout(1000) 

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)

    chain_names = {
        'sepolia': 'SEPO',
        'arb-sepolia': 'ARB',
        'base-sepolia': 'BASE',
        'opt-sepolia': 'OPT',
        'blast-sepolia': 'BLAST',
        'brn': 'REWARD'
    }

    previous_balances = {} 

    refresh_interval = 10
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()

        col_width = max(len(name) for name in addresses.keys()) + 2
        col_width = max(col_width, 15) 

        stdscr.addstr(0, 0, "+" + "-" * (col_width - 1) + "+")
        col = 1
        for name in addresses.keys():
            if col * col_width >= max_x:
                break
            stdscr.addstr(0, col * col_width, "+" + "-" * (col_width - 1) + "+")
            stdscr.addstr(1, col * col_width, f"{name}".center(col_width - 1))
            col += 1
        stdscr.addstr(1, 0, " " * col_width)
        stdscr.addstr(2, 0, "+" + "-" * (col_width - 1) + "+")
        for i in range(1, col):
            stdscr.addstr(2, i * col_width, "+" + "-" * (col_width - 1) + "+")

        row = 3
        for chain_name, web3 in web3_instances.items():
            if web3 is None:
                continue 
            if row >= max_y - 1:
                break
            stdscr.addstr(row, 0, f"{chain_names[chain_name]}".center(col_width - 1))
            col = 1
            for address in addresses.values():
                if col * col_width >= max_x:
                    break
                balance = get_balance(web3, address)
                for python_exec in python_executables:
                    if shutil.which(python_exec) is not None:
                        try:
                            if chain_name == 'arb-sepolia' and balance > float(0.02):
                                subprocess.Popen([python_exec, "ext/arb.py"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif chain_name == 'opt-sepolia' and balance > float(0.02):
                                subprocess.Popen([python_exec, "ext/optimism.py"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif chain_name == 'base-sepolia' and balance > float(0.02):
                                subprocess.Popen([python_exec, "ext/base.py"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif chain_name == 'blast-sepolia' and balance > float(0.02):
                                subprocess.Popen([python_exec, "ext/blast.py"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        except Exception as e:
                            print(f"Failed to run with {python_exec}: {e}")
                if chain_name == 'brn':
                    balance_str = f"{balance:.5f}".strip()
                    stdscr.addstr(row, col * col_width, balance_str.center(col_width - 1), curses.color_pair(1))
                elif chain_name == 'arb-sepolia':
                    balance_str = f"{balance:.5f} ETH".strip()
                    stdscr.addstr(row, col * col_width, balance_str.center(col_width - 1), curses.color_pair(2))
                else:
                    balance_str = f"{balance:.5f} ETH".strip()
                    stdscr.addstr(row, col * col_width, balance_str.center(col_width - 1))
                col += 1
            row += 1
            stdscr.addstr(row, 0, "+" + "-" * (col_width - 1) + "+")
            for i in range(1, col):
                stdscr.addstr(row, i * col_width, "+" + "-" * (col_width - 1) + "+")
            row += 1

        if not previous_balances:
            previous_balances = {address: get_balance(web3_instances['brn'], address) for address in addresses.values()}

        if 'brn' in web3_instances and web3_instances['brn'] is not None:
            stdscr.addstr(row, 0, "Change".center(col_width - 1), curses.color_pair(3))
            col = 1
            for address in addresses.values():
                if col * col_width >= max_x:
                    break
                new_balance = get_balance(web3_instances['brn'], address)
                change = calculate_change(new_balance, previous_balances[address])
                change_str = f"{change:.5f}".strip()
                if change > 0:
                    color = curses.color_pair(4)  
                elif change == 0:
                    color = curses.color_pair(5) 
                else:
                    color = curses.color_pair(1) 
                stdscr.addstr(row, col * col_width, change_str.center(col_width - 1), color)
                previous_balances[address] = new_balance 
                col += 1
            row += 1
            stdscr.addstr(row, 0, "+" + "-" * (col_width - 1) + "+")
            for i in range(1, col):
                stdscr.addstr(row, i * col_width, "+" + "-" * (col_width - 1) + "+")
            row += 1

        max_y, max_x = stdscr.getmaxyx()
        for remaining in range(refresh_interval, 0, -1):
            if row + 7 < max_y:  
                try:
                    stdscr.addstr(row, 0, "Refreshing in".center(max_x))
                    draw_large_number(stdscr, str(remaining // 10), row + 1, max_x // 2 - 6)
                    draw_large_number(stdscr, str(remaining % 10), row + 1, max_x // 2)
                    stdscr.refresh()
                except curses.error:
                    pass  
            time.sleep(1)
        
        stdscr.refresh()

curses.wrapper(main)
