import openai
import os
import aiohttp
import asyncio
import ast
import os
import requests
import json

class GPTHass:
    def __init__(self, config):
        self.headers = {
            'Authorization': 'Bearer {}'.format(config["hass_token"]),
            'Content-Type': 'application/json',
        }
        
        self.user_name = config["user_name"]
        openai.api_key = config["openai_api_key"]
        self.hass_host = config["hass_host"]
        
        self.command_result_callback = None
        self.tts_result_callback = None

        self.get_hass_entities()
        
        self.interaction_counter = self.last_prompt_number()
        self.training = False
        self.file = None
        
    def indent_with_tabs(input_string):
        indented_string = "    ".join(input_string.splitlines(True))
        return indented_string.strip().replace("\"", "\\\"")
        
    def last_prompt_number(self):
        files = os.listdir('./training/')
        prompt_files = [f for f in files if f.startswith('prompt-') and f.endswith('.yml')]
        if prompt_files:
            prompt_numbers = [int(f.split('-')[1].split('.')[0]) for f in prompt_files]
            return max(prompt_numbers) + 1
        else:
            return 0
        
    def write_prompt(self, content):
        if self.training:
            self.file = open(f"training/prompt-{self.interaction_counter}.yml", "w")
            self.file.write(\
                f"prompt: >\n" \
                f"    \"{GPTHass.indent_with_tabs(content)}\"" \
                "\n"
            )
            
    def write_answer(self, content):
        if self.training:
            self.file.write(\
                "\nanswer: >\n" \
                f"    \"{GPTHass.indent_with_tabs(content)}\""
            )
            self.file.close()
        
    def get_hass_entities(self):
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
       
    def assistant_answer(self, asr_text, positive=True):
        
        mood = "positively and affirmatively" if positive else "negatively"
        
        prompt = \
        f"My name is {self.user_name}. You are HAL 9000 and you are connected to the smart home system. " \
        f"Give me what HAL 9000 would reply {mood} to this command: \"{asr_text}\" " \
        "HAL 9000: "
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = response["choices"][0].message["content"]
        
        if self.tts_result_callback != None:
            self.tts_result_callback(content)
        
    def answer(self, asr_text):
        prompt = \
        "Entities:\n" \
        f"{self.entities}\n" \
        "\n" \
        f"For the prompt \"{asr_text}\", as long as it contains a valid entity, " \
        "I need a python list where each item is a dictionary with the service " \
        "and entity_id for each item to send trough the Home Assistant API, potentially " \
        "with data if needed. If not, just answer the word Error."
        
        self.write_prompt(prompt)
        print(prompt)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        except:
            if self.tts_result_callback != None:
                self.tts_result_callback("GPT-4 is not available at the moment")
                
        content = response["choices"][0].message["content"]
        content = content.replace("```", "")
        content = content.replace("python", "").replace("\n", "").replace("\t", "").replace(" ", "")
        
        self.write_answer(content)
        self.interaction_counter += 1
        
        try:
            commands = json.loads(content)
                
            if  self.command_result_callback != None:
                self.command_result_callback(commands)
                
            asyncio.run(self.send_all_commands(commands, asr_text))
        except Exception as e:
            print("Error parsing the response: {}".format(e))
            self.assistant_answer(asr_text)
         
    async def send_command(self, command):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = 'http://{}/api/services/'.format(self.hass_host) + \
                    command['service'].split('.')[0] + \
                    '/' + command['service'].split('.')[1]

            json = { "entity_id": command['entity_id']}
            if 'data' in command:
                json.update(command['data'])
                
            print(json)
            async with session.post(url, json=json) as response:
                print(await response.text())
                pass
                
    async def send_all_commands(self, commands, tts_response):
        await asyncio.gather(*[self.send_command(command) for command in commands])
        self.assistant_answer(tts_response)



    


