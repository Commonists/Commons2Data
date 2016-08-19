import json
import argparse
import os
#os.path.join("item", "truc.txt")

#statements = ["P571\t+1887-01-01T00:00:00Z/9"]

def loads_items_petscan(input_file):
    with open(input_file) as json_data:
        items_json = json.load(json_data)
        item = [line['q']
                for line in items_json['*'][0]['a']['*']]
    return item

def loads_items_query(input_file):
    with open(input_file) as json_data:
        items = json.load(json_data)
    return items

def loads_items(source):
    if(source == "query"):
        return loads_items_query
    if(source == "petscan"):
        return loads_items_petscan
    else:
        raise ValueError("Only supported sources are query and petsan")

def loads_statements(source):
    if(source == "query"):
        return loads_statements_query
    if(source == "petscan"):
        return loads_statements_petscan
    else:
        raise ValueError("Only supported sources are query and petsan")

def loads_statements_petscan(input_statements):
    with open(input_statements) as data:
        statements = data.readlines()
    return statements

def loads_statements_query(input_statements):
    with open(input_statements) as data:
            statements = json.load(data)
    return statements

def generates_codes_petscan(items, statements):
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

def q(item):
    return item["item"][31:] #removes http://www.wikidata.org/entity/

def generates_code_query(items, statements):
    lines = []
    for item in items:
        for key in statements:
            if (key not in item):
                lines.append("%s\t%s" % (q(item), statements[key]))
    return "\n".join(lines)

def generates_code(source):
    if(source == "query"):
        return generates_code_query
    if(source == "petscan"):
        return generates_code_petscan
    else:
        raise ValueError("Only supported sources are query and petsan")

def main():
    from argparse import ArgumentParser
    description = 'Translating Commons categories semantic into Wikidata statements'
    parser = ArgumentParser(description=description)
    parser.add_argument('-s', '--source',
                        type=str,
                        dest='source',
                        required=False,
                        default="query",
                        help='Source of the JSON for items : petscan or query')
    parser.add_argument('-f', '--filename',
                        type=str,
                        dest='filename',
                        required=True,
                        default=None,
                        help='File with the items in a JSON format')
    args = parser.parse_args()
    input_items = args.filename
    input_statements = input_items.replace(".json", ".txt")
    statements = loads_statements(args.source)(input_statements)
    output_file = input_statements.replace("items", "statements")
    items = loads_items(args.source)(input_items)
    lines = generates_code(args.source)(items, statements)
    with open(output_file, 'w') as output:
        output.write(lines)

if __name__ == "__main__":
    main()
