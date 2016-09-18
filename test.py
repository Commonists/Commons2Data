#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json
import pywikibot

from pywikibot import page

categories={}

tree = {}

commons = pywikibot.Site('commons', 'commons')

finals = ["Paintings by Vincent van Gogh by name",
     "Lithographs by Vincent van Gogh by name",
     "Drawings by Vincent van Gogh by name",
     "Portrait paintings by Vincent van Gogh by title"]

def enrich(category):
    print category
    for prop in categories[category]:
        print prop+" "+categories[category][prop]
    cont = True
    while cont:
        text = input("Add fact: ")
        cont = text is not None and len(text) > 0
        if cont:
            qs = re.match('^(P[0-9]+) (Q[0-9]+)$', text)
            categories[category][qs.group(1)] = qs.group(2)
    print "Final statements"
    print categories[category]

#category is a String
#parent is a String
def treat_category(category, parent):
    if category in categories:
        categories[category].update(categories[parent])
    else:
        if parent in categories:
            categories[category] = categories[parent].copy()
        else:
            if parent == category:
                print "Treating a root category"
            else:
                print "Treating a category with no parent in the tree"
                print u"Parent: "+parent+u"; Category: "+category

# category is a PageCategory
def is_artwork(category):
    result = False
    i = 0
    super_categories = list(category.categories())
    try:
        while (not result) and i < len(super_categories):
            title = super_categories[i].title()
            result = title in finals
            i = i+1
        return result
    except:
        print "Errror in is_arwork with: "+title
        raise

# category is a string
def deep_loading(category):
    queue = [(category,category)]
    while len(queue) > 0:
        (child, parent) = queue.pop()
        treat_category(child, parent)
        subs = page.Category(commons, child).subcategoriesList()
        for sub in subs:
            if not is_artwork(sub):
                queue.append((sub.title(),child))

def main():
    categories_list =[
    u"Drawings by Vincent van Gogh",
    u"Lithographs by Vincent van Gogh",
    u"Paintings by Vincent van Gogh",
    u"Van Gogh works by date",
    u"Works by Vincent van Gogh by museum"
    u"Works by Vincent van Gogh by subject"]
    print ("JSON loading")
    with open("categories.json") as data:
        categories = json.loads(data.read())
    loaded_categories = []
    print ("Commons loading")
    for category in categories_list:
        deep_loading(category)
#    for category in categories
#        enrich(category)
    print ("Writting file")
    with open ("test.json", "w") as data:
        json.dump(categories, data)
    print "Done !"


if __name__ == "__main__":
    main()
