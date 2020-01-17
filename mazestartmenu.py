from urwid import ExitMainLoop, IntEdit, Button, Padding, AttrMap, \
				  SolidFill, Divider, LineBox, Filler, Pile, Overlay, \
				  MainLoop, connect_signal, Text
from mazegame import MazeGame
# настройка ширины и высоты лабиринта перед игрой

# палитра
palette = [
    ('blueprint', 'white', 'light blue'),
    ('empty', '', ''),
    ('violet', 'white', 'dark magenta'),
    ('cyan', 'white', 'dark cyan'),
    ('caffe', 'white', 'brown'),
    ]

def start_game(buttom):
	raise ExitMainLoop()

def menu():	
	hello = Text("Приветствую! Для продолжения настройте параметры лабиринта.\n"+
					   "Если карта лабиринта будет некорректно отображаться, "+
					   "попробуйте уменьшить значение ширины или развернуть окно.")
	height_enter = IntEdit("Высота лабиринта: ", 30)
	width_enter = IntEdit("Ширина лабиринта: ", 45)
	done = Button("Готово")
	done_pad = Padding(done, align="center", width=10)

	back = AttrMap(SolidFill("\u25E6"), "blueprint")
	pile = Pile([hello, Divider("\u2500"), height_enter, width_enter, done_pad])
	menu = Filler(LineBox(pile))
	main_widget = Overlay(menu,
											back,
											align="center",
											width=35,
											height=12,
											valign="middle")
	loop = MainLoop(main_widget, palette)
	connect_signal(done, 'click', start_game)
	loop.run()
	
	return MazeGame(height_enter.value(), width_enter.value())
	
if __name__ == "__main__":	
	game = menu()
########################################################################################################################
########################################################################################################################
