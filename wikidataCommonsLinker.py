# coding: utf-8
import pywikibot
from pywikibot import page

COMMONS = pywikibot.Site('commons', 'commons')
WIKIDATA = pywikibot.Site("wikidata", "wikidata")
REPO = WIKIDATA.data_repository()

IMG_PROPERTY = "P18"
COMMONS_CAT_PROPERTY = "P373"


def streets(streets_category, city_item):
    streets = pywikibot.Category(COMMONS, streets_category).subcategories()
    street_items =
    for item in street_items:
        if IMG_PROPERTY in item.claims:
            image = item.claims[imageProperty].target()[]
            for category in image.categories():
                if category in streets:
                    item.setSitelink(category, summary="#WikidataCommonsLinker Commons sitelink.")
                    claim = pywikibot.Claim(repo, COMMONS_CAT_PROPERTY)
                    claim.setTarget(category.title())
                    item.addClaim(claim, summary="#WikidataCommonsLinker Commons claim")
