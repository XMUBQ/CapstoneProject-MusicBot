import ibm_watson
import json
import random
import spotipy
import spotipy.util as util
import requests
import webbrowser
from scipy.io.wavfile import write
import time
from lyrics_extractor import Song_Lyrics
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ToneAnalyzerV3
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

authenticator1 = IAMAuthenticator('_tanh4s-cY3X2aPnk57lFTQXRwJGziBE5LrRhA0u_1zY')
service = ibm_watson.AssistantV2(
    version='2019-08-20',
    authenticator = authenticator1
)
service.set_service_url('https://gateway.watsonplatform.net/assistant/api')

authenticator2 = IAMAuthenticator('KD730gX9LuGsu6SsV_LCVSseUHKFRKpOvLwmNZGbju6n')
tone_analyzer = ToneAnalyzerV3(
    version='2019-10-22',
    authenticator=authenticator2
)
tone_analyzer.set_service_url('https://gateway.watsonplatform.net/tone-analyzer/api')



# Get sessionId
sessionId = service.create_session(
    assistant_id='d11ac974-e98d-4324-99e4-d3640ebd3411'
).get_result()
intent = ""
mood = ""
genre = ""
songs = {}
songsUrl=[]
randomSong = 0
fs = 44100  # Sample rate
seconds = 3  # Duration of recording

def search_music(mood): 
    searchQuery= mood
    print()
    searchResult=spotifyObject.search(searchQuery,1,0,'playlist')
    listTrack = searchResult['playlists']['items']
    songDict = {}
    for i in listTrack:
        href = i['href']
        req = requests.get(href, headers=headers)
        data = json.loads(req.text)
        #print(data)
        for j in data['tracks']['items']:
            print(j)
            songDict[j['track']['external_urls']['spotify']] = j['track']["name"]
    return songDict

def generate_music(url, name):
    # webbrowser.open(url)
    print(url)
    extract_lyrics = Song_Lyrics('AIzaSyC59PrvBlrBW0bO7vQZvT6tWtvvVRY2L6k', '009765437464940284290:6xtc324s40i')
    song_title, song_lyrics = extract_lyrics.get_lyrics(name)
    print("Here are lyrics of this song. Enjoy it!")
    print()
    print(song_title+"\n"+song_lyrics)
    time.sleep(5)
    return song_title,song_lyrics

mood=""
songs={}
songsUrl=[]
randomSong=0
st=""
sl=""

sad_list=["sad","sadness","fear","anger"]
happy_list=["joy","polite"]
query_list=["hello","change to happy","change to sad","change song"]

