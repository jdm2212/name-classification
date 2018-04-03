'''
Ingests a file of ID,name pairs and uses an API to classify
them by region and nationality.
'''

import json
import urllib.request

API_URL = 'http://www.textmap.com/ethnicity_api/api'
HEADERS = {'content-type': 'application/json'}
CACHE_FILE = "cache.csv"
BATCH_SIZE = 2000

def _load_batch(names):
    """
    Load responses the ethnicity classification API.
    """
    if len(names) == 0:
        return {}
    arguments = {"names": names}
    json_data = json.dumps(arguments).encode('utf8')
    request = urllib.request.Request(API_URL, data=json_data, headers=HEADERS)
    response = urllib.request.urlopen(request)
    output = response.read()
    json_result = json.loads(output) #.decode('utf8')
    return json_result

def _load_batch_and_cache(names):
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
    loaded = _load_batch(names_to_load)
    new_cache = {**loaded, **cache}
    pretty_printed_cache = json.dumps(new_cache, indent=4, sort_keys=True)

    file = open(CACHE_FILE, 'w')
    file.write(pretty_printed_cache)
    file.close()

    values_to_return = {}
    for name in names:
        values_to_return[name] = new_cache[name]
    return values_to_return

def _load_all(names):
    index = 0
    while index < len(names):
        next_index = min(index + BATCH_SIZE, len(names))
        next_batch = names[index:next_index]
        _load_batch_and_cache(next_batch)
        index = next_index
    return _load_batch_and_cache(names)

def _highest_scores_for_name(name_scores):
    continent = name_scores[0]['best']
    region = name_scores[1]['best']
    return [continent, region]

def _load_names_and_get_highest_ethnicities(names):
    batch_results = _load_all(names)
    results = {}
    for name, scores in batch_results.items():
        results[name] = _highest_scores_for_name(scores)
    return results



NAMES = ["George Washington", "Barack Obama", "Xi Jinping", "Janet Lu", "Jeffrey Martin"]
output = _load_names_and_get_highest_ethnicities(NAMES)
print(output)
