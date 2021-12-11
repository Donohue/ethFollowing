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
    following = TwitterAPI.get_following_by_username(username)
    
    wallets = []
    for user in following:
        if not user.ens:
            continue
        try:
            wallets.append(Wallet(user.ens))
        except Exception as e:
            continue
    
    print('Username,ENS,Address,ETH Balance')
    following_username_map = {user.ens:user for user in following}
    for wallet in wallets:
        user = following_username_map[wallet.ens]
        print('%s,%s,%s,%.002f' % (user.username, wallet.ens, wallet.address, wallet.ether_balance))

if __name__ == '__main__':
    main()
