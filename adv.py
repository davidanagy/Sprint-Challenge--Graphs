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
traversal_path = []


# class GridNode:
#     def __init__(self, id, location, exits):
#         self.id = id
#         self.location = location
#         self.n = False
#         self.s = False
#         self.e = False
#         self.w = False
#         for d in exits:
#             setattr(self, d, True)
#         self.fully_explored = False

#     def __repr__(self):
#         return f'Room {self.id}'

    # def connect_nodes(self, direction, other_node):
    #     direction_pairs = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
    #     setattr(self, direction, other_node)
    #     setattr(other_node, direction_pairs[direction], self)

    # def check_if_fully_explored(self):
    #     fully_explored = True
    #     for d in [self.n, self.s, self.e, self.w]:
    #         if d == '?':
    #             fully_explored = False
    #             break
    #     self.fully_explored = fully_explored


class Grid:
    def __init__(self):
        self.matrix = {}
        self.rooms_explored = 0
        self.current_loc = None

    def copy(self):
        new_grid = Grid()
        new_grid.matrix = self.matrix.copy()
        new_grid.rooms_explored = self.rooms_explored
        new_grid.current_loc = self.current_loc
        return new_grid

    def get_matrix_directions(self, location):
        directions = {}
        x = location[0]
        y = location[1]
        directions['n'] = (x, y+1)
        directions['s'] = (x, y-1)
        directions['e'] = (x+1, y)
        directions['w'] = (x-1, y)
        return directions

    def make_new_matrix_node(self, id, location, exits):
        self.matrix[location] = {}
        new_node = self.matrix[location]
        new_node['id'] = id
        new_node['exits'] = {}
        directions = self.get_matrix_directions(location)
        for e in exits:
            exit_loc = directions[e]
            if exit_loc in self.matrix:
                new_node['exits'][e] = self.matrix[exit_loc]['id']
            else:
                new_node['exits'][e] = '?'
        self._check_if_fully_explored(location)
        self.rooms_explored += 1
        self.current_loc = location

    def get_unexplored_exits(self, location):
        exits = self.matrix[location]['exits']
        unexplored_exits = []
        for e in exits:
            if exits[e] == '?':
                unexplored_exits.append(e)
        return unexplored_exits

    def _check_if_fully_explored(self, location):
        if location in self.matrix:
            node = self.matrix[location]
            fully_explored = True
            for e in node['exits']:
                if node['exits'][e] == '?':
                    fully_explored = False
                    break
            node['fully_explored'] = fully_explored

    def _update_matrix_exits(self, location):
        if location in self.matrix:
            node = self.matrix[location]
            directions = self.get_matrix_directions(location)
            old_exits = node['exits']
            new_exits = {}
            for e in old_exits:
                exit_loc = directions[e]
                if exit_loc in self.matrix:
                    exit_id = self.matrix[exit_loc]['id']
                    new_exits[e] = exit_id
                else:
                    new_exits[e] = '?'
            if old_exits == new_exits:
                exit_changed = False
            else:
                node['exits'] = new_exits
                exit_changed = True
            return exit_changed

    def update_matrix_values(self):
        changed_exit = True
        while changed_exit:
            for location in self.matrix:
                changed_exit = self._update_matrix_exits(location) 
        for location in self.matrix:
            self._check_if_fully_explored(location)

    def bfs_for_closest_unexplored_room(self, location):
        searched_locs = {location}
        queue = []
        current_traversal_tuple = ([], location)
        while True:
            current_traversal = current_traversal_tuple[0]
            current_loc = current_traversal_tuple[1]
            exits = self.matrix[current_loc]['exits']
            directions = self.get_matrix_directions(current_loc)
            for e in exits:
                new_loc = directions[e]
                if new_loc not in searched_locs:
                    new_traversal = current_traversal.copy()
                    new_traversal.append(e)
                    new_node = self.matrix[new_loc]
                    if not new_node['fully_explored']:
                        return (new_traversal, new_loc)
                    else:
                        searched_locs.add(new_loc)
                        queue.append((new_traversal, new_loc))
            current_traversal_tuple = queue.pop(0)

    def bfs_go_to_location(self, start_loc, dest_loc):
        searched_locs = {start_loc}
        queue = []
        current_traversal_tuple = ([], start_loc)
        while True:
            current_traversal = current_traversal_tuple[0]
            current_loc = current_traversal_tuple[1]
            exits = self.matrix[current_loc]['exits']
            directions = self.get_matrix_directions(current_loc)
            for e in exits:
                new_loc = directions[e]
                if new_loc not in searched_locs:
                    new_traversal = current_traversal.copy()
                    new_traversal.append(e)
                    if new_loc == dest_loc:
                        return new_traversal
                    else:
                        searched_locs.add(new_loc)
                        queue.append((new_traversal, new_loc))
            current_traversal_tuple = queue.pop(0)

    # def find_dirs_with_least_unexplored_rooms(self, current_loc):
    #     exits = self.matrix[current_loc]['exits']
    #     unexplored_exits = []
    #     for e in exits:
    #         if exits[e] == '?':
    #             unexplored_exits.append(e)
    #     if len(unexplored_exits) == 1:
    #         return unexplored_exits[0]
    #     num_unexplored_rooms = []
    #     for e in unexplored_exits:
    #         unexplored_rooms = 0
    #         for loc in self.matrix:
    #             if not self.matrix[loc]['fully_explored']:
    #                 if e == 'n':
    #                     if loc[1] > current_loc[1]:
    #                         unexplored_rooms += 1
    #                 elif e == 's':
    #                     if loc[1] < current_loc[1]:
    #                         unexplored_rooms += 1
    #                 elif e == 'e':
    #                     if loc[0] > current_loc[0]:
    #                         unexplored_rooms += 1
    #                 elif e == 'w':
    #                     if loc[0] < current_loc[0]:
    #                         unexplored_rooms += 1
    #         num_unexplored_rooms.append(unexplored_rooms)
    #     min_unexplored_rooms = num_unexplored_rooms[0]
    #     return_exits = [unexplored_exits[0]]
    #     for i in range(1, len(num_unexplored_rooms)):
    #         if num_unexplored_rooms[i] < min_unexplored_rooms:
    #             min_unexplored_rooms = num_unexplored_rooms[i]
    #             return_exits = [unexplored_exits[i]]
    #         elif num_unexplored_rooms[i] == min_unexplored_rooms:
    #             return_exits.append(unexplored_exits[i])
    #     return return_exits


