import os
import json

curdir = os.path.dirname(os.path.realpath(__file__))

selectors_file = "selectors.json"

selectors = None

with open(os.path.join(curdir,selectors_file),'r') as sfile:
    selectors = json.load(sfile)


if __name__ == "__main__":
    print("Selectors file is :"+curdir)
    print("- Telegram Page CSS Selectors -")
    keys = selectors.keys()
    for key in keys:
        print(key + " : " + selectors[key])