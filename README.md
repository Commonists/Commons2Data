# Commons2Data
Transpose semantic of commons categories into wikidata statements

The end-goal is to have all the knowledge stored as categories and categories tree copied to wikidata. Imagine a world in which we would have dynamic, request-based, multilingual categories instead of static, English-but-not-always, "1880s paintings in France of women in red dresses facing right" categories.

# How it works
From a Commons categories,
  We generate the list of items "within" this category (threw petscan for the moment)
  We translate the semantic of the category as facts (by a human)
  We generate the missing statements
  We had that to an external tool (QuickStatements) to contribute to Wikidata
