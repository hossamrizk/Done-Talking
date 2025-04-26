import pandas as pd

def load_csv(csv_path: str) -> pd.DataFrame:
    all_csv = pd.read_csv(csv_path)
    speakers = all_csv["speaker"].tolist()
    text = all_csv["text"].tolist()
    return speakers, text 

