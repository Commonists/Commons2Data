import json
import requests
import re
import datetime
from datetime import datetime
from datetime import timedelta
import pywikibot
from pywikibot import page

commons = pywikibot.Site('commons', 'commons')
commonsedge = "https://tools.wmflabs.org/commonsedge/api.php?file="
itemExpression = re.compile("Q\d+")
cache = json.loads(open("dump.json").read())
delta = timedelta(days=150)
dateFormat = "%Y-%m-%d %H:%M:%S.%f"

def loads_items(category, depth=2):
    items = []
    pages = sub(category, depth)
    for page in pages:
        it = item(page)
        if it[0]:
            items.append(it[1])
    return items

def now():
    return {"Timestamp":str(datetime.now())}

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

def isExpired(property):
    return "Timestamp" not in property.keys()
    or datetime.now() -datetime.strptime(property["Timestamp"], "%Y-%m-%d %H:%M:%s.%Z") > delta

def oldInstitution(categoryName):
    if (categoryName in cache.keys()
        and "Properties" in cache[categoryName]
        and "P195" in cache[categoryName]["Properties"]
        and (not isExpired(cache[categoryName]["Properties"]["P195"]))):
        return cache[categoryName]["Properties"]["P195"]["Value"]
    else:
        return "not found"

def institution(categoryName, height=4, stores=True):
    print categoryName
    print height
    result = oldInstitution(categoryName)
    if result == "not found":
        category = page.Category(commons, categoryName)
        if height <= 0:
            inst = [i for i in category.articles(namespaces=106)]
            if len(inst) == 0:
                result = None
            else:
                items = itemExpression.findall(inst[0].get())
                if len(items) is not 0:
                    result = items[0]
        else:
            result = institution(categoryName, 0, True)
            for parent in category.categories():
                if result is not None:
                    break
                result = institution(parent.title(), height-1)
        print "Storing"
        fill(categoryName, result, cache)
    else:
        print "Already found"
        result = None
    print "result"
    print result
    return result

def value(item):
    return {"Value":item,"Timestamp":datetime.now()}

def fill(category, item, result):
    if category not in result.keys() or "P195" not in result[category].keys() or result[category]["P195"]["Value"] is None:
        dict={}
        dict["P195"] = value(item)
        dict["P276"] = value(item)
        result[category] = {"Properties":dict}

def institutions(categoryName):
    category = page.Category(commons, categoryName)
    for subPage in sub(categoryName):
        if subPage.isCategory():
            institution(subPage.title(0), stores=True)
            print "Institution found"
    print "Institutions"
    with open("dumpR.json", "w") as data:
        data = json.dumps(cache, indent=2)
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

#institutions("Paintings by Carlo Crivelli by museum")
institutions("Paintings by Aelbert Cuyp by museum")
