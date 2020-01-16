import shutil # для подстройки размеров под окно терминала
import urwid
from mazegame import MazeGame
# TODO сделать меню с заданием параметров
# добавить объектов
# факел - повышает вероятность найти что-нибудь
# ориентир - позволяет совместить лист и карту
# то есть можно сделать точку, и если она есть на блоке и на листе, совместить


# для начала и так
size = input("Введите высоту и ширину лабиринта через пробел.\n"+
			"(для больших значений ширины потребуется развернуть окно): ").split()
try:
	height, width = int(size[0]), int(size[1])
	game = MazeGame(height, width)
except:
	print("Введены некорректные параметры!")
	exit()
	
max_stored_steps = 15
game_over = False

lipsum = """
"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum."
"""


# обработка нажатий кнопок для движения по лабиринту
def move(key):
	# так то бы перенести почти всё в mazegame...
	# all_directions, possible_directions = game.relative_directions()

	#if key in possible_directions.values():
	if key in game.mazeclass.choose_way(mode="default", step=1):
		game.face = key

		# убрали метку игрока со старых координат
		game.mazeclass.maze[game.row, game.col] = game.mazeclass.PATH
		# костыль для используемого способа отрисовки общей карты
		# не создавать заготовку каждый раз, а использовать созданный
		# при инициализации массив
		if game.fog_of_maze[game.row, game.col] != game.mazeclass.HIDE:
			game.fog_of_maze[game.row, game.col] = game.mazeclass.PATH
		# использую ту же функцию, которой "разрушал стены" и искал выход,
		# только не передаю список посещённых точек
		row, col = game.mazeclass.carve(direction=key, step=1)
		game.mazeclass.maze[row, col] = game.mazeclass.PLAYER # теперь здесь метка игрока
		game.mazeclass.player_pos = (row, col) # для choose_way
		game.row, game.col = row, col

		# миникарта
		# добавим _новую_ точку в список для миникарты
		if (row, col) not in game.last_steps:
			game.last_steps.append((row, col))
		# будем помнить ограниченное число посещённых точек
		if len(game.last_steps) > max_stored_steps:
			game.last_steps = game.last_steps[1:]

		# если есть лист бумаги и/или карандаш
		if game.use_sheet and (row, col) not in game.current_sheet:
			game.current_sheet.append((row, col))
			if len(game.current_sheet) >= game.sheet_limit:
				game.sheets.append(game.current_sheet.copy())
				game.current_sheet.clear()
				game.has_sheet -= 1
				game.use_sheet = False

		# нашли выход
		if game.row == game.mazeclass.height-2 and game.col == game.mazeclass.width-2:
			global game_over
			game_over = True

			#text.set_text("Вы выбрались из лабиринта!")
			# не будем запускать matplotlib
			# game.mazeclass.print_maze(interpolation="nearest")
			# запустим перевод в текст
			full_map = game.mazeclass.maze_to_string(None,1,1,game.mazeclass.height,
															  game.mazeclass.width)
			text = urwid.Text(full_map+"Лабиринт пройден!", align="center")
			main_widget.original_widget = urwid.LineBox(urwid.Filler(text, valign="middle"))
			#input("Лабиринт пройден! Нажмите любую клавишу для завершения.")
			#raise urwid.ExitMainLoop()

		# изменяем описание места и меняем доступные кнопки
		change_buttons_and_descr()


def exit(key):
    raise urwid.ExitMainLoop()


# TODO переделать
def short_description(possible_directions):
	text = ""
	#print(possible_directions)
	dnums = len(possible_directions) # количество "развилок"
	if dnums >= 3:
		text += f"Вы находитесь на перекрёстке."
	elif dnums <= 1:
		text += f"Вы находитесь в тупике. Похоже, придётся выбрать другой путь."
	#'''
	else:
		# ...
		if ("up" in possible_directions and \
		("left" in possible_directions or \
		"right" in possible_directions)) or \
		("down" in possible_directions and \
		("left" in possible_directions or \
		"right" in possible_directions)):
			text += f"Здесь поворот."
		else:
			text += f"Вы в коридоре."
	#'''
	return text


def change_buttons_and_descr():
	filler.original_widget = create_buttons_and_descr()


def create_buttons_and_descr():
	#place, possible_directions, event_text = game.get_moving_buttons_and_descr()
	possible_directions = game.mazeclass.choose_way(mode="default", step=1)
	event_text = game.get_event()

	location_text = urwid.Text(short_description(possible_directions) + "\n" + event_text, align="center")


	inventory = urwid.Pile([urwid.Text(lipsum, align="center")])

	pile = urwid.LineBox(urwid.Pile([create_minimap()]),
						tlcorner='', tline='', lline='', trcorner='', blcorner='', rline='│', bline='', brcorner='')

	column = urwid.Columns([inventory, create_minimap(), urwid.BoxAdapter(urwid.Filler(location_text, valign="middle"), 10)])
	
	return column


