from crewai import Agent, Task, LLM, Process, Crew
from textwrap import dedent
from services.BaseService import BaseService
from models import MeetingSummary
import os
import json

class SummarizationService(BaseService):
    def __init__(self, model: LLM = None):
        super().__init__()
        
        self.output_path = self.generated_reports_path
        self.report_filename = "summarized_report.json"
        
        self.target_path = os.path.join(self.output_path, self.report_filename)
        
        self.temp_filename = self.report_filename
        
        self.logger.info(f"Target path for final output: {self.target_path}")

        if model is None:
            self.model = LLM(
                model="ollama/gemma2:9b", 
                temperature=0.6, 
                base_url="http://localhost:11434"
            )
        else:
            self.model = model
        self.logger.info("SummarizationAgent initialized")

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

    def summarization_task(self, speakers, text):
        return Task(
            description=dedent(f"""
                You are provided with two lists:
                - speakers: {speakers}
                - corresponding text: {text}
                
                Your job:
                1. Write a clear, structured summary of the meeting.
                2. Identify which speaker talked the most (by number of utterances).
                3. Highlight their main contributions separately.
                
                Do not include any additional text, markdown formatting, or explanation outside of this JSON structure.
            """),
            expected_output="A valid JSON object containing the meeting summary that strictly follows the MeetingSummary model format.",
            output_json=MeetingSummary,
            output_file=self.temp_filename,  
            agent=self.summarization_agent()
        )
    
    def summarization_crew(self, speakers, text):
        return Crew(
            agents=[self.summarization_agent()],
            tasks=[self.summarization_task(speakers, text)],
            process=Process.sequential,
            verbose=True
        )
    
    def run_summarization_crew(self, speakers: list, text: list):
        try:
            self.logger.info("Starting summarization crew")
            self.logger.info(f"Using temporary filename: {self.temp_filename}")
            self.logger.info(f"Final target path: {self.target_path}")
            
            cwd = os.getcwd()
            self.logger.info(f"Current working directory: {cwd}")
            
            temp_file_path = os.path.join(cwd, self.temp_filename)
            self.logger.info(f"Expected temporary file path: {temp_file_path}")
            
            crew_instance = self.summarization_crew(speakers, text)
            result = crew_instance.kickoff()
            
            if os.path.exists(temp_file_path):
                self.logger.info(f"Temporary file found at: {temp_file_path}")

                os.makedirs(os.path.dirname(self.target_path), exist_ok=True)
                
                with open(temp_file_path, 'r') as f:
                    data = json.load(f)
                
                with open(self.target_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self.logger.info(f"Successfully copied file to target path: {self.target_path}")
                
                os.remove(temp_file_path)
                self.logger.info(f"Removed temporary file: {temp_file_path}")
            else:
                self.logger.warning(f"Temporary file not found at expected location: {temp_file_path}")

                for root, dirs, files in os.walk(cwd):
                    if self.temp_filename in files:
                        found_path = os.path.join(root, self.temp_filename)
                        self.logger.info(f"Found file at: {found_path}")
                        
                        with open(found_path, 'r') as f:
                            data = json.load(f)
                        
                        os.makedirs(os.path.dirname(self.target_path), exist_ok=True)
                        
                        with open(self.target_path, 'w') as f:
                            json.dump(data, f, indent=2)
                        
                        self.logger.info(f"Successfully copied file to target path: {self.target_path}")
                        
                        os.remove(found_path)
                        self.logger.info(f"Removed temporary file: {found_path}")
                        break
            
            self.logger.info("Summarization completed successfully")
            print(result)
            return result
        except Exception as e:
            self.logger.error(f"Summarization failed: {str(e)}")
            raise