import os
import sys
import pygame
import pygame_gui
from gameScreen import startGame

class EventHandler:
    def __init__(self):
        self.buttons = []
        self.toggleButtons = []
        self.sliders = []
        self.vars = {}
        self.button_sound = pygame.mixer.Sound(os.path.join(current_directory, 'assets/buttonsound.mp3'))

    def setValue(self, varname, value):
        self.vars[varname] = value

    def getValue(self, varname):
        return self.vars.get(varname)

    def newButtonEvent(self, button, varname, value):
        self.buttons.append((button, varname, value))
        curr_value = self.vars.get(varname)
        if curr_value is None:
            self.setValue(varname, value)

    def newToggleButtonEvent(self, button, varname, true_text, false_text):
        self.toggleButtons.append((button, varname, true_text, false_text))
        curr_value = self.vars.get(varname)
        if curr_value is None:
            self.setValue(varname, True)

    def newSliderEvent(self, slider, varname, increment, link_text):
        self.sliders.append((slider, varname, increment, link_text))
        curr_value = self.getValue(varname)
        if curr_value is None:
            self.setValue(varname, slider.get_current_value())

    def setSliders(self):
        for slider, varname, _, text in self.sliders:
            value = self.getValue(varname)
            slider.set_current_value(value)
            text.set_text(f"{value}")

    def setToggles(self):
        for button, varname, true_text, false_text in self.toggleButtons:
            if self.getValue(varname):
                button.set_text(true_text)
            else:
                button.set_text(false_text)
    
    def runEvent(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for button, varname, value in self.buttons:
                if event.ui_element == button:
                    if varname is not None:
                        self.vars[varname] = value
                        self.button_sound.play()

            for button, varname, true_text, false_text in self.toggleButtons:
                if event.ui_element == button:
                    if varname is not None:
                        self.vars[varname] = not self.vars[varname]
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            for slider, varname, increment, text in self.sliders:
                if event.ui_element == slider:
                    value = round(event.value / increment) * increment
                    if varname is not None:
                        self.setValue(varname, value)
        gui_manager.process_events(event)


class ScreenState:
    def __init__(self, gui, events, colour=(0, 0, 0)):
        self.my_gui = gui
        self.my_events = events
        self.colour = colour
        self.objects = []

    def newButton(self, x_pos, y_pos, x_dim, y_dim, text, varname, value):
        new_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x_pos, y_pos), (x_dim, y_dim)), 
            text=text, manager=self.my_gui)
        new_button.visible = False
        self.objects.append(new_button)
        self.my_events.newButtonEvent(new_button, varname, value)

    def newToggleButton(self, x_pos, y_pos, x_dim, y_dim, varname, true_text, false_text):
        new_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x_pos, y_pos), (x_dim, y_dim)), 
            text=true_text, manager=self.my_gui)
        new_button.visible = False
        self.objects.append(new_button)
        self.my_events.newToggleButtonEvent(new_button, varname, true_text, false_text)

    def newText(self, x_pos, y_pos, x_dim, y_dim, text, font_size=6):
        new_text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((x_pos, y_pos), (x_dim, y_dim)), 
            html_text=f"<font size={font_size}>{text}</font>", manager=self.my_gui)
        new_text.visible = False
        self.objects.append(new_text)

    def newSlider(self, x_pos, y_pos, x_dim, y_dim, min_val, max_val, inc_val, varname):
        new_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((x_pos, y_pos), (x_dim - 50, y_dim)), 
            start_value=min_val, value_range=(float(min_val), float(max_val)), click_increment=inc_val, manager=self.my_gui)
        new_slider.visible = False
        link_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((x_pos + x_dim - 50, y_pos), (50, y_dim)), 
            text=f"{min_val}", manager=self.my_gui)
        link_text.visible = False
        self.objects.append(new_slider)
        self.objects.append(link_text)
        self.my_events.newSliderEvent(new_slider, varname, inc_val, link_text)

    def show(self):
        display.fill(self.colour)
        for object in self.objects:
            object.show() 
        
    def hide(self):
        for object in self.objects:
            object.hide() 


current_directory = os.path.dirname(__file__)
pygame.init()
pygame.mixer.init()
gameover_sound = pygame.mixer.Sound(os.path.join(current_directory, 'assets/gameoversound.mp3'))
# create display window
display = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Elden Blocks")
# gui manager and event handler
gui_manager = pygame_gui.UIManager((800, 600))
event_handler = EventHandler()
screens = []
font_list = []
gui_manager.add_font_paths('Mantinia Regular', os.path.join(current_directory, 'assets/Mantinia Regular.otf'))
for size in range(1, 49):
    font_list.append({'name': 'Mantinia Regular', 'point_size': size, 'style': 'regular'})
gui_manager.preload_fonts(font_list)
gui_manager.get_theme().load_theme(os.path.join(current_directory, 'assets/theme.json'))
pygame.mixer.music.load(os.path.join(current_directory, 'assets/music.mp3'))

