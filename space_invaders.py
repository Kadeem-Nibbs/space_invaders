import sys, pygame, random
from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN
from random import randrange

pygame.init()

DELAY = 100 # delay between graphic refresh cycles in ms
ALIEN_WINGS_DOWN_IMAGE_FILE = "alien.bmp"
ALIEN_WINGS_UP_IMAGE_FILE = "alien_wings_up.png"
PLAYER_IMAGE_FILE = "cannon.jpg"
LASER_IMAGE_FILE = "laser.jpg"

SCREEN_ROWS = 10 # number of rows that aliens descend through
SIZE = WIDTH, HEIGHT = (600, 400) # screen dimensions in pixels
ALIEN_ROWS = 3
ALIENS_PER_ROW = 3
HORIZONTAL_SPACING = WIDTH / ALIENS_PER_ROW # space between alien fleet
                                    # columns
VERTICAL_SPACING = HEIGHT / SCREEN_ROWS # space between alien fleet rows

ALIEN_SPEED = 15
ALIEN_MOVE_PERIOD = 5 # How many refresh cycles it takes for aliens to be
                # redrawn

PLAYER_SPEED = 15
LASER_SPEED = 15

RIGHT = (PLAYER_SPEED, 0) # increments of player movement
LEFT = (-PLAYER_SPEED, 0) # ...
DOWN = (0, ALIEN_SPEED) # increment of alien movement
UP = (0, -LASER_SPEED)

BLACK = (0, 0, 0)
alien_velocity = [ALIEN_SPEED, 0] # first index is x velocity,
                        # second is y velocity
                        # all alien's share this velocity

screen = pygame.display.set_mode(SIZE)
WINGS_DOWN = pygame.image.load(ALIEN_WINGS_DOWN_IMAGE_FILE).convert()
WINGS_UP = pygame.image.load(ALIEN_WINGS_UP_IMAGE_FILE).convert()
alien_image = WINGS_DOWN

class Alien(pygame.sprite.Sprite):

    def __init__(self, x, y):
        """
        Initialize alien with coordinates (x, y).

        Parameters:
        -----------
        x: positive real number
            The x coordinate at which to initialize the alien.  Floating point
            numbers are converted to ints.
        y: positive real number
            The y coordinate at which to initialize the alien.  Floating point
            numbers are converted to ints.

        """
        pygame.sprite.Sprite.__init__(self)
        self.image = alien_image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x-self.rect.left, y-self.rect.top) # move
                                                    # to (x, y)
        self.velocity = alien_velocity

    def update(self):
        """
        Updates the alien's coordinates.  Reverses the alien's velocity at
        random or if it hits the edges of the window.

        """
        self.rect = self.rect.move(self.velocity)
        if self.rect.left < 0 or self.rect.right > WIDTH: # Alien is outside of
                                                    # window
            self.velocity[0] = -self.velocity[0]
            self.rect = self.rect.move(self.velocity)
            self.rect = self.rect.move(self.velocity)
            self.velocity[1] = ALIEN_SPEED # comment out this and following
                            # line to not have aliens get closer
            self.rect = self.rect.move(DOWN)
        if self.image == WINGS_UP: # alternate alien images
            self.image = WINGS_DOWN
        else:
            self.image = WINGS_UP

class Player(pygame.sprite.Sprite):

    def __init__(self):
        """
        Initializes player at bottom of window.

        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(PLAYER_IMAGE_FILE).convert()
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(0, HEIGHT-self.rect.bottom)

    def move(self, direction):
        """
        Moves player sprite in specified direction. Won't let player sprite
        move outside the window's bounds.

        Parameters:
        -----------
        direction: 2-tuple of ints
            (pixels to the right, pixels to the left)
        """
        self.rect = self.rect.move(direction)
        if self.rect.left < 0: # move player back onto screen
            self.rect = self.rect.move(-self.rect.left, 0)
        elif self.rect.right > WIDTH:
            self.rect = self.rect.move(WIDTH-self.rect.right, 0)

class Laser(pygame.sprite.Sprite):

    def __init__(self, player_rect):
        self.image = pygame.image.load(LASER_IMAGE_FILE).convert()
        self.rect = self.image.get_rect()
        x = ((player_rect.left + player_rect.right) / 2) - \
            ((self.rect.right - self.rect.left) / 2)  # line up bullet with
                                    # center of player sprite
        y = player_rect.top + (self.rect.bottom - self.rect.top) # align
                                # bottom of bullet with top of player sprite
        self.rect = self.rect.move(-self.rect.left+x, -self.rect.top+y)

    def move(self):
        self.rect = self.rect.move(UP)

def update_player_position(screen, player, keys_pressed):
    if keys_pressed[K_LEFT] and keys_pressed[K_RIGHT]:
        pass
    elif keys_pressed[K_LEFT]:
        player.move(LEFT)
    elif keys_pressed[K_RIGHT]:
        player.move(RIGHT)
    screen.blit(player.image, player.rect)

def update_laser_positions(screen, player, laser_list, keys_pressed):
    if keys_pressed[K_UP]:
        laser = Laser(player.rect)
        laser_list.append(laser)
    for laser in laser_list:
        laser.move()
        screen.blit(laser.image, laser.rect)

def create_alien_fleet():
    alien_fleet = []
    for y in range(ALIEN_ROWS): # space aliens throughout top of window
        alien_row = [Alien(x*HORIZONTAL_SPACING, y*VERTICAL_SPACING) \
            for x in range(ALIENS_PER_ROW)]
        alien_fleet.append(alien_row)
    return alien_fleet

def update_alien_positions(screen, alien_fleet, counter):
    if alien_velocity[0] < 0: # fleet moving left
        for alien_row in alien_fleet: # move and redraw aliens
            for alien in alien_row:
                if (counter % ALIEN_MOVE_PERIOD) == 0:
                    alien.update()
                screen.blit(alien.image, alien.rect)
    else: # fleet moving right
        for alien_row in alien_fleet:
            for alien in alien_row[::-1]: # reverse row so that the first
                # alien to contact the window boundaries will be updated
                # first
                if (counter % ALIEN_MOVE_PERIOD) == 0:
                    alien.update()
                screen.blit(alien.image, alien.rect)
    if alien_velocity[1]:
        alien_velocity[1] = 0

def run():
    """Runs the game until one of the following game over conditions is met:
            The player dies
            All aliens die
            The game window is closed
       Moves aliens and allows for keyboard controlled player movement.

    """
    player = Player()
    alien_fleet = create_alien_fleet()
    laser_list = []

    counter = 0 # number of game ticks
    while True:
        screen.fill(BLACK) # clear screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        keys_pressed = pygame.key.get_pressed()
        update_player_position(screen, player, keys_pressed)
        update_laser_positions(screen, player, laser_list, keys_pressed)
        update_alien_positions(screen, alien_fleet, counter)

        pygame.display.flip()
        counter += 1
        pygame.time.delay(DELAY)

if __name__ == "__main__":
    run()