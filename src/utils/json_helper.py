import json


def extract_json(string):
    try:
        json_object = json.loads(string)
        return json_object
    except ValueError as e:
        print ("Invalid json received. Trying to extract it")
    
    # find the json in the text
    start = string.find("{")
    end = string.rfind("}")
    json_string = string[start:end+1]
    print(json_string)

    # remove any characters before the first " and after the last "
    start = string.find("\"")
    end = string.rfind("\"")
    json_string = f"{{{string[start:end+1]}}}"
    print(json_string)

    # put newlines into json formatting
    # json_string = json_string.replace('\n', '\\n') # TODO: only rewrite newlines in values
    print(json_string)
    return json.loads(json_string)
