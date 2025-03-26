import requests 
from requests.auth import HTTPBasicAuth
import os
from pydantic import BaseModel
from langchain.tools import StructuredTool
from dotenv import load_dotenv


class TicketSchema(BaseModel):
    ticket_id: str

class SprintSchema(BaseModel):
    sprint_name: str

class NoInputSchema(BaseModel):
    pass


class JIRAToolkit:
    def __init__(self, email, auth_token):
        self.api_url = "https://throwawayfortrashplz.atlassian.net/rest/api/latest/"
        self.auth = HTTPBasicAuth(email, auth_token)
    
    def get_all_tickets_for_current_sprint(self):
        url = self.api_url + "search/jql"
        # print(url)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        query = {
            'jql': "project = 'CPSX' AND sprint in openSprints()",
            'fields' : ['description', 'summary']
        }

        response = requests.request(
            "GET", 
            url,
            headers=headers,
            params=query,
            auth=self.auth
        )

        issues =[]
        res = response.json().get("issues", [])
        for issue in res:
            key = issue["key"]
            summary = issue["fields"]["summary"]
            description = issue["fields"].get("description", "No description entered")
            issues.append([key, summary, description])
        return issues
    
    def get_ticket_details(self, ticket_id):
        url = self.api_url + "search/jql"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        query = {
            'jql': f"key ={ticket_id}  AND project = 'CPSX'",
            'fields' : ['description', 'summary']
        }

        response = requests.request(
            "GET", 
            url,
            headers=headers,
            params=query,
            auth=self.auth
        )

        issues =[]
        res = response.json().get("issues", [])
        for issue in res:
            key = issue["key"]
            summary = issue["fields"]["summary"]
            description = issue["fields"].get("description", "No description entered")
            issues.append([key, summary, description])
        return issues
    
    def generate_tools(self):
        get_ticket_details_tool = StructuredTool.from_function(
            self.get_ticket_details,
            name = "get_ticket_details",
            description="Given a ticket ID, retrieves the title and description of the specified Jira ticket. This tool is useful for fetching detailed information about a single ticket to understand its purpose and context.",
            args_schema=TicketSchema
        )

        get_all_tickets_for_current_sprint_tool = StructuredTool.from_function(
            self.get_all_tickets_for_current_sprint,
            name = "get_all_tickets_for_current_sprint",
            description="Retrieves the title and description of all tickets in the current sprint. This tool does not require any arguments and is useful for obtaining an overview of all active tickets in the current sprint.",
            args_schema = NoInputSchema
        )

        return [
            get_ticket_details_tool,
            get_all_tickets_for_current_sprint_tool
        ]