# отрисовка нескольких точек, посещённых последними
def create_minimap():
	# миникарта
	if game.last_steps:
		last_steps = ''
		minimap = game.show_part_of_map(mode="minimap")
		last_steps = game.mazeclass.maze_to_string(minimap, row_end=minimap.shape[0], col_end=minimap.shape[1])

	return urwid.BoxAdapter(urwid.Filler(urwid.Text(("empty", last_steps), align="center"), valign="middle"), 21)


# сделать отметку
def mark(key):
	game.mark(key)
	change_buttons_and_descr()

# создание карты для urwid
def create_map():
		_map = urwid.Text(game.mazeclass.maze_to_string(maze=game.show_part_of_map(),
																row_start=1,
																col_start=1,
																row_end=(game.mazeclass.height+5),
																col_end=(game.mazeclass.width+5)),
																align='center',
																wrap='space',
																layout=None)
		return urwid.LineBox(urwid.ListBox([_map]))


# создание overlay с картой
def show_map(_map):
	lines = shutil.get_terminal_size()[1] # число строк в окне
	main_widget.original_widget = urwid.Overlay(_map,
												box,
												align="center",
												width=(game.mazeclass.width*2+5),
												#height=50 if height>25 else height+4,#(game.mazeclass.height+5),
												height=int(lines*0.9) if height > lines*0.9 else height+4,
												valign="middle")
	button_power.overlay = 1


def create_copybook():
	_copybook = game.show_part_of_map(mode="copybook")
	#print(len(_copybook))
	if len(_copybook)>0:
		body = []
		for idx, sheet in enumerate(_copybook):
			#print(idx, sheet)
			body.append(urwid.Text(game.mazeclass.maze_to_string(maze=sheet,
																row_start=1,
																col_start=1,
																row_end=31,
																col_end=31),
																align='center',
																wrap='space',
																layout=None))
		
		return body

def show_copybook(body):
	main_widget.original_widget = urwid.Overlay(urwid.LineBox(
												urwid.ListBox([*body])),
												box,
												align="center",
												width=62,#(game.mazeclass.width*2+5),
												height=31,#(game.mazeclass.height+5),
												valign="middle")

	#меняем фокус на последний зарисованный участок лабиринта
	#оверлей с верхним виджетом - LineBox       # виджет внутри LineBox - ListBox
	main_widget.original_widget.contents[1][0].original_widget.change_focus((20,20),
																			len(body)-1,
																			offset_inset=0,
																			coming_from=None,
																			cursor_coords=None,
																			snap_rows=None)
	button_power.overlay = 1


# обработка нажатий клавиш
def button_power(key):
	if not game_over:
		if key in ["m","M", "ь", "Ь"]:
			if button_power.overlay == 0:
				# нарисуем карту
				show_map(create_map())
			else:
				# из оверлея берём нижний, который у нас основной
				main_widget.original_widget = main_widget.original_widget.contents[0][0]
				button_power.overlay = 0

		# записи на листах
		elif key in ["c", "C", "с", "С"]:
			body = create_copybook()
			if body:
				if button_power.overlay == 0:
					show_copybook(body)
				else:
					# из оверлея берём нижний, который у нас основной
					main_widget.original_widget = main_widget.original_widget.contents[0][0]
					button_power.overlay = 0
			
		# блокируем нажатия при включенной карте
		if button_power.overlay == 0:
			#all_directions = game.relative_directions()[0]
			if key == "esc":
				raise urwid.ExitMainLoop()
			elif key in ("down", "up","left", "right"):
				#move(all_directions[key])
				move(key)

			elif key == "q":
				if game.has_sheet > 0:
					game.use_sheet = True

			# test
			'''
			elif key == "f":
				import numpy as np
			
				if game.mazeclass.WAY_OUT in game.maze:
					for r, c in game.mazeclass.walk:
						game.maze[r, c] = game.mazeclass.PATH

				game.mazeclass.find_way(start_x=game.col, start_y=game.row)
				for r, c in game.mazeclass.walk:
					game.maze[r, c] = game.mazeclass.WAY_OUT
			'''

			if game.chalk > 0:
				if key == "ctrl up":
					mark("up")
				elif key == "ctrl down":
					mark("down")
				elif key == "ctrl left":
					mark("left")
				elif key == "ctrl right":
					mark("right")


palette = [
    ('blueprint', 'white', 'light blue'),
    ('empty', '', ''),
    ]

# первоначальное создание описания
interface = create_buttons_and_descr()
#box = urwid.LineBox(interface)
filler = urwid.Filler(interface, valign="middle")
box = urwid.LineBox(filler)
button_power.overlay = 0
main_widget = urwid.WidgetPlaceholder(box)
urwid.MainLoop(main_widget, palette, unhandled_input=button_power).run()
