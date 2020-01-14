from random import choice, sample, randint
from typing import List, Dict
import numpy as np
from simple_maze import SimpleMaze

class MazeGame():
	
	
	__slots__ = ["mazeclass", "row", "col", "face", "markers", "chalk", "last_steps", 
				 "maze", "map_parts", "sheets", "has_sheet", "current_sheet", 
				 "sheet_limit", "use_sheet", "event_text", "map_points",
				 "chalk_points", "sheets_points"]
	
	def __init__(self, height, width):
		self.mazeclass = SimpleMaze(height, width)
		self.row = 1
		self.col = 1
		
		self.maze = self.mazeclass.maze
		self.maze[self.row, self.col] = self.mazeclass.PLAYER
		# разворачиваем игрока лицом в коридор
		possible = self.mazeclass.choose_way(maze_creation=False, step=1, player_row=self.row, player_col=self.col)
		self.face = choice(possible) # face - куда смотрит игрок относительно лабиринта, начало координат внизу
		
		# на стенах лабиринта можно оставлять пометки в виде стрелок 
		self.markers = {} # {(1, 1): {"up":"", "down":"", "left":"", "right":""}} # значения - стрелки из юникода
		self.chalk = 100
		
		# будет хранить последные пройденные координаты
		self.last_steps = [(self.row, self.col)]
		
		# бумага для черчения пути
		self.sheets = [] # попробуем листы разделять / #{"sheet_1":[], "sheet_2":[], "sheet_3":[], "sheet_4":[], "sheet_5":[], "sheet_6":[]}
		self.has_sheet = 2 
		self.sheet_limit = 30
		self.current_sheet = []
		self.use_sheet = False
		
		#  для отрисовки частей карты лабиринта на общей карте
		self.map_parts = []
		#for _ in range(10):
		#	self.map_parts.append(self.init_map_parts())
			
		self.event_text = {"arrows":"", "copybook":"", "sheet":"", "chalk":"", 
						   "map_part":"", "find_chalk":"", "find_sheet":""}	
		
		# раскидаем места с частями карты
		free_points = tuple((map(tuple, np.argwhere(self.maze==self.mazeclass.PATH).tolist())))
		self.map_points = sample(free_points, int(max(self.mazeclass.height, self.mazeclass.width)/2))		
		self.chalk_points = sample(free_points, int(max(self.mazeclass.height, self.mazeclass.width)/2))		
		self.sheets_points = sample(free_points, int(max(self.mazeclass.height, self.mazeclass.width)/4))		
		
	# переводит направления в лабиринте в относительные направления для игрока
	def relative_directions(self):
		# доступные пути
		maze = self.mazeclass.maze
		directions = self.mazeclass.choose_way(maze_creation=False, step=1, player_row=self.row, player_col=self.col)
		# все направления
		all_directions: Dict[str, str] = {} # направление относительно игрока: направление в лабиринте
		
		for idx, d in enumerate(["up", "down", "left", "right"]):
			if self.face == "down":
				if d == "left": all_directions["right"] = d
				if d == "right": all_directions["left"] = d
				if d == "up": all_directions["back"] = d
				if d == "down": all_directions["forward"] = d
			elif self.face == "up":
				if d == "up": all_directions["forward"] = d
				if d == "down": all_directions["back"] = d
				if d == "left": all_directions["left"] = d
				if d == "right": all_directions["right"] = d
			elif self.face == "left":
				if d == "left": all_directions["forward"] = d
				if d == "right": all_directions["back"] = d
				if d == "up": all_directions["right"] = d
				if d == "down": all_directions["left"] = d
			elif self.face == "right":
				if d == "left": all_directions["back"] = d
				if d == "right": all_directions["forward"] = d
				if d == "up": all_directions["left"] = d
				if d == "down": all_directions["right"] = d
		
		possible_directions = {k:v for k, v in all_directions.items() if v in directions}
		return all_directions, possible_directions

		
	# описание доступных с этого места действий
	def place_buttons(self, all_directions, possible_directions) -> dict:
		# проверяем _все_ направления, чтобы узнать, что вокруг игрока	
		place: Dict(str, tuple) = {"forward": "", "back": "", "left": "", "right": ""}
		obj: str = ""
		for relative_d, global_d in all_directions.items(): 

			row, col = self.mazeclass.carve(direction=global_d, step=1, player_row=self.row, player_col=self.col)
			
			if self.mazeclass.maze[row, col] == self.mazeclass.BORDER: obj = "стена"
			if self.mazeclass.maze[row, col] == self.mazeclass.PATH: obj = "коридор"
			if self.mazeclass.maze[row, col] == self.mazeclass.EXIT: obj = "выход"

			if relative_d == "forward":
				place[relative_d] = (f"Впереди: {obj}", choice(("Идти", "Пойти вперёд", "Двигаться дальше")), obj)
			elif relative_d == "back":
				place[relative_d] = (f"Позади: {obj}", choice(("Повернуть назад", "Двинуться в обратном направлении")), obj)
			elif relative_d == "left":
				place[relative_d] = (f"Слева: {obj}", choice(("Повернуть налево", "Свернуть налево")), obj)
			elif relative_d == "right":
				place[relative_d] = (f"Справа: {obj}", choice(("Повернуть направо", "Свернуть направо")), obj)
		
		return place
	
	
	# нарисовать/зачеркнуть стрелку по направлению движения
	def mark(self, key):
		if key == "up":
			arrow = ("\u25B2", "\u25B3") # не зачёркнута/зачёркнута
		elif key == "down":
			arrow = ("\u25BC", "\u25BD")
		elif key == "left":
			arrow = ("\u25C0", "\u25C1")
		elif key == "right":
			arrow = ("\u25B6", "\u25B7")
		
		if (self.row, self.col) not in self.markers:
			self.markers[(self.row, self.col)] = {"up":"", "down":"", "left":"", "right":""}
		self.markers[(self.row, self.col)][key] = arrow[1] if self.markers[(self.row, self.col)][key] else arrow[0]
		self.chalk -= 3
		
	# описание событий
	def get_event(self, all_directions):
		# если нашли стрелку
		if self.markers.get((self.row, self.col)):
			arrows = "".join(self.markers[(self.row, self.col)].values())	
			self.event_text["arrows"] = "Отметки: " + arrows + "\n"
		else:	
			self.event_text["arrows"] = ""
		
		if self.has_sheet > 0:
			self.event_text["copybook"] = f"Листов для записей: {self.has_sheet}\n"
			if self.use_sheet:
				self.event_text["copybook"] += f"Вы зарисовываете маршрут.\n"
		else:
			self.event_text["copybook"] = f"У вас закончились листы для записей.\n"
			self.use_sheet = False
		
		
		# предупредим, что место на листе скоро закончится
		if self.has_sheet > 0:
			sheet_lim = self.sheet_limit - len(self.current_sheet)
			if sheet_lim >= 25:
				self.event_text["sheet"] = "На текущем листе полно места.\n"
			elif sheet_lim == 20:
				self.event_text["sheet"] = "Примерно треть листа занята чертежом.\n"
			elif sheet_lim == 15:
				self.event_text["sheet"] = "Осталась половина листа.\n"
			elif sheet_lim == 10:
				self.event_text["sheet"] = "Осталась треть листа.\n"
			elif sheet_lim == 5:
				self.event_text["sheet"] = "Место на листе скоро закончится.\n"
			#elif sheet_lim == 0:
			#	self.event_text["sheet"] = "Лист закончился!.\n"
		else:
			self.event_text["sheet"] = ""
		
		if self.chalk > 70:
			self.event_text["chalk"] = "У вас есть мел.\n"
		elif 0 < self.chalk < 20:
			self.event_text["chalk"] = "Мела почти не осталось...\n"
		elif self.chalk == 0:
			self.event_text["chalk"] = "у вас нет мела.\n"
			
		
		if (self.row, self.col) in self.map_points:
			self.map_parts.append(self.init_map_parts())
			self.map_points.pop(self.map_points.index((self.row, self.col)))
			self.event_text["map_part"] = "***Вы нашли часть карты лабиринта!***\n"
		else:
			self.event_text["map_part"] = ""	
		
		if (self.row, self.col) in self.chalk_points:
			self.chalk += randint(20, 60)
			self.event_text["find_chalk"] = "***Вы нашли часть кусочек мела.***\n"
			self.chalk_points.pop(self.chalk_points.index((self.row, self.col)))
		else:
			self.event_text["find_chalk"] = ""	
		
		if (self.row, self.col) in self.sheets_points:
			self.has_sheet += 1
			self.event_text["find_sheet"] = "***Вы нашли чистый лист бумаги!***\n"
			self.sheets_points.pop(self.sheets_points.index((self.row, self.col)))
		else:
			self.event_text["find_sheet"] = ""	
		
		return "".join(self.event_text.values())


	# компас для интерфейса urwid
	def draw_compass(self):
		compass = "\nСогласно компасу, вы смотрите на "
		if self.face == "up":
			#north, south, east, west  = "\n\u22CF", "\n", "  ", "  "
			#compass += "⍏"
			compass += "север"
		elif self.face == "down":
			#south, north, east, west  = "\u22CE\n", "\n", "  ", "  "
			#compass += "⍖"
			compass += "юг"
		elif self.face == "left":
			#south, north, east, west  = "\n", "\n", "  ", " \u227A"
			#compass += "⍅"
			compass += "запад"
		elif self.face == "right":
			#south, north, east, west  = "\n", "\n", " \u227B", "  "
			#compass += "⍆"
			compass += "восток"
			
		# compass = f"N{north}\n\u2503\nW{west}\u2501\u2501\u2501\u2501\u2503\u2501\u2501\u2501\u2501{east}E\n\u2503\n{south}S" # big
		# compass = f"N{north}\n\u2503\nW{west}\u2501\u2501\u2503\u2501\u2501{east}E\n\u2503\n{south}S" # small
		return compass
	
	
	def init_map_parts(self) -> tuple():
		rand_row = randint(0, self.mazeclass.height-5)
		rand_col = randint(0, self.mazeclass.width-5)
		return (rand_row, # start row
				rand_col, # start col
				rand_row+choice((5,10)), # end row
				rand_col+choice((5,10))) # end col
	
	
	# покажем кусочки карты
	def show_part_of_map(self, mode="part"): # или по точкам - point
		modes = ("part", "minimap", "copybook")
		if mode in modes:
			# заготовка
			zeros = np.zeros((self.mazeclass.height, self.mazeclass.width), dtype="int")
			if mode == "part":
				# для примера, надо заготовить части при инициализации, 
				# потом рандомно добавлять в список с координатами
				# перенесли на заготовку нужный кусок
				for part in self.map_parts:
					zeros[part[0]:part[2], part[1]:part[3]] = self.maze[part[0]:part[2], part[1]:part[3]]
			
			elif mode in modes[1:]:	
				if mode == "minimap":			
					rows = set([point[0] for point in self.last_steps])
					cols = set([point[1] for point in self.last_steps])
					# скопируем точки из списка посещённых
					for r, c in self.last_steps:
						zeros[r-1:r+2, c-1:c+2] = self.maze[r-1:r+2, c-1:c+2]
					# обрежем пустое место в заготовке
					zeros = zeros[min(rows)-1:max(rows)+2, min(cols)-1:max(cols)+2]
					# положение игрока в урезанном массиве
					center = np.argwhere(zeros == self.mazeclass.PLAYER) 
					temp = np.zeros((15,15), dtype="int")
					limit = temp.shape[0]-1
					#'''
					# это позволит отметке игрока находится в центре миникарты
					# полная жесть, но пока мои полномочия всё...
					for idx_r, r in enumerate(zeros):
						for idx_c, c in enumerate(r):
							temp_row_start = 7-center[0][0]+idx_r 
							temp_col_start = 7-center[0][1]+idx_c
							if temp_row_start < 0: temp_row_start = 0
							if temp_row_start > limit: temp_row_start = limit
							if temp_col_start < 0: temp_col_start = 0
							if temp_col_start > limit: temp_col_start = limit
							temp[temp_row_start, temp_col_start] = c
					#'''
					zeros = temp
				elif mode == "copybook": 
				
					copybook = []
					s = self.sheets.copy()
					if len(self.current_sheet)>0: 
						s.append(self.current_sheet)

					if len(s)>0:
						for sheet in s:
							rows = set([point[0] for point in sheet])
							cols = set([point[1] for point in sheet])
							# скопируем точки из списка посещённых
							for r, c in sheet:
								zeros[r-1:r+2, c-1:c+2] = self.maze[r-1:r+2, c-1:c+2]
							
							# обрежем пустое место в заготовке и добавим кусочек в тетрадь
							copybook.append(zeros[min(rows)-1:max(rows)+2, min(cols)-1:max(cols)+2])
							zeros = np.zeros_like(zeros)
						zeros = copybook
					else:
						zeros = []
					
			return zeros
			
		
	def get_moving_buttons_and_descr(self): # для urwid
		
		all_directions, possible_directions  = self.relative_directions()
		place = self.place_buttons(all_directions, possible_directions)
		event_text = self.get_event(all_directions)
				
		return place, {k:p for k, p in place.items() if k in possible_directions}, event_text


