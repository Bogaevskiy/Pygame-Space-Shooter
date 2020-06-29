# music by tgfcoder - FrozenJam-SeamlessLoop.mp3 <https://twitter.com/tgfcoder> licensed under CC-BY-3
# sound effects made with bfxr - https://www.bfxr.net/
# sprites and art made by Kenney, https://opengameart.org/content/space-shooter-redux

import pygame
import random
import os

width = 800
height = 600
fps = 60

#colors
black = (0, 0, 0)
white = (255, 255, 255)
grey = (100, 100, 100)
red = (120, 0, 0)
b_red = (255, 0, 0)
yellow = (255, 225, 0)
green = (0, 200, 0)

#general
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Another Shooter")
clock = pygame.time.Clock()

#folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
snd_folder = os.path.join(game_folder, 'snd')

#loading sounds
shoot_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'pew.wav'))
no_shoot_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'no_shoot.wav'))
powerup_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'powerup.wav'))
player_expl_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'player_explosion.wav'))
expl_sounds = []
explosions = ['expl3.wav', 'expl6.wav']
for sound in explosions:
    expl_sounds.append(pygame.mixer.Sound(os.path.join(snd_folder, sound)))
pygame.mixer.music.load(os.path.join(snd_folder, 'tgfcoder-FrozenJam-SeamlessLoop.mp3'))
pygame.mixer.music.set_volume(0.3)

#loading graphics
player_img = pygame.image.load(os.path.join(img_folder, 'playerShip2_red.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (20, 20))
player_mini_img.set_colorkey(black)
meteor_images = []
meteor_list = ['meteorBrown_big3.png', 'meteorBrown_big4.png',
               'meteorBrown_med1.png', 'meteorBrown_med3.png',
               'meteorBrown_small1.png', 'meteorBrown_small2.png',
               'meteorBrown_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(img_folder, img)).convert())
laser_img = pygame.image.load(os.path.join(img_folder, 'laserRed07.png')).convert()
background = pygame.image.load(os.path.join(img_folder, 'starfield.png')).convert()
background_rect = background.get_rect
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
expl_folder = os.path.join(img_folder, 'explosions')
for i in range(9):
    filename = 'regularExplosion0' + str(i) + '.png'
    img = pygame.image.load(os.path.join(expl_folder, filename)).convert()
    img.set_colorkey(black)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0' + str(i) + '.png'
    img = pygame.image.load(os.path.join(expl_folder, filename)).convert()
    img.set_colorkey(black)
    explosion_anim['player'].append(img)
powerup_images = {}
powerup_images['shield'] = pygame.image.load(os.path.join(img_folder, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(os.path.join(img_folder, 'bolt_gold.png')).convert()

#classes
class Player(pygame.sprite.Sprite):    
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)        
        self.image = pygame.transform.scale(player_img, (50, 50))
        self.image.set_colorkey(black)        
        self.rect = self.image.get_rect()        
        self.radius = int(self.rect.width * 0.92 / 2)
        self.power = False
        self.power_time = pygame.time.get_ticks()
        self.powerup_length = 4000
        #pygame.draw.circle(self.image, b_red, self.rect.center, self.radius)
        
        self.rect.centerx = width/2
        self.rect.bottom = height -10
        self.speedx = 0
        self.shield = 100
        self.score = 0
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        
    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx

        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left <0:
            self.rect.left = 0
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = width/2
            self.rect.bottom = height -10
        if self.power and pygame.time.get_ticks() - self.power_time > self.powerup_length:
            self.power = False

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            if self.score > 10:
                self.last_shot = now
                bullet = Bullet(self.rect.centerx, self.rect.top, '')
                if self.power:  
                    bullet2 = Bullet(self.rect.centerx, self.rect.top, 'left')
                    bullet3 = Bullet(self.rect.centerx, self.rect.top, 'right')
                    all_sprites.add(bullet, bullet2, bullet3)
                    bullets.add(bullet, bullet2, bullet3)
                else:
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                shoot_sound.play()
                self.score -= 10
            else:
                no_shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (width / 2, height + 300)

    def powerup(self):
        self.power = True
        self.power_time = pygame.time.get_ticks()

class Mob(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #self.image_orig = pygame.transform.scale(meteor_img, (40, 40))
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(black)
        self.image = self.image_orig.copy()        
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.94 / 2)
        #pygame.draw.circle(self.image, b_red, self.rect.center, self.radius)
        
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(2, 8)
        self.speedx = random.randrange(-2, 2)
        
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > height + 10:
            self.rect.x = random.randrange(width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
        if self.rect.left < 0 or self.rect.right > width:
            self.speedx = 0 - self.speedx
        self.rotate()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = laser_img        
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(laser_img, (8, 20))
        self.image.set_colorkey(black)
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
        self.speedx = 0
        if direction == 'left':
            self.speedx = -3
        elif direction == 'right':
            self.speedx = 3

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.bottom < 0:
            self.kill()

class Powerup(pygame.sprite.Sprite):

    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.rect = self.image.get_rect() 
        self.image.set_colorkey(black)
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom > height:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, white)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    if pct > 0:
        pygame.draw.rect(surf, green, fill_rect)
    pygame.draw.rect(surf, white, outline_rect, 2)
    if pct < 20:
        font = pygame.font.Font(font_name, 16)
        text_surface = font.render('low shield!', True, b_red)
        text_rect = text_surface. get_rect()
        text_rect.topleft = (x, y + 12)
        surf.blit(text_surface, text_rect)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def show_go_screen():
    screen.fill(black)
    screen.blit(background, (0,0))
    draw_text(screen, "Another Shooter", 64, width/2, height * 0.2)
    draw_text(screen, "Arrow keys to move, Space to shoot", 22, width/2, height * 0.4)
    draw_text(screen, "Each shot costs 10 points", 22, width/2, height * 0.6)
    draw_text(screen, "Press any key to start", 18, width/2, height * 0.8)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

def end_screen(score):
    screen.fill(black)
    screen.blit(background, (0,0))
    draw_text(screen, "Thank you for playing!", 32, width/2, height * 0.25)
    draw_text(screen, "You have got {0} points".format(str(score)), 22, width/2, height /2)
    draw_text(screen, "Press any key to start again", 18, width/2, height * 0.75)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
bullets = pygame.sprite.Group()
mobs = pygame.sprite.Group()
for i in range(8):
    newmob()
powerups = pygame.sprite.Group()


pygame.mixer.music.play(loops = -1)

game_over = True
running = True
show_go_screen()
while running:
    if game_over:        
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            newmob()        
        
    clock.tick(fps)    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    player.score += 0.06
    if player.shield < 100:
        player.shield += 0.007

    #hitting player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player_expl_sound.play()
            player.hide()
            if player.score > 100:
                player.score -= 100
            else:
                player.score = 0
            player.lives -= 1
            player.shield = 100

    #meteor shot down
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        player.score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        newmob()
        if random.random() > 0.9:
            powerup = Powerup(hit.rect.center)
            all_sprites.add(powerup)
            powerups.add(powerup)

    #powerup taken
    hits = pygame.sprite.spritecollide(player, powerups, True, pygame.sprite.collide_circle)
    for hit in hits:
        powerup_sound.play()
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield > 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()

    if player.lives == 0 and not death_explosion.alive():
        end_screen(int(player.score))
        game_over = True

    screen.fill(black)
    screen.blit(background, (0,0))
    all_sprites.draw(screen)
    draw_text(screen, str(int(player.score)), 18, width / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, width - 90, 10, player.lives, player_mini_img)
    pygame.display.flip()
   
