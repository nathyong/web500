var ws = new WebSocket("ws://" + location.host + "/chat/ws");

ws.onopen = function() {
    $('#msglist').append('<tr class="chatline"><td class="prefix">—</td><td class="message">Connected to chat server</td></tr>');
};

ws.onmessage = function(evt) {
    data = JSON.parse(evt.data);
    switch (data.act) {
        case 'chat':
            $('#msglist tr:last').after('<tr class="chatline"><td class="prefix">' + data.from + ':</td><td class="message">' + data.message + '</td></tr>');
            break;
        case 'users':
            $('#onlineusers ul').empty();
            for (var user of data.users) {
                $('#onlineusers ul').append('<li>' + user + '</li>');
            }
            break;
        default:
            $('#msglist tr:last').after('<tr class="chatline chatline-important"><td class="prefix">DEBUG:</td><td class="message">' + evt.data + '</td></tr>');
            break;
    }
};

function sendmsg() {
    data = {
        act : 'chat',
        message : $('#msgbox').val(),
    };
    ws.send(JSON.stringify(data));
    $('#msgbox').val('');
}
