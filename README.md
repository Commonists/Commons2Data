# Commons2Data
Transpose semantic of commons categories into wikidata statements

The end-goal is to have all the knowledge stored as categories and categories tree copied to wikidata. Imagine a world in which we would have dynamic, request-based, multilingual categories instead of static, English-but-not-always, "1880s paintings in France of women in red dresses facing right" categories.

# How it works
From a Commons categories,
* We generate the list of items "within" this category, threw interwiki and {{artwork}} parameter
* We translate the semantic of the category as facts (by a human)
* We generate the missing statements
* We add that to wikidata

# Tools used
* pywikibot, commonsedge

# What it needs
* Moving to toolslab and working with dumps
* Improving the algorithm (mixing reading and writting ? Multithread ? Better tree exploration ?)
* Creating an UI to collects the category->facts translation
* Dynamic facts within the tree (a daughter category has all the statements of its mother + some)