def move_player(player, direction, traversal_path):
    traversal_path.append(direction)
    player.travel(direction)


def make_traversal_path(player, direction_order):
    traversal_path = []
    room_grid = Grid()
    start_id = player.current_room.id
    start_exits = player.current_room.get_exits()
    room_grid.make_new_matrix_node(start_id, (0,0), start_exits)
    target_rooms = len(room_graph)
    current_loc = (0,0)
    rooms_explored = 1

    while True:
        room_grid.update_matrix_values()
        current_node = room_grid.matrix[current_loc]
        if not current_node['fully_explored']:
            unexplored_exits = room_grid.get_unexplored_exits(current_loc)
            for d in direction_order:
                if d in unexplored_exits:
                    next_dir = d
                    break
            move_player(player, next_dir, traversal_path)
            rooms_explored += 1
        
            room = player.current_room
            room_id = room.id
            grid_directions = room_grid.get_matrix_directions(current_loc)
            current_loc = grid_directions[next_dir]
            room_exits = room.get_exits()
            room_grid.make_new_matrix_node(room_id, current_loc, room_exits)
            if rooms_explored == target_rooms:
                break

        else:
            traversal_dirs = room_grid.bfs_for_closest_unexplored_room(current_loc)
            for d in traversal_dirs[0]:
                move_player(player, d, traversal_path)
            current_loc = traversal_dirs[1]

    return_path = room_grid.bfs_go_to_location(current_loc, (0,0))
    for d in return_path:
        player.travel(d)
    return traversal_path

### README ###
# The below is the last idea I had. Basically, I wanted to do a depth-first traversal
# for each possible direction to move (when there are unexplored exits), find which direction
# results in the smallest possible path, and return that. But the logic here is quite complicated
# and I wasn't able to figure it out in time.

# room_grid = Grid()
# start_id = player.current_room.id
# start_exits = player.current_room.get_exits()
# room_grid.make_new_matrix_node(start_id, (0,0), start_exits)
# target_rooms = len(room_graph)
# traversal_path = []
# def make_traversal_path(player, room_grid, traversal_path):
#     new_path = traversal_path.copy()
#     new_grid = room_grid.copy()
#     new_grid.update_matrix_values()
#     current_node = room_grid.matrix[new_grid.current_loc]
#     if not current_node['fully_explored']:
#         paths = []
#         unexplored_exits = new_grid.get_unexplored_exits(new_grid.current_loc)
#         for d in unexplored_exits:
#             next_dir = d
#             move_player(player, next_dir, new_path)
#             room = player.current_room
#             room_id = room.id
#             grid_directions = new_grid.get_matrix_directions(new_grid.current_loc)
#             new_loc = grid_directions[next_dir]
#             room_exits = room.get_exits()
#             new_grid.make_new_matrix_node(room_id, new_loc, room_exits)
#             if new_grid.rooms_explored == target_rooms:
#                 return new_path
#             else:
#                 return_loc = new_grid.current_loc
#                 path_grid_tuple = make_traversal_path(player, new_grid, new_path)
#                 grid = path_grid_tuple[1]
#                 return_path = grid.bfs_go_to_location(grid.current_loc, return_loc)
#                 for d in return_path:
#                     player.travel(d)
#                 paths.append(path_grid_tuple)
#         path_lengths = [len(path[0]) for path in paths]
#         min_length = path_lengths[0]
#         min_i = 0
#         for i in range(1, len(path_lengths)):
#             if path_lengths[i] < min_length:
#                 min_length = path_lengths[i]
#                 min_i = i
#         return paths[min_i]

#     else:
#         traversal_dirs = new_grid.bfs_for_closest_unexplored_room(new_grid.current_loc)
#         for d in traversal_dirs[0]:
#             move_player(player, d, new_path)
#         new_grid.current_loc = traversal_dirs[1]
#         return make_traversal_path(player, new_grid, new_path)

