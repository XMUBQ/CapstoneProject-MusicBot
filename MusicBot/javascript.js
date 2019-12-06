// const fs = require('fs');
// const TextToSpeechV1 = require('ibm-watson/text-to-speech/v1');
// const { IamAuthenticator } = require('ibm-watson/auth');

// const textToSpeech = new TextToSpeechV1({
//   authenticator: new IamAuthenticator({
//     apikey: 'HYQ9Ng3S_w_FvKAthbpiEQwVdWRbZZIFBjSZNw5CBhuO',
//   }),
//   url: 'https://gateway-wdc.watsonplatform.net/text-to-speech/api',
// });

var socket;
var current=0;
var total;
var beforetime;
var sendChannel,
    chatWindow = document.querySelector('.chat-window'),
    chatWindowMessage = document.querySelector('.chat-window-message'),
    chatThread = document.querySelector('.chat-thread');



var SpeechRecognition = window.webkitSpeechRecognition;

var recognition = new SpeechRecognition();



connect();
function connect() {
    var host = "ws://127.0.0.1:9999/" ;
    socket = new WebSocket(host);
    try {
        socket.onopen = function (msg) {
            document.getElementById("btnSend").disabled = "";
        };
        socket.onmessage = function (msg) {
        displayContent(msg.data);
        current=0;
        total=0;    
    };

    socket.onerror = function (error) {alert("Error："+ error.name); };

    socket.onclose = function (msg) {
        document.getElementById("btnSend").disabled = true;
    };
}
catch (ex) {
    log(ex);
}

}
async function record() {
    chatWindowMessage.value = " ";
    var Content = '';
    recognition.start();
    recognition.continuous = true;
    recognition.onresult = function(event) {
        var current = event.resultIndex;
        var transcript = event.results[current][0].transcript;
        Content += transcript;
        chatWindowMessage.value=Content;
    };
    function stopRecord() {
        recognition.stop();
        alert('Recording ended.');
    }
      
    setTimeout(stopRecord, 5000);
    
}
// async function endRecord(){
//     recognition.abort();
//     console.log('Speech recognition aborted.');
// }

async function chooseType(type){
    socket.send(type)
}
async function send() {
    var reg = /[~#^$@%&!*;?|^<>`=]/gi;
    var str = chatWindowMessage.value;
    var chatNewThread = document.createElement('li');
    var chatNewMessage;
    if(reg.test(str)){
        chatNewMessage = document.createTextNode(str);
        chatNewThread.appendChild(chatNewMessage);
        chatThread.appendChild(chatNewThread);
        chatThread.scrollTop = chatThread.scrollHeight;
        var chatErrorMessage = document.createTextNode("Sorry, your input is invalid");
        chatNewThread = document.createElement('li');
        chatNewThread.appendChild(chatErrorMessage);
    }
    else{
        chatNewMessage = document.createTextNode(str);
        chatNewThread.appendChild(chatNewMessage);
    }
    chatNewThread.onclick = function(){
        var msg = new SpeechSynthesisUtterance(str);
        window.speechSynthesis.speak(msg);
    }
    chatThread.appendChild(chatNewThread);
    chatThread.scrollTop = chatThread.scrollHeight;
    chatWindowMessage.value = '';
    if (!reg.test(str)){
        socket.send(str);
    }
}
async function displayContent(msg) {
    var messages = msg.split("\n");
    var chatNewThread = document.createElement('li');
    var chatNewMessage;
    var i;
    var url;
    for (i = 0; i<msg.length; i++){
        if (messages[i] !== undefined){
            if (messages[i].includes('http')){
                url = messages[i].slice(messages[i].indexOf("track")+6);
                url = "https://open.spotify.com/embed/track/"+ url;
                var ifrm= document.getElementById("music");
                ifrm.setAttribute("src", url);
                ifrm.style.width = "640px";
                ifrm.style.height = "480px";
                ifrm.frameBorder = 0;
                ifrm.setAttribute('allowtransparency', 'true');
                ifrm.setAttribute('allow', 'encrypted-media');
                chatNewThread.appendChild(ifrm);
                chatNewThread.appendChild(document.createElement("br"));
            }
            else{
                chatNewMessage = document.createTextNode(messages[i]);
                chatNewThread.appendChild(chatNewMessage);
                chatNewThread.appendChild(document.createElement("br"));
            }
           
        }
        
    }
    chatNewThread.onclick = function(){
        var mesg = new SpeechSynthesisUtterance(msg);
        window.speechSynthesis.speak(mesg);
    }
    chatThread.appendChild(chatNewThread);
    chatThread.scrollTop = chatThread.scrollHeight;

}

chatWindowMessage.addEventListener("keyup", function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        chatWindowMessage.value = chatWindowMessage.value.replace(/(\r\n|\n|\r)/gm, "");
        send();
    }
});

window.onbeforeunload = function () {
try {
    socket.close();
    socket = null;
}
catch (ex) {
}
};


function handleMessage(event) {
    var chatNewThread = document.createElement('li'),
        chatNewMessage = document.createTextNode(event.data);

    // Add message to chat thread and scroll to bottom
    chatNewThread.appendChild(chatNewMessage);
    chatThread.appendChild(chatNewThread);
    chatThread.scrollTop = chatThread.scrollHeight;

    // Clear text value
    chatWindowMessage.value = '';
}


