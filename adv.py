from room import Room
from player import Player
from world import World

import random
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
def add_current_room_to_room_dict(player, room_dict):
    room = player.current_room
    room_id = room.id
    room_dict[room_id] = {'exits': {}}
    room_info = room_dict[room_id]
    exits = room.get_exits()
    for d in exits:
        room_info['exits'][d] = '?'
    if len(room_info['exits']) == 1:
        room_info['fully_explored'] = True
    else:
        room_info['fully_explored'] = False


def check_if_fully_explored(room_dict, room_id):
    exits = room_dict[room_id]['exits']
    fully_explored = True
    for d in exits:
        if exits[d] == '?':
            fully_explored = False
            break
    room_dict[room_id]['fully_explored'] = fully_explored


def travel_and_log(player, direction, traversal_path, room_dict, rooms_explored):
    current_room_id = player.current_room.id
    print(f'Traveling {direction} from room {current_room_id}')
    traversal_path.append(direction)
    player.travel(direction)
    next_room_id = player.current_room.id
    room_dict[current_room_id]['exits'][direction] = next_room_id
    check_if_fully_explored(room_dict, current_room_id)
    if next_room_id not in room_dict:
        add_current_room_to_room_dict(player, room_dict)
        rooms_explored += 1
    direction_pairs = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
    opp_dir = direction_pairs[direction]
    room_dict[next_room_id]['exits'][opp_dir] = current_room_id
    check_if_fully_explored(room_dict, next_room_id)
    return rooms_explored


def bfs_for_unexplored_room(player, room_dict):
    room_id = player.current_room.id
    searched_rooms = {room_id}
    queue = []
    current_path = [room_id]
    while True:
        current_room_id = current_path[-1]
        exits = room_dict[current_room_id]['exits']
        for d in exits:
            room_in_d_id = exits[d]
            if room_in_d_id not in searched_rooms:
                new_path = current_path.copy()
                new_path.append(room_in_d_id)
                if not room_dict[room_in_d_id]['fully_explored']:
                    return new_path
                else:
                    searched_rooms.add(room_in_d_id)
                    queue.append(new_path)
        current_path = queue.pop(0)


traversal_path = []

room_dict = {}


start_id = player.current_room.id
start_exits = player.current_room.get_exits()
room_dict[start_id] = {'exits': {}, 'fully_explored': False}
for d in start_exits:
    room_dict[start_id]['exits'][d] = '?'
rooms_explored = 1
target_rooms = len(room_graph)

while True:
    room = player.current_room
    room_id = room.id
    exits = room_dict[room_id]['exits']
    for d in exits:
        if exits[d] == '?':
            next_dir = d
            break
    rooms_explored = travel_and_log(player, next_dir, traversal_path, room_dict, rooms_explored)
    if rooms_explored == target_rooms:
        break

    next_room = player.current_room
    next_room_id = next_room.id
    next_room_info = room_dict[next_room_id]
    if next_room_info['fully_explored']:
        final_path = bfs_for_unexplored_room(player, room_dict)
        for i in range(len(final_path)-1):
            current_room_id = final_path[i]
            next_room_id = final_path[i+1]
            exits = room_dict[current_room_id]['exits']
            for d in exits:
                if exits[d] == next_room_id:
                    next_d = d
                    break
            rooms_explored = travel_and_log(player, next_d, traversal_path, room_dict, rooms_explored)
            if rooms_explored == target_rooms:
                break


# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")



#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")
