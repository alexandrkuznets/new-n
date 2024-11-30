import requests
import json

starship_info = dict()

my_req = requests.get("https://www.swapi.tech/api/starships/12/")

data = json.loads(my_req.text)

for elem in data["result"]["properties"]:
    if elem in ("starship_class", "max_atmosphering_speed", "name"):
        starship_info[elem] = data["result"]["properties"][elem]
    elif elem == "pilots":
        starship_info["pilots"] = []
        for pilot in data["result"]["properties"]["pilots"]:
            pilot_req = requests.get(pilot)
            data_pilot = json.loads(pilot_req.text)
            dict_pilot = dict()
            for i_pilot in data_pilot["result"]["properties"]:
                if i_pilot in ("height", "name", "mass"):
                    dict_pilot[i_pilot] = data_pilot["result"]["properties"][i_pilot]
                elif i_pilot == "homeworld":
                    planet_req = requests.get(data_pilot["result"]["properties"][i_pilot])
                    data_planet = json.loads(planet_req.text)
                    for i_planet in data_planet["result"]["properties"]:
                        if i_planet == "name":
                            dict_pilot["homeworld"] = data_planet["result"]["properties"]["name"]
                        elif i_planet == "url":
                            dict_pilot["homeworld_url"] = data_planet["result"]["properties"]["url"]
            starship_info["pilots"].append(dict_pilot)


print(starship_info)
with open("starship_info.json", "w") as file:
    json.dump(starship_info, file, indent=4)
