from crewai import Agent, Task, LLM, Process, Crew
from textwrap import dedent
from models import MeetingSummary
import os

class SummarizationAgent:
    def __init__(self, model: LLM = LLM(model="ollama/gemma2:9b", temperature=0.6, base_url="http://localhost:11434")):
        self.output_path = ("assets/generated_reports")
        os.makedirs(self.output_path, exist_ok=True)
        self.model = model

    def summarization_agent(self):
        return Agent(
            role="Meeting Summarizer and Speaker Analyzer",
            goal="Summarize the meeting based on provided text and identify who spoke the most.",
            backstory=dedent("""
                You are an expert meeting summarizer. 
                You are given diarized meeting data: lists of speakers and what each said. 
                Your job is to create a structured, readable summary of the conversation. 
                You must also identify the speaker who contributed the most and highlight their key points.
            """),
            llm=self.model,
            verbose=True
        )

    def summarization_task(self):
        return Task(
            description=dedent("""
                You are provided with two lists:
                - speakers: {speakers}
                - corresponding text: {text}
                
                Your job:
                1. Write a clear, structured summary of the meeting.
                2. Identify which speaker talked the most (by number of utterances).
                3. Highlight their main contributions separately.
            """),
            expected_output="A JSON object containing the meeting summary.",
            output_json=MeetingSummary,
            output_file=os.path.join(self.output_path, "summarized_report.json"),
            agent=self.summarization_agent()
        )
    
    def summarization_crew(self):
        return Crew(
            agents = [self.summarization_agent()],
            tasks = [self.summarization_task()],
            process = Process.sequential,
            verbose=True
        )
    
    def run_summarization_crew(self, speakers: list, text: list):
        crew_instance = self.summarization_crew()
        result = crew_instance.kickoff(inputs={"speakers": speakers, "text": text})
        return result