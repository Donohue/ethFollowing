import json
import os

import requests

from ethereum import Wallet

class TwitterUser(object):
    def __init__(self, data):
        self.id = data['id']
        self.name = data.get('name')
        self.location = data.get('location')
        self.username = data.get('username')

    @property
    def ens(self):
        fields = ['location', 'name']
        for field in fields:
            data = getattr(self, field)
            ens = Wallet.parse_ens(data)
            if ens:
                return ens
        return None


class TwitterAPI(object):
    TWITTER_API_URL = 'https://api.twitter.com/2'

    @classmethod
    def bearer_token(cls):
        try:
            return os.environ['TWITTER_BEARER_TOKEN']
        except KeyError:
            raise ValueError('Set TWITTER_BEARER_TOKEN environment variable to fetch transactions') from None

    @classmethod
    def get_id_by_username(self, username):
        headers = {'Authorization': 'Bearer %s' % self.bearer_token()}
        request = requests.get('%s/users/by/username/%s' % (self.TWITTER_API_URL, 'bthdonohue'), headers=headers)
        return request.json()['data']['id']

    @classmethod
    def get_following(self, user_id):
        following = []
        headers = {'Authorization': 'Bearer %s' % self.bearer_token()}
        params = {'max_results': 1000, 'user.fields': 'id,name,location,url'}
        has_next = True
        next_token = True
        
        while next_token:
            request = requests.get('%s/users/%s/following' % (self.TWITTER_API_URL, user_id), params=params, headers=headers)
            request_json = request.json()
            if not 'data' in request_json:
                raise ValueError('Twitter request failed: %s' % json.dumps(request_json))
            users = request_json['data']
            following += [TwitterUser(user_data) for user_data in users]
            next_token = request_json.get('meta', {}).get('next_token')
            if next_token:
                params['pagination_token'] = next_token
        
        return following

    @classmethod
    def get_following_by_username(self, username):
        user_id = self.get_id_by_username(username)
        return self.get_following(user_id)
