import sys, pygame, random
from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN

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

screen = pygame.display.set_mode(SIZE)
WINGS_DOWN_IMG = pygame.image.load(ALIEN_WINGS_DOWN_IMAGE_FILE).convert()
WINGS_UP_IMG = pygame.image.load(ALIEN_WINGS_UP_IMAGE_FILE).convert()

class Alien(pygame.sprite.Sprite):
    velocity = [15, 0]
    moving_down = False
    image = WINGS_UP_IMG

    @classmethod
    def toggle_image(cls):
        if cls.image == WINGS_UP_IMG: # alternate alien images
            cls.image = WINGS_DOWN_IMG
        else:
            cls.image = WINGS_UP_IMG

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
        self.rect = Alien.image.get_rect()
        self.rect = self.rect.move(x-self.rect.left, y-self.rect.top) # move to (x, y)

    def update(self):
        """
        Updates the alien's coordinates.  Reverses the alien's velocity at
        random or if it hits the edges of the window.

        """
        if Alien.moving_down:
            self.rect = self.rect.move(DOWN)
            return
        self.rect = self.rect.move(Alien.velocity)
        if self.rect.left < 0 or self.rect.right > WIDTH: # Alien is outside of
                                                    # window
            Alien.moving_down = True
            Alien.velocity[0] = -Alien.velocity[0]
            self.rect = self.rect.move(Alien.velocity)
            self.rect = self.rect.move(DOWN)

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
        """
        Initializes laser just above player's position.

        Parameters:
        -----------
        player_rect: pygame.rect
            A rect that contains the bounds of the players rectangular image

        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(LASER_IMAGE_FILE).convert()
        x, y = calculate_position(player_rect)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(-self.rect.left+x, -self.rect.top+y)

    def calculate_position(self, player_rect):
        """
        Determine the proper coordinates to place the laser at the tip of the
        player's cannon.

        Parameters:
        -----------
        player_rect: pygame.rect
            A rect that contains the bounds of the players rectangular image

        Returns:
        --------
        x, y: ints
            Coordinates of laser
        """
        x = ((player_rect.left + player_rect.right) / 2) - \
            ((self.rect.right - self.rect.left) / 2)  # line up bullet with
                                    # center of player sprite
        y = player_rect.top + (self.rect.bottom - self.rect.top) # align
                                # bottom of bullet with top of player sprite
        return x, y
    def move(self):
        self.rect = self.rect.move(UP)

    def is_off_screen(self):
        if self.rect.bottom < 0:
            return True
        else:
            return False

def create_alien_fleet():
    """
    Initializes and returns alien fleet as two dimensional array of Alien
    objects. Earlier rows of aliens are displayed higher on the screen than
    later rows, and aliens within each row are ordered from furthest left to
    furthest right.

    """
    alien_fleet = []
    for y in range(ALIEN_ROWS): # space aliens throughout top of window
        alien_row = [Alien(x*HORIZONTAL_SPACING, y*VERTICAL_SPACING) \
                     for x in range(ALIENS_PER_ROW)]
        alien_fleet.append(alien_row)
    return alien_fleet

def update_player_position(screen, player, keys_pressed):
    """
    Updates player_position according to keys being pressed

    Parameters:
    -----------
    screen: pygame.Surface
        A surface representing the window that all game objects are drawn to.
    player: Player
        A Player containing a rect to move around the screen.
    keys_pressed: list
        List containing the keys currently being pressed by the player.

    """
    if keys_pressed[K_LEFT] and keys_pressed[K_RIGHT]:
        pass
    elif keys_pressed[K_LEFT]:
        player.move(LEFT)
    elif keys_pressed[K_RIGHT]:
        player.move(RIGHT)
    screen.blit(player.image, player.rect)

def update_laser_positions(screen, player, laser_list, keys_pressed):
    """
    Moves existing lasers along the screen and adds new lasers if the up arrow
    key is pressed.

    Parameters:
    -----------
    screen: pygame.Surface
        A surface representing the window that all game objects are drawn to.
    player: Player
        A Player containing a rect to move around the screen.
    laser_list: pygame.sprite.Group
        A group containing all of the lasers currently on the screen
    keys_pressed: list
        List containing the keys currently being pressed by the player.

    """
    if keys_pressed[K_UP]:
        laser = Laser(player.rect)
        laser_list.add(laser)
    for laser in laser_list:
        laser.move()
        if laser.is_off_screen():
            laser.kill()
    laser_list.draw(screen)

def update_alien_fleet(screen, alien_fleet, alien_group, counter):
    """
    Updates alien positions.

    Parameters:
    -----------
    screen: pygame.Surface
        A surface representing the window that all game objects are drawn to.
    alien_fleet: list of list of Alien objects
        2-d list containing entire alien fleet, both alive and dead.
    alien_group: pygame.sprite.Group
        Group containing aliens on screen.
    counter: int
        The total number of ticks elapsed since the game started.

    """
    if Alien.velocity[0] < 0: # fleet moving left
        for alien_row in alien_fleet: # move and redraw aliens
            for alien in alien_row:
                if (counter % ALIEN_MOVE_PERIOD) == 0:
                    Alien.toggle_image()
                    alien.update()
    else: # fleet moving right
        for alien_row in alien_fleet:
            for alien in alien_row[::-1]: # reverse row so that the first
                # alien to contact the window boundaries will be updated
                # first
                if (counter % ALIEN_MOVE_PERIOD) == 0:
                    Alien.toggle_image()
                    alien.update()
    if Alien.moving_down:
        Alien.moving_down = False
    alien_group.draw(screen)

def remove_collisions(alien_fleet, laser_list):
    """
    Clears aliens and lasers that collided from screen.

    Parameters:
    -----------
    alien_fleet: list of list of Alien objects
        List containing all of the aliens remaining on screen.
    laser_list: pygame.sprite.Group
        A group containing all of the lasers currently on the screen

    """
    for alien_row in alien_fleet:
        for alien in alien_row:
            lasers_hit = pygame.sprite.spritecollide(alien, laser_list, True)
            if lasers_hit:
                alien.kill() # remove alien from all groups it is a part of,
                             # stops it from being redrawn

def run():
    """Runs the game until one of the following game over conditions is met:
            The player dies
            All aliens die
            The game window is closed
       Moves aliens and allows for keyboard controlled player movement.

    """
    player = Player()
    alien_fleet = create_alien_fleet() # all aliens, alive and dead
    alien_group = pygame.sprite.Group() # live aliens
    for alien_row in alien_fleet:
        for alien in alien_row:
            alien_group.add(alien)
    laser_list = pygame.sprite.Group()

    t_elapsed = 0 # number of game ticks
    while True:
        if not alien_group:
            pygame.time.delay(1000)
            raise SystemExit # temporary Game Over mechanism
        screen.fill(BLACK) # clear screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        keys_pressed = pygame.key.get_pressed()
        update_player_position(screen, player, keys_pressed)
        update_laser_positions(screen, player, laser_list, keys_pressed)
        update_alien_fleet(screen, alien_fleet, alien_group, t_elapsed)
        remove_collisions(alien_fleet, laser_list)
        alien_group.draw(screen)
        pygame.display.flip()
        t_elapsed += 1
        pygame.time.delay(DELAY)

if __name__ == "__main__":
    run()
