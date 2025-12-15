import requests
import gtfs_realtime_pb2
import pandas as pd
from io import StringIO
from google.protobuf import json_format

def get_positions() -> list[dict[str, str]]:
    '''Download data and return an array of objects corresponding to trams'''

    updates = requests.get("https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=trip_updates.pb")
    positions = requests.get("https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_positions.pb")

    if updates.status_code != 200:
        return None, updates.status_code
    
    if positions.status_code != 200:
        return None, positions.status_code
    
    info_upd = gtfs_realtime_pb2.FeedMessage()
    info_upd.ParseFromString(updates.content)

    info_pos = gtfs_realtime_pb2.FeedMessage()
    info_pos.ParseFromString(positions.content)

    entities_pos = info_pos.entity
    entities_upd = info_upd.entity

    tram_pos = list(filter(lambda entity: int(entity.id) < 1000, entities_pos))
    tram_upd = list(filter(lambda entity: int(entity.id) < 1000, entities_upd))

    def flatten(dictionary: dict) -> dict:
        flattened = {}

        for key, value in dictionary.items():
            if type(value) == dict:
                flattened = flattened | flatten(value)
            elif type(value) == list:
                if len(value) > 1:
                    print(value)
                flattened = flattened | flatten(value[0])
            else:
                flattened[key] = value
        return flattened

    def to_dict(entity) -> dict:
        json = json_format.MessageToDict(entity)
        return flatten(json)

    tram_pos_json = list(map(to_dict, tram_pos))
    tram_upd_json = list(map(to_dict, tram_upd))

    trams_json = list(map(lambda tram: tram[0] | tram[1], zip(tram_pos_json, tram_upd_json)))

    return trams_json, 200

def get_vehicle_dictionary() -> pd.DataFrame:

    vehicle_data = requests.get("https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_dictionary.csv")

    if vehicle_data.status_code != 200:
        return None, vehicle_data.status_code
    
    return pd.read_csv(StringIO(vehicle_data.text), index_col=0), 200

def get_vehicle_data() -> pd.DataFrame:

    vehicle_models = pd.read_csv("vehicle_models.csv", index_col=0)

    vehicle_dictionary = get_vehicle_dictionary()

    if vehicle_dictionary[1] != 200:
        return vehicle_dictionary

    return vehicle_models.join(vehicle_dictionary[0]), 200
