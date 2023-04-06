from porcupine import Porcupine
from recorder import Recorder
from asr import ASR
from gpt import GPTHass
import os
from dotenv import load_dotenv

class AssistantEngine:
    def __init__(self):
        load_dotenv()
        
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
        
        self.gpt = GPTHass()
        self.gpt_result_callback = self.gpt_result
        
        self.wake_word_engine.callback = self.wake_word_detected
        
        while True:
            self.wake_word_engine.run()
        
    def wake_word_detected(self, keyword_index):
        print("wake word detected {}".format(keyword_index))
        self.wake_word_engine.stop()
        self.asr_active = True
        self.recorder.record()
            
    def start_asr(self, file_path):
        print("start asr")
        
        self.asr_engine.transcribe(file_path)
            
    def asr_result(self, result):
        self.gpt.answer(result)
         
    def gpt_result(self, result):
        print("gpt result {}".format(result))

assistant = AssistantEngine()