def record(input_data):
    global mood
    global songs
    global songsUrl
    global randomSong
    global st
    global sl

    # print ("Start recording")
    # myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels =1)
    # sd.wait()  # Wait until recording is finished
    # write('input.wav', fs, myrecording)  # Save as WAV file 
    
    # with open('input.wav','rb') as audio_file:
    #     speech_recognition_results = speech_to_text.recognize(
    #     audio=audio_file,
    #     content_type='audio/wav',
    # ).get_result()
    # print (speech_recognition_results)
    # message = speech_recognition_results["results"][0]["alternatives"][0]["transcript"]
    direct_search=0
    if "bye" in input_data.lower():
        return ["Bye! Have a nice day!!"]
    
    if "song" == input_data.lower():
        return ["Nice. Input anything you want to search."] 

    if "mood" == input_data.lower():
        return ["Good. Then How are you today?"]   


    if input_data.lower() not in query_list:
        text = input_data
        tone_analysis = tone_analyzer.tone(
            {'text': text},
            content_type='application/json'
        ).get_result()

        if len(tone_analysis["document_tone"]["tones"])>0:
            query=tone_analysis["document_tone"]["tones"][0]["tone_name"]
            if query.lower() in sad_list: 
                input_data="sad" 
            elif query.lower() in happy_list:
                input_data="happy"
            else:
                direct_search=1
        else:
            direct_search=1

    #print(tone_analysis["document_tone"]["tones"][0]["tone_name"])
    #print(json.dumps(tone_analysis, indent=2))
    
    returned_list=[]
    if direct_search==0:
        response = service.message(
        assistant_id='d11ac974-e98d-4324-99e4-d3640ebd3411',
        session_id=sessionId["session_id"],
        input={
            'message_type': 'text',
            'text': input_data
        }
        ).get_result()
        intent = response["output"]["intents"][0]["intent"] 

        bot_answer = response["output"]["generic"][0]["text"]
        print ("Bot says: ", bot_answer)

        returned_list.append(bot_answer)
    else:
        intent="SongSpecific"

    if intent == "Sad" or intent == "ChangeToSad":
        mood = "sad" 

    elif intent == "Happy" or intent == "ChangeToHappy":
        mood = "happy"
    
    elif intent == "ChangeSone":
        songsUrl.pop(randomSong)
        randomSong = random.randint(0,len(songsUrl)-1)
        st,sl=generate_music(songsUrl[randomSong],songs[songsUrl[randomSong]] )
        returned_list.append(songsUrl[randomSong] + "\n"+ st+"\n"+sl)

    elif intent == "SongSpecific":
        songs = search_music(input_data)
        songsUrl = list(songs.keys())
        if len(songsUrl)==0:
            returned_list.append("Sorry I cannot find a song related to that. Do you want to try other input?")
        else:
            randomSong = random.randint(0,len(songsUrl)-1)
            st,sl=generate_music(songsUrl[randomSong],songs[songsUrl[randomSong]] )
            returned_list.append(songsUrl[randomSong]+ "\n" + st+"\n"+sl)

    elif intent== "songType" or intent == "ChangeSongType":
        genre = response["output"]["entities"][0]["value"]
        songs = search_music(mood+genre)
        songsUrl = list(songs.keys())
        randomSong = random.randint(0,len(songsUrl)-1)
        st,sl=generate_music(songsUrl[randomSong],songs[songsUrl[randomSong]] )
        returned_list.append(songsUrl[randomSong]+"\n" +  st+"\n")
    return returned_list



###########################gui########################################


from threading import Thread
import struct
import time
import hashlib
import base64
import socket
import time
import types
import multiprocessing
import os
mode = "initialize"
pic_size = 0
pic_receive = 0
pic = ""
pic_repeat = []

