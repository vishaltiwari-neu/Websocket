from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, emit
from datetime import datetime

from services.room_service import Rooms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

rooms = Rooms()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join room')
def handle_join_room(data):
    user = data['user']
    room = data['room']
    
    # Add user to the room
    rooms.add_user_to_room(user, room)
    
    join_room(room)
    total_users = rooms.get_users_in_room(room)
    emit('user list', total_users, to=room)
    emit('message', f'{user} has entered the room.', to=room)
    print(f'{user} joined room: {room}')

@socketio.on('leave room')
def handle_leave_room(data):
    user = data['user']
    room = data['room']
    
    # Remove user from the room
    rooms.remove_user_from_room(user, room)
    
    leave_room(room)
    total_users = rooms.get_users_in_room(room)
    emit('user list', total_users, to=room)
    emit('message', f'{user} has left the room.', to=room)
    print(f'{user} left room: {room}')

@socketio.on('chat message')
def handle_chat_message(data):
    user = data['user']
    room = data['room']
    msg = data['msg']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    emit('chat message', {'user': user, 'msg': msg, 'timestamp': timestamp}, to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
