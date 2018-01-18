# -*- coding: utf-8 -*-
import logging
import json
import sys
import requests
import pywikibot
from pywikibot import page

commons = pywikibot.Site('commons', 'commons')
tree = {}
nbCalls = 0
frequency = 50

# Logger logging on console and in debug
LOG = logging.getLogger("categories")
LOG_LEVEL = logging.DEBUG
consolehandler = logging.StreamHandler(stream=sys.stdout)
fmt = '%(asctime)s    %(levelname)s    %(message)s'
consolehandler.setFormatter(logging.Formatter(fmt))
consolehandler.setLevel(LOG_LEVEL)
LOG.addHandler(consolehandler)
LOG.setLevel(LOG_LEVEL)

def flush():
    LOG.info("Writting")
    with open ("tree.json", "w") as data:
        json.dump(tree, data)

def build_tree(category, children_depth=0, parents_depth=0, with_files=False):
    global nbCalls
    nbCalls = nbCalls + 1
    if (nbCalls % frequency) == 0:
        flush()
    if category not in tree:
        LOG.info(category)
        node = {}
        parents = [p.title() for p in
        page.Category(commons, category).categories()]
        node["Parents"] = parents
        children = [p.title() for p in
        page.Category(commons, category).subcategories()]
        node["Children"] = children
        tree[category] = node
        if children_depth > 0:
            for child in children:
                build_tree(child, children_depth-1, parents_depth)
        if parents_depth > 0:
            for parent in parents:
                build_tree(parent, with_children, parents_depth-1)
        if with_files:
            for file in page.Category(commons, category).fil

def paintings_by_year():
    taboo=[u"Paintings by artist by year‎",
"Paintings by country by year‎",
"Paintings by genre by year‎",
"Paintings by style by year‎",
"Paintings by technique by year‎",
"Paintings by year by artist‎",
"Paintings by year by country‎",
"Paintings not categorised by year‎",
"Paintings with years of production (artist)‎",
"Paintings of people by year‎",
"Paintings from the United States by year‎"]
'''    "Properties": {
      "P31": {
        "Value": "Q3305213"
      },
      "P571": {
        "Value": {
          "Year":1912
          }
        }'''
    motherCat = page.Category(commons, "Paintings by year")
    for cat in motherCat.categories():
        if cat.title() not in taboo:
            tree[cat.title()]

def main():
    categories =[u"Lena temp2"]
    if len(tree) > 0:
        LOG.info("Already %d elements",len(tree))
    LOG.info("Building tree")
    for category in categories:
        build_tree(category, children_depth=1, parents_depth=1, with_files=True)
    flush()

if __name__ == "__main__":
    main()


