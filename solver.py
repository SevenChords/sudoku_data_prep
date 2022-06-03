import os, os.path
import numpy as np
import re
import multiprocessing

def read(_line):
  filename = 'input'
  puzzle_string = ''
  with open(filename, 'r') as puzzle_collection:
    for i, line in enumerate(puzzle_collection):
      if(i == _line):
        puzzle_string = line.strip()
      elif i > _line:
        break
  puzzle_string = re.sub('\.', '0', puzzle_string)
  puzzle_array = np.zeros((9, 9), np.byte)
  i = 0
  for r in range(9):
    for c in range(9):
      puzzle_array[r][c] = puzzle_string[i]
      i = i + 1
  return puzzle_array

def write(_puzzle, _solution, _worker_index):
  filename = 'sudoku_data'
  DIR = 'worker_' + str(_worker_index)
  if(not(os.path.exists(DIR))):
    os.makedirs(DIR)
  with open(os.path.join(DIR, filename), 'ab') as puzzle_data:
    puzzle_data.write(bytearray(_puzzle.flatten()))
    puzzle_data.write(bytearray(_solution.flatten()))

def errors_on_board(_puzzle):
  check_groups = np.zeros((27, 9))
  for i in range(9):
    for j in range(9):
      check_groups[i][j] = _puzzle[i][j]
      check_groups[i + 9][j] = _puzzle[j][i]
  for i in range(3):
    for j in range(3):
      for k in range(3):
        for l in range(3):
          check_groups[i * 3 + j][k * 3 + l] = _puzzle[i * 3 + k][j * 3 + l]
  for group in check_groups:
    empty_index = 10
    for i in range(9):
      if(group[i] == 0):
        group[i] = empty_index
        empty_index = empty_index + 1
    if(len(group) != len(set(group))):
      return True
  return False

def check_placement(_puzzle, _x, _y, _n):
  possible = True
  for i in range(9):
    if(_n == _puzzle[i][_y]):
      possible = False
    if(_n == _puzzle[_x][i]):
      possible = False
  square_x = int(_x/3)
  square_y = int(_y/3)
  for i in range(3):
    for j in range(3):
      target_x = (square_x * 3) + i
      target_y = (square_y * 3) + j
      target = _puzzle[target_x][target_y]
      if(_n == target):
        possible = False
  return possible

def get_possible_numbers(_puzzle, _number_stack):
  possibilities = [[[] for j in range(9)] for i in range(9)]
  for x in range(9):
    for y in range(9):
      if(_puzzle[x][y] == 0):
        for n in range(1,10):
          if(check_placement(_puzzle, x, y, n) and not(check_stack(_number_stack, x, y, n))):
            possibilities[x][y].append(n)
  return possibilities

def place_obvious(_puzzle, _possible_numbers):
  for x in range(9):
    for y in range(9):
      if(len(_possible_numbers[x][y]) == 1):
        _puzzle[x][y] = _possible_numbers[x][y][0]
  return 0

def check_stack(_stack, _x, _y, _n):
  for element in _stack:
    if(element[0] == _x):
      if(element[1] == _y):
        if(element[2] == _n):
          return True
  return False

def get_x_y_attempt(_possibilities):
  max_possibilities = 10
  x = 9
  y = 9
  for i in range(9):
    for j in range(9):
      if(len(_possibilities[i][j]) < max_possibilities and _possibilities[i][j]):
        max_possibilities = len(_possibilities[i][j])
        x = i
        y = j
        if(max_possibilities == 2):
          return x, y
  return x, y

def get_sum(_possibilities):
  total = 0
  for x in range(9):
    for y in range(9):
      total = total + len(_possibilities[x][y])
  return total

def solve(_puzzle):
  guesses = 0
  puzzle = _puzzle.copy()
  last_state = puzzle.copy()
  backup_stack = []
  number_stack = []
  while(0 in puzzle):
    possible_numbers = get_possible_numbers(puzzle, number_stack)
    place_obvious(puzzle, possible_numbers)
    if(np.array_equal(puzzle, last_state)
       and get_sum(possible_numbers) >= 2
       and not(errors_on_board(puzzle))):
      solve_failed = True
      attempt_go = False
      x, y = get_x_y_attempt(possible_numbers)
      for n in range(1,10):
        if(not(check_stack(number_stack, x, y, n))
           and not(attempt_go)
           and n in possible_numbers[x][y]):
          number_stack.append([x, y, n])
          backup_stack.append([puzzle.copy(), number_stack.copy()])
          puzzle[x][y] = n
          solve_failed = False
          attempt_go = True
          guesses = guesses + 1
          #print(guesses)
      if(solve_failed):
        puzzle = backup_stack[-1][0]
        number_stack.clear()
        number_stack = backup_stack[-1][1]
        backup_stack.pop()
    elif(errors_on_board(puzzle) or (get_sum(possible_numbers) == 0 and 0 in puzzle)):
      puzzle = backup_stack[-1][0]
      number_stack.clear()
      number_stack = backup_stack[-1][1]
      backup_stack.pop()
    last_state = puzzle.copy()
  return puzzle

def worker(_work_queue, _done_queue):
  while(True):
    job = _work_queue.get(True)
    sleep(0.1*job[0])
    index = job[0]
    while(index <= 49157):
      write(read(index), solve(read(index)), job[0])
      index = index + 8
    _done_queue.put(job[0], False)

def work():
  done_queue = multiprocessing.Queue(8)
  work_queue = multiprocessing.Queue(8)
  instances = []
  for i in range(8):
    instance = multiprocessing.Process(target=worker, args=(work_queue, done_queue))
    instance.daemon = True
    instance.start()
    instances.append(instance)
  for i in range(8):
    job = [i]
    work_queue.put(job, False)
  done_counter = 0
  while(done_counter < 8):
    done_index = done_queue.get(True)
    print('worker ', done_index, ' is done.')
    done_counter = done_counter = 1
  for instance in instances:
    instance.terminate()
  return 0
if(__name__ == '__main__'):
  multiprocessing.freeze_support()
  work()
  print('all done.')

