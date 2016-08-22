 # -*- coding: utf-8 -*-

import json
# import os
# os.path.join("item", "truc.txt")
# statements = ["P571\t+1887-01-01T00:00:00Z/9"]

categoriesFile = "categories.json"

def loads_statements(source):
    if(source == "query"):
        return loads_statements_query
    if(source == "petscan"):
        return loads_statements_petscan
    else:
        raise ValueError("Only supported sources are query and petsan")


def loads_statements_petscan(input_statements):
    with open(input_statements) as data:
        statements = data.readlines()
    return statements


def loads_statements_query(input_statements):
    with open(input_statements) as data:
            statements = json.load(data)
    return statements

def loads_facts(category):
    with open("categories.json") as data:
        facts = json.loads(data.read().decode())
        print facts
    return facts[category]
