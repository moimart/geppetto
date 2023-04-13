GePpeTto - GPT-Whisper-based Voice Assistant for Home Assistant (Experimental)
====

This is a small experiment to create a fully functional Voice Assistant for Home Assistant in the least time possible. 
This uses Porcupine's wake word engine for wake word recognition, OpenAI's Whisper for Speech-To-Text transcription, GPT-4 chat 
completion model and Google Cloud TTS API for answers. Most of the code, in the form of snippets, was also generated by asking ChatGPT.

### Features:
* Control lights, switches, locks, covers, climate and mediaplayers 
** Simultaneous commands, granular
* Generic assistant questions – including time
* Text-to-speech responses with Google Cloud TTS

### Not supported:
* Weather
* Timers

This was developed for personal use and I have no intention on making this a project for general use. I might add features for myself (like Local TTS and better dialog management) but that's only to scratch an itch out of desperation with existing data-collecting incompetent assistants from the big three. 

This fetches your switches, buttons, fans, covers and mediaplayers from Home Assistant. OpenAI has a limit for 4096 tokens, so if you have lots and lots of devices you might be out of luck with this approach and perhaps you'll have to fine tune a model. *If you make this run with an Stanford Alpaca local model, I'll buy you few beers!*

## Setup

DISCLAIMER: Tested with Python 3.10.9 - it does not work with 3.11 yet due to the dependencies

```
$ pip install -r requirements.txt
```

Create a .env file based on the .env.example file and add your API keys, Wake Word models and Home Assistant host and Long-lived Access Token

.env file:

```
HASS_TOKEN="" # Long-lived Access Token
HASS_HOST="" # Your Home Assistant server (with :port)
OPENAI_API_KEY=""
PORCUPINE_ACCESS_KEY=""
PORCUPINE_KEYWORD="" # keyword of your model – The name of the assistant
PORCUPINE_KEYWORD_PATH="" # full path to wake word model file – if you leave both KEYWORD AND KEYWORD_PATH will use default porcupine models and wake words
GOOGLE_APPLICATION_CREDENTIALS="" # A service account file with Cloud TTS API access
USER_NAME="Pinocchio" # How you want the assistant to call you
```

Then just:

```
$ python assistant.py
```

## Notes:

If you want to record the prompts and answer for fine-tuning set the environment var GEPPETTO_TRAINING=True prior to run the script. This creates .yml files that can be processed for creating the payload for the OpenAI fine-tuning endpoint

