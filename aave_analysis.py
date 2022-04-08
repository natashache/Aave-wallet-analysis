# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 16:32:43 2022

@author: NChe
"""
import pandas as pd
import requests
from datetime import datetime
import os

address = os.environ.get('WALLET')
api_key = os.environ.get('APIKEY')

token_tnxs = pd.DataFrame()
start_block = 11790178
end_block = 13532886
block = start_block

while int(block) < end_block:
    print(block)
    token_tnxs_url = "https://api.etherscan.io/api?module=account&action=tokentx&address={}&startblock={}&sort=asc&apikey={}".format(address, block, api_key)
    response = requests.get(token_tnxs_url)
    json_data = response.json()['result']
    json_data = pd.DataFrame(json_data)
    token_tnxs = token_tnxs.append(json_data, ignore_index=True)
    block = token_tnxs['blockNumber'].max()

token_tnxs.drop_duplicates(keep=False,inplace=True)
tokenList = token_tnxs['tokenName'].unique()

aaveTokens_addresses = 'https://aave.github.io/aave-addresses/mainnet.json'
response1 = requests.get(aaveTokens_addresses).json()['proto']
aaveTokens = pd.DataFrame(response1)
aaveSymbols = list(aaveTokens['aTokenSymbol'])
list1 = [aaveTokens['aTokenAddress'], aaveTokens['stableDebtTokenAddress'], aaveTokens['variableDebtTokenAddress']]
aaveTokenAddresses = pd.concat(list1, ignore_index=True)
aaveTokenAddresses = list(aaveTokenAddresses)
aaveTokenAddresses = [x.lower() for x in aaveTokenAddresses]

def filter1(symbol):
    if symbol in aaveSymbols:
        return True
    else:
        return False

def filter2(address):
    if str(address) in aaveTokenAddresses:
        return True
    else:
        return False

aaveInteractions = token_tnxs[token_tnxs['tokenSymbol'].apply(filter1)]
aaveInteractions['dateTime'] = pd.to_datetime(aaveInteractions['timeStamp'],unit='s')

aaveInteractions1 = token_tnxs[token_tnxs['contractAddress'].apply(filter2)]
aaveInteractions1['dateTime'] = pd.to_datetime(aaveInteractions1['timeStamp'],unit='s')
aaveInteractions1.drop(aaveInteractions1[aaveInteractions1['blockNumber'].astype(int) > end_block].index, inplace = True)

aaveInteractions1.to_csv('aave_transactions.csv')