function SocketService(socketLocation) {
    var service = {};
    var listeners = {};

    function init() {
        service = {};
        listeners = {};

        ws = new WebSocket(socketLocation);

        ws.onopen = function () {};
        ws.onclose = function() {};

        ws.onmessage = function (message) {
            listener(JSON.parse(message.data));
        };
    }

    init();

    function listener(message) {
        if (!listeners[message.act]) {
            console.log('No listener for act: ' + message.act);
            return;
        }
        listeners[message.act](message);
    }

    function sendRequest(request) {
        ws.send(JSON.stringify(request));
    }
    
    function addListener(act, callback) {
        listeners[act] = callback;
    }

    function removeListener(act) {
        return delete listeners[act];
    }

    service.sendRequest = sendRequest;
    service.addListener = addListener;
    service.removeListener = removeListener;

    return service;
}
