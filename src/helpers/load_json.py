import json 

def load_json(json_path: str):
    with open(json_path, 'r') as file:
        data = json.load(file)

    meeting_topic = data["meeting_topic"]
    summary = data["summary"]
    return meeting_topic, summary