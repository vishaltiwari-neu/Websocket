from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS, cross_origin
from datetime import datetime

from services.room_service import Rooms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = Rooms()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bidding.html')
def bidding():
    return render_template('bidding.html')

@socketio.on('joinRoom')
def handle_join_room(data):
    print(data)
    user = data['user']
    room = data['room']
    
    # Add user to the room
    rooms.add_user_to_room(user, room)
    
    join_room(room)
    total_users = rooms.get_users_in_room(room)
    emit('user_list', total_users, to=room)
    emit('chatMessage', f'{user} has entered the room.', to=room)
    print(f'{user} joined room: {room}')

@socketio.on('leaveRoom')
def handle_leave_room(data):
    user = data['user']
    room = data['room']
    
    # Remove user from the room
    rooms.remove_user_from_room(user, room)
    
    leave_room(room)
    total_users = rooms.get_users_in_room(room)
    emit('user_list', total_users, to=room)
    emit('chat_message', f'{user} has left the room.', to=room)
    print(f'{user} left room: {room}')

@socketio.on('chatMessage')
def handle_chat_message(data):
    user = data['user']
    room = data['room']
    msg = data['message']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{user} sent message: {msg} in room: {room}')
    emit('chatMessage', {'user': user, 'message': msg, 'timestamp': timestamp}, room=room)

@socketio.on('placeBid')
def handle_chat_message(data):
    user = data['user']
    room = data['room']
    bid = data['bid']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    emit('placeBid', {'user': user, 'msg': bid, 'timestamp': timestamp}, to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
