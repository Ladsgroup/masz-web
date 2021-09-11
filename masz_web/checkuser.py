import urllib.parse

import requests

GODS = ['Ladsgroup']

allowed_wikis = [
    'en.wikipedia.org',
    'fa.wikipedia.org',
    'it.wikipedia.org',
    'cs.wikipedia.org']


def auth_user_in_wiki(username, wiki):
    if username in GODS:
        return True
    if wiki not in allowed_wikis:
        return False
    api_result = requests.get('https://' + wiki + '/w/api.php', {
        'action': 'query',
        'list': 'users',
        'ususers': username,
        'usprop': 'groups',
        'format': 'json'
    }).json()
    users = api_result.get('query', {}).get('users')
    if not users:
        return False
    if 'checkuser' in users[0].get('groups', []):
        return True
    return False
