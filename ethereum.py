from datetime import datetime
import os
import re
import requests
from functools import cached_property
from ens import ENS
from web3.auto.infura import w3
    
class Transaction(object):
    def __init__(self, data, wallet=None):
        self.hash = data['hash']
        self.from_address = data['from']
        self.to_address = data['to']
        self.timestamp = int(data['timeStamp'])
        self.dt = datetime.fromtimestamp(self.timestamp)
        self.value = int(data['value'])
        self.input = data['input']
        self.wallet = wallet

    @property
    def ether_value(self):
        return w3.fromWei(self.value, 'ether')

    @cached_property
    def contract_name(self):
        # Contract interactions will have data in input field
        if not self.input:
            return None
        return EtherscanAPI.fetch_contract(self.to_address).get('ContractName')

class Wallet(object):    
    def __init__(self, ens):
        if not self.parse_ens(ens):
            raise ValueError('Invalid ENS name provided: %s' % str(ens))

        self.ens = ens
        self.address = self.resolve_ens_address(self.ens)
        if not self.address:
            raise ValueError('Unable to resolve address for ENS name: %s' % str(ens))

        self.balance = w3.eth.get_balance(self.address)

    def sent_transaction(self, transaction):
        # Etherscan addresses are returned lowercased, normalize what is received from web3 library/Infura
        return self.address.lower() == transaction.from_address.lower()

    @property
    def ether_balance(self):
        return w3.fromWei(self.balance, 'ether')

    @cached_property
    def transactions(self):
        # Fetch transactions from Etherscan. Can't just query the blockchain, Etherscan holds transactions in queryable format.
        return [Transaction(data, wallet=self) for data in EtherscanAPI.fetch_transactions(self.address)]
            

    @classmethod
    def resolve_ens_address(self, ens):
        # Leverage ENS library and Infura to resolve ENS names
        return ENS(w3.provider).address(ens)

    @classmethod
    def parse_ens(self, words):
        for word in (words or '').split():
            # Fairly certain this logic will not work for all ETH addresses, PR welcome
            match = re.match(r'([a-zA-Z0-9])+\.eth', word)
            if match:
                return match.group(0)
        return None

class EtherscanAPI(object):
    ETHERSCAN_API = 'https://api.etherscan.io/api'

    @classmethod
    def api_token(cls):
        try:
            return os.environ['ETHERSCAN_API_TOKEN']
        except KeyError:
            raise ValueError('Set ETHERSCAN_API_TOKEN environment variable to fetch transactions') from None

    @classmethod
    def fetch_transactions(cls, address):
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': 50,
            'sort': 'dsc',
            'apiKey': cls.api_token()
        }
        return requests.get(cls.ETHERSCAN_API, params=params).json()['result']

    @classmethod
    def fetch_contract(cls, address):
        params = {
            'module': 'contract',
            'action': 'getsourcecode',
            'address': address,
            'apiKey': cls.api_token()
        }
        return requests.get(cls.ETHERSCAN_API, params=params).json()['result'][0]
