import json

categoriesFile = "categories.json"

def loads_facts(category):
    with open("categories.json") as data:
        facts = json.loads(data.read().decode())
        print facts
    return facts[category]
