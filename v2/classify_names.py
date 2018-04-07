'''
Ingests a file of ID,name pairs and uses an API to classify
them by region and nationality.
'''

from string import Template
import sys
import json
import urllib.request
import urllib.parse
import csv

CACHE_FILE = "cache.json"
OUTPUT_FILE = "classified_names.csv"
BATCH_SIZE = 2000
NATIONALITY = "nat"
ETHNICITY = "eth" 

API_URL_TEMPLATE = Template('http://www.name-prism.com/api_token/$type/json/$apiToken/$urlEncodedName')

HEADER = ["name", "nat:African:EastAfrican","nat:African:SouthAfrican","nat:African:WestAfrican","nat:CelticEnglish",
          "nat:EastAsian:Chinese","nat:EastAsian:Indochina:Cambodia","nat:EastAsian:Indochina:Myanmar",
          "nat:EastAsian:Indochina:Thailand","nat:EastAsian:Indochina:Vietnam","nat:EastAsian:Japan",
          "nat:EastAsian:Malay:Indonesia","nat:EastAsian:Malay:Malaysia","nat:EastAsian:South Korea","nat:European:Baltics",
          "nat:European:EastEuropean","nat:European:French","nat:European:German","nat:European:Italian:Italy",
          "nat:European:Italian:Romania","nat:European:Russian","nat:European:SouthSlavs","nat:Greek",
          "nat:Hispanic:Philippines","nat:Hispanic:Portuguese","nat:Hispanic:Spanish","nat:Jewish",
          "nat:Muslim:ArabianPeninsula","nat:Muslim:Maghreb","nat:Muslim:Nubian","nat:Muslim:Pakistanis:Bangladesh",
          "nat:Muslim:Pakistanis:Pakistan","nat:Muslim:Persian","nat:Muslim:Turkic:CentralAsian","nat:Muslim:Turkic:Turkey",
          "nat:Nordic:Finland","nat:Nordic:Scandinavian:Denmark","nat:Nordic:Scandinavian:Norway","nat:Nordic:Scandinavian:Sweden",
          "nat:SouthAsian","eth:2PRACE","eth:AIAN","eth:API","eth:Black","eth:Hispanic","eth:White"]

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
        NATIONALITY: _load_name_type(name, apiToken, NATIONALITY),
        ETHNICITY: _load_name_type(name, apiToken, ETHNICITY)
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
    print("batch size: " + str(len(names)) + ", cache misses: ", str(len(names_to_load)))

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
    print("====================================================")
    index = 0
    while index < len(names):
        next_index = min(index + BATCH_SIZE, len(names))
        print("next batch: names[" + str(index) + ":" + str(next_index) + "]")
        next_batch = names[index:next_index]
        _load_batch_and_cache(next_batch, apiToken)
        index = next_index
    print("====================================================")
    print("loading everything... should just be from the cache")
    return _load_batch_and_cache(names, apiToken)

def _classified_name_to_csv_row(name, classification):
    row = [name]
    for value in classification[NATIONALITY].values():
        row.append(value)
    for value in classification[ETHNICITY].values():
        row.append(value)
    return row

def _print_csv(classifiedNames):
    with open(OUTPUT_FILE, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(HEADER)
        for name, classification in classifiedNames.items():
            csvwriter.writerow(_classified_name_to_csv_row(name, classification))


if len(sys.argv) is not 2:
    print("Usage: python classify_names.py API_TOKEN")
    exit(1)

apiToken = sys.argv[1]

NAMES = ["George Washington", "Barack Obama", "Xi Jinping", "Janet Lu", "Jeffrey Martin"]
output = _load_all([name.upper() for name in NAMES], apiToken)
_print_csv(output)
