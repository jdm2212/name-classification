'''
Ingests a file of ID,name pairs and uses an API to classify
them by region and nationality.
'''

import json
import urllib.request

API_URL = 'http://www.textmap.com/ethnicity_api/api'
HEADERS = {'content-type': 'application/json'}

def _load_batch(names):
    arguments = {"names": names}
    json_data = json.dumps(arguments).encode('utf8')
    request = urllib.request.Request(API_URL, data=json_data, headers=HEADERS)
    response = urllib.request.urlopen(request)
    output = response.read()
    json_result = json.loads(output) #.decode('utf8')
    return json_result

def _highest_scoring_ethnicity(ethnicity_scores):
    """
    the ethnicity block looks like:
    [{'score': '.05', ethnicity: 'foo'}, {'score': '0.4', ethnicity: 'bar'}]
    """
    best = {'score': -1, 'ethnicity': 'ERROR_ETHNICITY'}
    for ethnicity_score in ethnicity_scores:
        print(ethnicity_score)
        if float(ethnicity_score['score']) > best['score']:
            best['score'] = float(ethnicity_score['score'])
            best['ethnicity'] = ethnicity_score['ethnicity']
    return best

def _highest_scores_for_name(name_scores):
    print(name_scores)
    continent = _highest_scoring_ethnicity(name_scores[0]['scores'])
    region = _highest_scoring_ethnicity(name_scores[1]['scores'])
    return [continent['ethnicity'],
            continent['score'],
            region['ethnicity'],
            region['score']]

def _load_names_and_get_highest_ethnicities(names):
    batch_results = _load_batch(names)
    print(batch_results)
    results = {}
    for name, scores in batch_results.items():
        print("name:" + name)
        print("scores:" + str(scores))
        results[name] = _highest_scores_for_name(scores)
    return results

NAMES = ["George Washington", "Barack Obama"]
output = _load_names_and_get_highest_ethnicities(NAMES)
print(output)
