import facts
import items
import statements

def main():
    from argparse import ArgumentParser
    description = 'Translating Commons categories semantic into Wikidata statements'
    parser = ArgumentParser(description=description)
    parser.add_argument('-c', '--category',
                        type=str,
                        dest='category',
                        required=True,
                        default="query",
                        help='Category from which to generate the statements')
    args = parser.parse_args()
    its = items.loads_items(args.category)
    fcts = facts.loads_facts(args.category)
    statements.write(args.category, its, fcts)

if __name__ == "__main__":
    main()
