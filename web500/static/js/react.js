var socket = new SocketService("ws://" + location.host + location.pathname + '/ws');

var Message = React.createClass({
    render: function() {
        return (<li className="chatline"><div className="prefix">{this.props.from}: </div>{this.props.message}</li>);
    }
});

var MessageList = React.createClass({
    getInitialState: function() {
        return {messages: []};
    },
    componentWillMount: function() {
        var messageList = this;
        socket.addListener('messages', function(message) {
            messageList.setState({messages: message.messages});
            $('#msglist').scrollTop($("#msglist")[0].scrollHeight);
        });
    },
    render: function() {
        var allMessages = this.state.messages.map(function(message) {
            return (<Message from={message.from} message={message.messsage} />);
        });
        return (<ul id="msglist">{allMessages}</ul>);
    }
});

var ChatBox = React.createClass({
    handleSubmit: function(e) {
        e.preventDefault();
        var author = 'user';
        var input = this.refs.text.getDOMNode();
        var text = input.value.trim();
        if (text === '') return;

        socket.sendRequest({
            act: 'chat',
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