class returnCrossDomain(Thread):
    def __init__(self, connection):
        Thread.__init__(self)
        self.con = connection
        self.isHandleShake = False

    def run(self):
        global mode
        global pic_size
        global pic_receive
        global pic
        global pic_repeat
        while True:
            if not self.isHandleShake:
                # 开始握手阶段
                header = self.analyzeReq()
                secKey = header['Sec-WebSocket-Key']

                acceptKey = self.generateAcceptKey(secKey)

                response = "HTTP/1.1 101 Switching Protocols\r\n"
                response += "Upgrade: websocket\r\n"
                response += "Connection: Upgrade\r\n"
                response += "Sec-WebSocket-Accept: %s\r\n\r\n" % (acceptKey.decode('utf-8'))
                self.con.send(response.encode())
                self.isHandleShake = True
                if(mode=="initialize"):
                    mode = "get_order"
                print('response:\r\n' + response)
                # 握手阶段结束

                #读取命令阶段
            elif mode == "get_order":
                opcode = self.getOpcode()
                if opcode == 8:
                    self.con.close()
                self.getDataLength()
                clientData = self.readClientData()
                print('客户端数据：' + str(clientData))
                # 处理数据
                ans = self.answer(clientData)
                ans="\n".join(ans)
                self.sendDataToClient(ans)
                
                #for item in ans:
                    #self.sendDataToClient(item)
                # if (ans != "Unresolvable Command!" and ans != "hello world"):
                #     pic_size = int(clientData[3:])
                #     pic_receive = 0
                #     pic = ""
                #     pic_repeat=[]
                #     print("需要接收的数据大小：", pic_size)
                #     mode = "get_pic"

                #读取图片阶段
            elif mode == "get_pic":
                opcode = self.getOpcode()
                if opcode == 8:
                    self.con.close()
                self.getDataLength()
                clientData = self.readClientData()
                print('客户端数据：' + str(clientData))
                pic_receive += len(clientData)
                pic += clientData
                if pic_receive < pic_size:
                    self.sendDataToClient("Receive:"+str(pic_receive)+"/"+str(pic_size))
                    print("图片接收情况:",pic_receive,"/",pic_size)
                    #print("当前图片数据:",pic)
                else:
                    print("完整图片数据:",pic)
                    self.sendDataToClient("Receive:100%")
                    result = self.process(pic)
                    self.sendDataToClient(result)
                    pic_size = 0
                    pic_receive = 0
                    pic = ""
                    pic_repeat=[]
                    mode = "get_order"
                # 处理数据

                # self.sendDataToClient(clientData)

    def legal(self, string):  # python总会胡乱接收一些数据。。只好过滤掉
        if len(string) == 0:
            return 0
        elif len(string) <= 100:
            if self.loc(string) != len(string):
                return 0
            else:
                if mode != "get_pic":
                    return 1
                elif len(string) + pic_receive == pic_size:
                    return 1
                else:
                    return 0
        else:
            if self.loc(string) > 100:
                if mode != "get_pic":
                    return 1
                elif string[0:100] not in pic_repeat:
                    pic_repeat.append(string[0:100])
                    return 1
                else:
                    return -1  # 收到重复数据，需要重定位
            else:
                return 0

    def loc(self, string):
        i = 0
        while(i<len(string) and self.rightbase64(string[i])):
            i = i+1
        return i

    def rightbase64(self, ch):
        if (ch >= "a") and (ch <= "z"):
            return 1
        elif (ch >= "A") and (ch <= "Z"):
            return 1
        elif (ch >= "0") and (ch <= "9"):
            return 1
        elif ch == '+' or ch == '/' or ch == '|' or ch == '=' or ch == ' ' or ch == "'" or ch == '!' or ch == ':':
            return 1
        else:
            return 0

    def analyzeReq(self):
        reqData = self.con.recv(1024).decode()
        reqList = reqData.split('\r\n')
        headers = {}
        for reqItem in reqList:
            if ': ' in reqItem:
                unit = reqItem.split(': ')
                headers[unit[0]] = unit[1]
        return headers

    def generateAcceptKey(self, secKey):
        sha1 = hashlib.sha1()
        sha1.update((secKey + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode())
        sha1_result = sha1.digest()
        acceptKey = base64.b64encode(sha1_result)
        return acceptKey

    def getOpcode(self):
        first8Bit = self.con.recv(1)
        first8Bit = struct.unpack('B', first8Bit)[0]
        opcode = first8Bit & 0b00001111
        return opcode

    def getDataLength(self):
        second8Bit = self.con.recv(1)
        second8Bit = struct.unpack('B', second8Bit)[0]
        masking = second8Bit >> 7
        dataLength = second8Bit & 0b01111111
        #print("dataLength:",dataLength)
        if dataLength <= 125:
            payDataLength = dataLength
        elif dataLength == 126:
            payDataLength = struct.unpack('H', self.con.recv(2))[0]
        elif dataLength == 127:
            payDataLength = struct.unpack('Q', self.con.recv(8))[0]
        self.masking = masking
        self.payDataLength = payDataLength
        #print("payDataLength:", payDataLength)



    def readClientData(self):

        if self.masking == 1:
            maskingKey = self.con.recv(4)
        data = self.con.recv(self.payDataLength)

        if self.masking == 1:
            i = 0
            trueData = ''
            for d in data:
                trueData += chr(d ^ maskingKey[i % 4])
                i += 1
            return trueData
        else:
            return data

    def sendDataToClient(self, text):
        sendData = ''
        sendData = struct.pack('!B', 0x81)

        length = len(text)
        if length <= 125:
            sendData += struct.pack('!B', length)
        elif length <= 65536:
            sendData += struct.pack('!B', 126)
            sendData += struct.pack('!H', length)
        elif length == 127:
            sendData += struct.pack('!B', 127)
            sendData += struct.pack('!Q', length)

        sendData += struct.pack('!%ds' % (length), text.encode())
        dataSize = self.con.send(sendData)

    def answer(self,data):
        return record(data)

    def padding(self,data):
        missing_padding = 4 - len(data) % 4
        if missing_padding:
            data += '='*missing_padding
        return data

    def process(self,pic):

        #此处是图片处理阶段

        return pic

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 9999))
    sock.listen(5)
    webbrowser.open("/Users/jiangao/Desktop/MusicBot 2/Home.html", new = 2)
    while True:
        try:
            connection, address = sock.accept()
            returnCrossDomain(connection).start()
           
        except:
            time.sleep(1)

if __name__ == "__main__":
    main()