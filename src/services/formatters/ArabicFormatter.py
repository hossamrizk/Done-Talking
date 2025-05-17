from .AbstractFormatter import AbstractFormatter
import re

ARABIC_ORDINALS = [
    "الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس",
    "السابع", "الثامن", "التاسع", "العاشر", "الحادي عشر", "الثاني عشر",
]

class ArabicFormatter(AbstractFormatter):

    def format_summary(self, data: dict) -> str:
        formatted = {}

        # أكثر المتحدثين
        speakers = data.get("أكثر المتحدثيين هم", [])
        formatted["أكثر المتحدثين هم"] = f": {', '.join(speakers)}."

        # إجمالي وقت التحدث
        durations = data.get("اجمالى وقت التحدث", {})
        formatted_duration = ", ".join([f"{s}: {t} ثانية" for s, t in durations.items()])
        formatted["اجمالى وقت التحدث لجميع المتحدثين هو"] = f": {formatted_duration}."

        # أكثر الكلمات استخدامًا
        most_used = data.get("أكثر الكلمات استخدامآ", ())
        if most_used and isinstance(most_used, tuple):
            word, count, speaker_count = most_used
            distribution = ", ".join([f"{s}: {c}" for s, c in speaker_count.items()])
            formatted["الكلمة الأكثر استخدامًا هى"] = f": {word} ({count} مرة), وتوزيع الاستخدام بين المتحدثين: {distribution}."
        else:
            formatted["الكلمة الأكثر استخدامًا هى"] = "بيانات أكثر الكلمات استخدامًا مفقودة أو مشوهة."

        return "\n".join(f"{k}{v}" for k, v in formatted.items())

    def replace_speaker_tags(self, text):
        def repl(match):
            idx = int(match.group(1))
            return f"المتحدث {ARABIC_ORDINALS[idx]}" if idx < len(ARABIC_ORDINALS) else f"المتحدث {idx}"

        if isinstance(text, str):
            return re.sub(r"SPEAKER_(\d\d)", repl, text)
        elif isinstance(text, list):
            return [self.replace_speaker_tags(t) for t in text]
        elif isinstance(text, dict):
            return {self.replace_speaker_tags(k): self.replace_speaker_tags(v) for k, v in text.items()}
        return text

    def clean_field(self, value):
        if isinstance(value, list):
            return [v for v in value if not re.match(r"SPEAKER_\d\d", str(v))]
        return value
