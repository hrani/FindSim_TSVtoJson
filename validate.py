import json
import jsonschema
import argparse

def main():
    parser = argparse.ArgumentParser( description = "JSON schema validator." )
    parser.add_argument( 'script', type = str, help = 'Required: Json script to be validated' )
    parser.add_argument( 'schema', type = str, help = 'Required: Json schema to do the validation' )

    args = parser.parse_args()
    
    with open ( args.schema ) as schema_file:
        schema = json.load( schema_file )
    with open ( args.script ) as script_file:
        script = json.load( script_file )


    jsonschema.validate( script, schema )
    print( "If this is the only message, then the validation was good")

if __name__ == '__main__':
    main()
