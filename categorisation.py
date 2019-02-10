# coding: utf-8
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import re
import sys
import bs4
import json
import codecs
import logging
import requests
import pywikibot
from pywikibot import page
from bs4 import BeautifulSoup



LOG =  logging.getLogger(name=__name__)
HANDLER = logging.StreamHandler(stream=sys.stdout)
HANDLER.setFormatter(logging.Formatter('%(asctime)s    %(module)s    %(levelname)s    %(message)s'))
HANDLER.setLevel(logging.DEBUG)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)

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
blackListLang=[u'lang', u'1', u'title', u'Title']

LOG =  logging.getLogger(name=__name__)
HANDLER = logging.StreamHandler(stream=sys.stdout)
HANDLER.setFormatter(logging.Formatter('%(asctime)s    %(module)s    %(levelname)s    %(message)s'))
HANDLER.setLevel(logging.DEBUG)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)

def sanitize(word):
    if type(word) is unicode:
        return word.replace("'","")
    else:
        return word['name'].replace("'","")

def templateToQitem(d, keys):
    pageName = None
    for key in keys:
        if key in d:
            pageName = d[key][0][0]['name']
            break
    if pageName is not None:
        page = pywikibot.Page(commons, pageName)
        if page.isRedirectPage():
            page = page.getRedirectTarget()
        return [re.search(itemExpression, page.text).group(0), re.split(":", pageName)[1]]
    else:
        return None

def createur(d):
    return templateToQitem(d, ["artist", "Artist"])

def institution(d):
    return templateToQitem(d, ["institution", "Institution"])

def harvestMultilang(d):
    result = {}
    for element in d:
        if 'params' in element[0]:
            for key in element[0]['params']:
                if key not in blackListLang:
                    result[key] = sanitize(element[0]['params']['en'][0][0])
            if 'lang' in element[0]['params']:
                result[element[0]['params']['lang'][0][0].lower()]=element[0]['params']['1'][0][0]
            if 'name' in element[0]:
                key = element[0]['name'].lower()
                if key not in blackListLang:
                    result[element[0]['name'].lower()]=element[0]['params']['1'][0][0]
    return result

def harvestPage(filename):
    content=requests.get(commonsedge+filename).json()
    result={}
    if "error" in content and "Artwork" in content["error"]:
        d = content["error_data"][0]["params"]
        if "description" in d:
            if "name" in d["description"][0][0]:
                lang = d["description"][0][0]["name"].lower()
                if lang not in blackListLang:
                    title = sanitize(d["description"][0][0]["params"]["1"][0][0])
                    result["label"]={lang:title}
            else:
                result["label"]={"en":sanitize(d["description"][0][0])}
        if "Title" in d:
            result["label"]=harvestMultilang(d["Title"])
        if "title" in d:
            result["label"]=harvestMultilang(d["title"])
        inst = institution(d)
        if inst:
            result[collection]=inst[0]
            result[localization]=inst[0]
        artist = createur(d)
        if artist:
            result[creator] = artist[0]
            result['artist'] = '('+artist[1]+')'
    return result

def createItem(info, filename="", qitem=""):
    if qitem is not "":
        item = pywikibot.ItemPage(repo,qitem)
        item.get()
    else:
        item = pywikibot.ItemPage(wikidata)
        LOG.info("Languages of labels")
        for lang in info["label"]:
            LOG.info(lang)
        item.editLabels(info["label"], summary="#Commons2Data label")
        item.get()
    for p in info:
        if p not in ["label", "artist"] and p not in item.claims:
            claim = pywikibot.Claim(repo, p)
            claim.setTarget(pywikibot.ItemPage(repo,info[p]))
            item.addClaim(claim, summary=p)
    if imageProperty not in item.claims:
        claim = pywikibot.Claim(repo, imageProperty)
        claim.setTarget(pywikibot.FilePage(commons,filename))
        item.addClaim(claim, summary=u'Image')

def hidden(category):
    return "Category:Hidden categories" in [c.title() for c in category.categories()]

def fusion_cat(images,qitem="", cat_name="", label_dict={}, descr_dict={}, objectCat=True, createCat=True, harvestImages=True):
    categories=[]
    img = None
    item = None
    info = {"label":label_dict}
    for image in images:
        img = image.title()[5:]
        if harvestImages and ("label" not in info or not any(info["label"])):
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
        if 'en' in item.labels:
            info["label"]["en"]=item.labels["en"]
        if 'fr' in item.labels:
            info["label"]["fr"]=item.labels["fr"]
    else:
        item = pywikibot.ItemPage(wikidata)
        LOG.info("Languages of labels")
        for lang in info["label"]:
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
    if "label" in info and "en" in info["label"]:
        title = info["label"]["en"]
    else:
        title = info["label"]["fr"]
    if creator in info:
        title = title + info['artist']
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


def creators_of(category_name):
    category = pywikibot.Category(commons, category_name)
    for subcat in category.subcategories():
        item = creator_of(subcat)
        if item is not None:
            dict_creator[subcat.title()]={
            "Properties":{"P170":{"Value":item.title()}},
            "Parents":[category_name]}
        else:
            missing.append(subcat.title())
    with open ("creators.json", "w") as data:
        json.dump(dict_creator, data, indent=2, ensure_ascii=False)
    with open ("missing.json", "w") as data:
        json.dump({"Missing":missing},data, indent=2, ensure_ascii=False)

def item_of(category_name):
    category = pywikibot.Category(commons, category_name)

def item_of(file):
    result = []


def main():
    file_name = "Category:Lena temp1"
    q_item = "Q50807788"
    temp = True
    harvestImages = False
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    p = pywikibot.Page(commons, file_name)
    if p.isCategory():
        cat = pywikibot.Category(p)
        if temp:
            LOG.info("Examining files on temp category %s", file_name)
            blackList.insert(0, file_name)
            fusion_cat([m for m in cat.members(namespaces=FILE_NAMESPACE)],
                cat_name="",
                qitem=q_item,
                harvestImages=False)
        else:
            LOG.info("Importing every image of category %s", file_name)
            for image in cat.members(namespaces=FILE_NAMESPACE):
                img = image.title()[5:]
                LOG.info("Creating item for %s", img)
                info = harvestPage(img)
                createItem(info, img)
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
