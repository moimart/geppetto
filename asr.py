import whisper
import time

class ASR:
    def __init__(self):
        self.result_callback = None
        self.model = whisper.load_model("base")

    
    def transcribe(self,file_path):
        print("Transcribing {}".format(file_path))
        result = self.model.transcribe(file_path)

        if self.result_callback is not None:
            self.result_callback(result["text"])



