var ws = new WebSocket("ws://" + location.host + "/socket");
ws.onopen = function() {
    //ws.send("Hello, world");
};
ws.onmessage = function(evt) {
    data = JSON.parse(evt.data);
    if (data.act === 'chat') {
        $('#msglist tr:last').after('<tr><td>' + data.from + ':</td><td>' + data.message + '</td></tr>');
    }
};

function sendmsg() {
    data = {
       act : 'chat',
       message : $('#msgbox').val(),
    }
    ws.send(JSON.stringify(data));
    $('#msgbox').val('');
}
