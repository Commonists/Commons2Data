# coding: utf-8
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import re
import sys
import json
import codecs
import logging
import pywikibot
from pywikibot import page

LOG =  logging.getLogger(name=__name__)
HANDLER = logging.StreamHandler(stream=sys.stdout)
HANDLER.setFormatter(logging.Formatter('%(asctime)s    %(module)s    %(levelname)s    %(message)s'))
HANDLER.setLevel(logging.DEBUG)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)

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

duplicates=[depict, creator]

FILE_NAMESPACE = 6
CREATOR_NAMESPACE = 100

blackList=["Category:Rituels grecs – Une expérience sensible","Category:Details of paintings by Georges de La Tour"]

def hidden(category):
    return "Category:Hidden categories" in [c.title() for c in category.categories()]

def fusion_cat(images,qitem="", cat_name="", label_dict={}, descr_dict={}, objectCat=True, createCat=True):
    categories=[]
    img = None
    item = None
    page = pywikibot.Category(commons, tempCat)
    for image in page.members(namespaces=FILE_NAMESPACE):
        img = image.title()[5:]
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
        item.editLabels(label_dict, summary="#Commons2Data label")
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
                    else:
                        print (cat)
                        print (p)
        else:
            print (cat)
    title = cat_name
    if title is "":
        title = label(item)
    if createCat:
        print_category(item.title(), title, categories,objectCat)
        categories.append("Category:"+tempCat)
        for image in page.members(namespaces=FILE_NAMESPACE):
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

def label(item):
    title=""
    if u"en" in item.labels:
        title = item.labels["en"]
    elif u"fr" in item.labels:
        title = item.labels["fr"]
    if catalog in item.claims:
        if item.claims[catalog][0].target is not None:
            title = title+" ("+item.claims[catalog][0].target+")"
        elif item.claims[catalog][1].target is not None:
            title = title+" ("+item.claims[catalog][1].target+")"
    elif inventory in item.claims:
        title = title+" ("+item.claims[inventory][0].target+")"
    elif creator in item.claims:
        itemAuthor = item.claims[creator][0].target
        itemAuthor.get()
        title = title+" ("+itemAuthor.labels["en"]+")"
    return title

def print_category(item, title, addList, objectCat=True):
    if title is not "":
        result = ""
        if item is not "" and objectCat:
            result = "<onlyinclude>\n{{User:Rama/Catdef|"+item+"}}\n</onlyinclude>"
        category = pywikibot.Category(commons, title)
        for add in addList:
            result = result+"\n[["+add+"]]"
        category.text = result
        category.save("#FileToCat Category creation")

def clean_image(image, title, removeList):
    t = image.text
    for r in removeList:
        pattern = re.compile("\[\["+r+"(\|\w+)?\]\]")
        s = re.search(pattern, t)
        if s is not None:
            t = t.replace(s.group(0),"")
    t = t+"\n[[Category:"+title+"]]"
    image.text = t
    image.save("#FileToCat Image in its own category")

def creator_of(category):
    try:
        creator = category.members(namespaces=CREATOR_NAMESPACE).next()
        if re.search(itemExpression, creator.text) is not None:
            return re.search(itemExpression, creator.text).group(0)
        else:
            return None
    except StopIteration:
        return None

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
    file_name = "User:Donna Nobot/clusterArtworks/inp"
    height=1
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    page = pywikibot.Page(commons, file_name)
    if page.isCategory():
        LOG.info("Clustering files from a temp category %s", file_name)
        blackList.add(file_name)
        fusion_cat([image for image in page.members(namespaces=FILE_NAMESPACE)])
    else: # galleries
        LOG.info(u"Clustering files from a galleries at %s", file_name)
        regex = u"<gallery mode=\"packed\">[\w|\s|:|.|,|-|é]+</gallery>"
        LOG.info("Found %d clusters",len(re.findall(regex, page.text)))

if __name__ == '__main__':
    main()
