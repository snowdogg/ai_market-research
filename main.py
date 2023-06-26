from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import requests
from dotenv import load_dotenv
from langchain.agents import load_tools, initialize_agent
from langchain.llms import OpenAI
from langchain.agents import AgentType
import json


app = FastAPI()
load_dotenv()

# Load the API key from environment variable
API_KEY = os.getenv("MY_API_KEY")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = "https://api.openai.com/v1/chat/completions"


llm = OpenAI(temperature=0)
tool_names = ["serpapi"]
tools = load_tools(tool_names)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)


class Data(BaseModel):
    text: str


security = HTTPBasic()

def verify_api_key(credentials: HTTPBasicCredentials = Depends(security)):
    # Check if the password part of the Basic Auth header matches the API_KEY
    if credentials.password != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return credentials


@app.options("/query_chatgpt")
def handle_options(request: Request, credentials: HTTPBasicCredentials = Depends(verify_api_key)):
    return {"status": "OK"}

@app.get("/")
def read_root():
    return {"Health": "Check"}

@app.post("/")
def read_root():
    return {"Health": "Check"}

@app.post("/query_chatgpt")
def query_chatgpt(request: Request, data: Data, credentials: HTTPBasicCredentials = Depends(security)):    # Verify API key through Basic Auth
    verify_api_key(credentials)
    zing = agent.run('''Tell me detailed information about this company, 
    including Company Size, Industry, Business Summary, Website URL, Revenue. 
    Only Return data that is verified as probably being true.
    Industry should be what kind of business it is.
    do not just append industry to the name of the company, we want to know the industry that the company is in.
    Make sure all the responses are about the same company. 
    website should be the url of the company's website.
    Company Size should be a number of employees. This is very important.
    Make sure you're giving information about the business and not just random junk from search results. Be smart about it and analyse the data.
    Make sure the Revenue is an annual revenue number in USD.
    Please construct a valid JSON object that has each of these datapoints as a quoted key where the value is the information summarized. 
    The company is called''' + data.text)
    try:
        data = json.loads(zing)
    except: 
        print('couldn\'t parse json')
        # this bit is ugly but i was running out of serpapi credits and didnt have enough to properly troubleshoot
        try:
            data = json.loads(json.loads(json.dumps(zing)))
        except: 
            data = zing
        

    return data
