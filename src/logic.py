import random
import math
from typing import List, Dict

"""
This file can be a nice home for your Battlesnake's logic and helper functions.

We have started this for you, and included some logic to remove your Battlesnake's 'neck'
from the list of possible moves!
"""

def get_info() -> dict:
    """
    This controls your Battlesnake appearance and author permissions.
    For customization options, see https://docs.battlesnake.com/references/personalization

    TIP: If you open your Battlesnake URL in browser you should see this data.
    """
    return {
        "apiversion": "1",
        "author": "Mr. Tortoise Team",  # TODO: Your Battlesnake Username
        "color": "#71A46E",  # TODO: Personalize
        "head": "beluga",  # TODO: Personalize
        "tail": "hook",  # TODO: Personalize
    }


def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """
    my_snake = data["you"]      # A dictionary describing your snake's position on the board
    my_head = my_snake["head"]  # A dictionary of coordinates like {"x": 0, "y": 0}
    my_body = my_snake["body"]  # A list of coordinate dictionaries like [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}]
    my_tail = my_body[-1]
  
    hungry = (my_snake['health'] < 60)

    other_snakes = data["board"]["snakes"][1:]
    # print("OTHER SNAKES")
    # print(other_snakes)
  

  
    # Uncomment the lines below to see what this data looks like in your output!
    # print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    # print(f"All board data this turn: {data}")
    # print(f"My Battlesnake this turn is: {my_snake}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")
    # print()

    possible_moves = ["up", "down", "left", "right"]

    # head coordinates for if the snake chooses LRUD
    head_up = {"x":my_head["x"], "y":my_head["y"]+1}
    head_down = {"x":my_head["x"], "y":my_head["y"]-1}
    head_left = {"x":my_head["x"]-1, "y":my_head["y"]}
    head_right = {"x":my_head["x"]+1, "y":my_head["y"]}
  
    # Step 0: Don't allow your Battlesnake to move back on it's own neck.
    possible_moves = _avoid_my_neck(my_body, possible_moves)

    # TODO: Step 1 - Don't hit walls.
    # Use information from `data` and `my_head` to not move beyond the game board.
    board = data['board']
    board_height = board['height']
    board_width = board['width']
    corners = [{'x':0, 'y':0}, {'x':board_width, 'y':0}, {'x':0, 'y':board_height},{'x':board_width, 'y':board_height},]

    # print("FUTURE HEADS")
    # print(head_up)
    # print(head_down)
    # print(head_left)
    # print(head_right)
    print("PRE MOVES WALLS")
    print(possible_moves)
    possible_moves = avoid_walls(head_up, head_down, head_left, head_right, board_height, board_width, possible_moves)
    print("POST MOVES WALLS")
    print(possible_moves)    

    # TODO: Step 2 - Don't hit yourself.
    # Use information from `my_body` to avoid moves that would collide with yourself.
    print("PRE MOVES SELF")
    print(possible_moves)
    possible_moves = avoid_self(my_body[:-1], head_up, head_down, head_left, head_right, possible_moves)
    print("POST MOVES SELF")
    print(possible_moves)
    # TODO: Step 3 - Don't collide with others.
    # Use information from `data` to prevent your Battlesnake from colliding with others.
    if other_snakes:
      possible_moves = avoid_snakes(head_up, head_down, head_left, head_right, other_snakes, possible_moves)
      
    print("PRE MOVES")
    print(possible_moves)
    if len(possible_moves) > 1:
      possible_moves = check_move_safe(my_snake, my_head, my_body, other_snakes, possible_moves)

    if len(possible_moves) > 1:
      possible_moves = check_move_safe2(my_snake, my_head, my_body, other_snakes, board_height, board_width, possible_moves)

    print("AFTER MOVES")
    print(possible_moves)

    # TODO: Step 4 - Find food.
    # Use information in `data` to seek out and find food.
    food = data['board']['food']
  
    if len(possible_moves) > 1:
      if food and my_snake['length'] == 3:
        possible_moves = find_food1(my_head, head_up, head_down, head_left, head_right, food, other_snakes, possible_moves)  

        print("GOING FOR FOOD")  
        
     
        
      elif my_snake['health'] > 40:
        if len(possible_moves) > 1:
          # if checkbodyincorner(my_body, corners) == False:
          #   possible_moves = find_food1(my_head, head_up, head_down, head_left, head_right, corners, other_snakes, possible_moves)
          #   print("GOING TO CORNER")
  
  
          # else:
          possible_moves = chase_tail(my_head, head_up, head_down, head_left, head_right, my_tail, food, possible_moves)
          print("CHASING TAIL")

      elif food:
        possible_moves = find_food(my_head, head_up, head_down, head_left, head_right, food, other_snakes, possible_moves)  

        print("GOING FOR FOOD") 

    # Choose a random direction from the remaining possible_moves to move in, and then return that move

    move = random.choice(possible_moves)
    print("MOVE")
    print(move)
    return move
    # TODO: Explore new strategies for picking a move that are better than random

def checkbodyincorner(my_body, corners):
  for link in my_body:
    if link in corners:
      return True

  return False
  
def cal_dist(me, food):
  x_distance = abs(me['x']-food['x'])
  y_distance = abs(me['y']-food['y'])

  total_distance = x_distance + y_distance
  return total_distance

def find_closest(choices, coord):
  temp_closest = choices[0]
  temp_min_dist = cal_dist(coord, temp_closest)
  for c in choices:
    dist = cal_dist(coord, c)
    if dist < temp_min_dist:
      temp_min_dist = dist
      temp_closest = c
  return temp_closest

  
def find_closest_food(food, you, other_snakes):

  for c in food:
    food_dists = []
    food_dist = []
    dist = cal_dist(you, c)
    food_dist.append(food)
    food_dist.append(dist)
    food_dists.append(food_dist)
    
  food_dists = sorted(food_dists, key=lambda x: x[1])     
  
  food = []
  for f in food_dists:
    food.append(f[0])
  temp_closest = food[0][0]

  
  for c in food[0]:
    # print(c)
    snake_dists = []
    snake_dist = []
    your_dist = cal_dist(you, c)
    snake_dist.append("you")
    snake_dist.append(your_dist)
    snake_dists.append(snake_dist)
    
    for snake in other_snakes:
      snake_dist = []
      their_dist = cal_dist(snake['head'], c)
      snake_dist.append(snake)
      snake_dist.append(their_dist)
      snake_dists.append(snake_dist)
      
    snake_dists = sorted(snake_dists, key=lambda x: x[1])      
      
    min_dist = snake_dists[0][1]
    # print(min_dist)
    count = 0
    you_min = False
    for dist in snake_dists:
      if dist[0] == "you" and dist[1] == min_dist:
        you_min = True
        
      if dist[1] == min_dist:
        count += 1

      if count == 2:
        break

    if you_min == True and count != 2:
      return c
    
  return temp_closest
  
def _avoid_my_neck(my_body: dict, possible_moves: List[str]) -> List[str]:
    """
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0}]
    possible_moves: List of strings. Moves to pick from.
            e.g. ["up", "down", "left", "right"]

    return: The list of remaining possible_moves, with the 'neck' direction removed
    """
    my_head = my_body[0]  # The first body coordinate is always the head
    my_neck = my_body[1]  # The segment of body right after the head is the 'neck'

    if my_neck["x"] < my_head["x"]:  # my neck is left of my head
        possible_moves.remove("left")
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
        possible_moves.remove("right")
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
        possible_moves.remove("down")
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
        possible_moves.remove("up")

    return possible_moves


def avoid_walls(head_up, head_down, head_left, head_right, board_height, board_width, possible_moves):
  if head_up['y'] > board_height-1:
    possible_moves.remove("up")

  if head_down['y'] < 0:
    possible_moves.remove("down")

  if head_right['x'] > board_width-1:
    possible_moves.remove("right")

  if head_left['x'] < 0:
    possible_moves.remove("left")

  return possible_moves

def avoid_self(my_body, head_up, head_down, head_left, head_right, possible_moves):
  if head_up in my_body and "up" in possible_moves:
    possible_moves.remove("up")

  if head_down in my_body and "down" in possible_moves:
    possible_moves.remove("down")

  if head_right in my_body and "right" in possible_moves:
    possible_moves.remove("right")

  if head_left in my_body and "left" in possible_moves:
    possible_moves.remove("left")

  return possible_moves


# this function doesn't take into consideration moves where the other snake(s)'s head will be in the future, thus risking head to head collisions
def avoid_snakes(head_up, head_down, head_left, head_right, other_snakes, possible_moves):
  for snake in other_snakes:
    snake_body = snake["body"]

    if head_up in snake_body and "up" in possible_moves:
      possible_moves.remove("up")
  
    if head_down in snake_body and "down" in possible_moves:
      possible_moves.remove("down")
  
    if head_right in snake_body and "right" in possible_moves:
      possible_moves.remove("right")
  
    if head_left in snake_body and "left" in possible_moves:
      possible_moves.remove("left")

  return possible_moves


#takes the first food in the array and returns the optimal move(s) for it
def find_food(my_head, head_up, head_down, head_left, head_right, food, other_snakes, possible_moves):
  target = find_closest_food(food, my_head, other_snakes)
  move_dist = []

  for move in possible_moves:
    new_move = []

    if move == "up":
      dist = cal_dist(head_up, target)

      
    elif move == "down":
      dist = cal_dist(head_down, target)

        
    elif move == "left":
      dist = cal_dist(head_left, target)

    else:
      dist = cal_dist(head_right, target)

    new_move.append(move)
    new_move.append(dist)
    move_dist.append(new_move)

  move_dist = sorted(move_dist, key=lambda x: x[1])
  shortest_dist = move_dist[0][1]

  possible_moves = []
  for dist in move_dist:
    if dist[1] == shortest_dist:
      possible_moves.append(dist[0])

    else:
      break

  return possible_moves

def find_food1(my_head, head_up, head_down, head_left, head_right, food, other_snakes, possible_moves):
  target = find_closest(food, my_head)
  move_dist = []

  for move in possible_moves:
    new_move = []

    if move == "up":
      dist = cal_dist(head_up, target)

      
    elif move == "down":
      dist = cal_dist(head_down, target)

        
    elif move == "left":
      dist = cal_dist(head_left, target)

    else:
      dist = cal_dist(head_right, target)

    new_move.append(move)
    new_move.append(dist)
    move_dist.append(new_move)

  move_dist = sorted(move_dist, key=lambda x: x[1])
  shortest_dist = move_dist[0][1]

  possible_moves = []
  for dist in move_dist:
    if dist[1] == shortest_dist:
      possible_moves.append(dist[0])

    else:
      break

  return possible_moves

def chase_tail(my_head, head_up, head_down, head_left, head_right, my_tail, food, possible_moves):
  target = my_tail
  move_dist = []

  for move in possible_moves:
    new_move = []

    if move == "up":
      dist = cal_dist(head_up, target)

      
    elif move == "down":
      dist = cal_dist(head_down, target)

        
    elif move == "left":
      dist = cal_dist(head_left, target)

    else:
      dist = cal_dist(head_right, target)

    new_move.append(move)
    new_move.append(dist)
    move_dist.append(new_move)

  move_dist = sorted(move_dist, key=lambda x: x[1])
  shortest_dist = move_dist[0][1]

  possible_moves = []
  for dist in move_dist:
    if dist[1] == shortest_dist:
      possible_moves.append(dist[0])

    else:
      break

  if my_head in food:
    if head_up == target:
      possible_moves = ['up']
  
    elif head_down == target:
      possible_moves = ['down']    
  
    elif head_left == target:
      possible_moves = ['left']  
  
    elif head_right == target:
      possible_moves = ['right']  
  return possible_moves

def check_move_safe(my_snake, my_head, my_body, other_snakes, possible_moves):
  # other_snakes.append(body)
  head_up = {"x":my_head["x"], "y":my_head["y"]+1}
  head_down = {"x":my_head["x"], "y":my_head["y"]-1}
  head_left = {"x":my_head["x"]-1, "y":my_head["y"]}
  head_right = {"x":my_head["x"]+1, "y":my_head["y"]}

  count = 0

  for s in other_snakes:
    my_shead = s['head']
    future_shead = []
    shead_up = {"x":my_shead["x"], "y":my_shead["y"]+1}
    shead_down = {"x":my_shead["x"], "y":my_shead["y"]-1}
    shead_left = {"x":my_shead["x"]-1, "y":my_shead["y"]}
    shead_right = {"x":my_shead["x"]+1, "y":my_shead["y"]}

    future_shead.append(shead_up)
    future_shead.append(shead_down)    
    future_shead.append(shead_left)    
    future_shead.append(shead_right)  



    if s['length'] >= my_snake['length'] and len(possible_moves) > 1:
      if "up" in possible_moves and head_up in future_shead:
        possible_moves.remove("up")
        # print("UP")
  
      elif "down" in possible_moves and head_down in future_shead:
        possible_moves.remove("down")
        # print("DOWN")
  
      elif "left" in possible_moves and head_left in future_shead:
        # print("LEFT")
        possible_moves.remove("left")
  
      elif "right" in possible_moves and head_right in future_shead:
        # print("RIGHT")
        possible_moves.remove("right")
  return possible_moves

# make a boolean func that checks whether a move is safe
# checks future heads for the future move, if 3 heads are occupied don't go

def check_move_safe2(my_snake, my_head, my_body, other_snakes, board_height, board_width, possible_moves):
  head_up = {"x":my_head["x"], "y":my_head["y"]+1}
  head_down = {"x":my_head["x"], "y":my_head["y"]-1}
  head_left = {"x":my_head["x"]-1, "y":my_head["y"]}
  head_right = {"x":my_head["x"]+1, "y":my_head["y"]}
  
  for move in possible_moves:
    if move == "up":
      f_move = head_up

    elif move == "down":
      f_move = head_down

    elif move == "left":
      f_move = head_left

    elif move == "right":
      f_move = head_right

    f_up = {"x":f_move["x"], "y":f_move["y"]+1}
    f_down = {"x":f_move["x"], "y":f_move["y"]-1}
    f_left = {"x":f_move["x"]-1, "y":f_move["y"]}
    f_right = {"x":f_move["x"]+1, "y":f_move["y"]}

  fpossible_moves = ['left', 'right', 'up', 'down']
  fpossible_moves = _avoid_my_neck(my_body, fpossible_moves)
  fpossible_moves = avoid_walls(f_up, f_down, f_left, f_right, board_height, board_width, fpossible_moves)
  fpossible_moves = avoid_self(my_body, f_up, f_down, f_left, f_right, fpossible_moves)
  fpossible_moves = avoid_snakes(f_up, f_down, f_left, f_right, other_snakes, fpossible_moves)

  if len(fpossible_moves) == 0 and len(possible_moves) > 1:
    possible_moves.remove(move)

  return possible_moves