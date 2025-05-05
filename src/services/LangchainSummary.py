from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
#from BaseService import BaseService
#from models import MeetingSummary
from typing import List
from pydantic import BaseModel, Field

class MeetingSummary(BaseModel):
    meeting_topic: str = Field(..., description="The topic of the meeting.")
    summary: str = Field(..., description="A summary of the meeting, including key points and decisions made.")

class LangchainSummaryService:
    def __init__(self, model: str = "deepseek-r1:8b", temperature: float = 0):
        #super().__init__()
        self.llm = OllamaLLM(model=model, temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=MeetingSummary)

    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            template="""
                You are an expert meeting summarizer. 
                You are given transcription meeting data. Your job is :-
                Write a clear, structured summary of the meeting.
                Highlight their main contributions separately.\n{format_instructions}\n{text}\n""",
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
    
    def summarize(self, text):
        prompt = self.get_prompt_template()
        prompt_and_model =  prompt | self.llm
        output = prompt_and_model.invoke(input=text)
        return self.parser.invoke(output)
    


if __name__ == "__main__":
    service = LangchainSummaryService()
    text = """
        These growing pains the next decade means there's going to be a lot of growth, but there'll be a lot of prosperity to follow.
        It's a big day for downtown Salt Lake City today. I'm Fox 13 news reporter Mike Ligobi, their couple of important development projects on the agenda for tonight's city council meeting that could change the landscape of downtown, literally and figuratively.
        When I first opened up this location, there was nothing in this area.
        about a block away from Curry chicken in Salt Lake City was the old Sears building.
        So when Sears was there, we had a lot of people coming in, shopping, school shopping, so we had a lot of people coming in to have lunches or dinners. Ever since they've closed down and then tore down the spot, we're just kind of waiting to see something that would pop up there.
        In December 2021, Intermountain held bought the building left behind when Sears closed the store on the corner of 800 South in State Street. They demolished the building the following October and has been an empty lot ever since. Except for some birds that visit the dubbed Sears Lake. Here are some renderings Intermountain shared with City Council earlier this summer.
        You know the hospital is not a bad idea, definitely. It'll kind of change the genre of this area, I guess you could say. But like retail would help so we can have more people down here shopping, eating, dining, having a good time so that our downtown is something that people are looking forward to to come down.
        on City Council's agenda Tuesday night is to rezone that land to build an urban.
        I certainly hope that they don't increase parking lots and that we see more of a focus on trying to help patients access our natural urban environment.
        Other downtown projects being discussed is funding the capital improvement program, which includes the Green Loop installation. Think of a big park with active spaces connected by trees. And also rezoning part of downtown for the sports, entertainment, culture and convention district. One of those changes would be allowing the maximum height of structures to be 600 feet instead of 125.
        We're cultivating a new future and we're ushering in not just a world-class city, but a future where every resident can create a home here in Salt Lake.
        And as for the hospital, people hope it can make patients in the city healthier.
        So I think that the downtown holds a big responsibility on showcasing what Utah's all about.
        the Salt Lake City Council going on now with the formal meeting starting at 7 p.m. that would include the public hearing, presentations and some votes coming up as well. In downtown Salt Lake City, I am Mike Ligobby, Fox 13 News Utah."
    """
summary = service.summarize(text)
print(summary)
print(type(summary))