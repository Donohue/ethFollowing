#!/usr/bin/env python
import os
import sys

from twitter import TwitterAPI
from ethereum import Wallet

def main():
    if len(sys.argv) != 2:
        print('Usage: %s <twitter-username>' % sys.argv[0])
        sys.exit(-1)

    username = sys.argv[1]
    print('Fetching following for %s' % username)
    following = TwitterAPI.get_following_by_username(username)
    
    print('Following %d users on Twitter, initializing wallets' % len(following))
    wallets = []
    for user in following:
        if not user.ens:
            continue
        try:
            wallets.append(Wallet(user.ens))
        except Exception as e:
            print('Error adding wallet for @%s: %s' % (user.username, str(e)))
    
    print('Initialized %d wallets from Twitter users, fetching transactions' % len(wallets))   
    transactions = []
    for wallet in wallets:
        # Collect transactions via API call to etherscan
        transactions += wallet.transactions

    print('Found %d transactions across %d wallets\n' % (len(transactions), len(wallets)))
    # Loop through reverse chronological
    for transaction in sorted(transactions, key=lambda t: t.timestamp, reverse=True):
        wallet = transaction.wallet
        verb = 'sent %.2f to' if wallet.sent_transaction(transaction) else 'received %.2f from'
        verb = verb % transaction.ether_value

        # Get contract name via API call to etherscan
        if wallet.sent_transaction(transaction):
            subject = transaction.contract_name or Wallet.resolve_ens_address(transaction.to_address) or transaction.to_address
        else:
            subject = Wallet.resolve_ens_address(transaction.from_address) or transaction.from_address

        print('%s %s %s at %s (Tx ID: %s)' % (wallet.ens, verb, subject, transaction.dt, transaction.hash))

if __name__ == '__main__':
    main()
