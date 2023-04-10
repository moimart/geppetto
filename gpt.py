import openai
import os
import aiohttp
import asyncio
import ast
import os
import requests
import json
from dotenv import load_dotenv

class GPTHass:
    def __init__(self):
        self.headers = {
            'Authorization': 'Bearer {}'.format(os.environ.get('HASS_TOKEN')),
            'Content-Type': 'application/json',
        }
        
        load_dotenv()
        
        self.gpt_result_callback = None
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        self.hass_host = os.environ.get('HASS_HOST')
        
        self.get_entities()
        
    def get_entities(self):
        url = 'http://{}/api/states'.format(self.hass_host)
        
        #use requests to make it synchronous
        response = requests.get(url, headers=self.headers)

        self.entities = ""
        if response.status_code == 200:
            for state in json.loads(response.text):
                entity_id = state["entity_id"]
                entity_name = state["attributes"].get("friendly_name")
                if entity_name is not None:
                    if "switch." in entity_id or "button." in entity_id or \
                        "light." in entity_id or "media_player." in entity_id or \
                        "fan." in entity_id or "cover." in entity_id:
                        self.entities += entity_id + " = " + entity_name + "\n"
            self.entities += "\n"
        
        
    def answer(self, asr_text):
        prompt = \
        """
        Entities:
        {}

        I need a python list where each item is a dictionary with the service and entity_id for each item to send trough the Home Assistant API for the following prompt "{}"
        """.format(self.entities, asr_text)
        
        print(prompt)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = response["choices"][0].message["content"]
        
        try:
            commands = ast.literal_eval(content)

            print(commands)
            
            if  self.gpt_result_callback is not None:
                self.gpt_result_callback(commands)
                
            asyncio.run(self.send_all_commands(commands))
        except:
            print("Error parsing commands")
         
    async def send_command(self, command):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = 'http://{}/api/services/'.format(self.hass_host) + \
                    command['service'].split('.')[0] + \
                    '/' + command['service'].split('.')[1]
                    
            print (url)

            json = { "entity_id": command['entity_id']}
            async with session.post(url, json=json) as response:
                print(await response.text())
                
    async def send_all_commands(self, commands):
        await asyncio.gather(*[self.send_command(command) for command in commands])



    


