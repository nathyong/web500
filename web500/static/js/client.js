var ws = new WebSocket("ws://" + location.host + location.pathname + '/ws');

ws.onopen = function() {
    add_msg('chatbot', 'Connected to chat server! Play nice!');
};

ws.onmessage = function(evt) {
    data = JSON.parse(evt.data);
    switch (data.act) {
        case 'chat':
            add_msg(data.from, data.message);
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

function sendmsg(msg) {
    data = {
        act : 'chat',
        data : msg,
    };
    ws.send(JSON.stringify(data));
}

function add_msg(user, msg) {
    var chatline_classes = ['chatline'];
    if (user === 'chatbot') {
        chatline_classes.push('chatline-announce');
    }
    $('#msglist').append('<li class="' + chatline_classes.join(' ') + '"><span class="prefix">' + user + ': </span>' + msg + '</li>');
    $('#msglist').scrollTop($("#msglist")[0].scrollHeight);
}

$('#msgform').submit(function(e) {
    e.preventDefault();
    var msg = $('#msgbox').val();
    if (msg) {
        sendmsg(msg);
    }
    $('#msgbox').val('');
});

