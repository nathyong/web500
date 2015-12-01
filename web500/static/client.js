var ws = new WebSocket("ws://" + location.host + "/chat/ws");

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

function sendmsg() {
    data = {
        act : 'chat',
        message : $('#msgbox').val(),
    };
    ws.send(JSON.stringify(data));
    $('#msgbox').val('');
}

var msg_height = 0;

function add_msg(user, msg) {
    $('#msglist').append('<li class="chatline ' + user + '"><span class="prefix">' + user + ': </span>' + msg + '</li>');
    msg_height += parseInt($('#msglist li').last().height());
    $('#msglist').stop().animate({scrollTop: msg_height});
}
