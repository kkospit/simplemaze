import shutil # для подстройки размеров под окно терминала
import mazestartmenu
from urwid import Text, Padding, Pile, Columns, Overlay, WidgetPlaceholder,\
					ExitMainLoop, LineBox, BoxAdapter, AttrMap, Filler, \
					ListBox, MainLoop

# палитра
palette = [
    ('blueprint', 'white', 'light blue'),
    ('empty', '', ''),
    ('violet', 'white', 'dark magenta'),
    ('cyan', 'white', 'dark cyan'),
    ('caffe', 'white', 'brown'),
    ('help', 'light gray', ''),
    ]

game_over = False # установка окончания игры
game = mazestartmenu.menu()

lipsum = """
"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum."
"""

########################################################################################################################
########################################################################################################################
# обработка нажатий кнопок для движения по лабиринту
def move(key):
		# основная функция в mazegame
		game.move(key)
		# нашли выход
		if game.row == game.mazeclass.height-2 and game.col == game.mazeclass.width-2:
			global game_over
			game_over = True

			# запустим перевод в текст
			full_map = game.mazeclass.maze_to_string(None,1,1,game.mazeclass.height,
															  game.mazeclass.width)
			text = Text("Лабиринт пройден!\n"+full_map, align="center")
			main_widget.original_widget = LineBox(Filler(text, valign="middle"))

		# изменяем описание места и меняем доступные кнопки
		change_main_widgets()


def exit(key):
    raise ExitMainLoop()
########################################################################################################################
########################################################################################################################



########################################################################################################################
########################################################################################################################
#Блок функций основного интерфейса
# обновить виджеты
def change_main_widgets():
	minimap.set_text(("blueprint",create_minimap("update")))
	location_text.set_text(create_location_text("update"))
	#description.set_text(create_descriprion("update"))


# создать разметку
def create_interface():
	m_map = Padding(LineBox(minimap, 
							tlcorner='', tline='', lline='', trcorner='', 
							blcorner='', rline='│', bline='', brcorner=''), 
							align="center", width=35)
	_help = Text(("help", "Карта - m, тетрадь - c,\nНачать зарисовку - q\n"+
						"сделать отметку - CTRL+arrow_key"), align="center")						
	#column = Columns([description, Pile([m_map, _help]), BoxAdapter(
	column = Columns([description, m_map, BoxAdapter(
					Filler(location_text, valign=("relative", 20)), 20)])
					
	return Filler(Padding(column, align="center", width=120), valign="middle")


# отрисовка нескольких точек, посещённых последними
# миникарта
def create_minimap(mode="creation") -> str:
	# миникарта
	if game.last_steps:
		last_steps = ''
		minimap = game.show_part_of_map(mode="minimap")
		last_steps = game.mazeclass.maze_to_string(minimap, row_end=minimap.shape[0], col_end=minimap.shape[1])
	if mode == "creation":
		return Text(("blueprint", last_steps), align="center")
	elif mode == "update":
		return last_steps


# краткое описание места
def create_location_text(mode="creation"):
	possible_directions = game.mazeclass.choose_way(mode="default", step=1)
	event_text = game.get_event()
	if mode == "creation":
		return Text(short_description(possible_directions) + "\n" + event_text, align="center")
	elif mode == "update":
		return short_description(possible_directions) + "\n" + event_text
		
		
# расширенное описание место, возможно, с выбором действий
def create_descriprion(mode="creation"):
	if mode == "creation":
		return Text(lipsum, align="center")
	elif mode == "update":
		return "changed description"
		

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
		# ...ну...
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
########################################################################################################################
########################################################################################################################

# сделать отметку
def mark(key):
	game.mark(key)
	change_main_widgets()


########################################################################################################################
########################################################################################################################
# функции для общей карты и тетради
# создание текстового представления карты
def create_map():
		# проверим, нет ли в зарисовках уже открытых частей карты,
		# и, если есть, перенесём зарисовку на карту
		game.show_part_of_map(mode="copybook")
		_map = Text(game.mazeclass.maze_to_string(maze=game.show_part_of_map(),
																row_start=1,
																col_start=1,
																row_end=(game.mazeclass.height+5),
																col_end=(game.mazeclass.width+5)),
																align='center',
																wrap='space',
																layout=None)
		listbox = ListBox([_map])
		# сдвинем фокус, чтобы игрок всегда был видел
		offset = 15 if game.maze.shape[0] > 15 else game.maze.shape[0]
		listbox.shift_focus((game.mazeclass.width*2+5, game.mazeclass.height), -(game.row-offset))
		return LineBox(listbox)


# создание overlay с картой
def show_map(_map):
	lines = shutil.get_terminal_size()[1] # число строк в окне
	main_widget.original_widget = Overlay(_map, box, align="center",
								width=(game.mazeclass.width*2+5),
								height=int(lines*0.9) if game.mazeclass.height 
														> lines*0.9 else 
														game.mazeclass.height+4,
								valign="middle")
	button_power.overlay = 1


def create_copybook():
	_copybook = game.show_part_of_map(mode="copybook")
	#print(len(_copybook))
	if len(_copybook)>0:
		body = []
		for idx, sheet in enumerate(_copybook):
			#print(idx, sheet)
			body.append(Text(game.mazeclass.maze_to_string(maze=sheet,
						row_start=1, col_start=1, row_end=31, col_end=31),
						align='center', wrap='space', layout=None))		
		return body


def show_copybook(body):
	listbox = ListBox([*body])
	main_widget.original_widget = Overlay(LineBox(listbox), box, 
						align="center", width=62, height=31, valign="middle")

	#меняем фокус на последний зарисованный участок лабиринта
	listbox.change_focus((20,20), len(body)-1, offset_inset=0,
						coming_from=None, cursor_coords=None, snap_rows=None)
	button_power.overlay = 1
########################################################################################################################
########################################################################################################################

# обработка нажатий клавиш
def button_power(key):
	if not game_over:
		if key in ["m","M", "ь", "Ь"]:
			if button_power.overlay == 0:
				# нарисуем карту
				show_map(create_map())
			else:
				main_widget.original_widget = box
				button_power.overlay = 0

		# записи на листах
		elif key in ["c", "C", "с", "С"]:
			body = create_copybook()
			if body:
				if button_power.overlay == 0:
					show_copybook(body)
				else:
					main_widget.original_widget = box
					button_power.overlay = 0
			
		# блокируем нажатия при включенной карте
		if button_power.overlay == 0:
			#all_directions = game.relative_directions()[0]
			if key == "esc":
				raise ExitMainLoop()
			elif key in ("down", "up","left", "right"):
				#move(all_directions[key])
				move(key)

			elif key in ("q","Q", "Й", "й"):
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
button_power.overlay = 0 # проверка на то, что карта или тетрать отображаются


# элементы основного экрана
minimap = create_minimap()
location_text = create_location_text()
description = create_descriprion()
# создали разметку с этими элементами
interface = create_interface()
box = LineBox(interface)
main_widget = WidgetPlaceholder(box)
# запуск
main_loop = MainLoop(main_widget, palette, unhandled_input=button_power)
main_loop.run()
