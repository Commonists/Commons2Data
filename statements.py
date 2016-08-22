import pywikibot

site = pywikibot.Site('wikidata', 'wikidata')  # any site will work, this is just an example
repo = site.data_repository()  # this is a DataSite object

def write(category, items, facts):
    output_file = "output/"+category+".txt"
    lines = statements(items, facts)
    with open(output_file, 'w') as output:
        output.write("\n".join(lines))

def q(item):
    return item["item"][31:]  # removes http://www.wikidata.org/entity/

def statements(items, facts):
    result = []
    for q in items:
        item = pywikibot.ItemPage(repo, q)
        item.get()
        if item.claims:
            for prop in facts:
                if("Value" in facts[prop]):
                    statement = facts[prop]["Value"]
                    result.append("%s\t%s\t%s" % (q, prop, statement))
    return result

def generates_code_petscan(items, statements):
    """Generate code associating all statements to each item

    Args:
        items (list): list of wikidata item
        statements (list): list of wikidata statements formated for
            quickstatement

    Returns:
        str: Generated code for quickstatement

    Example:
        >>> generate_code(["Q42", "Q43"], ["P1\tQ2"]
        'Q42\tP1\tQ2\nQ43\tP1\tQ2'
    """
    lines = []  # lines of code
    for item in items:
        for statement in statements:
            lines.append("%s\t%s" % (item, statement))
    return "".join(lines)

def generates_code(items, statements):
    lines = []
    for item in items:
        for key in statements:
            if (key not in item):
                lines.append("%s\t%s" % (item, statements[key]))
    return "\n".join(lines)


#def generates_code(source):
#    if source == "query":
#        return generates_code_query
#    if source == "petscan":
#        return generates_code_petscan
#    else:
#        raise ValueError("Only supported sources are query and petsan")


