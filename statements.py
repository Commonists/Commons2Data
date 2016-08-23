import pywikibot

wikidata = pywikibot.Site('wikidata', 'wikidata')  # any site will work, this is just an example
repo = wikidata.data_repository()  # this is a DataSite object

def write(category, items, facts):
    output_file = "output/"+category+".txt"
    lines = statements(items, facts)
    with open(output_file, 'w') as output:
        output.write("\n".join(lines))

def statements(items, facts):
    result = []
    for q in items:
        item = pywikibot.ItemPage(repo, q)
        item.get()
        for prop in facts:
            if prop not in item.claims:
                if("Value" in facts[prop]):
                    statement = facts[prop]["Value"]
                    result.append("%s\t%s\t%s" % (q, prop, statement))
    return result
