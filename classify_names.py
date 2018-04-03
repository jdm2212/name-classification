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
    print(output)
    json_result = json.loads(output) #.decode('utf8')
    return json_result


NAMES = ["George Washington", "Barack Obama"]
print(_load_batch(NAMES)[NAMES[0]])