if __name__ == "__main__":
	
	##TODO создать отдельную функцию
	game = MazeGame(17, 17)
	#game.make_step()
	game.show_part_of_map()
	game.mazeclass.find_way(game.row, game.col)
	#print(game.mazeclass.walk[1:])
	game.face = "up"
	previous_point = (game.row, game.col)
	text = ["отсюда иди:"]
	current_face = game.face
	for row, col in game.mazeclass.walk[1:]:
		if row > previous_point[0]:
			if game.face == "down":
				direction = "вперёд"
			elif game.face == "up":
				direction = "назад"
			elif game.face == "left":
				direction = "налево"
			elif game.face == "right":
				direction = "направо"
			game.face = "down"
	
		elif row < previous_point[0]:
			if game.face == "down":
				direction = "назад"
			elif game.face == "up":
				direction= "вперёд"
			elif game.face == "left":
				direction = "направо"
			elif game.face == "right":
				direction = "налево"
			game.face = "up"
	
		elif col > previous_point[1]:
			if game.face == "down":
				direction = "налево"
			elif game.face == "up":
				direction = "направо"
			elif game.face == "left":
				direction = "назад"
			elif game.face == "right":
				direction = "вперёд"
			game.face = "right"
		
		elif col < previous_point[1]:
			if game.face == "down":
				direction = "направо"
			elif game.face == "up":
				direction = "налево"
			elif game.face == "left":
				direction = "вперёд"
			elif game.face == "right":
				direction = "назад"
			game.face = "left"
		
		if direction != text[-1]: text.append(direction)
		previous_point = (row, col)
	game.face = current_face
	#print(current_face, text, game.face)
	print(text[0], ", ".join(text[1:]))
	game.mazeclass.print_maze(mode="way", interpolation="nearest", size_x=10, size_y=10)
