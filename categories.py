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

def build_tree(category, with_children=True, with_parents=False):
    global nbCalls
    nbCalls = nbCalls + 1
    if (nbCalls % frequency) == 0:
        flush()
    if category not in tree:
        node = {}
        parents = [p.title() for p in
        page.Category(commons, category).categories()]
        node["Parents"] = parents
        children = [p.title() for p in
        page.Category(commons, category).subcategories()]
        node["Children"] = children
        tree[category] = node
        if with_children:
            for child in children:
                build_tree(child, with_children, with_parents)
        if with_parents:
            for parent in parents:
                build_tree(parent, with_children, with_parents)

def main():
    categories =[u"Paintings by Vincent van Gogh in the Art Institute of Chicago"]
    if len(tree) > 0:
        LOG.info("Already %d elements",len(tree))
        LOG.info("Building tree")
        for category in categories:
            build_tree(category, with_children=True, with_parents=False)
        flush()

if __name__ == "__main__":
    main()
