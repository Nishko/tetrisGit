import pygame
import pygame_gui

class EventHandler:
    def __init__(self):
        self.buttons = []
        self.vars = {}

    def defaultValue(self, varname, value):
        self.vars[varname] = value

    def newButtonEvent(self, button, varname, value):
        self.buttons.append((button, varname, value))
        curr_value = self.vars.get(varname)
        if curr_value is None:
            self.defaultValue(varname, value)

    def getValue(self, varname):
        return self.vars.get(varname)
    
    def runEvent(self, event):
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            for button, varname, value in self.buttons:
                if event.ui_element == button:
                    if varname is not None:
                        self.vars[varname] = value


class ScreenState:
    def __init__(self, gui, events):
        self.my_gui = gui
        self.my_events = events
        self.buttons = []
        self.colour = (255, 255, 255)

    def newButton(self, x_pos, y_pos, x_dim, y_dim, button_text, varname, value):
        new_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((x_pos, y_pos), (x_dim, y_dim)), text=button_text, manager=self.my_gui)
        self.buttons.append(new_button)
        self.my_events.newButtonEvent(new_button, varname, value)

    def setColour(self, red, green, blue):
        self.colour = (red, green, blue)

    def show(self):
        display.fill(self.colour)
        for button in self.buttons:
            button.show()
        
    def hide(self):
        for button in self.buttons:
            button.hide() 


pygame.init()
# create display window
display = pygame.display.set_mode((800, 600))
pygame.display.set_caption("The Spectacularly Silly Shape Shuffling Showdown")
# gui manager and event handler
gui_manager = pygame_gui.UIManager((800, 600))
event_handler = EventHandler()
screens = []

# Main Menu
main_menu = ScreenState(gui_manager, event_handler)
screens.append(main_menu)
main_menu.newButton(300, 250, 200, 50, "Settings", "menustate", 1)

# Settings Menu
settings = ScreenState(gui_manager, event_handler)
screens.append(settings)
settings.newButton(300, 250, 200, 50, "Main Menu", "menustate", 0)

# Default Values
event_handler.defaultValue("menustate", 0)

# Run game
clock = pygame.time.Clock()
is_running = True
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        gui_manager.process_events(event)

        if event.type == pygame.USEREVENT:
            event_handler.runEvent(event)

    gui_manager.update(clock.tick(60) / 1000.0)
    current_screen = event_handler.getValue("menustate")
    for i in range(len(screens)):
        if current_screen == i:
            screens[i].show()
        else:
            screens[i].hide()
    gui_manager.draw_ui(display)
    pygame.display.flip()

pygame.quit()