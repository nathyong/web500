var socketService = new SocketService("ws://" + location.host + location.pathname + '/ws');

var Message = React.createClass({
    render: function() {
        return (<li className="chatline"><div className="prefix">{this.props.from}: </div>{this.props.message}</li>);
    }
});

var MessageList = React.createClass({
    render: function() {
        var allMessages = this.props.messages.map(function(message) {
            return (<Message from={message.from} message={message.messsage} />);
        });
        return (<ul id="msglist">{allMessages}</ul>);
    }
});

var ChatBox = React.createClass({
    getInitialState: function() {
        return {messages: []};
    },
    componentWillMount: function() {
        var chatBox = this;
        var socket = this.props.socketService;
        socket.addListener('messages', function(message) {
            chatBox.setState({messages: message.messages});
        });
    },
    handleSubmit: function(e) {
        e.preventDefault();
        var author = 'user';
        var input = this.refs.text.getDOMNode();
        var text = input.value.trim();
        if (text === '') return;

        var socket = this.props.socketService;
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
            <MessageList messages={this.state.messages} />
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
        var socket = this.props.socketService;
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

ReactDOM.render(<ChatBox socketService={socketService}/>, document.getElementById('chatbox'))
ReactDOM.render(<OnlineUsersList socketService={socketService} />, document.getElementById('onlineusers'))
