import os, sys
import pygame
from pygame.locals import * # Adds constants and functions into global namespace

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')

WIDTH,HEIGHT = 468,60
TITLE = "Monkey Fever"

def load_image(name, colorkey=None):
    # Create working pathname for any OS
    fullname = os.path.join('data', name) 
    try:
        # Load Image
        image = pygame.image.load(fullname) 
    except pygame.error as message:
        # Print error message and gracefully exit
        print('Cannot load image: ', name)
        raise SystemExit(message)

    # Converts color format and depth to match display
    image = image.convert()
    
    if colorkey is not None:
        if colorkey is -1:
            # Set color key to color of pixel at 0,0
            colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    # Create class with dummy play method 
    class NoneSound:
        def play(self): pass

    if not pygame.mixer:
        return NoneSound()

        #Create working pathname for any OS
    fullname = os.path.join('data', name)

    try:
        # Load Sound
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        # Print error message and gracefully exit
        print('Cannot load sounds: ', wav)
        raise SystemExit(message)
    return sound

class Fist(pygame.sprite.Sprite):
    """Moves a clenched fist on the screen, following the mouse"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self) # Call Sprite Initializer
        self.image, self.rect = load_image('fist.bmp', -1)
        self.punching = 0

    def update(self): # Called once per frame
        """Move the fist based on mouse position"""
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos # Moves fist to mouse.get_pos()
        if self.punching:
            self.rect.move_ip(5, 10) # Offsets fist slightly when punching

    def punch(self, target):
        """Returns true if the fist collides with the target"""
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5,-5) 
            return hitbox.colliderect(target.rect) # Check if self.rect is colliding with target.rect

    def unpunch(self):
        """Called to pull fist back"""
        self.punching = 0

class Chimp(pygame.sprite.Sprite):
    """Moves a monkey across the screen. It can the spin the
        monkey when it is punched"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self) # Call Sprite Initializer
        self.image, self.rect = load_image('chimp.bmp', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10,10
        self.move = 9
        self.dizzy = 0

    def update(self):
        """Walk or spin, depending on the monkeys state"""
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        """Move the monkey across the screen and turn at each end"""
        newpos = self.rect.move((self.move, 0))
        if not self.area.contains(newpos):
            if self.rect.left < self.area.left or self.rect.right > self.area.right: # Turn monkey around at end 
                self.move = -self.move
                newpos = self.rect.move((self.move, 0))
                self.image = pygame.transform.flip(self.image, 1, 0)
            self.rect = newpos

    def _spin(self):
        """Spin the monkey"""
        center = self.rect.center
        self.dizzy += 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def punched(self):
        """Spin Monkey"""
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image

def main():
    pygame.init() # Initialize PyGame
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption(TITLE)
    pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250,250,250))

    if pygame.font:
        font = pygame.font.Font(None, 36) # Use default font
        text = font.render("Pummel the Chimp, and Win $$$", 1, (10,10,10)) # Anti-aliased dark-grey text
        textpos = text.get_rect(centerx=background.get_width()/2)
        background.blit(text,textpos) # Copy pixels onto background

    screen.blit(background, (0,0))
    pygame.display.flip()

    #Sounds
    whiff_sound = load_sound('whiff.wav')
    punch_sound = load_sound('punch.wav')

    # Game Objects
    chimp = Chimp()
    fist = Fist()

    # Simple Render Group
    allsprites = pygame.sprite.RenderPlain((fist,chimp))

    clock = pygame.time.Clock()

    # Game Loop
    while 1:
        clock.tick(60) # 60 FPS

        for event in pygame.event.get():
            # Quit the Game
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return

            # Punch the Monkey
            elif event.type == MOUSEBUTTONDOWN:
                if fist.punch(chimp):
                    punch_sound.play() # PUNCH
                    chimp.punched()
                else:
                    whiff_sound.play() # Miss

            # Retract Fist
            elif event.type == MOUSEBUTTONUP:
                fist.unpunch()
        allsprites.update()

        screen.blit(background, (0,0))
        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()

# Game Over

if __name__ == '__main__':
    main()
