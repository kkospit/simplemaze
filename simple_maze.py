from numpy import full, argwhere, ndarray
from random import choice, sample, randint
# import matplotlib.pyplot as pyplot
from typing import List, Dict, Union


class SimpleMaze():
		
	__slots__ = ["width", "height", "way", "walk", "maze", "player_pos", "objects"]
	
	def __init__(self, height=15, width=15):
		if width < 5: width = 5
		if height < 5: height = 5
		# нам нужны нечётные значения ширины и высоты, поэтому:
		if width % 2 == 0: width += 1
		if height % 2 == 0: height += 1
		
		self.width = width
		self.height = height
		
		self.way: list() = [] # стек точек при постройке лабиринта
		self.walk: list() = [] # стек точек при поиске пути
		
		self.objects = {"border":1, "knot":2, "path":3, "hide":0, 
						"way_out": 4, "bad_way":5, "player":8,
						"landmark":9}

		self.maze = self.create_maze() # готовый лабиринт
		# буду сюда записывать координаты игрока, чтобы не передавать кучу параметров
		self.player_pos = (1,1)
		
				
	# заготовка лабиринта
	def create_grid(self) -> ndarray:
		grid = full((self.height, self.width), self.objects["border"], dtype="int")
		
		# сетка из точек, которые будут опорными при построении лабиринта
		for idx_row, row in enumerate(grid):
			for idx_col, col in enumerate(row):
				if idx_col % 2 != 0 and idx_row % 2 != 0:
					grid[idx_row][idx_col] = self.objects["knot"]

		return grid
		
		
	# выбирает, куда можно двинуться от данной точки
	# obj - значение, по которому можно прокладывать путь. 
	# BORDER - при создании лабиринта, как бы разрушаются стены для создания пути
	# PATH - при поиске пути, то есть пространство между стенами, по которому можно "идти"
	def choose_way(self, maze=None, mode="creation", step=2) -> list():
		if type(maze) != ndarray:
			maze = self.maze

		dirs: List[str] = []
				
		if mode == "creation": 
			obj = (self.objects["border"],)
			row, col = self.way[-1]
		elif mode == "default":
			obj = (self.objects["path"], self.objects["way_out"]) 
			row, col = self.player_pos
		elif mode == "search":
			obj = (self.objects["path"], self.objects["player"]) 
			row, col = self.walk[-1]
		else:
			print('Выберите режим: "default", "creation", "search"')
			
		# col+step(=2) при создании - попадание на KNOT
		# col+1 при создании - попадание на BORDER
		if col+step < self.width and maze[row, col+1] in obj:
			if mode == "creation" and maze[row, col+2] == self.objects["knot"]:
				dirs.append("right")
			#elif maze_creation == False:
			elif mode != "creation":
				dirs.append("right")
		
		if col-step >= 0 and maze[row, col-1] in obj:
			if  mode == "creation" and maze[row, col-2] == self.objects["knot"]:
				dirs.append("left")
			elif mode != "creation":
				dirs.append("left")
		
		if row+step < self.height and maze[row+1, col] in obj:
			if  mode == "creation" and maze[row+2, col] == self.objects["knot"]:
				dirs.append("down")
			elif mode != "creation":
				dirs.append("down")
		
		if row-step >= 0 and maze[row-1, col] in obj:
			if  mode == "creation" and maze[row-2, col] == self.objects["knot"]:
				dirs.append("up")
			elif mode != "creation":
				dirs.append("up")
		return dirs
		
	# добавляет следующую точку в стек, и возвращает координаты "разрушенной" точки стены
	# так же используется для перемещения игрока
	def carve(self, direction, mode="default", step=2) -> (int, int):
		
		if mode == "creation": row, col = self.way[-1]
		elif mode == "search": row, col = self.walk[-1]
		elif mode == "default": row, col = self.player_pos
		
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
		row, col = choice(argwhere(maze==self.objects["knot"]))
		# стек посещённых точек при постройке лабиринта
		self.way.append((row, col))
		
		# пока будут доступные точки, куда можно проложить путь
		while True:
			if not self.way:
				break
			directions = self.choose_way(maze = maze, mode="creation")
			if not directions:
				self.way.pop(-1)
				continue
			new_y, new_x = self.carve(choice(directions), mode="creation")
			# покрасим последнюю точку в стеке в цвет прохода
			maze[self.way[-1][0], self.way[-1][1]] = self.objects["path"]
			# покрасим "разрушенную" стену в цвет прохода
			maze[new_y, new_x] = self.objects["path"]
		
		return maze
		
		
	# решить лабиринт	
	def find_way(self, start_y=1, start_x=1, returned=False): # будет ли возвращать массив-лабиринт с найденным путём
		row: int = start_y
		col: int = start_x
		maze = self.maze.copy()
		
		self.walk.clear()		
		self.walk.append((row, col))# стек для поиска пути
		maze[row, col] = self.objects["way_out"]
		
		while True:
			if not self.walk or (self.walk[-1][0] == self.height-2 and self.walk[-1][1] == self.width-2):
				break
			
			directions = self.choose_way(maze, mode="search", step=1)
			if not directions:
				maze[self.walk[-1][0], self.walk[-1][1]] = self.objects["bad_way"]
				self.walk.pop(-1)
				continue
			
			next_row, next_col = self.carve(choice(directions), mode = "search", step=1)
			maze[next_row, next_col] = self.objects["way_out"]
			#self.walk.append((next_row, next_col)) # добавление происходит в carve в режиме search
		
		if returned:
			return maze
	
	
	# можно сделать несколько комнат, просто заменим определённую область на PATH
	def make_rooms(self, nums=1):
		for _ in range(nums):
			start_row = randint(1,self.height-4)
			start_col = randint(1,self.width-4)
			self.maze[start_row:start_row+3, start_col:start_col+3] = full((3,3), self.objects["path"])
		
	'''	
	# вывести массив numpy(лабиринт) в виде картинки, используя matplotlib	
	def print_maze(self, mode="original", interpolation="nearest", size_x=5, size_y=5):	
		
		interpolation = [None, 'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
	   'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
	   'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']
		
		if mode == "way":
			maze = self.find_way(1, 1, True)
		else:
			maze = self.maze

		pyplot.figure(figsize=(size_x, size_y))
		pyplot.imshow(maze, cmap=pyplot.cm.gist_ncar, interpolation=interpolation)
		pyplot.xticks([]), pyplot.yticks([])
		pyplot.show()
	'''
	
	# как вариант, сделать чтобы куски карты открывались постепенно
	# текущая релизация - отображает кусок карты определённого размера вокруг начальной точки
	# TODO сделать возможность отображать пройденный маршрут
	def maze_to_string(self, maze, row_start=1, col_start=1, row_end=2, col_end=2):
		if type(maze) != ndarray:
			maze = self.maze
		
		if row_start > row_end:
			row_end, row_start = row_start, row_end
		if col_start > col_end:
			col_end, col_start = col_start, col_end
			
		maze_strings = ("\u2591", "\u2588", 
						"\u25C9", "\u25E6", 
						"\u272F", "!", 
						"*")
		maze_numbers = (self.objects["border"], self.objects["path"], 
						self.objects["player"], self.objects["hide"], 
						self.objects["way_out"], self.objects["bad_way"], 
						self.objects["landmark"])
						
		part = maze[min(row_start, row_end)-1:max(row_start, row_end)+2, min(col_start, col_end)-1:max(col_start, col_end)+2]
		
		text = ""
		for row in part:
			for col in row:
				if col in maze_numbers:
					text += maze_strings[maze_numbers.index(col)]*2
			text += '\n'
		
		return text

		
if __name__ == "__main__":
	maze = SimpleMaze(40, 40)
	print(maze.maze_to_string(maze.find_way(returned=True),1,1,47,41))
	print(maze.maze_to_string(maze.maze,1,1,40,40))
