import json
import requests
import re
import datetime
import pywikibot
from pywikibot import page

commons = pywikibot.Site('commons', 'commons')
commonsedge = "https://tools.wmflabs.org/commonsedge/api.php?file="
itemExpression = re.compile("Q\d+")
cache = open("cachedItems.json").read()

def loads_items(category, depth=2):
    items = []
    pages = sub(category, depth)
    for page in pages:
        it = item(page)
        if it[0]:
            items.append(it[1])
    return items

def now():
    return {"Timestamp":datetime.datetime.now()}

def sub(category, depth=1):
    files = page0.Category(commons, category).articlesList()
    if depth <= 0:
        return files
    else:
        categories = page.Category(commons, category).subcategoriesList()
        result =  list(files)
        result = result+categories
        for cat in categories:
            result = result+sub(cat.title(), depth-1)
        return result

def institution(categoryName, height=4):
    category = page.Category(commons, categoryName)
    if height <= 0:
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
        result = institution(categoryName, 0)
        if result is None:
            for parent in category.categories():
                result = institution(parent.title(), height-1)
                if result is not None:
                    break
        return result

def value(item):
    return {"Value":item}

def fill(category, item, result):
    print category
    print item
    dict={}
    dict["P195"] = value(item)
    dict["P276"] = value(item)
    result[category] = dict

def institutions(categoryName):
    result = {}
    category = page.Category(commons, categoryName)
    for subPage in sub(categoryName):
        if subPage.isCategory():
            fill(subPage.title(),institution(subPage.title()), result)
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

