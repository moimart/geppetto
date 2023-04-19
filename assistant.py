from porcupine import Porcupine
from recorder import Recorder
from asr import ASR
from gpt import GPTHass
from tts import TTS
from soundboard import SoundBoard
import os
from dotenv import load_dotenv

class AssistantEngine:
    def __init__(self):
        load_dotenv()
        
        self.shared_data = None
        
        self.asr_active = False
        
        self.wake_word_engine = Porcupine(
        keywords=[os.environ.get("PORCUPINE_KEYWORD")] if os.environ.get("PORCUPINE_KEYWORD") != "" else None,
        keyword_paths=[os.environ.get("PORCUPINE_KEYWORD_PATH")] if os.environ.get("PORCUPINE_KEYWORD_PATH") != "" else None,
        access_key=os.environ.get("PORCUPINE_ACCESS_KEY"),
        sensitivities=[0.9],
        input_device_index=-1
        )

        self.recorder = Recorder()
        self.recorder.recording_done_callback = self.start_asr
        
        self.asr_engine = ASR()
        self.asr_engine.result_callback = self.asr_result
        
        self.soundboard = SoundBoard()
        
        self.gpt = GPTHass(
            config={ \
                "hass_token": os.environ.get("HASS_TOKEN"), \
                "hass_host": os.environ.get("HASS_HOST"), \
                "user_name": os.environ.get("USER_NAME"), \
                "openai_api_key": os.environ.get("OPENAI_API_KEY") \
            }
        )
        
        self.gpt.command_result_callback = self.command_result
        self.gpt.tts_result_callback = self.tts_result
        
        self.wake_word_engine.callback = self.wake_word_detected
        
        self.tts = TTS(config={"credentials": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")})
        
    def run(self):
        while True:
            self.shared_data = {"state": "idle"}
            self.wake_word_engine.run()
        
    def wake_word_detected(self, keyword_index):
        self.shared_data = {"state": "detected"}
        print("wake word detected {}".format(keyword_index))
        self.wake_word_engine.stop()
        self.asr_active = True
        self.soundboard.play("chime")
        self.shared_data = {"state": "detecting"}
        self.recorder.record()
            
    def start_asr(self, file_path):
        self.shared_data = {"state": "transcribing"}
        print("Starting ASR...")
        self.asr_engine.transcribe(file_path)
            
    def asr_result(self, result):
        self.shared_data = {"state": "processing"}
        self.gpt.answer(result)
         
    def command_result(self, result):
        self.shared_data =  {"state": "result_received"}
        pass
        
    def tts_result(self, result):
        print(result)
        self.shared_data = {"state": "speaking"}
        self.tts.speak(result)
