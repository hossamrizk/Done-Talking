from services import AudioDiarization, AudioSummarization, AudioTranscription

file = "/home/hossam/Speech-Projects/Podcast-Summarizer/src/assets/downloaded_audios/Talks of police department reform at center of Salt Lake City council meeting.mp3"

audio_diarization = AudioDiarization()
audio_summarization = AudioSummarization()
audio_transcription = AudioTranscription(audio_path=file)

print("Running diarization...")
diarization = audio_diarization.diarize(audio_file=file)

print("Building transcript...")
transcript = audio_transcription.build_trascript(diarization=diarization)

print("Formatting transcript...")
formatted = audio_summarization.format_transcript_for_prompt(transcript=transcript)

prompt = f"""
Below is a transcript of a meeting. Summarize it and extract action items. Identify speaker roles if possible.

{formatted}
"""

print("Generating summary with GPT-4...")
summary = audio_summarization.summarization(prompt)

print("Generating report...")
audio_summarization.generate_report(summary)

print("Done. Output saved to report.md")

