import os, os.path
import numpy as np
import re

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
  for r in range(8):
    for c in range(8):
      puzzle_array[r][c] = puzzle_string[i]
      i = i + 1
  return puzzle_array

def write(_puzzle, _solution):
  filename = 'sudoku_data'
  with open(filename, 'ab') as puzzle_data:
    puzzle_data.write(bytearray(_puzzle.flatten()))
    puzzle_data.write(bytearray(_solution.flatten()))

def solve(_puzzle):
  puzzle = _puzzle.copy()
  while(0 in puzzle):
    
