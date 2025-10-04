from .AbstractFormatter import AbstractFormatter
import inflect


class EnglishFormatter(AbstractFormatter):
    def __init__(self):
        self.p = inflect.engine()

    def _extract_number(self, speaker_id):
        return int(speaker_id.split("_")[-1])

    def format_summary(self, data: dict) -> str:
        talked = data.get("most_talked_speakers", [])
        most_talked = ", ".join(f"SPEAKER {self._extract_number(s)}" for s in talked)
        sentence1 = f"The most talked speakers are {most_talked}."

        durations = data.get("total_duration", {})
        duration_parts = [
            f"for speaker number {self._extract_number(s)} spoke for {d} seconds"
            for s, d in durations.items()
        ]
        sentence2 = "Total speaking duration for all speakers are: " + ", ".join(duration_parts) + "."

        # Most used word
        word_info = data.get("most_used_word", [])
        if len(word_info) == 3:
            word, total_count, speaker_counts = word_info
            details = ", ".join(
                f"speaker number {self._extract_number(s)} said it {self.p.number_to_words(c)} time{'s' if c != 1 else ''}"
                for s, c in speaker_counts.items()
            )
            sentence3 = (
                f"The most used word is {word} and it is mentioned {total_count} times, {details}."
            )
        else:
            sentence3 = "Most used word data is missing or malformed."

        return f"{sentence1}\n{sentence2}\n{sentence3}"
