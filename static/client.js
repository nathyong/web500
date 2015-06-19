var ws = new WebSocket("ws://" + location.host + "/socket");
ws.onopen = function() {
    ws.send(JSON.stringify({act : 'auth'}));
};
ws.onmessage = function(evt) {
    data = JSON.parse(evt.data);
    if (data.act === 'chat') {
        $('#msglist tr:last').after('<tr><td>' + data.from + ':</td><td>' + data.message + '</td></tr>');
    }
    else if (data.act === 'auth') {
        if (data.response === 'success') {
            $('#username').val(data.username);
            $('#secretkey').html(data.secretkey);
            $('#error').hide();
        } else if (data.response === 'taken') {
            //prompt for login or new username
            $('#error, #login').show();
        } else if (data.response === 'changed') {
            $.ajax({
                type: "POST",
                url: "/cookie",
                data: "username=" + data.username + "&secretkey=" + data.secretkey,
            });
        } else {
            //unsuitable user name (anonymous)
            $('#username').val(data.username);
            $('#error').show();
        }
    }
};

function setuser(name, key) {
    key = typeof key !== 'undefined' ? key : '';
    data = {
        act : 'auth',
        username : name,
        secretkey : key,
    }
    ws.send(JSON.stringify(data));
}

function sendmsg() {
    data = {
       act : 'chat',
       message : $('#msgbox').val(),
    }
    ws.send(JSON.stringify(data));
    $('#msgbox').val('');
}

$("#keyprompt").keypress(function(event) {
    if (event.which == 13) {
        setuser($('#username').val(), $(this).val());
    }
});

$("#username").keypress(function(event) {
    if (event.which == 13) {
        setuser($(this).val());
    }
});


