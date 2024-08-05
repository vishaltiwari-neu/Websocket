from datetime import datetime
import redis
import json
from pymongo import MongoClient

class Rooms:

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.redis_client_room = redis.Redis(host='localhost', port=6379, db=1)
        self.redis_client_activity = redis.Redis(host='localhost', port=6379, db=2)
        self.mongo_client = MongoClient('localhost', 27017)
    
    def add_room(self, room):
        if room not in self.rooms:
            self.rooms[room] = set()
    
    def remove_room(self, room):
        if room in self.rooms:
            del self.rooms[room]
    
    def add_user_to_room(self, user, room, request_id):
        user_body = json.dumps({'name': user, 'room': room})
        self.redis_client.set(request_id, user_body)
        self.redis_client_room.sadd(room, user)
    
    def remove_user_from_room(self, user, room, request_id):
        self.redis_client.delete(request_id)
        self.redis_client_room.srem(room, user)
    
    def get_users_in_room(self, room):
        users = self.redis_client_room.smembers(room)
        users = [user.decode('utf-8') for user in users]
        return users

    def get_rooms(self):
        rooms = self.redis_client_room.keys()
        rooms = [room.decode('utf-8') for room in rooms]
        return rooms
    
    def add_activity(self, room, activity):
        key_name = room + '_activity'
        activity_json = json.dumps(activity)
        self.redis_client_activity.set(key_name, activity_json)    

    def get_activity(self, room):
        key_name = room + '_activity'
        activity = self.redis_client_activity.get(key_name)
        print("Activity")
        return json.loads(activity) if activity else {}
    
    def get_room_from_request_id(self, request_id):
        res = self.redis_client.get(request_id)
        if res:
            return json.loads(res)
        return {}

    def check_user_in_room(self, user, room):
        doc = self.mongo_client['auction']['rooms'].find_one({'users': user, 'name': room})
        if doc:
            del doc['_id']
            doc["isEmpty"] = False
        else:
            doc = {}
            doc["isEmpty"] = True
        return doc if doc else {}
     
    def create_room(self, room, users, admin):
        room_obj = {}
        room_obj['name'] = room
        room_obj['users'] = users
        room_obj['createdBy'] = admin
        room_obj['createdAt'] = datetime.now()
        room_obj['completed'] = False
        room_obj['winner'] = {}
        room_obj['users'].append(admin) # Add admin to the list of users
        self.mongo_client['auction']['rooms'].insert_one(room_obj)
    
    def complete_auction(self, room, data):
        winner = {}
        winner['user'] = data['user']
        winner['bid'] = data['bid']
        winner['timestamp'] = datetime.now()
        self.mongo_client['auction']['rooms'].update({'name': room}, {'$set': {'completed': True, 'winner': winner}})