var ws = new WebSocket("ws://" + location.host + "/socket");
ws.onopen = function() {
   ws.send("Hello, world");
};
ws.onmessage = function (evt) {
   alert(evt.data);
};
