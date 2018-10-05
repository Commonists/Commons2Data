# coding: utf-8
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import codecs
import json
import logging
import requests
import pywikibot
import sys
import re
import bs4
from bs4 import BeautifulSoup
from pywikibot import page


commonsedge = "https://tools.wmflabs.org/commonsedge/api.php?file="
commons = pywikibot.Site('commons', 'commons')
wikidata = pywikibot.Site("wikidata", "wikidata")
repo = wikidata.data_repository()

itemExpression = re.compile("Q\d+")

dict_creator = {}

missing = []

cache = json.loads(open("dump.json").read())


#Properties
catalog = "P528"
inventory = "P217"
commonsCat = "P373"
imageProperty = "P18"
depict = "P180"
creator = "P170"
collection = "P195"
localization = "P276"

duplicates=[depict, creator]

FILE_NAMESPACE = 6
CREATOR_NAMESPACE = 100

blackList=["Category:Rituels grecs – Une expérience sensible","Category:Details of paintings by Georges de La Tour"]

LOG =  logging.getLogger(name=__name__)
HANDLER = logging.StreamHandler(stream=sys.stdout)
HANDLER.setFormatter(logging.Formatter('%(asctime)s    %(module)s    %(levelname)s    %(message)s'))
HANDLER.setLevel(logging.DEBUG)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)

def sanitize(word):
    return word.replace("'","")

def institution(d):
    inst = None
    if 'institution' in d:
        inst = d['institution'][0][0]['name']
    elif 'Institution' in d:
        inst = d['Institution'][0][0]['name']
    if inst is not None:
        page = pywikibot.Page(commons, inst)
        if page.isRedirectPage():
            page = page.getRedirectTarget()
        return re.search(itemExpression, page.text).group(0)
    else:
        return None

def harvestPage(filename):
    json=requests.get(commonsedge+filename).json()
    result={}
    if "error" in json and "Artwork" in json["error"]:
        d = json["error_data"][0]["params"]
        if "description" in d:
            if "name" in d["description"][0][0]:
                lang = d["description"][0][0]["name"].lower()
                title = sanitize(d["description"][0][0]["params"]["1"][0][0])
                result["label"]={lang:title}
            else:
                result["label"]={"en":sanitize(d["description"][0][0])}
        if "Title" in d:
            t = d["Title"][0][0]["params"]
            result["label"]={}
            for key in t:
                result["label"][key]=sanitize(t[key][0][0])
        if "title" in d:
            if 'params' in d["title"][0][0]:
                t = d["title"][0][0]["params"]
                result["label"]={}
                for key in t:
                    if key not in [u'lang', u'1']:
                        result["label"][key]=sanitize(t[key][0][0])
            else:
                result["label"]={"en":sanitize(d["title"][0][0])}
        inst = institution(d)
        if inst:
            result[collection]=inst
            result[localization]=inst
    return result


def hidden(category):
    return "Category:Hidden categories" in [c.title() for c in category.categories()]

def fusion_cat(images,qitem="", cat_name="", label_dict={}, descr_dict={}, objectCat=True, createCat=True):
    categories=[]
    img = None
    item = None
    info = {"label":label_dict}
    for image in images:
        img = image.title()[5:]
        if "label" not in info or not any(info["label"]):
            info = harvestPage(img)
        for cat in image.categories():
            if createCat:
                if cat.title() not in blackList and not hidden(cat):
                    categories.append(cat.title())
                    blackList.append(cat.title())
            elif not hidden(cat):
                for parent in cat.categories():
                    if parent not in blackList:
                        categories.append(parent.title())
                        blackList.append(parent.title())
    if qitem is not "":
        item = pywikibot.ItemPage(repo,qitem)
        item.get()
    else:
        item = pywikibot.ItemPage(wikidata)
        item.editLabels(info["label"], summary="#Commons2Data label")
        item.editDescriptions(descr_dict, summary="#Commons2Data description")
        item.get()
    for cat in categories:
        if cat in cache:
            for p in cache[cat]["Properties"]:
                if p not in item.claims or p in duplicates:
                    claim = pywikibot.Claim(repo, p)
                    if "Value" in cache[cat]["Properties"][p]:
                        if "Q" in cache[cat]["Properties"][p]["Value"]:
                            claim.setTarget(pywikibot.ItemPage(repo,cache[cat]["Properties"][p]["Value"]))
                        else:
                            claim.setTarget(pywikibot.WbTime(year=cache[cat]["Properties"][p]["Value"]["Year"]))
                        item.addClaim(claim, summary=u'#Commons2Data adding claim')
    title = info["label"]["en"]
    LOG.info(title)
    if createCat:
        print_category(item.title(), title, categories,objectCat)
        categories.append(blackList[0])
        LOG.info("Will remove "+blackList[0])
        for image in images:
            clean_image(image, title, categories)
    # Wikidata
    if imageProperty not in item.claims:
        claim = pywikibot.Claim(repo, imageProperty)
        claim.setTarget(pywikibot.FilePage(commons,img))
        item.addClaim(claim, summary=u"Commons2Data image")
    category = pywikibot.Category(commons, title)
    item.setSitelink(category, summary="#FileToCat Commons sitelink.")
    claim = pywikibot.Claim(repo, commonsCat)
    claim.setTarget(title)
    item.addClaim(claim, summary="#FileToCat Commons claim")


def print_category(item, title, addList, objectCat=True):
    LOG.info("Creating Commons category "+title)
    if title is not "":
        result = ""
        if item is not "" and objectCat:
            result = "{{Wikidata Infobox}}"
        category = pywikibot.Category(commons, title)
        for add in addList:
            result = result+"\n[["+add+"]]"
        category.text = result
        category.save("#FileToCat Category creation")

def clean_image(image, title, removeList):
    t = image.text
    for r in removeList:
        pattern = re.compile("\[\["+r+"(\|(\w|;|>)+)?\]\]")
        s = re.search(pattern, t)
        if s is not None:
            t = t.replace(s.group(0),"")
    t = t+"\n[[Category:"+title+"]]"
    image.text = t
    image.save("#FileToCat Image in its own category")

def main():
    file_name = "Category:Lena temp1"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    p = pywikibot.Page(commons, file_name)
    if p.isCategory():
        LOG.info("Examining files on temp category %s", file_name)
        blackList.insert(0, file_name)
        cat = pywikibot.Category(p)
        fusion_cat([m for m in cat.members(namespaces=FILE_NAMESPACE)],
            cat_name="",
            qitem="Q56880840")
    else:
        LOG.info("Examining galleries on page %s", file_name)
        soup = BeautifulSoup(p.text, 'html.parser')
        filess = [re.split("\n", soup.contents[i].contents[0])[1:-1] for i in range(len(soup.contents)) if isinstance(soup.contents[i], bs4.element.Tag)]
        LOG.info("Found %d galleries", len(filess))
        print(filess)
        for files in filess:
            fusion_cat([pywikibot.Page(commons, file) for file in files])

if __name__ == '__main__':
    main()