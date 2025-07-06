
# TODO 3D Engine (kinda)
class Engine:
    def __init__(self):
        self.player_coords = (1.00, 1.00)
        self.player_angle = 0 # ]-180;180]

    def turn(self, angle):
        """
        Parameters:
            angle (int): Negative to turn left, positive to turn right, in degrees
        """
        self.player_angle += angle

        while not (-180 < self.player_angle <= 180):
            if self.player_angle > 180:
                self.player_angle -= 360
            elif self.player_angle <= -180:
                self.player_angle += 360

    def move_forward(self, units):
        added_x = units - (0.01*self.player_angle)
        added_y = units + (0.01*self.player_angle)
        self.player_coords = (self.player_coords[0]+added_x, self.player_coords[1]+added_y)
