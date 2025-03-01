import warnings
warnings.filterwarnings('ignore')

import os
import json

from crewai import Agent, Crew, Task
from pprint import pprint
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()


# AGENT 1: Venue Coordinator
venue_coordinator = Agent(
    role="Venue Coordinator",
    goal="Identify and book an appropriate venue "
    "based on event requirements",
    tools=[search_tool, scrape_tool],
    verbose=True,
    backstory=(
        "With a keen sense of space and "
        "understanding of event logistics, "
        "you excel at finding and securing "
        "the perfect venue that fits the event's theme, "
        "size, and budget constraints."
    )
)


# AGENT 2: Logistics Manager
logistics_manager = Agent(
   role='Logistics Manager',
   goal=(
       "Manage all logistics for the event "
       "including catering and equipment"
   ),
   tools=[search_tool, scrape_tool],
   verbose=True,
   backstory=(
       "Organized and detail-oriented, "
       "you ensure that every logistical aspect of the event "
       "from catering to equipment setup "
       "is flawlessly executed to create a seamless experience."
   )
)


# AGENT 3: Marketing and Communications Agent
marketing_communications_agent = Agent(
    role="Marketing and Communications Agent",
    goal="Effectively market the event and "
         "communicate with participants",
    tools=[search_tool, scrape_tool],
    verbose=True,
    backstory=(
        "Creative and communicative, "
        "you craft compelling messages and "
        "engage with potential attendees "
        "to maximize event exposure and participation."
    )
)

#CREATING VENUE DETAILS Pydantic Object - to store the venue details
from pydantic import BaseModel
class VenueDetails(BaseModel):
    name: str
    address: str
    capacity: int
    booking_status: str


#CREATING TASKS
#VENUE TASK
venue_task = Task(
    description="Find a venue in {event_city} "
                "that meets criteria for {event_topic}.",
    expected_output="All the details of a specifically chosen"
                    "venue you found to accommodate the event.",
    human_input=True,
    output_json=VenueDetails,
    output_file="venue_details.json",  
      # Outputs the venue details as a JSON file
    agent=venue_coordinator
)

#LOGISTICS TASK
logistics_task = Task(
    description="Coordinate catering and "
                 "equipment for an event "
                 "with {expected_participants} participants "
                 "on {tentative_date}.",
    expected_output="Confirmation of all logistics arrangements "
                    "including catering and equipment setup.",
    human_input=True,
    agent=logistics_manager
)

#MARKETING TASK
marketing_task = Task(
    description="Promote the {event_topic} "
                "aiming to engage at least"
                "{expected_participants} potential attendees.",
    expected_output="Report on marketing activities "
                    "and attendee engagement formatted as markdown.",
    async_execution=True,
    output_file="marketing_report.md",
    agent=marketing_communications_agent
)


# CREATING THE CREW
event_management_crew = Crew(
    agents=[venue_coordinator, 
            logistics_manager, 
            marketing_communications_agent],
    
    tasks=[venue_task, 
           logistics_task, 
           marketing_task],
    
    verbose=True
)

#RUN CREW
event_details = {
    'event_topic': "Tech Innovation Conference",
    'event_description': "A gathering of tech innovators "
                         "and industry leaders "
                         "to explore future technologies.",
    'event_city': "San Francisco",
    'tentative_date': "2024-09-15",
    'expected_participants': 500,
    'budget': 20000,
    'venue_type': "Conference Hall"
}

result = event_management_crew.kickoff(inputs=event_details)


#DISPLAY VENUE DETAILS in JSON
with open('venue_details.json') as f:
   data = json.load(f)

pprint(data)

# Escribir y mostrar el marketing report
with open('marketing_report.md', 'w') as f:
    f.write(str(result))  # Convertimos el resultado a string

# DISPLAY MARKETING REPORT in MARKDOWN
from IPython.display import Markdown
display(Markdown(str(result)))




