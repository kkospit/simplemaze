from random import choice, sample, randint
from typing import List, Dict
import numpy as np
from simple_maze import SimpleMaze
from math import sqrt
class MazeGame():
	
	
	__slots__ = ["mazeclass", "row", "col", "face", "markers", "chalk", "last_steps", 
				 "maze", "map_parts", "sheets", "has_sheet", "current_sheet", 
				 "sheet_limit", "use_sheet", "event_text", "map_points",
				 "chalk_points", "sheets_points"]
	
	def __init__(self, height, width):
		self.mazeclass = SimpleMaze(height, width)
		self.row = 1
		self.col = 1
		
		largest_dim = max(self.mazeclass.height, self.mazeclass.width)
		
		self.maze = self.mazeclass.maze
		self.mazeclass.make_rooms(int(largest_dim/10)) # комнаты, просто уберём стены в области
		self.maze[self.row, self.col] = self.mazeclass.PLAYER
		# разворачиваем игрока лицом в коридор
		possible = self.mazeclass.choose_way(mode="default", step=1)
		self.face = choice(possible) # face - куда смотрит игрок относительно лабиринта, начало координат внизу
		
		# на стенах лабиринта можно оставлять пометки в виде стрелок 
		self.markers = {} # {(1, 1): {"up":"", "down":"", "left":"", "right":""}} # значения - стрелки из юникода
		self.chalk = 100
		
		# будет хранить последные пройденные координаты
		self.last_steps = [(self.row, self.col)]
		
		# бумага для черчения пути
		self.sheets = [] 
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
		self.map_points = sample(free_points, int(largest_dim/2))		
		self.chalk_points = sample(free_points, int(largest_dim/2))		
		self.sheets_points = sample(free_points, int(largest_dim/4))		
		
		
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
		self.markers[(self.row, self.col)][key] = arrow[1] if self.markers[(self.row, self.col)].get(key) == arrow[0] else arrow[0]
		self.chalk -= 3
		
	# описание событий
	def get_event(self):
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
		else:
			self.event_text["sheet"] = ""
		
		if self.chalk > 20:
			self.event_text["chalk"] = "У вас есть мел.\n"
		elif 0 < self.chalk <= 20:
			self.event_text["chalk"] = "Мела почти не осталось...\n"
		elif self.chalk <= 0:
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
	
	
	def init_map_parts(self) -> tuple():
		rand_row = randint(0, self.mazeclass.height-5)
		rand_col = randint(0, self.mazeclass.width-5)
		return (rand_row, # start row
				rand_col, # start col
				#rand_row+choice((5,10)), # end row
				#rand_col+choice((5,10))) # end col
				rand_row+int(sqrt(self.mazeclass.height)), # end row
				rand_col+int(sqrt(self.mazeclass.width)) )# end col
	
	
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
	

if __name__ == "__main__":
	pass
