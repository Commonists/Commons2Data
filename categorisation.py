# coding: utf-8
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import codecs
import json
import pywikibot
import sys
import re
from pywikibot import page

commons = pywikibot.Site('commons', 'commons')
wikidata = pywikibot.Site("wikidata", "wikidata")
repo = wikidata.data_repository()

itemExpression = re.compile("Q\d+")

cache = json.loads(open("dump.json").read())

#Properties
catalog = "P528"
inventory = "P217"
commonsCat = "P373"
imageProperty = "P18"
depict = "P180"

duplicates=[depict]

FILE_NAMESPACE = 6

label_dict={"en":"The Dream", "de":"Der Traum"}
descr_dict={"en":"Franz Marc painting", "fr":"Peinture de Franz Marc"}

blackList=[""]

def hidden(category):
    return "Category:Hidden categories" in [c.title() for c in category.categories()]

def fusion_cat(tempCat,qitem=""):
    categories=[]
    img = None
    item = None
    page = pywikibot.Category(commons, tempCat)
    for image in page.members(namespaces=FILE_NAMESPACE):
        img = image.title()[5:]
        for cat in image.categories():
            if cat.title() not in blackList and not hidden(cat):
                categories.append(cat.title())
                blackList.append(cat.title())
    if qitem is not "":
        item = pywikibot.ItemPage(repo,qitem)
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
                        if "Q" in cache[cat]["Properties"][p]["Value"]:
                            claim.setTarget(pywikibot.ItemPage(repo,cache[cat]["Properties"][p]["Value"]))
                        else:
                            claim.setTarget(pywikibot.WbTime(year=cache[cat]["Properties"][p]["Value"]["Year"]))
                        item.addClaim(claim, summary=u'#Commons2Data adding claim')
            else:
                print(cat)
    title = label(item)+" (Franz Marc)"
    print_category(item.title(), title, categories)
    categories.append("Category:"+tempCat)
    for image in page.members(namespaces=FILE_NAMESPACE):
        clean_image(image, title, categories)
    # Wikidata
    claim = pywikibot.Claim(repo, imageProperty)
    claim.setTarget(pywikibot.FilePage(commons,img))
    item.addClaim(claim, summary="Commons2Data image")
    category = pywikibot.Category(commons, title)
    item.setSitelink(category, summary="#FileToCat Commons sitelink.")
    claim = pywikibot.Claim(repo, commonsCat)
    claim.setTarget(title)
    item.addClaim(claim, summary="#FileToCat Commons claim")

def label(item):
    title=""
    item.get()
    if u"en" in item.labels:
        title = item.labels["en"]
        if catalog in item.claims:
            if item.claims[catalog][0].target is not None:
                title = title+" ("+item.claims[catalog][0].target+")"
            elif item.claims[catalog][1].target is not None:
                title = title+" ("+item.claims[catalog][1].target+")"
        elif inventory in item.claims:
            title = title+" ("+item.claims[inventory][0].target+")"
    return title


def print_category(item, title, addList):
    if title is not "":
        result = ""
        if item is not "":
            result = "<onlyinclude>\n{{User:Rama/Catdef|"+item+"}}\n</onlyinclude>"
        category = pywikibot.Category(commons, title)
        for add in addList:
            result = result+"\n[["+add+"]]"
        category.text = result
        category.save("#FileToCat Category creation")

def clean_image(image, title, removeList):
    t = image.text
    for r in removeList:
        t = t.replace("[["+r+"]]","")
    t = t+"\n[[Category:"+title+"]]"
    image.text = t
    image.save("#FileToCat Image in its own category")

fusion_cat("Lena temp1", "Q18685517")
