import numpy as np
from random import choice, sample, randint
import matplotlib.pyplot as pyplot
from typing import List, Dict, Union

class SimpleMaze():

	BORDER: int = 1
	KNOT: int = 2
	PATH: int = 3
	HIDE: int = 0
 
	WAY_OUT: int = 4
	BAD_WAY: int = 5

	PLAYER = 8
	EXIT = 30
	
	__slots__ = ["width", "height", "way", "walk", "maze"]
	
	
	def __init__(self, width=15, height=15):
		self.width = width
		self.height = height
		self.way: list() = [] # стек точек при постройке лабиринта
		self.walk: list() = [] # стек точек при поиске пути
		
		self.maze = self.create_maze() # готовый лабиринт
			
	# заготовка лабиринта
	def create_grid(self) -> np.ndarray:
		grid = np.full((self.height, self.width), self.BORDER, dtype="int")
		
		# сетка из точек, которые будут опорными при построении лабиринта
		for idx_row, row in enumerate(grid):
			for idx_col, col in enumerate(row):
				if idx_col % 2 != 0 and idx_row % 2 != 0:
					grid[idx_row][idx_col] = self.KNOT

		return grid
		
		
	# выбирает, куда можно двинуться от данной точки
	# obj - значение, по которому можно прокладывать путь. 
	# BORDER - при создании лабиринта, как бы разрушаются стены для создания пути
	# PATH - при поиске пути, то есть пространство между стенами, по которому можно "идти"
	def choose_way(self, maze=None, maze_creation=True, step=2, player_row=-1, player_col=-1) -> list():
		if type(maze) != np.ndarray:
			maze = self.maze
		
		dirs: List[str] = []
				
		if maze_creation: 
			obj = [self.BORDER]
			row, col = self.way[-1]
		else:
			obj = [self.PATH, self.WAY_OUT]
			# для поиска доступных направлений игрока
			if player_row >= 0 and player_col >= 0:
				row, col = player_row, player_col
			else:
				row, col = self.walk[-1]
			
		
		if col+step < self.width and maze[row, col+1] in obj:
			if maze_creation and maze[row, col+2] == self.KNOT:
				dirs.append("right")
			elif maze_creation == False:
				dirs.append("right")
		
		if col-step >= 0 and maze[row, col-1] in obj:
			if maze_creation and maze[row, col-2] == self.KNOT:
				dirs.append("left")
			elif maze_creation == False:
				dirs.append("left")
		
		if row+step < self.height and maze[row+1, col] in obj:
			if maze_creation and maze[row+2, col] == self.KNOT:
				dirs.append("down")
			elif maze_creation == False:
				dirs.append("down")
		
		if row-step >= 0 and maze[row-1, col] in obj:
			if maze_creation and maze[row-2, col] == self.KNOT:
				dirs.append("up")
			elif maze_creation == False:
				dirs.append("up")
		
		return dirs
		
	# добавляет следующую точку в стек, и возвращает координаты "разрушенной" точки стены
	# так же используется для перемещения игрока
	def carve(self, direction, mode="none", step=2, player_row=-1, player_col=-1) -> (int, int):
		
		if mode == "creation": row, col = self.way[-1]
		if mode == "search": row, col = self.walk[-1]
		
		if player_row >= 0 and player_col >= 0:
			row, col = player_row, player_col
		
		if direction == "up":
			if mode == "creation": self.way.append((row-step, col))	
			if mode == "search": self.walk.append((row-step, col))	
			row = row - 1
		elif direction == "down":
			if mode == "creation": self.way.append((row+step, col))
			if mode == "search": self.walk.append((row+step, col))
			row = row + 1
		elif direction == "right":
			if mode == "creation": self.way.append((row, col+step))
			if mode == "search": self.walk.append((row, col+step))
			col = col + 1
		elif direction == "left":
			if mode == "creation": self.way.append((row, col-step))
			if mode == "search": self.walk.append((row, col-step))
			col -= 1
		
		return row, col	


	# основная функция при постройке лабиринта
	def create_maze(self):
		# заготовка
		maze = self.create_grid()

		# начальная точка
		row, col = choice(np.argwhere(maze==self.KNOT))

		# стек посещённых точек при постройке лабиринта
		self.way.append((row, col))
		
		# пока будут доступные точки, куда можно проложить путь
		while True:
			if not self.way:
				break
			directions = self.choose_way(maze = maze)
			if not directions:
				self.way.pop(-1)
				continue
			new_y, new_x = self.carve(choice(directions), mode="creation")
			# покрасим последнюю точку в стеке в цвет прохода
			maze[self.way[-1][0], self.way[-1][1]] = self.PATH
			# покрасим "разрушенную" стену в цвет прохода
			maze[new_y, new_x] = self.PATH
		
		return maze
		
		
	# решить лабиринт	
	def find_way(self, start_y, start_x, returned=False): # будет ли возвращать массив-лабиринт с найденным путём
		row: int = start_y
		col: int = start_x
		maze = self.maze.copy()
		self.walk.append((row, col))# стек для поиска пути
		maze[row, col] = self.WAY_OUT
		
		while True:
			if not self.walk or (self.walk[-1][0] == self.height-2 and self.walk[-1][1] == self.width-2):
				break
			
			directions = self.choose_way(maze, maze_creation=False, step=1)
			if not directions:
				maze[self.walk[-1][0], self.walk[-1][1]] = self.BAD_WAY
				self.walk.pop(-1)
				continue
			
			next_row, next_col = self.carve(choice(directions), mode = "search", step=1)
			maze[next_row, next_col] = self.WAY_OUT
			#self.walk.append((next_row, next_col)) # добавление происходит в carve в режиме search
		
		if returned:
			return maze

		
	# вывести массив numpy(лабиринт) в виде картинки, используя matplotlib	
	def print_maze(self, mode="original", interpolation="nearest", size_x=5, size_y=5):	
		'''
		interpolation
	   [None, 'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
	   'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
	   'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']
		'''
		if mode == "way":
			maze = self.find_way(1, 1, True)
		else:
			maze = self.maze

		pyplot.figure(figsize=(size_x, size_y))
		pyplot.imshow(maze, cmap=pyplot.cm.gist_ncar, interpolation=interpolation)
		pyplot.xticks([]), pyplot.yticks([])
		pyplot.show()
	
	
	# как вариант, сделать чтобы куски карты открывались постепенно
	# текущая релизация - отображает кусок карты определённого размера вокруг начальной точки
	# TODO сделать возможность отображать пройденный маршрут
	def maze_to_string(self, maze, row_start=1, col_start=1, row_end=2, col_end=2):
		if type(maze) != np.ndarray:
			maze = self.maze
	
		maze_table = f"{self.BORDER}{self.PATH}{self.PLAYER}{self.HIDE}"
		#maze_string = "\u2588\u2591\u2727"
		maze_string = "\u2591\u2588\u25C9\u25E6"
		table = str.maketrans(maze_table, maze_string)

		part = maze[min(row_start, row_end)-1:max(row_start, row_end)+2, min(col_start, col_end)-1:max(col_start, col_end)+2]
		
		text = ""
		for row in part:
			for col in row:
				text += str(col).translate(table) + str(col).translate(table)
			text += '\n'
	
		return text
		
if __name__ == "__main__":
	maze = SimpleMaze(21, 21)
	# original - лабиринт без найденного пути, way - копия лабиринта с найдённым путём
	# print(maze.maze)
	#maze.print_maze(mode="way", interpolation="quadric", size_x=5, size_y=5)
	print(maze.maze_to_string(None,1,1,20,20))
	
