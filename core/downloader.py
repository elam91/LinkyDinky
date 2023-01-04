import requests
from core.friend_request_core import FriendRequestBot

URLS = {'user1': {
    'config': 'https://api.npoint.io/examplenotrealchangeme',
    'keywords': 'https://api.npoint.io/examplenotrealchangeme'
},
    'user2':
        {'config': 'https://api/examplenotrealchangeme',
         'keywords': 'https://api/examplenotrealchangeme'},
}


def download_config(user):
    user_urls = URLS.get(user)
    config = requests.get(user_urls['config']).json()
    FriendRequestBot.list_to_json('./config/config.json', config)


def download_keywords(user):
    user_urls = URLS.get(user)
    keywordskeep = requests.get(user_urls['keywords']).json()
    FriendRequestBot.list_to_json('./config/keywordskeep.json', keywordskeep)
    FriendRequestBot.list_to_json('./config/keywords.json', keywordskeep)
