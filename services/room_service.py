class Rooms:

    def __init__(self):
        self.rooms = {}
    
    def add_room(self, room):
        if room not in self.rooms:
            self.rooms[room] = set()
    
    def remove_room(self, room):
        if room in self.rooms:
            del self.rooms[room]
    
    def add_user_to_room(self, user, room):
        if room in self.rooms:
            self.rooms[room].add(user)
        else:
            self.rooms[room] = set([user])
    
    def remove_user_from_room(self, user, room):
        if room in self.rooms and user in self.rooms[room]:
            self.rooms[room].remove(user)
    
    def get_users_in_room(self, room):
        if room in self.rooms:
            return list(self.rooms[room])
        return []

    