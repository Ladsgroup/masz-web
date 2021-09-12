import urllib.parse

import requests

GODS = ['Ladsgroup']

allowed_wikis = sorted([
    #'en.wikipedia.org',
    'fa.wikipedia.org',
    'it.wikipedia.org',
    'cs.wikipedia.org',
    'es.wikipedia.org',
    'simple.wikipedia.org',
    'en.wikinews.org',
    'pt.wikipedia.org',
    'www.wikidata.org',
])


special_wikis = {
    'www.wikidata.org': 'wikidatawiki',
}

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

def get_wiki_db_name(url):
    if url in special_wikis:
        return special_wikis[url]
    if '.wikipedia.org' in url:
        return url.split('.')[0] + 'wiki'
    return url.split('.')[0] + url.split('.')[1]
