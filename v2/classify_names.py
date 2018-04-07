'''
Ingests a file of ID,name pairs and uses an API to classify
them by region and nationality.
'''

from string import Template
import sys
import json
import urllib.request
import urllib.parse

API_URL = 'http://www.textmap.com/ethnicity_api/api'
HEADERS = {'content-type': 'application/json'}
CACHE_FILE = "cache.json"
BATCH_SIZE = 2000

API_URL_TEMPLATE = Template('http://www.name-prism.com/api_token/$type/json/$apiToken/$urlEncodedName')

def _load_name_type(name, apiToken, type):
    urlEncodedName = urllib.parse.quote_plus(name)
    url = API_URL_TEMPLATE.substitute(type=type, apiToken=apiToken, urlEncodedName=urlEncodedName)
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    output = response.read()
    json_result = json.loads(output) #.decode('utf8')
    return json_result

def _load_name(name, apiToken):
    return {
        "nat": _load_name_type(name, apiToken, "nat"),
        "eth": _load_name_type(name, apiToken, "eth")
    }

def _load_batch(names, apiToken):
    """
    Load responses the ethnicity classification API.
    """
    result = {}
    for name in names:
        result[name] = _load_name(name, apiToken)
    return result

def _load_batch_and_cache(names, apiToken):
    """
    Hit the cache file for any names already known.
    For the rest, got to the API and then add the
    results to the cache file.
    """
    file = open(CACHE_FILE, 'r')
    text = file.read().strip()
    file.close()
    cache = json.loads(text)

    names_to_load = []
    for name  in names:
        if name not in cache:
            names_to_load.append(name)
    loaded = _load_batch(names_to_load, apiToken)
    new_cache = {**loaded, **cache}
    pretty_printed_cache = json.dumps(new_cache, indent=4, sort_keys=True)

    file = open(CACHE_FILE, 'w')
    file.write(pretty_printed_cache)
    file.close()

    values_to_return = {}
    for name in names:
        values_to_return[name] = new_cache[name]
    return values_to_return

def _load_all(names, apiToken):
    index = 0
    while index < len(names):
        next_index = min(index + BATCH_SIZE, len(names))
        next_batch = names[index:next_index]
        _load_batch_and_cache(next_batch, apiToken)
        index = next_index
    return _load_batch_and_cache(names, apiToken)

if len(sys.argv) is not 2:
    print("Usage: python classify_names.py API_TOKEN")
    exit(1)

apiToken = sys.argv[1]

NAMES = ["George Washington", "Barack Obama", "Xi Jinping", "Janet Lu", "Jeffrey Martin"]
output = _load_all(NAMES, apiToken)
print(output)
