import ibm_watson
import json
import random
import spotipy
import spotipy.util as util
import requests
import webbrowser
from ibm_watson import TextToSpeechV1
from ibm_watson import SpeechToTextV1
import simpleaudio as sa
import sounddevice as sd
from scipy.io.wavfile import write


def search_music(mood): 
    searchQuery= mood
    print()
    searchResult=spotifyObject.search(searchQuery,1,0,'playlist')
    listTrack = searchResult['playlists']['items']
    attributes=[]
    songName=[]
    songUrl=[]
    for i in listTrack:
        href = i['href']
        req = requests.get(href, headers=headers)
        data = json.loads(req.text)
        for j in data['tracks']['items']:
            songUrl.append(j['track']['external_urls']['spotify'])
            name = j['track']["name"]
            song_ids = j['track']['uri'].split(':')[2]
            song_attributes = requests.get(f"https://api.spotify.com/v1/audio-features/{song_ids}", headers=headers)
            attributes.append(json.loads(song_attributes.text))
            songName.append(name)
    return songUrl

    


username = 'kpobc3etyuy2b8nq6tso9efx4'
scope = 'user-library-read user-read-playback-state user-modify-playback-state'
token = util.prompt_for_user_token(username,scope,
                          client_id='313abb4a0cbf4b1ea70b569b294272e2',
                          client_secret='a4a260687b334ea4a91858bcae1582ee',
                          redirect_uri='http://google.com/')

headers = {"Authorization": "Bearer {}".format(token)}
spotifyObject = spotipy.Spotify(auth=token)
user = spotifyObject.current_user()

displayName=user['display_name']
followers=user['followers']['total']

service = ibm_watson.AssistantV2(
     iam_apikey='_tanh4s-cY3X2aPnk57lFTQXRwJGziBE5LrRhA0u_1zY',
    version='2019-08-20',
    url='https://gateway.watsonplatform.net/assistant/api'
)

text_to_speech = TextToSpeechV1(
    iam_apikey='HYQ9Ng3S_w_FvKAthbpiEQwVdWRbZZIFBjSZNw5CBhuO',
    url='https://gateway-wdc.watsonplatform.net/text-to-speech/api'
)

speech_to_text = SpeechToTextV1(
    iam_apikey='kg5vrpybjpY9JwUOGEOLM7bmlTEqsotnz3mGhD6L9UNS',
    url='https://gateway-wdc.watsonplatform.net/speech-to-text/api'
)



# Get sessioId
sessionId = service.create_session(
    assistant_id='d11ac974-e98d-4324-99e4-d3640ebd3411'
).get_result()


intent = ""
mood = ""
genre = ""
songs = []
randomSong = 0
fs = 44100  # Sample rate
seconds = 2  # Duration of recording
while intent != "Bye":
    print ("Start recording")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels =1)
    sd.wait()  # Wait until recording is finished
    write('input.wav', fs, myrecording)  # Save as WAV file 
    
    with open('input.wav','rb') as audio_file:
        speech_recognition_results = speech_to_text.recognize(
        audio=audio_file,
        content_type='audio/wav',
    ).get_result()
    print (speech_recognition_results)
    message = speech_recognition_results["results"][0]["alternatives"][0]["transcript"]
    #message = input("User says: ")
    response = service.message(
        assistant_id='d11ac974-e98d-4324-99e4-d3640ebd3411',
        session_id=sessionId["session_id"],
        input={
            'message_type': 'text',
            'text': message
        }
    ).get_result()
    intent = response["output"]["intents"][0]["intent"]
    
    if intent == "Sad" or intent == "ChangeToSad":
        mood = "sad"
        songs = search_music(mood)
        randomSong = random.randint(0,len(songs)-1)
        webbrowser.open(songs[randomSong])
    #elif intent == "Greeting":
        #webbrowser.open("http://127.0.0.1:5500/index.html")
        
    elif intent == "Happy" or intent == "ChangeToHappy":
        mood = "happy"
        songs = search_music(mood)
        randomSong = random.randint(0,len(songs)-1)
        webbrowser.open(songs[randomSong])
    elif intent == "ChangeSone":
        songs.pop(randomSong)
        randomSong = random.randint(0,len(songs)-1)
        webbrowser.open(songs[randomSong])
        
# #     elif intent== "songType" or intent == "changeSongType":
# #         genre = response["output"]["entities"][0]["value"]
    
    bot_answer = response["output"]["generic"][0]["text"]
    print ("Bot says: ", bot_answer)
    with open('output.wav', 'wb') as audio_file:
        audio_file.write(
                text_to_speech.synthesize(
                        bot_answer,
                        voice='en-US_AllisonVoice',
                        accept='audio/wav'        
                ).get_result().content)
    wave_obj = sa.WaveObject.from_wave_file("output.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()

   
    

