import pygame
import os
import time
import random

FPS = 60

# Colors
BLACK = (0,0,0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0 ,0)
# WIDTH & HEIGHT of the screen
WIDTH, HEIGHT = 750, 750
pygame.init()

#spaceships images
YELLOW_SPACESHIP=pygame.image.load("pixel_ship_yellow.png")
YELLOW_LASER = pygame.image.load("pixel_laser_yellow.png")

RED_SPACESHIP = pygame.image.load("pixel_ship_red_small.png")
GREEN_SPACESHIP = pygame.image.load("pixel_ship_green_small.png")
BLUE_SPACESHIP = pygame.image.load("pixel_ship_blue_small.png")
RED_LASER = pygame.image.load("pixel_laser_red.png")
GREEN_LASER = pygame.image.load("pixel_laser_green.png")
BLUE_LASER = pygame.image.load("pixel_laser_blue.png")

screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Title & Icon
pygame.display.set_caption("1nvad3rs")
icon = pygame.image.load("spaceship.png")
pygame.display.set_icon(icon)

#background
BG = pygame.transform.scale(pygame.image.load("background-black.png"),(WIDTH,HEIGHT))

class Ship:
    COOLDOWN=30
    def __init__(self, x, y, health =100):
        self.x=x
        self.y=y
        self.health=health
        self.ship_img=None
        self.laser_img=None
        self.lasers=[]
        self.cooldown_count=0

    def draw(self, window):
        window.blit(self.ship_img,(self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health-=10
                self.lasers.remove(laser)


    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


    def shoot(self):
        if self.cooldown_count == 0:
            laser = Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cooldown_count = 1

    def cooldown(self):
        if self.cooldown_count >= self.COOLDOWN:
            self.cooldown_count = 0
        if self.cooldown_count > 0:
            self.cooldown_count += 1


class Player(Ship):
    def __init__(self,x,y,health =100):
        super().__init__(x,y,health)
        self.ship_img=YELLOW_SPACESHIP
        self.laser_img=YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health=health

    def healthbar(self,window):
        pygame.draw.rect(window,RED,(self.x,self.y+self.ship_img.get_height()+10,self.ship_img.get_width(),10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_health), 10))

    def draw(self,window):
        super().draw(window)
        self.healthbar(window)


    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)


class Enemy(Ship):
    COLOR_MAP={"red":(RED_SPACESHIP,RED_LASER),
               "green":(GREEN_SPACESHIP,GREEN_LASER),
               "blue": (BLUE_SPACESHIP,BLUE_LASER)}
    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.ship_img,self.laser_img=self.COLOR_MAP[color]
        self.mask=pygame.mask.from_surface(self.ship_img)

    def move(self, val):
        self.y+=val

    def shoot(self):
        if self.cooldown_count == 0:
            laser = Laser(self.x-18,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cooldown_count = 1

class Laser:
    def __init__(self,x,y,img):
        self.x=x
        self.y=y
        self.img=img
        self.mask=pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img, (self.x,self.y))

    def move(self,vel):
        self.y+=vel

    def off_screen(self,height):
        return not(self.y <= height and self.y >= 0)


    def collision(self,obj):
        return collide(self,obj)

def collide( obj1,obj2):
    offset_x=obj2.x-obj1.x
    offset_y=obj2.y-obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y))!= None

# game loop
def main():
    clock = pygame.time.Clock()
    run = True
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("ariel",50)
    lost_font = pygame.font.SysFont("ariel", 60)
    player_speed = 5
    enemies = []
    wave_len = 5
    enemyvel  = 2
    lost =False
    lost_count=0
    laser_vel = 6


    player = Player(300,630)

    def redraw_window():
        screen.blit(BG, (0, 0))
        level_label = main_font.render(f"Level: {level}", True, BLUE)
        if lives<2:
            lives_label = main_font.render(f"Lives: {lives}", True, RED)
        else:
            lives_label = main_font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_label, (10, 10))
        screen.blit(level_label, (WIDTH-level_label.get_width()-10,10))

        for enemy in enemies:
            enemy.draw(screen)
        if lost:
            lost_label =lost_font.render("YOU DIED",1,RED)
            screen.blit(lost_label,(WIDTH/2 - lost_label.get_width()/2,350))

        player.draw(screen)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        if lives <= 0 or player.health <= 0 :
            lost = True
            lost_count+=1
        if lost:
            if lost_count > FPS *3:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level  += 1
            for i in range(0,5):
                wave_len=5+i
            for i in range(wave_len):
                enemy = Enemy(random.randrange(50,WIDTH-100), random.randrange(-1500,-100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player_speed > 10:#Left
            player.x -= player_speed
        if keys[pygame.K_d] and player.x+ player_speed < WIDTH- player.get_width():#Right
            player.x += player_speed
        if keys[pygame.K_w] and player.y-player_speed > 0:#UP
            player.y -= player_speed
        if keys[pygame.K_s] and player.y+player_speed+18 < HEIGHT-player.get_height():#Down
            player.y += player_speed
        if keys[pygame.K_SPACE]:
            player.shoot()


        for enemy in enemies[:]:
            enemy.move(enemyvel)
            enemy.move_lasers(laser_vel,player)
            if random.randrange(0,125)==1:
                enemy.shoot()
            if collide(enemy,player):
                player.health-=10
                enemies.remove(enemy)
            if enemy.y+enemy.get_height() > HEIGHT:
                lives-=1
                enemies.remove(enemy)


        player.move_lasers(-laser_vel,enemies)


def main_menu():
    title_font= pygame.font.SysFont("comocsans",70)
    run = True
    while run:
        screen.blit(BG, (0,0))
        title_label= title_font.render("Press mouse to begin...", 1 , WHITE)
        screen.blit(title_label,((WIDTH/2 - title_label.get_width()/2),350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


main_menu()