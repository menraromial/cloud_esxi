import json

with open('config\deploy_to_many_esxi.json') as file:
    data = json.load(file)
    for key, value in data.items():
        print(key, value)
    #print(data)

