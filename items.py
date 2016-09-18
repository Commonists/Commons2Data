import json
import requests
import re
import pywikibot
from pywikibot import page

commons = pywikibot.Site('commons', 'commons')
commonsedge = "https://tools.wmflabs.org/commonsedge/api.php?file="
itemExpression = re.compile("Q\d+")

def loads_items(category, depth=2):
    items = []
    pages = sub(category, depth)
    for page in pages:
        it = item(page)
        if it[0]:
            items.append(it[1])
    return items

def sub(category, depth=1):
    files = page.Category(commons, category).articlesList()
    if depth <= 0:
        return files
    else:
        categories = page.Category(commons, category).subcategoriesList()
        result =  list(files)
        result = result+categories
        for cat in categories:
            result = result+sub(cat.title(), depth-1)
        return result

def institution(categoryName, height=0, cached=set([])):
    if categoryName in cached:
            return None
    cached.add(categoryName)
    category = page.Category(commons, categoryName)
    if height == 0:
        inst = [i for i in category.articles(namespaces=106)]
        if len(inst) == 0:
            return None
        else:
            items = itemExpression.findall(inst[0].get())
            if len(items) == 0:
                return None
            else:
                return items[0]
    else:
        result = institution(categoryName, height=0)
        if result is None:
            for parent in category.categories():
                result = institution(parent.title(), height-1,cached)
                if result is not None:
                    break
        return result

def item(page):
    try:
        item = page.data_item().title()
        return [True, item]
    except pywikibot.NoPage:
        if page.isImage():
            json=requests.get(commonsedge+page.title()[5:]).json()
            if json["status"] == "ERROR":
                if "Artwork" in json["error"]:
                    if u'wikidata' in json["error_data"][0]["params"]:
                        return[True,json["error_data"][0]["params"]["wikidata"][0][0]]
                    else:
                        return[False, "No wikidata item"]
                else:
                    return[False, "No Artwork template"]
            else:
                return [False, "Non-Artwork related error"]
        else:
            return [False, "Not a file"]
    except pywikibot.data.api.APIError:
        return [False, "API Error"]
