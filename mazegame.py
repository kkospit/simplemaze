from random import choice, sample, randint
from typing import List, Dict
from numpy import argwhere, zeros, zeros_like
from simple_maze import SimpleMaze
from math import sqrt


class MazeGame():
	
	
	__slots__ = ["mazeclass", "row", "col", "face", "markers", "chalk", "last_steps", 
				 "maze", "map_parts", "sheets", "has_sheet", "current_sheet", 
				 "sheet_limit", "use_sheet", "event_text", "map_points",
				 "chalk_points", "sheets_points", "max_stored_steps", "beacon", 
				 "fog_of_maze"]
	
	def __init__(self, height, width):
		if width < 5: width = 5
		if height < 5: height = 5
		# нам нужны нечётные значения ширины и высоты, поэтому:
		if width % 2 == 0: width += 1
		if height % 2 == 0: height += 1
		
		self.mazeclass = SimpleMaze(height, width)
		self.row = 1
		self.col = 1
		
		largest_dim = max(height, width)
		
		self.maze = self.mazeclass.maze
		self.mazeclass.make_rooms(int(largest_dim/10)) # комнаты, просто уберём стены в области
		self.maze[self.row, self.col] = self.mazeclass.objects["player"]
		# разворачиваем игрока лицом в коридор
		possible = self.mazeclass.choose_way(mode="default", step=1)
		self.face = choice(possible) # face - куда смотрит игрок относительно лабиринта, начало координат внизу
		
		# на стенах лабиринта можно оставлять пометки в виде стрелок 
		self.markers = {} # {(1, 1): {"up":"", "down":"", "left":"", "right":""}} # значения - стрелки из юникода
		self.chalk = 100
		
		# будет хранить последные пройденные координаты
		self.last_steps = [(self.row, self.col)]
		self.max_stored_steps = 15
		
		# бумага для черчения пути
		self.sheets = [] 
		self.has_sheet = 0 if height*width <= 400 else 2
		self.sheet_limit = 35#int(sqrt(largest_dim))
		self.current_sheet = []
		self.use_sheet = False
		
		#  для отрисовки частей карты лабиринта на общей карте
		self.map_parts = [] # откроем стартовую точку
			
		self.event_text = {"arrows":"", "copybook":"", "sheet":"", "chalk":"", 
						   "map_part":"", "find_chalk":"", "find_sheet":""}	
		
		# раскидаем места с предметами
		free_points = tuple((map(tuple, argwhere(self.maze==self.mazeclass.objects["path"]).tolist())))
		self.map_points = sample(free_points, int(largest_dim/3))		
		self.chalk_points = sample(free_points, int(largest_dim/3))		
		self.sheets_points = [] if height*width < 500 else sample(free_points, int(largest_dim/8))		
		
		# пустой массив с размерностью как у лабиринта, на который будем наносить 
		# открываемые части общей карты
		self.fog_of_maze = zeros((self.mazeclass.height, self.mazeclass.width), dtype="int")
		self.fog_of_maze[0:6, 0:6] = self.maze[0:6, 0:6]
		
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
			self.event_text["copybook"] = f"Листов для записей:{self.has_sheet}\n"
			#self.event_text["sheets_count"] = f"\u250C\u2510   \n\u2514\u2518: {self.has_sheet}"
			if self.use_sheet:
				self.event_text["copybook"] += f"Вы зарисовываете маршрут.\n"
		else:
			self.event_text["copybook"] = f"У вас закончились листы для записей.\n"
			self.use_sheet = False
		
		
		# предупредим, что место на листе скоро закончится
		if self.has_sheet > 0:
			sheet_lim = ((self.sheet_limit - len(self.current_sheet))/self.sheet_limit)
			if sheet_lim >= 0.8:
				self.event_text["sheet"] = "На текущем листе полно места.\n"
			elif 0.6 < sheet_lim <= 0.75:
				self.event_text["sheet"] = "Примерно треть листа занята чертежом.\n"
			elif 0.3 < sheet_lim <= 0.5:
				self.event_text["sheet"] = "Осталась половина листа.\n"
			elif 0.1 < sheet_lim <= 0.3:
				self.event_text["sheet"] = "Осталась треть листа.\n"
			elif sheet_lim <= 0.05:
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
		
		# test
		if (self.row, self.col) == (1, 1):
			self.fog_of_maze[1, 1] = 9 
		
		return "".join(self.event_text.values())
	
	
	def init_map_parts(self) -> tuple():
		add_row = int(sqrt(self.mazeclass.height))
		add_col = int(sqrt(self.mazeclass.width))
		rand_row = randint(0, self.mazeclass.height-add_row)
		rand_col = randint(0, self.mazeclass.width-add_col)
		return (rand_row, # start row
				rand_col, # start col
				rand_row+add_row, # end row
				rand_col+add_col)# end col

	
	# покажем кусочки карты
	def show_part_of_map(self, loop=None, mode="part"):
		modes = ("part", "minimap", "copybook")
		if mode in modes:
			# заготовка
			if mode == "part":
				# попробуем не создавать каждый раз массив, а заполнять созданный
				# при инициализации
				blank_map = self.fog_of_maze
				# костыль для отображения игрока на карте перемещения
				# только если игрок в открытой области
				# стирание "следа" см. в def move
				if blank_map[self.row, self.col] == self.mazeclass.objects["path"]:
					blank_map[self.row, self.col] = self.mazeclass.objects["player"]	
				# перенесли на заготовку нужный кусок
				if len(self.map_parts) > 0:
					for part in self.map_parts.copy():
						# если область ещё не добавлена
						#if zeros[part[0], part[1]] == self.mazeclass.HIDE:
						blank_map[part[0]:part[2], part[1]:part[3]] = self.maze[part[0]:part[2], part[1]:part[3]]
						self.map_parts.pop(self.map_parts.index(part))	
				return blank_map
						
			elif mode in modes[1:]:	
				
				if mode == "minimap":	
					blank_minimap = zeros((15, 15), dtype="int")
					# смещение, 7 - центр
					row_mod = (self.row-7)
					col_mod = (self.col-7)
					for r, c in self.last_steps:
						new_r = r - row_mod
						new_c = c - col_mod
						# если точка не влазит на миникарту
						if new_r<=0:continue
						if new_r+2>14:continue
						if new_c<=0:continue
						if new_c+2>14:continue
						try:
							# даже если какая-то ошибка произойдёт,
							# миникарта отрисуется нормально
							blank_minimap[new_r-1:new_r+2, new_c-1:new_c+2] = self.maze[r-1:r+2, c-1:c+2]
						except:
							# пока оставим для проверки
							print(new_r, new_c, self.row, self.col)
					return blank_minimap 		
						
				elif mode == "copybook": 
					copybook = []
					s = self.sheets.copy()
					if len(self.current_sheet) > 0: 
						s.append(self.current_sheet)

					if len(s)>0:
						for sheet in s:
							on_map=False
							rows = set([point[0] for point in sheet])
							cols = set([point[1] for point in sheet])
							min_row = min(rows)
							min_col = min(cols)
							height = len(rows)
							width = len(cols) 
							
							blank_sheet = zeros((height+2, width+2), dtype="int")
							for r, c in sheet:
								# учитывая стены, которые могут быть над строкой
								new_r = r - min_row + 1 
								new_c = c - min_col + 1
								#if new_r<=0:continue
								#if new_r>height:continue
								#if new_c<=0:continue
								#if new_c>width:continue
								blank_sheet[new_r-1:new_r+2, new_c-1:new_c+2] =  self.maze[r-1:r+2, c-1:c+2]
								# если какая-либо точка открыта на карте
								if self.fog_of_maze[r, c] == self.mazeclass.objects["path"]:
									on_map=True

							copybook.append(blank_sheet)

							if on_map:
								print("asdasdasadad")
								# добавим зарисованный путь на карту
								self.add_sheet_to_map(sheet)
								# on_map = False	
								# не будем хранить перенесённые зарисовки
								if sheet in self.sheets:
									self.sheets.pop(self.sheets.index(sheet))
									break
					return copybook

					'''
					blank_map = zeros((self.mazeclass.height, self.mazeclass.width), dtype="int")
					copybook = []
					s = self.sheets.copy()
					if len(self.current_sheet)>0: 
						s.append(self.current_sheet)

					if len(s)>0:
						on_map=False
						for sheet in s:
							rows = set([point[0] for point in sheet])
							cols = set([point[1] for point in sheet])
							# скопируем точки из списка посещённых
							for r, c in sheet:
								blank_map[r-1:r+2, c-1:c+2] = self.maze[r-1:r+2, c-1:c+2]
								# если на общей карте уже есть зарисованный путь
								if self.fog_of_maze[r, c] == self.mazeclass.objects["path"]:
									on_map=True
									#break # нужно ведь в тетреди дорисовать лист...
							if on_map:
								# добавим зарисованный путь на карту
								self.add_sheet_to_map(sheet)
								on_map = False	
								# не будем хранить перенесённые зарисовки
								if sheet in self.sheets:
									self.sheets.pop(self.sheets.index(sheet))
									break
									
							# обрежем пустое место в заготовке и добавим кусочек в тетрадь
							copybook.append(blank_map[min(rows)-1:max(rows)+2, min(cols)-1:max(cols)+2])
							blank_map = zeros_like(blank_map)
						return copybook
						'''
					
					
	# см. show_part_of_map mode=copybook
	def add_sheet_to_map(self, sheet):
		for r, c in sheet:
			self.fog_of_maze[r-1:r+2, c-1:c+2] = self.maze[r-1:r+2, c-1:c+2]
	
	
	# обработка нажатий кнопок для движения по лабиринту		
	def move(self, key):

		if key in self.mazeclass.choose_way(mode="default", step=1):
			self.face = key

			# убрали метку игрока со старых координат
			self.mazeclass.maze[self.row, self.col] = self.mazeclass.objects["path"]
			# костыль для используемого способа отрисовки общей карты
			# не создавать заготовку каждый раз, а использовать созданный
			# при инициализации массив, тут стираем "след" игрока
			if self.fog_of_maze[self.row, self.col] != self.mazeclass.objects["hide"]: #hide==0
				self.fog_of_maze[self.row, self.col] = self.mazeclass.objects["path"]
			# использую ту же функцию, которой "разрушал стены" и искал выход,
			# только не передаю список посещённых точек
			row, col = self.mazeclass.carve(direction=key, step=1)
			self.mazeclass.maze[row, col] = self.mazeclass.objects["player"] # теперь здесь метка игрока
			self.mazeclass.player_pos = (row, col) # для choose_way
			self.row, self.col = row, col

			# добавим _новую_ точку в список для миникарты
			if (row, col) not in self.last_steps:
				self.last_steps.append((row, col))
			# будем помнить ограниченное число посещённых точек
			if len(self.last_steps) > self.max_stored_steps:
				self.last_steps = self.last_steps[1:]

			# если есть лист бумаги и/или карандаш(?)
			if self.use_sheet and (row, col) not in self.current_sheet:
				self.current_sheet.append((row, col))
				if len(self.current_sheet) >= self.sheet_limit:
					self.sheets.append(self.current_sheet.copy())
					self.current_sheet.clear()
					self.has_sheet -= 1
					self.use_sheet = False


if __name__ == "__main__":
	pass
