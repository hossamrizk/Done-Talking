import json 

def load_json(json_path: str):
    with open(json_path, 'r') as file:
        data = json.load(file)

    meeting_topic = data["meeting_topic"]
    #key_speakers = data["key_speakers"]
    #key_decisions = data["key_decisions"]
    #action_items = data["action_items"]
    #discussion_highlights = data["discussion_highlights"]
    summary = data["summary"]
    #return meeting_topic, key_speakers, key_decisions, action_items, discussion_highlights
    return meeting_topic, summary