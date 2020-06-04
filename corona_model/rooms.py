

class rooms:
    def __init__(self, id_num, room_name = "unnamed_room", capacity = 20, default_people = []):
        self.id_num = id_num
        self.room_name = room_name
        self.capacity = capacity
        self.people_in_room = default_people

    def enter_room(self, id):
        self.people_in_room.append(id)

    def leave_room(self, id):
        if id in self.people_in_room:
            self.people_in_room.remove(id)

    def update(self, people_dict):
        for people in self.people_in_room:
            pass