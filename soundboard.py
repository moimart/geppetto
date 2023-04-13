import yaml
import io
from pydub import AudioSegment
from pydub.playback import play

class AudioPlayer:
    def __init__(self, filename):
        self.filename = filename
        self.sound = AudioSegment.from_file(self.filename)
    
    def start(self):
        play(self.sound)

class SoundBoard:
    def __init__(self):
        try:
            self.config = yaml.safe_load(open("soundboard.yml"))
        except:
            self.config = {}
    
        for sound in self.config["sounds"]:
            try:
                sound["player"] = AudioPlayer(sound["file"])
            except Exception as e:
                print(f"Error loading sound: {e}" + sound["id"])
        
    def play(self, sound_id):
        for sound in self.config["sounds"]:
            if sound["id"] == sound_id:
                sound["player"].start()
                return
            
        print("Sound not found: " + sound_id)