# Main Menu
main_menu = ScreenState(gui_manager, event_handler)
screens.append(main_menu)
main_menu.newButton(300, 200, 200, 50, "Play Game", "gamestart", 1)
main_menu.newButton(300, 275, 200, 50, "Top Scores", "menustate", 2)
main_menu.newButton(300, 350, 200, 50, "Configure", "menustate", 1)
main_menu.newButton(300, 500, 200, 50, "Quit", "quitgame", 1)
main_menu.newText(0, 0, 800, 100, "Tetris", 7)
with open(os.path.join(current_directory, 'assets/creators.txt'), "r") as file:
    creators = file.read()
main_menu.newText(0, 450, 250, 150, creators, 4)

# Settings Menu
settings = ScreenState(gui_manager, event_handler)
screens.append(settings)
settings.newText(0, 0, 800, 100, "Configuration", 7)
settings.newButton(300, 500, 200, 50, "Return to Main Menu", "menustate", 0)
settings.newText(0, 100, 200, 75, "Difficulty", 4)
settings.newSlider(200, 100, 450, 75, 1, 5, 1, "speed")
settings.newText(0, 175, 200, 75, "Tower Width", 4)
settings.newSlider(200, 175, 450, 75, 15, 5, 1, "width")
settings.newText(0, 250, 200, 75, "Tower Height", 4)
settings.newSlider(200, 250, 450, 75, 20, 10, 1, "height")
settings.newText(0, 325, 200, 75, "Extended Shapes", 4)
settings.newToggleButton(210, 335, 430, 55, "ext_shapes", "Extended Shapes", "Default Shapes")
settings.newText(0, 400, 200, 75, "AI Mode", 4)
settings.newToggleButton(210, 410, 430, 55, "AI_mode", "AI controlled game", "Player controlled game")

# Highscore Menu
highscores = ScreenState(gui_manager, event_handler)
screens.append(highscores)
highscores.newText(0, 0, 800, 100, "Top Scores", 7)
highscores.newButton(300, 500, 200, 50, "Return to Main Menu", "menustate", 0)

# Gameplay
endgame = ScreenState(gui_manager, event_handler)
screens.append(endgame)
endgame.newText(0, 0, 800, 100, "You Died", 7)
endgame.newButton(300, 500, 200, 50, "Return to Main Menu", "menustate", 0)

# Default Values
event_handler.setValue("menustate", len(screens))
event_handler.setValue("gamestart", 0)
event_handler.setValue("quitgame", 0)
event_handler.setValue("width", 10)
event_handler.setValue("height", 20)
event_handler.setValue("speed", 3)
event_handler.setValue("ext_shapes", False)
event_handler.setValue("AI_mode", False)

# Run game
clock = pygame.time.Clock()
pygame.mixer.music.play(-1)
is_running = True

# Startup Sequence
introskip = False
if len(sys.argv) > 1:
    introskip = True
start_time = pygame.time.get_ticks()
for screen in screens:
        screen.hide()
startup_text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((0, 250), (800, 100)), 
    html_text=f"<font size={7}> </font>", manager=gui_manager)
startup_time = 10000
startup_text_lines = []
with open(os.path.join(current_directory, 'assets/creators.txt'), "r") as file:
    for line in file:
        startup_text_lines.append(line)
line = 0
while line < len(startup_text_lines) + 3 and not introskip:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        event_handler.runEvent(event)
    line = (pygame.time.get_ticks() - start_time) // 2185
    if line in range(len(startup_text_lines)):
        startup_text.set_text(f"<font size={4}>{startup_text_lines[line]}</font>")
    elif line == len(startup_text_lines):
        startup_text.set_text(f"<font size={5}>Presenting...</font>")
    else:
        startup_text.set_text(f"<font size={5}> </font>")
    gui_manager.update(clock.tick(60) / 1000.0)
    gui_manager.draw_ui(display)
    pygame.display.flip()
startup_text.visible = False

# Main Loop
event_handler.setValue("menustate", 0)
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        event_handler.runEvent(event)

    gui_manager.update(clock.tick(60) / 1000.0)
    if event_handler.getValue("quitgame") == 1:
        is_running = False
    current_screen = event_handler.getValue("menustate")
    if event_handler.getValue("gamestart") == 1:
        current_screen = len(screens)
    for i in range(len(screens)):
        if current_screen == i:
            screens[i].show()
            if i == 0 and not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        else:
            screens[i].hide()
    event_handler.setSliders()
    event_handler.setToggles()
    gui_manager.draw_ui(display)
    pygame.display.flip()
    if event_handler.getValue("gamestart") == 1:
        pygame.mixer.music.stop()
        event_handler.setValue("gamestart", 0)
        score = startGame(event_handler.getValue("width"), event_handler.getValue("height"), event_handler.getValue("ext_shapes"), 
                          event_handler.getValue("speed"), event_handler.getValue("AI_mode"), display, gui_manager)
        event_handler.setValue("menustate", 3)
        gameover_sound.play()

pygame.quit()