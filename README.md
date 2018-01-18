# Commons2Data
Transpose the semantics of Wikimedia Commons categories into Wikidata statements

The end-goal is to have all the knowledge stored as categories and the category tree synced with Wikidata. Imagine a world in which we would have dynamic, request-based, multilingual categories instead of static, English-but-not-always, "1880s paintings in France of women in red dresses facing right" categories.

# How it works
From a Commons category, we
* generate the list of items "within" this category, through interwiki and {{artwork}} parameters;
* translate the semantics of the category into facts (by a human);
* generate the missing statements;
* add that to Wikidata.

# Tools used
* pywikibot, commonsedge

# What it needs
* Moving to Tool Labs and working with dumps
* Improving the algorithm (mixing reading and writing ? Multithread ? Better tree exploration ?)
* Creating a UI to collect the category->facts translation
* Dynamic facts within the tree (a daughter category has all the statements of its mother + some)
