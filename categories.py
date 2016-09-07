import logging
import json
import sys

import pywikibot
from pywikibot import page



commons = pywikibot.Site('commons', 'commons')
tree = {}

# Logger logging on console and in debug
LOG = logging.getLogger("categories")
LOG_LEVEL = logging.DEBUG
consolehandler = logging.StreamHandler(stream=sys.stdout)
fmt = '%(asctime)s    %(levelname)s    %(message)s'
consolehandler.setFormatter(logging.Formatter(fmt))
consolehandler.setLevel(LOG_LEVEL)
LOG.addHandler(consolehandler)
LOG.setLevel(LOG_LEVEL)



def build_tree(category):
    if category not in tree:
        node = {}
        node["Parents"] = [p.title() for p in
        page.Category(commons, category).categories()]
        children = [p.title() for p in
        page.Category(commons, category).subcategories()]
        node["Children"] = children
        tree[category] = node
        for child in children:
            LOG.debug("Going through children of %s", child)
            build_tree(child)


def main():
    categories =[
    u"Drawings by Vincent van Gogh",
    u"Lithographs by Vincent van Gogh",
    u"Paintings by Vincent van Gogh",
    u"Van Gogh works by date",
    u"Works by Vincent van Gogh by museum"
    u"Works by Vincent van Gogh by subject"]
    LOG.info("Building tree")
    for category in categories:
        build_tree(category)
    LOG.info("Writting")
    with open ("tree.json", "w") as data:
        json.dump(tree, data)

if __name__ == "__main__":
    main()
