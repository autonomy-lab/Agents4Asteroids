import pyglet
import random
from enum import Enum
from math import cos, sin, pi


class TurnState(Enum):
    """ Is the player currently rotating? """
    STATIONARY = 1
    RIGHT = 2
    LEFT = 3


class BoostState(Enum):
    """ Is the ship moving? """
    STATIONARY = 1
    BOOSTING = 2


def multiplier(fps):
    return ((100 - fps) / 100) if fps < 80 else 0.2


class Particle:
    """ Bullets which are fired from the ship. """

    def __init__(self, centre_x, centre_y, velocity_x, velocity_y):
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def update(self, multiplier):
        """ Update the position of the bullet. """
        self.centre_x += self.velocity_x * multiplier
        self.centre_y += self.velocity_y * multiplier

    def draw(self):
        """ Draw the bullet on the new position. """
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2i', (int(self.centre_x), int(self.centre_y))))


class Ship:
    """ The ship with its constants. """
    def __init__(self, centre_x, centre_y):
        self.facing = 0
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.height = 10
        self.turn_speed = 0.3
        self.turn_state = TurnState.STATIONARY
        self.boost_state = BoostState.STATIONARY
        self.thrust = 0
        self.thrust_max = 2
        self.thrust_incr = 0.4
        self.particle_canon_speed = 20

    def turn_right(self):
        """ Changes the state of the ship if it turns right. """
        self.turn_state = TurnState.RIGHT

    def turn_left(self):
        """ Changes the state of the ship if it turns left. """
        self.turn_state = TurnState.LEFT

    def stop_turn(self):
        """ Changes state if the ship doesn't turn. """
        self.turn_state = TurnState.STATIONARY

    def turn(self, multiplier):
        """ Turns the ship according to the FPS. """
        if self.turn_state is TurnState.RIGHT:
            self.facing -= self.turn_speed * multiplier
        elif self.turn_state is TurnState.LEFT:
            self.facing += self.turn_speed * multiplier

    def boost(self):
        self.boost_state = BoostState.BOOSTING

    def stop_boost(self):
        self.boost_state = BoostState.STATIONARY

    def fire(self):
        """ Returns a particle object that is spawned from the front of the ship. """
        return Particle(
            self.centre_x + (2 * self.height * cos(self.facing)),
            self.centre_y + (2 * self.height * sin(self.facing)),
            self.particle_canon_speed * cos(self.facing),
            self.particle_canon_speed * sin(self.facing)
        )

    def velocity_handler(self):
        """
        Changes the value of the velocity of the ship in x and y axis.
        If the ship is already in the BOOSTING state it will create a higher trust.
        """
        if self.boost_state is BoostState.BOOSTING:
            if self.thrust < self.thrust_max:
                self.thrust += self.thrust_incr
            self.velocity_x += cos(self.facing) * self.thrust
            self.velocity_y += sin(self.facing) * self.thrust
        else:
            self.thrust = 0

    def update(self, window_width, window_height, multiplier):
        """ Update the various variables of the ship. """
        self.turn(multiplier)
        self.velocity_handler()
        self.centre_x += self.velocity_x * multiplier
        self.centre_y += self.velocity_y * multiplier
        if self.centre_x < -10:
            self.centre_x = window_width + 10
        elif self.centre_x > window_width + 10:
            self.centre_x = -10
        if self.centre_y < -10:
            self.centre_y = window_height + 10
        elif self.centre_y > window_height + 10:
            self.centre_y = -10

    def draw(self):
        """ Redraw the ship at the 'new' location. """
        pyglet.graphics.draw_indexed(3, pyglet.gl.GL_LINE_LOOP,
                                     [0, 1, 2],
                                     ('v2i', (int(self.centre_x + (2 * self.height * cos(self.facing))),
                                              int(self.centre_y + (2 * self.height * sin(self.facing))),
                                              int(self.centre_x + (self.height * cos(self.facing + 140))),
                                              int(self.centre_y + (self.height * sin(self.facing + 140))),
                                              int(self.centre_x + (self.height * cos(self.facing - 140))),
                                              int(self.centre_y + (self.height * sin(self.facing - 140)))))
                                     )


class Asteroid:
    """ Handles how the asteroids are being drawn and their velocity and positioning. """
    def __init__(self, centre_x, centre_y, velocity_x, velocity_y, size):
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.radius = size
        self.points = []
        self.num_of_points = 7
        for i in range(0, self.num_of_points):
            self.points.append(random.uniform(self.radius-(self.radius/5), self.radius+(self.radius/5))
                               * cos(i*((2 * pi)/self.num_of_points)))
            self.points.append(random.uniform(self.radius-(self.radius/5), self.radius+(self.radius/5))
                               * sin(i*((2 * pi)/self.num_of_points)))

    def update(self, multiplier):
        self.centre_x += self.velocity_x * multiplier
        self.centre_y += self.velocity_y * multiplier

    def draw(self):
        current_points = []
        for i in range(0, self.num_of_points*2, 2):
            current_points.append(int(self.centre_x + self.points[i]))
            current_points.append(int(self.centre_y + self.points[i+1]))
        pyglet.graphics.draw(self.num_of_points, pyglet.gl.GL_LINE_LOOP, ('v2i', current_points))
