var ws = new WebSocket("ws://" + location.host + "/chat/ws");
ws.onmessage = function(evt) {
    data = JSON.parse(evt.data);
    $('#msglist tr:last').after('<tr><td>' + data.from + ':</td><td>' + data.message + '</td></tr>');
};

function sendmsg() {
    data = {
        act : 'chat',
        message : $('#msgbox').val(),
    };
    ws.send(JSON.stringify(data));
    $('#msgbox').val('');
}
