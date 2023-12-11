from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import os
import numpy as np
import pandas as pd
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, request

#https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=speechtotext#prebuilt-neural-voices

region = "southeastasia"
key = "44d7d58744334bea8b7c72de640ed3e3"

list_voices = [
    "en-US-AmberNeural", 
    "en-US-AriaNeural", 
    "en-US-DavisNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-RogerNeural",
    "en-US-SaraNeural",
    "en-US-SteffanNeural",
    "th-TH-AcharaNeural",
    "th-TH-NiwatNeural",
    "th-TH-PremwadeeNeural"
]

try:
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    # speech_config.speech_synthesis_voice_name ="en-US-JaneNeural"
    speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config)

except Exception as e:
    print(e)

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Configure CORS for the '/main' and '/weather' endpoints
cors = CORS(app, resources={r"/rain": {"origins": "*"}, r"/temp": {"origins": "*"}, r"/bus": {"origins": "*"}, r"/tts": {"origins": "*"}})

@app.route('/rain')
def get_rainfall():
    load_dotenv()
    api_key = os.getenv('WEATHERBIT_KEY')  # Replace with your API key
    lat = os.getenv('SAMYAN_LAT')
    lng = os.getenv('SAMYAN_LNG')
    # lat = request.args.get('lat')
    # lng = request.args.get('lng')

    if not lat or not lng:
        return {'error': 'Latitude and longitude are required parameters.'}



    # weather_url = f'https://api.weatherbit.io/v2.0/forecast/daily?lat={lat}&lon={lng}&key={api_key}'
    # weather_response = requests.get(weather_url)
    # weather_data = weather_response.json()
    
    # percip = weather_data['data'][0]['pop']
    # location = weather_data['city_name']
    percip = 50
    location = 'Pathum Wan'
    if percip < 50:
        msg = 'Rain warning'
    elif percip >= 50 and percip < 75:
        msg = 'Moderate rain warning'
    elif percip >= 75:
        msg = 'Heavy rain warning'
    else:
        msg = 'Clear skies' 

    return {'percip': percip, 'location' : location, 'msg': msg}
    # if weather_data:
    #     return {'percip': percip, 'location' : location, 'msg': msg}
    # else:
        # return {'error': 'Could 5 fetch weather data.'}

@app.route('/temp', methods=['GET'])
def get_temp():
    load_dotenv()
    api_key = os.getenv('WEATHER_KEY')  # Replace with your API key
    lat = os.getenv('SAMYAN_LAT')
    lng = os.getenv('SAMYAN_LNG')
    # lat = request.args.get('lat')
    # lng = request.args.get('lng')


    if not lat or not lng:
        return {'error': 'Latitude and longitude are required parameters.'}

    weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={api_key}&units=metric'
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()
    if weather_data:
        print(type(weather_data['main']['temp']))
        return {'temp': round(weather_data['main']['temp']), 'feels': round(weather_data['main']['feels_like'])}
    else:
        return {'error': 'Could not fetch weather data.'}
    
@app.route('/bus')
def bus_info():
    df = pd.read_csv('busss - Sheet1.csv', header=None)
    df['Bus_No'] = df[0].str.split(' ').str[0]

    sample = df.sample(1)
    data = pd.DataFrame(columns=['Bus_No', 'Destination', 'ETA'])
    data['Bus_No'] = sample['Bus_No']
    data['Destination'] = sample[2].str.strip()
    # random time from 1 to sample[4]
    data['ETA'] = np.random.randint(1, sample[4])
    #assign new row index
    data.index = range(len(data))
    # turn into  dictionary
    output = dict()
    for i, d in enumerate(data.to_dict('records')):
        output[i] = d
    return output[0]

@app.route("/tts", methods=["POST", "GET"])
def speak(
    text: str = "Default Response",
    voice: str = "en-US-JaneNeural",
    style: str = "normal",
    log: bool = False,
    profanity : str ="2"
):
    try:
        x = request.get_json()
        # print(x)
        # print("synthesizing...","blue")
        bus_no = x['Bus_No']
        destination = x['Destination']
        text = '{bus_no} heading to {destination} is arriving soon.'
        voice = 'en-US-JaneNeural'
        style = 'normal'
        profanity = 2
    except Exception as e:
        print(e, "going with default values")
        pass

    try:
        # Read XML
        ssml_string = open("tts_voice_config.xml", "r").read()
        ssml_string = ssml_string.replace('TEXT', text)
        ssml_string = ssml_string.replace('STYLE', repr(style))
        ssml_string = ssml_string.replace('VOICE', repr(voice))

        #* Speech Config
        # speech_config.set_profanity = profanity
        # speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # sending & receiver from Azure
        result = speech_synthesizer.speak_ssml_async(ssml_string).get()
        print(f"\tsynthesized: {text=}")

        #* Convert into audio stream
        # stream = speechsdk.AudioDataStream(result)
        # stream.save_to_wav_file("tts_temp.wav")

        return {"synthesized": f"{text}"}

    except Exception as e:
        print(e)


def test():
    for i in list_voices:
        speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        audio_config = speechsdk.audio.AudioOutputConfig(
            suse_default_speaker=True)

        # The language of the voice that speaks.
        #speech_config.speech_synthesis_voice_name='en-US-JennyNeural'
        # speech_config.speech_synthesis_voice_name= list_voices[0]
        speech_config.speech_synthesis_voice_name = i
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config)
        print(i)

        text = "Hi there my name is Walkie, I will be your personal assistant"

        speech_synthesis_result = speech_synthesizer.speak_text_async(
            text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"\tsynthesized.")

        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(
                cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(
                        cancellation_details.error_details))
                    print(
                        "Did you set the speech resource key and region values?"
                    )