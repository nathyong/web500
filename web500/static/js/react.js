var socket = new SocketService("ws://" + location.host + location.pathname + '/ws');

var Message = React.createClass({
    render: function() {
        return (<li className="chatline"><div className="prefix">{this.props.message.from}: </div>{this.props.message.text}</li>);
    }
});

var MessageList = React.createClass({
    getInitialState: function() {
        return {messages: []};
    },
    addMessage: function(message) {
        var current = this.state.messages;
        current.push(<Message message={message} />);
        this.setState({messages: current});
        $('#msglist').scrollTop($("#msglist")[0].scrollHeight);
    },
    componentWillMount: function() {
        var messageList = this;
        socket.addListener('chat', function(message) {
            for (var m of message.data) {
                messageList.addMessage(m);
            }
        });
        socket.addListener('notice', function(message) {
            messageList.addMessage(message.data);
        });
    },
    render: function() {
        return (<ul id="msglist">{this.state.messages}</ul>);
    }
});

var ChatBox = React.createClass({
    handleSubmit: function(e) {
        e.preventDefault();
        var author = 'user';
        var input = this.refs.text.getDOMNode();
        var text = input.value.trim();
        if (text === '') return;

        //text starting with ! will be a game command like !bid, !play etc
        var action = (text[0] === '!') ? 'command': 'chat';

        socket.sendRequest({
            act: action,
            data: text,
        });

        input.value = '';
        return false;
    },
    render: function() {
        return (
        <div>
            <MessageList />
            <form id="msgform" onSubmit={this.handleSubmit}>
                <button>Send</button>
                <span>
                    <input autocomplete="off" placeholder="Say something nice" ref="text" />
                </span>
            </form>
        </div>
        );
    }
});

var OnlineUsersList = React.createClass({
    getInitialState: function() {
        return {users: []};
    },
    componentWillMount: function() {
        var userList = this; //keep track of instance
        socket.addListener('users', function(message) {
            userList.setState({users: message.users});
        });
    },
    render: function() {
        var userNodes = this.state.users.map(function(user) {
            return (
                <li>{user}</li>
            );
        });
        return (
        <div>
            <h3>Online Users</h3>
            <ul>{userNodes}</ul>
        </div>
        );
    },
});

ReactDOM.render(<ChatBox />, document.getElementById('chatbox'))
ReactDOM.render(<OnlineUsersList />, document.getElementById('onlineusers'))
