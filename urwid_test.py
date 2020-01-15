import urwid
from random import choice
from mazegame import MazeGame

game = MazeGame(10, 10)

max_stored_steps = 15
max_drawing_points = 30

# обработка нажатий кнопок для движения по лабиринту
def move(key):

	# all_directions, possible_directions = game.relative_directions()
	
	#if key in possible_directions.values():
	if key in game.mazeclass.choose_way(maze_creation=False, step=1, player_row=game.row, player_col=game.col):
		game.face = key
		
		# убрали метку игрока со старых координат
		game.mazeclass.maze[game.row, game.col] = game.mazeclass.PATH 
		# использую ту же функцию, которой "разрушал стены" и искал выход, 
		# только не передаю список посещённых точек
		row, col = game.mazeclass.carve(direction=key, step=1, player_row=game.row, player_col=game.col)
		game.mazeclass.maze[row, col] = game.mazeclass.PLAYER # теперь здесь метка игрока
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
	possible_directions = game.mazeclass.choose_way(maze_creation=False, step=1, player_row=game.row, player_col=game.col)
	event_text = game.get_event()
	
	location_text = urwid.Text(short_description(possible_directions) + "\n" + event_text, align="center")
	
	column = urwid.Columns([urwid.BoxAdapter(urwid.Filler(location_text, valign="middle"), 10)])
	pile = urwid.LineBox(urwid.Pile([create_minimap(), column]), 
						tlcorner='', tline='', lline='', trcorner='', blcorner='', rline='│', bline='', brcorner='')
	
	
	return pile


# отрисовка нескольких точек, посещённых последними
def create_minimap():
	# миникарта
	if game.last_steps:	
		last_steps = ''		
		minimap = game.show_part_of_map(mode="minimap")
		last_steps = game.mazeclass.maze_to_string(minimap, row_end=minimap.shape[0], col_end=minimap.shape[1])	
	
	return urwid.BoxAdapter(urwid.Filler(urwid.Text(("blueprint", last_steps), align="center"), valign="middle"), 21)


# сделать отметку
def mark(key):
	game.mark(key)
	change_buttons_and_descr()
	

def button_power(key):
	if key == "esc":
		raise urwid.ExitMainLoop()
	
	elif key in ["m","M", "ь", "Ь"]:

		if button_power.overlay == 0:
			# нарисуем карту
			_map = urwid.Text(game.mazeclass.maze_to_string(maze=game.show_part_of_map(), 
															row_start=1, 
															col_start=1, 
															row_end=(game.mazeclass.height+5), 
															col_end=(game.mazeclass.width*2+5)),
															align='center', 
															wrap='space', 
															layout=None)
			
			main_widget.original_widget = urwid.Overlay(urwid.LineBox(urwid.Filler(_map)), 
														box, 
														align="center", 
														width=(game.mazeclass.width*2+5), 
														height=(game.mazeclass.height+5), 
														valign="middle")
			button_power.overlay = 1
		else:
			# из оверлея берём нижний, который у нас основной	
			main_widget.original_widget = main_widget.original_widget.contents[0][0]
			button_power.overlay = 0
	
	# TODO зарисованные куски отображаются рядом друг с другом, попробовать через Grid, допустим, на шесть ячеек
	# grid не подойдёт, лучше ListBox, в идеале бы переписать, чтобы прокручивался по горизонтали
	elif key in ["c", "C", "с", "С"]:
		_copybook = game.show_part_of_map(mode="copybook")
		if len(_copybook)>0:
			body = []
			for sheet in _copybook:
				body.append(urwid.Text(game.mazeclass.maze_to_string(maze=sheet, 
																	row_start=1, 
																	col_start=1, 
																	row_end=31, 
																	col_end=31), 
																	align='center', 
																	wrap='space', 
																	layout=None))
				
			if button_power.overlay == 0:
				main_widget.original_widget = urwid.Overlay(urwid.LineBox(
																urwid.ListBox([*body])),
																box, 
																align="center", 
																width=62,#(game.mazeclass.width*2+5), 
																height=31,#(game.mazeclass.height+5), 
																valign="middle")
				button_power.overlay = 1
				
				#меняем фокус на последний зарисованный участок лабиринта
				#оверлей с верхним виджетом - LineBox       # виджет внутри LineBox - ListBox
				main_widget.original_widget.contents[1][0].original_widget.change_focus((20,20),
																						len(_copybook)-1, 
																						offset_inset=0, 
																						coming_from=None, 
																						cursor_coords=None, 
																						snap_rows=None)
				
			else:
				# из оверлея берём нижний, который у нас основной	
				main_widget.original_widget = main_widget.original_widget.contents[0][0]
				button_power.overlay = 0
						
	# блокируем нажатия при включенной карте
	if button_power.overlay == 0:
		all_directions = game.relative_directions()[0]
		if key in ("down", "up","left", "right"):
			#move(all_directions[key])
			move(key)
		
		elif key == "q": 
			if game.has_sheet > 0:
				game.use_sheet = True
		
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
filler = urwid.Filler(interface, valign="top")
box = urwid.LineBox(filler)
button_power.overlay = 0
main_widget = urwid.WidgetPlaceholder(box)
urwid.MainLoop(main_widget, palette, unhandled_input=button_power).run()
