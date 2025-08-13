function getCookieByName(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}

const client_id = getCookieByName("client_id");

var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
var messages = document.getElementById('chat');

ws.onmessage = function (event) {
    var message = document.createElement('p');
    var content = event.data;
    message.style.color = 'blue';
    message.style.textAlign = "start";
    message.innerHTML=content;
    messages.appendChild(message);

    messages.scrollTo({
        top: messages.scrollHeight,
        behavior: 'instant'
    });
};

function sendMessage(event) {
    var message = document.createElement('p');
    var text = document.getElementById("messageText")
    message.style.color = "black";
    message.style.textAlign= 'end';
    message.textContent = text.value;
    messages.appendChild(message);
    messages.scrollTo({
        top: messages.scrollHeight,
        behavior: 'instant'
    });
    ws.send(text.value);
    text.value = '';
    event.preventDefault()
}