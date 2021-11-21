import random
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '1500')
Config.set('graphics', 'height', '1000')

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout): 
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up
    
    menu_button = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    
    # Vertical Lines
    V_NUM_LINES = 8 # Number of vertical lines should be odd to implement central line
    V_LINES_SPACE = .4 # Percentage of screen WIDTH
    vertical_lines = []
    
    # Horizontal Lines
    H_NUM_LINES = 15
    H_LINES_SPACE = .1 # Percentage of screem HEIGHT
    horizontal_lines = []

    SPEED = .8
    current_offset_y = 0
    current_y_loop = 0

    SPEED_X = 3.0
    current_speed_x = 0
    current_offset_x = 0
      
    NUM_TILES = 16
    tiles = []
    tiles_coordinates = []
    
    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]
      
    state_game_over = False
    state_game_start = False
    
    menu_title = StringProperty('V  A  P  O  R     R  U  N  N  E  R')
    menu_button_title = StringProperty("S  T  A  R  T")
    home_button_title = StringProperty("H  O  M  E")
    score_txt = StringProperty()
    
    # Sound Queues
    sound_menu = None
    sound_begin = None
    sound_restart = None
    sound_game_over = None
    sound_theme = None
    
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.restart_game()
        
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down = self.on_keyboard_down)
            self._keyboard.bind(on_key_up = self.on_keyboard_up)
            
        Clock.schedule_interval(self.update, 1.0 / 60.0) # Update the flow of our horizontal lines 1/16 of a second
        self.sound_menu.play()
    
    
    def init_audio(self):
        self.sound_menu = SoundLoader.load("audio/Menu Theme.wav")
        self.sound_begin = SoundLoader.load("audio/Menu Button.wav")
        self.sound_game_over = SoundLoader.load("audio/Game Over.wav")
        self.sound_theme = SoundLoader.load("audio/Hide Away.wav")
        self.sound_restart = SoundLoader.load("audio/Menu Button.wav")
        
        self.sound_theme.volume = .25
        self.sound_begin.volume = .25
        self.sound_game_over.volume = .25
        self.sound_restart.volume = .25
        self.sound_menu.volume = .15
    
    def restart_game(self):
        # We need reinitialize most of our variables and functions
        # To reset the game to its start state again
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.tiles_coordinates = []
        
        # Recall the tile functions to regenerate our tiles
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.score_txt = "SCORE: " + str(self.current_y_loop)
        self.state_game_over = False
    
    def highscore(self):
        pass
    
    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False
    
    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()
    
    # We allow our ship to move along the tiles and adjust its collision contact point
    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height
        
        self.ship_coordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        # Expand our arguments using (*) so that we can pass 
        # The 2 arguments from ship_coordinates above^
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]
        
    # Collision point is adjusted here and user is given more flexibility
    # So that if our ship is half way off the track game over will not trigger
    # Making the movement along the track more fluid
    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            tile_x, tile_y = self.tiles_coordinates[i]
            if tile_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(tile_x, tile_y):
                return True
        return False
            
    def check_ship_collision_with_tile(self, tile_x, tile_y):
        xmin, ymin = self.get_tile_coordinates(tile_x, tile_y)
        xmax, ymax = self.get_tile_coordinates(tile_x + 1, tile_y + 1)
        
        # Check to see if we are still inside the tile
        # If we are in the tile we return true
        # Otherwise we will print game over to user
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False
    
    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NUM_TILES):
                self.tiles.append(Quad())
           
        
    def pre_fill_tiles_coordinates(self):
        for i in range(0, 15):
            self.tiles_coordinates.append((0, i))
            
    # We create an algorithm here to generate the tiles at random  
    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0
        
        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        print("foo1")

        for i in range(len(self.tiles_coordinates), self.NUM_TILES):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            
            start_index = -int(self.V_NUM_LINES / 2) + 1   # Border for start of plane
            end_index = start_index + self.V_NUM_LINES - 2 # Border for end of plane
            
            
            # We add collision statements to force the generated tiles within the plain
            # If the tiles are generated outside of our start index we force it to the right
            # From the end, we force it to the left
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

        print("foo2")

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_NUM_LINES):
                self.vertical_lines.append(Line())
                
    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACE * self.width
        offset = index - 0.5
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACE * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y
    
    def get_tile_coordinates(self, tile_x, tile_y):
        tile_y = tile_y - self.current_y_loop
        x = self.get_line_x_from_index(tile_x)
        y = self.get_line_y_from_index(tile_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.NUM_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0] + 1, tile_coordinates[1] + 1)
        
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
        
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_index = -int(self.V_NUM_LINES / 2) + 1
        for i in range(start_index, start_index + self.V_NUM_LINES):
            line_x = self.get_line_x_from_index(i) # Create the spacing between each vertical line starting from the left

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]
    
    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NUM_LINES):
                self.horizontal_lines.append(Line())
    
    def update_horizontal_lines(self):
        start_index = -int(self.V_NUM_LINES / 2) + 1
        end_index = start_index + self.V_NUM_LINES - 1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        
        for i in range(0, self.H_NUM_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]
            
    def update(self, dt):
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        
        
        # Stop game when we go out of track
        if not self.state_game_over and self.state_game_start:
            self.sound_menu.stop()
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor
        
            spacing_y = self.H_LINES_SPACE * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = "SCORE: " + str(self.current_y_loop)
                self.generate_tiles_coordinates()
                print("loop: " + str(self.current_y_loop))

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor
        
        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.menu_title = "G  A  M  E    O  V  E  R"
            self.menu_button_title = "R  E  S  T  A  R  T"
            self.menu_button.opacity = 1
            self.sound_theme.stop()
            self.sound_game_over.play()
            print("GAME OVER")
            
    def play_game_over_sound(self, dt):
        if self.state_game_over:
            self.sound_game_over.play() 
            
    def menu_button_pressed(self):
        print("BUTTON")
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_theme.play()
        self.restart_game()
        self.state_game_start = True
        self.menu_button.opacity = 0
            
class GalaxyApp(App):
    pass

GalaxyApp().run()
