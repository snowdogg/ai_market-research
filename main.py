from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv
from langchain.agents import load_tools, initialize_agent
from langchain.llms import OpenAI
from langchain.agents import AgentType
import json


app = FastAPI()
load_dotenv()


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

@app.options("/query_chatgpt")
def handle_options(request: Request):
    return {"status": "OK"}

@app.post("/query_chatgpt")
def query_chatgpt(request: Request, data: Data):

    zing = agent.run('''Tell me detailed information about this company, 
    including Company Size, Industry, Business Summary, Website URL, Revenue. 
    Only Return data that is verified as probably being true. 
    Make sure the Revenue is an annual revenue number in USD.
    Please construct a valid JSON object that has each of these datapoints as a quoted key where the value is the information summarized. 
    The company is called''' + data.text)
    try:
        data = json.loads(zing)
    except: 
        print('couldn\'t parse json')
        data = zing

    return data
    # text_input = data.text
    # print('running')

    # # Call OpenAI's API here with the text_input
    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": f"Bearer {openai_api_key}"
    # }


    # system_prompt = "You are a a salesman and you need to help write a straight and to the point email that responds to the following email:"
    # #"You are an expert in market research and you are working for a marketing professional as their assistant. Be direct and to the point."
    
    # user_prompt = text_input
    # payload = {
        
    #     "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
    #     "max_tokens": 100,
    #     "temperature": 0.2,
    #     "model": "gpt-3.5-turbo"
    # }

    # response = requests.post(openai_base_url, headers=headers, json=payload)
    # response_json = response.json()

    # # chat_response = response_json["choices"][0]["text"]
    # print(response_json)
    # return {"response": response_json}
