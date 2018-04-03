'''
Ingests a file of ID,name pairs and uses an API to classify
them by region and nationality.
'''

import json
import urllib.request

API_URL = 'http://www.textmap.com/ethnicity_api/api'
HEADERS = {'content-type': 'application/json'}
CACHE_FILE = "cache.csv"

def _load_batch(names):
    """
    Load responses the ethnicity classification API.
    """
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
    file = open(CACHE_FILE, 'w')
    file.write(json.dumps(new_cache,indent=4, sort_keys=True))
    file.close()

    values_to_return = {}
    for name in names:
        values_to_return[name] = new_cache[name]
    return values_to_return

def _highest_scoring_ethnicity(ethnicity_scores):
    """
    the ethnicity block looks like:
    [{'score': '.05', ethnicity: 'foo'}, {'score': '0.4', ethnicity: 'bar'}]

    This method returns the item with the highest score.
    """
    best = {'score': -1, 'ethnicity': 'ERROR_ETHNICITY'}
    for ethnicity_score in ethnicity_scores:
        if float(ethnicity_score['score']) > best['score']:
            best['score'] = float(ethnicity_score['score'])
            best['ethnicity'] = ethnicity_score['ethnicity']
    return best

def _highest_scores_for_name(name_scores):
    continent = _highest_scoring_ethnicity(name_scores[0]['scores'])
    region = _highest_scoring_ethnicity(name_scores[1]['scores'])
    return [continent['ethnicity'],
            continent['score'],
            region['ethnicity'],
            region['score']]

def _load_names_and_get_highest_ethnicities(names):
    batch_results = _load_batch_and_cache(names)
    results = {}
    for name, scores in batch_results.items():
        results[name] = _highest_scores_for_name(scores)
    return results



NAMES = ["George Washington", "Barack Obama", "Xi Jinping"]
output = _load_names_and_get_highest_ethnicities(NAMES)
print(output)
