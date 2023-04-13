import io
from google.cloud import texttospeech
import pyaudio
class TTS:
    def __init__(self, config):
        self.path_to_credentials = config["credentials"]
        self.client = texttospeech.TextToSpeechClient()
        
        self.tts_done_callback = None
        
    
    def speak(self, text):
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name="en-US-Neural2-D", ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Open a stream in memory to play the audio
        stream = io.BytesIO(response.audio_content)

        # Create an instance of the PyAudio class
        p = pyaudio.PyAudio()

        # Open a stream for playing the audio
        stream_player = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            output=True
        )

        # Play the audio stream
        data = stream.read(1024)
        while data:
            stream_player.write(data)
            data = stream.read(1024)

        # Stop and close the audio stream player and PyAudio instance
        stream_player.stop_stream()
        stream_player.close()
        p.terminate()
        
        if self.tts_done_callback is not None:
            self.tts_done_callback()

