# -*- coding: utf-8 -*-
import json

categoriesFile = "categories.json"

def loads_facts(category):
    with open("categories.json") as data:
        facts = json.loads(data.read().decode("utf8"))
        with open ("test.json", "w") as test:
        	json.dump(facts, test)
    return facts[category]
