#import pwb  # only needed if you haven't installed the framework as side-package
import pywikibot
import requests
site = pywikibot.Site('wikidata', 'wikidata')  # any site will work, this is just an example
repo = site.data_repository()  # this is a DataSite object

properties = {
    "P31":{
        "Fix":True,
        "Value":"Q31"
    },
    "P32":{
        "Fix":True,
        "Value":"coucou"
    },
    "P23":{
        "Fix":False,
        "values":{
            "1890":"Q23",
            "1889":"Q24"
        },
    },
    "P40":{
        "Fix":False,
        "values":{
            "Paris":"Q41",
            "Auvers":"Q42"
        }
    }
}

def q(fileName):
    url = "https://tools.wmflabs.org/commonsedge/api.php?file="
    json=requests.get(url+fileName).json()
    return json["error_data"]

def readItem(q):
    result = []
    item = pywikibot.ItemPage(repo, q)
    item.get()
    if item.claims:
        for prop in properties:
            if(properties[prop]["Fix"]):
                statement = properties[prop]["Value"]
                result.append("%s\t%s" % (q, statement))
    print result
    return result

q("Van Gogh - Wiese und Baum mit Blick auf den Mont Gaussier.jpeg")