# traversal_path = make_traversal_path(player, room_grid, traversal_path)
def create_direction_orders(all_orders, direction_order):
    order_finished = True
    for d in ['n', 's', 'e', 'w']:
        if d not in direction_order:
            new_order = direction_order.copy()
            new_order.append(d)
            create_direction_orders(all_orders, new_order)
            order_finished = False
    if order_finished:
        all_orders.append(direction_order)


all_direction_orders = []
create_direction_orders(all_direction_orders, [])

traversal_paths = []
for order in all_direction_orders:
    traversal_path = make_traversal_path(player, order)
    traversal_paths.append(traversal_path)

lengths = [len(path) for path in traversal_paths]
min_i = 0
min_len = lengths[0]
for i in range(1, len(lengths)):
    if lengths[i] < min_len:
        min_i = i
        min_len = lengths[i]
traversal_path = traversal_paths[min_i]
print(all_direction_orders[min_i]) # s, w, n, e

# while True:
#     traversal_path = make_traversal_path(player, all_direction_orders)
#     length = len(traversal_path)
#     print(f'New path made of length {length}')
#     if length < 960:
#         break

print(traversal_path)
with open('path.txt', 'w') as f:
    write_str = ''
    for i in range(len(traversal_path)-1):
        d = traversal_path[i]
        write_str += f'{d} '
    write_str += str(traversal_path[-1])
    f.write(write_str)

# traversal_path = make_traversal_path(player, ['s', 'w', 'n', 'e'])

# def add_current_room_to_room_dict(player, room_dict):
#     room = player.current_room
#     room_id = room.id
#     room_dict[room_id] = {'exits': {}}
#     room_info = room_dict[room_id]
#     exits = room.get_exits()
#     for d in exits:
#         room_info['exits'][d] = '?'
#     if len(room_info['exits']) == 1:
#         room_info['fully_explored'] = True
#     else:
#         room_info['fully_explored'] = False


# def check_if_fully_explored(room_dict, room_id):
#     exits = room_dict[room_id]['exits']
#     fully_explored = True
#     for d in exits:
#         if exits[d] == '?':
#             fully_explored = False
#             break
#     room_dict[room_id]['fully_explored'] = fully_explored


# def travel_and_log(player, direction, traversal_path, room_dict, rooms_explored):
#     current_room_id = player.current_room.id
#     print(f'Traveling {direction} from room {current_room_id}')
#     traversal_path.append(direction)
#     player.travel(direction)
#     next_room_id = player.current_room.id
#     room_dict[current_room_id]['exits'][direction] = next_room_id
#     check_if_fully_explored(room_dict, current_room_id)
#     if next_room_id not in room_dict:
#         add_current_room_to_room_dict(player, room_dict)
#         rooms_explored += 1
#     direction_pairs = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
#     opp_dir = direction_pairs[direction]
#     room_dict[next_room_id]['exits'][opp_dir] = current_room_id
#     check_if_fully_explored(room_dict, next_room_id)
#     return rooms_explored


# def bfs_for_unexplored_room(player, room_dict):
#     room_id = player.current_room.id
#     searched_rooms = {room_id}
#     queue = []
#     current_path = [room_id]
#     while True:
#         current_room_id = current_path[-1]
#         exits = room_dict[current_room_id]['exits']
#         for d in exits:
#             room_in_d_id = exits[d]
#             if room_in_d_id not in searched_rooms:
#                 new_path = current_path.copy()
#                 new_path.append(room_in_d_id)
#                 if not room_dict[room_in_d_id]['fully_explored']:
#                     return new_path
#                 else:
#                     searched_rooms.add(room_in_d_id)
#                     queue.append(new_path)
#         current_path = queue.pop(0)


# room_dict = {}


# start_id = player.current_room.id
# start_exits = player.current_room.get_exits()
# room_dict[start_id] = {'exits': {}, 'fully_explored': False}
# for d in start_exits:
#     room_dict[start_id]['exits'][d] = '?'
# rooms_explored = 1
# target_rooms = len(room_graph)

# while True:
#     room = player.current_room
#     room_id = room.id
#     exits = room_dict[room_id]['exits']
#     for d in exits:
#         if exits[d] == '?':
#             next_dir = d
#             break
#     rooms_explored = travel_and_log(player, next_dir, traversal_path, room_dict, rooms_explored)
#     if rooms_explored == target_rooms:
#         break

#     next_room = player.current_room
#     next_room_id = next_room.id
#     next_room_info = room_dict[next_room_id]
#     if next_room_info['fully_explored']:
#         final_path = bfs_for_unexplored_room(player, room_dict)
#         for i in range(len(final_path)-1):
#             current_room_id = final_path[i]
#             next_room_id = final_path[i+1]
#             exits = room_dict[current_room_id]['exits']
#             for d in exits:
#                 if exits[d] == next_room_id:
#                     next_d = d
#                     break
#             rooms_explored = travel_and_log(player, next_d, traversal_path, room_dict, rooms_explored)
#             if rooms_explored == target_rooms:
#                 break


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
