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
        self.textVars = []
        self.keyToggles = []
        self.user = None
        self.vars = {}
        self.button_sound = pygame.mixer.Sound(os.path.join(current_directory, 'assets/buttonsound.mp3'))

    def setValue(self, varname, value):
        self.vars[varname] = value

    def getValue(self, varname):
        return self.vars.get(varname)
    
    def getUser(self):
        return self.user.get_text()

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

    def newTextVar_(self, textbox, pre_text, varname, post_text):
        self.textVars.append((textbox, pre_text, varname, post_text))
        curr_value = self.vars.get(varname)
        if curr_value is None:
            self.setValue(varname, "")

    def newKeyDownToggle(self, keydown, varname):
        self.keyToggles.append((keydown, varname))
        curr_value = self.vars.get(varname)
        if curr_value is None:
            self.setValue(varname, True)

    def highScoreEntry(self, text_entry):
        self.user = text_entry

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

    def setTextVars(self):
        for textbox, pre_text, varname, post_text in self.textVars:
            value = self.getValue(varname)
            textbox.set_text(f"{pre_text}{value}{post_text}")

    def setAll(self):
        self.setSliders()
        self.setToggles()
        self.setTextVars()
    
    def runEvent(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for button, varname, value in self.buttons:
                if event.ui_element == button:
                    if varname is not None:
                        self.vars[varname] = value
                        self.button_sound.play()
                    continue
            for button, varname, _, _ in self.toggleButtons:
                if event.ui_element == button:
                    if varname is not None:
                        self.vars[varname] = not self.vars[varname]
                    continue
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            for slider, varname, increment, text in self.sliders:
                if event.ui_element == slider:
                    value = round(event.value / increment) * increment
                    if varname is not None:
                        self.setValue(varname, value)
                    continue
        elif event.type == pygame.KEYDOWN:
            for keydown, varname in self.keyToggles:
                if event.key == keydown:
                    if varname is not None:
                        self.vars[varname] = not self.vars[varname]
                    continue
        gui_manager.process_events(event)


class ScreenElements:
    def __init__(self, gui, events, colour=(0, 0, 0)):
        self.my_gui = gui
        self.my_events = events
        self.colour = colour
        self.objects = []
        self.focusobjects = []

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
        return new_text

    def newTextVar(self, x_pos, y_pos, x_dim, y_dim, pre_text, varname, post_text, font_size=6):
        new_text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((x_pos, y_pos), (x_dim, y_dim)), 
            html_text=f"<font size={font_size}> </font>", manager=self.my_gui)
        new_text.visible = False
        self.objects.append(new_text)
        self.my_events.newTextVar_(new_text, pre_text, varname, post_text)
        return new_text

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

    def highScoreTextEntry(self, x_pos, y_pos, x_dim, y_dim, text, font_size=6):
        new_entry = pygame_gui.elements.UITextEntryBox(relative_rect=pygame.Rect((x_pos + x_dim // 2, y_pos), (x_dim // 2, y_dim)), 
            initial_text="Default User", manager=self.my_gui)
        new_entry.visible = False
        new_entry.background_colour = pygame.Color("#444444")
        new_entry.text_horiz_alignment = "left"
        new_entry.rebuild()
        link_text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((x_pos, y_pos), (x_dim // 2, y_dim)), 
            html_text=f"<font size={font_size}>{text}</font>", manager=self.my_gui)
        link_text.visible = False
        link_text.text_horiz_alignment = "right"
        link_text.rebuild()
        self.objects.append(new_entry)
        self.focusobjects.append(new_entry)
        self.objects.append(link_text)
        self.my_events.highScoreEntry(new_entry)

    def show(self):
        display.fill(self.colour)
        for object in self.objects:
            object.show()
        for object in self.focusobjects:
            object.focus()
        
    def hide(self):
        for object in self.objects:
            object.hide()
        for object in self.focusobjects:
            object.unfocus()

class HighScores:
    def __init__(self, filename):
        self.filename = filename
        self.scores = []
        with open(filename, "r") as file:
            for line in file:
                if len(line.split(", ")) < 2:
                    continue
                name = line.split(", ")[0]
                score = int(line.split(", ")[1])
                self.scores.append((name, score))
        self.sortScores()
    
    def sortScores(self):
        self.scores = sorted(self.scores, key=lambda x: x[1], reverse=True)

    def getNames(self):
        names = ""
        for name, _ in self.scores:
            names += name + '\n'
        return names
    
    def getScores(self):
        out_scores = ""
        for _, score in self.scores:
            out_scores += f"{score}\n"
        return out_scores
    
    def scoreIsHigh(self, score):
        return score > self.scores[-1][1]
    
    def saveScores(self):
         with open(self.filename, "w") as file:
            for name, score in self.scores:
                file.write(f"{name}, {score}\n")

    def addScore(self, name, score):
        self.scores.append((name, score))
        self.sortScores()
        while len(self.scores) > 10:
            self.scores.pop()
        self.saveScores()


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
font_path = os.path.join(current_directory, 'assets/Mantinia Regular.ttf')
gui_manager.add_font_paths('Mantinia Regular', font_path)
for size in range(1, 49):
    font_list.append({'name': 'Mantinia Regular', 'point_size': size, 'style': 'regular'})
gui_manager.preload_fonts(font_list)
gui_manager.get_theme().load_theme(os.path.join(current_directory, 'assets/theme.json'))
game_music = os.path.join(current_directory, 'assets/gamemusic.mp3')

high_scores = HighScores(os.path.join(current_directory, 'assets/scores.txt'))
event_handler.setValue("names", high_scores.getNames())
event_handler.setValue("scores", high_scores.getScores())

# Main Menu
main_menu = ScreenElements(gui_manager, event_handler)
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
settings = ScreenElements(gui_manager, event_handler)
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
highscore_menu = ScreenElements(gui_manager, event_handler)
screens.append(highscore_menu)
highscore_menu.newText(0, 0, 800, 100, "Top Scores", 7)
highscore_menu.newButton(300, 500, 200, 50, "Return to Main Menu", "menustate", 0)
names = highscore_menu.newTextVar(0, 100, 390, 400, "", "names", "", 6)
scores = highscore_menu.newTextVar(410, 100, 390, 400, "", "scores", "", 6)
names.text_horiz_alignment = "right"
names.rebuild()
scores.text_horiz_alignment = "left"
scores.rebuild()

# Gameplay
endgame = ScreenElements(gui_manager, event_handler)
screens.append(endgame)
endgame.newText(0, 150, 800, 100, "<font color='#FF0000'>YOU DIED</font>", 7)
endgame.newButton(300, 500, 200, 50, "Return to Main Menu", "checkscore", 1)
endgame.newTextVar(0, 400, 800, 100, "Score: ", "score", "", 6)

# Highscore Entry
enter_name = ScreenElements(gui_manager, event_handler)
enter_name.highScoreTextEntry(200, 350, 400, 50, "Enter Name: ", 6)
enter_name.newText(0, 250, 800, 50, "Top 10 Score!", 6)

# Keyboard Inputs
event_handler.newKeyDownToggle(pygame.K_m, "mutemusic")

# Default Values
event_handler.setValue("menustate", len(screens))
event_handler.setValue("checkscore", 0)
event_handler.setValue("gamestart", 0)
event_handler.setValue("quitgame", 0)
event_handler.setValue("width", 10)
event_handler.setValue("height", 20)
event_handler.setValue("speed", 3)
event_handler.setValue("ext_shapes", False)
event_handler.setValue("AI_mode", False)
event_handler.setValue("score_entry", False)
event_handler.setValue("mutemusic", False)

# Run game
clock = pygame.time.Clock()
pygame.mixer.music.load(os.path.join(current_directory, 'assets/music.mp3'))
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
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        event_handler.runEvent(event)

    gui_manager.update(clock.tick(60) / 1000.0)

    # Music
    if event_handler.getValue("mutemusic"):
        pygame.mixer.music.set_volume(0)
    else:
        pygame.mixer.music.set_volume(1)

    # Quit game
    if event_handler.getValue("quitgame") == 1:
        is_running = False

    # Hide and show screen elements
    current_screen = event_handler.getValue("menustate")
    if event_handler.getValue("gamestart") == 1:
        current_screen = len(screens)
    for i in range(len(screens)):
        if current_screen == i:
            screens[i].show()
            # Restart music
            if i == 0 and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(os.path.join(current_directory, 'assets/music.mp3'))
                pygame.mixer.music.play(-1)
        else:
            screens[i].hide()

    # Show text entry for high score
    if event_handler.getValue("score_entry"):
        enter_name.show()
    else:
        enter_name.hide()
    
    # Set screen elements and draw screen
    event_handler.setAll()
    gui_manager.draw_ui(display)
    pygame.display.flip()

    # Play game
    if event_handler.getValue("gamestart") == 1:
        pygame.mixer.music.stop()
        event_handler.setValue("gamestart", 0)
        event_handler.setValue("score", startGame(event_handler.getValue("width"), event_handler.getValue("height"), event_handler.getValue("ext_shapes"), 
                          event_handler.getValue("speed"), event_handler.getValue("AI_mode"), display, gui_manager, game_music, font_path))
        event_handler.setValue("menustate", 3)
        if high_scores.scoreIsHigh(event_handler.getValue("score")) and not event_handler.getValue("AI_mode"):
            event_handler.setValue("score_entry", True)
        gameover_sound.play()

    # Handle score on game over
    if event_handler.getValue("checkscore") == 1:
        event_handler.setValue("checkscore", 0)
        if event_handler.getValue("AI_mode"):
            high_scores.addScore("AI", event_handler.getValue("score"))
        else:
            high_scores.addScore(event_handler.getUser(), event_handler.getValue("score"))
        event_handler.setValue("names", high_scores.getNames())
        event_handler.setValue("scores", high_scores.getScores())
        event_handler.setValue("score_entry", False)
        event_handler.setValue("menustate", 0)

# Save scores from current session before quit    
high_scores.saveScores()
pygame.quit()