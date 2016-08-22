import json
import requests

def loads_items_petscan(input_file):
    with open(input_file) as json_data:
        items_json = json.load(json_data)
        item = [line['q']
        for line in items_json['*'][0]['a']['*']]
        return item


def loads_items_query(input_file):
    with open(input_file) as json_data:
        items = json.load(json_data)
        return items

def load(source):
    if(source == "query"):
        return loads_items_query
    if(source == "petscan"):
        return loads_items_petscan
    else:
        raise ValueError("Only supported sources are query and petsan")

def loads_items(category):
    with open("items.json") as json_data:
        items_json = json.load(json_data)
        items = [line['q']
        for line in items_json[category]['*'][0]['a']['*']]
        print items
        return items

def q(fileName):
    url = "https://tools.wmflabs.org/commonsedge/api.php?file="
    json=requests.get(url+fileName).json()
    return json["error_data"]
