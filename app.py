from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS, cross_origin
from datetime import datetime
from flask import request

from services.room_service import Rooms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CORS_HEADERS'] = 'Content-Type'

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = Rooms()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bidding.html')
def bidding():
    user = request.args.get('userName')
    room = request.args.get('roomName')
    if user and room:
        return render_template('bidding.html', user=user, room=room)
    else:
        return "Missing userName or roomName", 400


@app.route('/completeAuction', methods=['POST'])
def complete_auction():
    room = request.json.get('roomName')
    bidder = request.json.get('bidder')
    bid = request.json.get('bid')

    if not(room and bidder and bid):
        return 400
    
    rooms.complete_auction(room, {'user': bidder, 'bid': bid, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')})


@app.route('/createRoom', methods=['POST'])
def create_room():
    room = request.json.get('roomName')
    emails = request.json.get('users')
    admin = request.json.get('admin')
    print (room, emails, admin)
    if room:
        rooms.create_room(room, emails, admin)
        
        return "Done", 200
    else:
        return "Missing roomName", 400

@app.route('/checkUser', methods=['GET'])
def check_user():
    user = request.args.get('userName')
    room = request.args.get('roomName')
    print (user, room)
    if user and room:
        data = rooms.check_user_in_room(user, room)
        print(data)
        return data, 200
    
    else:
        return {"error": "Missing userName or roomName"}, 400

@socketio.on('joinRoom')
def handle_join_room(data):
    print(data)
    user = data['user']
    room = data['room']
    
    # Add user to the room
    rooms.add_user_to_room(user, room, request.sid)
    
    join_room(room)
    total_users = rooms.get_users_in_room(room)
    print("AAAAAAA", total_users)
    emit('user_list', total_users, to=room)
    emit('notification', f'{user} has entered the room.', to=room)
    print(f'{user} joined room: {room}')


@socketio.on('chatMessage')
def handle_chat_message(data):
    user = data['user']
    room = data['room']
    msg = data['message']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f'{user} sent message: {msg} in room: {room}')
    emit('chatMessage', {'user': user, 'message': msg, 'timestamp': timestamp}, room=room)

@socketio.on('placeBid')
def handle_bid(data):
    user = data['user']
    room = data['room']
    bid = data['bid']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    current_bid = bid
    last_activity = rooms.get_activity(room)
    if last_activity and last_activity['timestamp'] >= timestamp:
        print ("Bid is older than current bid")
        emit('currentBid', {'user': user, 'bid': last_activity['bid'], 'timestamp': timestamp}, to=room)
        return
    
    elif last_activity is {}:
        print ("No activity")
        current_bid = bid
    
    elif last_activity and last_activity['timestamp'] < timestamp:
        current_bid = bid + last_activity['bid']
    
    rooms.add_activity(room, {'user': user, 'bid': current_bid, 'timestamp': timestamp})
    
    # emit('placeBid', {'user': user, 'bid': bid, 'timestamp': timestamp}, to=room)
    emit('currentBid', {'user': user, 'bid': current_bid, 'timestamp': timestamp}, to=room)


@socketio.on('leave')
def handle_disconnect(data):
    # Identify the user and room from the socket session
    print("Disconnect", request.sid)
    user = rooms.get_room_from_request_id(request.sid)
    if user:
        leave_room(user['room'])
        rooms.remove_user_from_room(user['name'], user['room'], request.sid)
        total_users = rooms.get_users_in_room(user['room'])
        emit('user_list', total_users, to=user['room'])
        emit('notification', {'user': 'System', 'message': f'{user["name"]} has left the room.', 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, room=user['room'])
        print(f'{user["name"]} disconnected from room: {user["room"]}')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
