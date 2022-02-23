import random as rand
import nxbt
import time
import sys

from Pattern import Pattern
from Color import Color

class Controller():
    def __init__(self, pattern:Pattern, debug=False) -> None:
        if not debug:
            self.nx = nxbt.Nxbt()
            self.pro_controller = self.nx.create_controller(nxbt.PRO_CONTROLLER)
            self.nx.wait_for_connection(self.pro_controller)
        
        self.total_index_changes = 0 #This mod 16 will give the current color index
        self.xPos = 0
        self.yPos = 0
        self.pattern = pattern
    
    def reset_canvas_pos(self) -> None:
        for x in range(16):
            self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_UP, nxbt.Buttons.DPAD_LEFT])
    
    def return_to_orgin(self) -> None:
        for x in range(max(self.xPos + 10, self.yPos + 10)):
        #Note that becuase we go an extra 10 presses, we can ensure we really are at 0, 0
            if x < self.xPos + 10:
                self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_LEFT])
            if x < self.yPos + 10:
                self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_UP])
        self.xPos = 0 
        self.yPos = 0
    
    def get_current_pos(self) -> 'tuple[int]':
        return self.xPos, self.yPos
    
    def get_point_sign(self, current_point:int, destination_point:int) -> int:
        if destination_point < current_point:
            return 1
        return -1
    
    def get_point_distance(self, destination_point:int, current_point:int) -> int:
        return abs(destination_point - current_point) * self.get_point_sign(destination_point, current_point)

    def move_to_location(self, x_point:int, y_point:int) -> None:
        xTravel = self.get_point_distance(x_point, self.xPos)
        yTravel = self.get_point_distance(y_point, self.yPos)

        for x in range(max(abs(xTravel), abs(yTravel))):

            if x < abs(xTravel):
                if xTravel > 0:
                    self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_RIGHT])
                    self.xPos += 1
                else:
                    self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_LEFT])
                    self.xPos -= 1
            
            if x < abs(yTravel):
                if yTravel > 0:
                    self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_DOWN])
                    self.yPos += 1
                else:
                    self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_UP])
                    self.yPos -= 1
    
    def certify_current_point(self) -> None:
        xHome = self.xPos
        yHome = self.yPos

        self.return_to_orgin()
        self.select_eye_dropper()
        self.total_index_changes = self.pattern.pattern_matrix[0][0]

        self.move_to_location(xHome, yHome)
    
    def get_nearest_validated(self) -> 'tuple[int]':
        col_point = 0
        if self.yPos % 4 == 0:
            col_point = self.xPos // 4
        else:
            col_point = min(round(self.xPos / 4), 7)
        return col_point*4, self.yPos // 4 * 4

    def correct_curent_point(self) -> None:
        point = self.get_nearest_validated()
        xHome = self.xPos
        yHome = self.yPos

        self.move_to_location(point[0], point[1])
        self.select_eye_dropper()
        self.total_index_changes = self.pattern.pattern_matrix[point[1]][point[0]]
        self.move_to_location(xHome, yHome)

    def select_color_tool(self) -> None:
        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.X])
        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_UP, nxbt.Buttons.DPAD_RIGHT], down=0.1)
        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.A])
    
    def select_pencil_from_color_tool(self) -> None:
        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_DOWN, nxbt.Buttons.DPAD_LEFT], down=0.1)
        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.A])
    
    def select_eye_dropper(self) -> None:
        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.R, nxbt.Buttons.L])

    def adjust_slider(self, value:int, reset_time:float) -> None:
        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_LEFT], down=reset_time) #This resets the slider value to 0
        for x in range(value):
            self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_RIGHT]) #Adjusting slider to desired value
    
    def adjust_color(self, hue:int, vividness:int, brighness:int) -> None:
        self.adjust_slider(hue, 3) #Changing the hue slider to the desired value

        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_DOWN]) #Moving to vividness slider
        self.adjust_slider(vividness, 2.75)

        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_DOWN]) #Moving to brightness slider
        self.adjust_slider(brighness, 2.75)

    def adjust_palette(self) -> None:
        self.select_color_tool()
        for x in self.pattern.palette:
            time.sleep(1)
            self.adjust_color(x.hue, x.vividness, x.brightness)
            time.sleep(1)
            self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.R])
            self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_DOWN])
        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.A])
    
    def change_color(self, color_index:int) -> None:
        if color_index > 15:
            raise ValueError("Color index cannot be larger than 15")
            
        normal_change = color_index - self.total_index_changes % 16

        #to find wraped change, go the other way from the normal change
        if normal_change > 0:
            wrapped_change = (self.total_index_changes % 16 * -1) + 1 + ((15 - color_index)*-1) -2 
        else: 
            wrapped_change =  (15 - self.total_index_changes % 16) + 1 + color_index
        
        if abs(normal_change) <= abs(wrapped_change):
            change = normal_change
        else:
            change = wrapped_change
        
        if change > 0:
            action = nxbt.Buttons.R
        else:
            action = nxbt.Buttons.L
        
        for x in range(abs(change)):
            self.nx.press_buttons(self.pro_controller, [action], down=0.3)
            time.sleep(0.3)
        
        self.total_index_changes += change
        
    def fill_pixel(self, color_index:int) -> None:
        self.change_color(color_index)
        self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.A])
    
    def fill_pattern(self) -> None:

        for i, r in enumerate(self.pattern.pattern_matrix):
            x_increment:int
            action:nxbt.Buttons
            reverse_function:function

            if i % 2 == 0:
                x_increment = 1
                action = nxbt.Buttons.DPAD_RIGHT
                reverse_function = lambda x: x
            else:
                x_increment = -1
                action = nxbt.Buttons.DPAD_LEFT
                reverse_function = reversed
            
            for c in reverse_function(r):
                self.fill_pixel(c)
                self.nx.press_buttons(self.pro_controller, [action])
                time.sleep(0.2)
                self.xPos += x_increment
            
            self.nx.press_buttons(self.pro_controller, [nxbt.Buttons.DPAD_DOWN])
            self.yPos += 1
    
    def test_color_indexing(self):
        count = 0
        last_num = 0
        while True:
            count += 1
            num = rand.randint(0, 15)

            print(f"Adjusting color to index {num} from {last_num} | {count} changes have been done in total")
            self.change_color(num)
            last_num = num
            
            time.sleep(1)

def main():
    pattern = Pattern.load_from_file(sys.argv[1])
    control = Controller(pattern)
    input("Press enter to continue with script execution: ")
    control.reset_canvas_pos()
    time.sleep(1)
    control.adjust_palette() #After this, press A to exit the menu
    time.sleep(1)
    control.select_pencil_from_color_tool()
    time.sleep(1)
    control.fill_pattern()
    control.move_to_location(12, 18)
    control.certify_current_point()
    print("Done!")

def test_main():
    pattern = Pattern.load_from_file(sys.argv[1])
    control = Controller(pattern, debug=True)
    control.xPos = 3
    control.yPos = 5
    print(control.get_nearest_validated())

if __name__ == "__main__":
    test_main()