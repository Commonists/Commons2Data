import pywikibot
from pywikibot import page

wikidata = pywikibot.Site('wikidata', 'wikidata')  # any site will work, this is just an example
repo = wikidata.data_repository()  # this is a DataSite object

def write(category, items, claims):
    result = []
    for q in items:
        item = pywikibot.ItemPage(repo, q)
        item.get()
        for prop in claims:
            if prop not in item.claims:
                if("Value" in claims[prop]):
                    target = claims[prop]["Value"]
                    write_statement(item, prop, target)

def write_statement(item, prop, target):
    claim = pywikibot.Claim(repo, prop)
    target = pywikibot.ItemPage(repo, target)
    claim.setTarget(target)
    item.addClaim(claim)
