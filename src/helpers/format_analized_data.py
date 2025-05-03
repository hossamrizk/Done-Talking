import inflect

def format_analized_data(data: dict) -> str:
    """
    Summarizes speaker data from a specific JSON structure into a readable paragraph.

    Args:
        data (dict): JSON-like dictionary with keys:
                     - "most_talked_speakers": list of speaker IDs
                     - "total_duration": dict of speaker IDs to durations
                     - "most_used_word": [word, total_count, {speaker_id: count}]

    Returns:
        str: A formatted multi-line string summary.
    """
    p = inflect.engine()

    # Helper to extract number from 'SPEAKER_01' → 1
    def extract_number(s):
        return int(s.split("_")[-1])

    # Sentence 1: Most talked speakers
    talked = data.get("most_talked_speakers", [])
    most_talked = ", ".join(f"SPEAKER {extract_number(s)}" for s in talked)
    sentence1 = f"The most talked speakers are {most_talked}."

    # Sentence 2: Total speaking durations
    durations = data.get("total_duration", {})
    duration_parts = [
        f"for speaker number {extract_number(s)} spoke for {d} seconds"
        for s, d in durations.items()
    ]
    sentence2 = "Total speaking duration for all speakers are: " + ", ".join(duration_parts) + "."

    # Sentence 3: Most used word
    word_info = data.get("most_used_word", [])
    if len(word_info) == 3:
        word, total_count, speaker_counts = word_info
        details = ", ".join(
            f"speaker number {extract_number(s)} said it {p.number_to_words(c)} time{'s' if c != 1 else ''}"
            for s, c in speaker_counts.items()
        )
        sentence3 = (
            f"The most used word is {word} and it is mentioned {total_count} times, {details}."
        )
    else:
        sentence3 = "Most used word data is missing or malformed."

    return f"{sentence1}\n{sentence2}\n{sentence3}"