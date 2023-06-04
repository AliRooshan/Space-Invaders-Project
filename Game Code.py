import pygame
import random
from pygame import mixer

# Initialising Pygame
pygame.init()

# Window
width, height = 1200, 600
win = pygame.display.set_mode((width, height))
pygame.display.set_caption('Space Invaders')

# Loading All Images
bg = pygame.transform.scale(pygame.image.load('bg.png'), (1200, 1000))
player_ship = pygame.image.load('Player Ship.png')
enemy_ship = pygame.transform.scale(pygame.image.load('Enemy Ship.png'), (125, 76))
laser = pygame.image.load('Bullet.png')
astriod_image = pygame.image.load('Asteroid.png')
heart_image = pygame.transform.scale(pygame.image.load('Heart.png'), (48, 48))
shield_image = pygame.transform.scale(pygame.image.load('Shield.png'), (80, 80))
gem_img = pygame.transform.scale(pygame.image.load('Gem.png'), (48, 48))

# Bg Music
mixer.music.load('background.wav')
mixer.music.play(-1)

# Loading All Sound Effects
bullet_sound = mixer.Sound('laser.wav')
collision_sound = mixer.Sound('Collision.wav')
health_sound = mixer.Sound('Health.wav')
shield_sound = mixer.Sound('Shield.wav')
gem_sound = mixer.Sound('Gem.wav')
over_sound = mixer.Sound('Lose.wav')
high_sound = mixer.Sound('Win.wav')


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height >= self.y >= - 10)

    def collision(self, obj):
        return collide(obj, self)


class Score:
    def __init__(self):
        self.score = 0
        self.font = pygame.font.SysFont('Times New Roman', 30)

    def increase_score(self, points):
        self.score += points

    def update(self, window):
        score_text = self.font.render("Score: " + str(self.score), True, (255, 255, 255))
        window.blit(score_text, (width - score_text.get_width() - 10, 10))


class Health:
    def __init__(self):
        self.health = 3
        self.font = pygame.font.SysFont('Times New Roman', 30)

    def decrease_health(self):
        self.health -= 1

    def increase_health(self):
        self.health += 1

    def update(self, window):
        health_text = self.font.render('Lives: ' + str(self.health), True, (255, 255, 255))
        window.blit(health_text, (10, 10))


class Ship:
    COOLDOWN = 90

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ship_img = None
        self.laser_image = None
        self.lasers = []
        self.cool = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(win)

    def cooldown(self):
        if self.cool >= self.COOLDOWN:
            self.cool = 0
        elif self.cool > 0:
            self.cool += 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.ship_img = player_ship
        self.laser_image = laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.health = 3

    def move_lasers(self, vel, objs, score):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height) and laser in self.lasers:
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        collision_sound.play()
                        score.increase_score(100)
                        objs.remove(obj)

    def shoot(self):
        if self.cool == 0:
            laser = Laser(self.x + 60, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool = 1


class Enemy(Ship):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.ship_img = enemy_ship
        self.laser_image = laser
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool == 0:
            laser = Laser(self.x + 50, self.y + 50, self.laser_image)
            self.lasers.append(laser)
            self.cool = 1

    def move_lasers(self, vel, obj, health):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height) and laser in self.lasers:
                self.lasers.remove(laser)
            elif laser.collision(obj):
                if not timer.started:
                    obj.health -= 1
                    health.health -= 1
                if laser in self.lasers:
                    self.lasers.remove(laser)


class Astroid(Ship):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.ship_img = astriod_image
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


class Power_up(Ship):
    def __init__(self, x, y, img):
        super().__init__(x, y)
        self.ship_img = img
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


class Timer:
    def __init__(self):
        self.font = pygame.font.SysFont('Times New Roman', 30)
        self.timer = 180
        self.started = False

    def update(self):
        if self.started:
            self.timer -= 1
            if self.timer <= 0:
                self.started = False

    def draw(self, window):
        text = self.font.render(f"Shield: {self.timer}", True, (255, 255, 255))
        window.blit(text, (10, 50))


# Collision check
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


timer = Timer()
highscore = 0


def main():
    global highscore
    mixer.music.set_volume(10)
    run = True
    FPS = 120
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    lost_font = pygame.font.SysFont('Times New Roman', 50)

    vel = 2

    astriods = []
    num_astriods = 5

    enemies = []
    num_enemies = 3
    shoot_vel = 4

    hearts = []

    shields = []

    gems = []
    num_gems = 3

    player = Player(525, 480)
    player_vel = 5

    score = Score()

    health = Health()

    file = open('Highscore.txt', 'r')
    for i in file:
        highscore = int(i)

    def draw_window():
        global highscore
        win.blit(bg, (0, 0))

        for gem in gems:
            gem.draw(win)

        for shield in shields:
            shield.draw(win)

        for heart in hearts:
            heart.draw(win)

        for astriod in astriods:
            astriod.draw(win)

        for enemy in enemies:
            enemy.draw(win)

        player.draw(win)

        if lost:
            if score.score > highscore:
                file = open('Highscore.txt', 'w')
                file.write(str(score.score))
                lost_label = lost_font.render('Game Over!', True, (0, 255, 0))
                highscore_label = lost_font.render('New High Score:' + str(score.score), True, (0, 255, 0))
                high_sound.play()
            else:
                lost_label = lost_font.render('Game Over!', True, (255, 0, 0))
                highscore_label = lost_font.render('Highest Score:' + str(highscore), True, (255, 0, 0))
                mixer.music.set_volume(0)
                over_sound.play()
            win.blit(highscore_label, (width / 2 - highscore_label.get_width() / 2, 300))
            win.blit(lost_label, (500, 250))
            pygame.display.update()

    while run:
        draw_window()
        score.update(win)
        health.update(win)
        if health.health == 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS:
                run = False
            else:
                continue

        # Increasing Difficulty
        if 5000 > score.score > 2000:
            vel = 3
            shoot_vel = 5

        if 7000 > score.score > 4000:
            num_astriods = 6
            num_enemies = 4

        if 10000 > score.score > 7000:
            vel = 4
            num_astriods = 7
            num_enemies = 5
            shoot_vel = 6

        if score.score > 10000:
            vel = 5
            num_astriods = 8
            num_enemies = 6
            shoot_vel = 7

        if len(gems) == 0:
            for i in range(num_gems):
                gem = Power_up(random.randrange(0, width - 48), random.randrange(-140, - 48), gem_img)
                gems.append(gem)

        if len(hearts) == 0:
            heart = Power_up(random.randrange(0, width - 48), random.randrange(-140, - 48), heart_image)
            hearts.append(heart)

        if len(shields) == 0:
            shield = Power_up(random.randrange(0, width - 80), random.randrange(-180, - 80), shield_image)
            shields.append(shield)

        if len(astriods) == 0:
            for i in range(num_astriods):
                astriod = Astroid(random.randrange(0, width - 120), random.randrange(-220, - 120))
                astriods.append(astriod)

        if len(enemies) == 0:
            for i in range(num_enemies):
                enemy = Enemy(random.randrange(0, width - 125), random.randrange(-176, - 76))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < width:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() < height:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            bullet_sound.play()
            player.shoot()

        for enemy in enemies:
            enemy.move(vel)
            enemy.move_lasers(shoot_vel, player, health)
            if random.randrange(0, 2 * FPS) == 1:
                enemy.shoot()
            if collide(enemy, player):
                if not timer.started:
                    player.health -= 1
                    health.decrease_health()
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() - 64 > height:
                enemies.remove(enemy)

        for astriod in astriods:
            astriod.move(vel)
            if collide(astriod, player):
                if not timer.started:
                    player.health -= 1
                    health.decrease_health()
                astriods.remove(astriod)
            elif astriod.y + astriod.get_height() - 64 > height:
                astriods.remove(astriod)

        for heart in hearts:
            heart.move(vel)
            if collide(heart, player):
                if health.health < 3:
                    player.health += 1
                    health.increase_health()
                    health_sound.play()
                hearts.remove(heart)
            elif heart.y + heart.get_height() - 48 > height:
                hearts.remove(heart)

        for shield in shields:
            shield.move(vel)
            if collide(shield, player):
                timer.timer = 180
                timer.started = True
                shield_sound.play()
                shields.remove(shield)
            elif shield.y + shield.get_height() - 80 > height:
                shields.remove(shield)

        for gem in gems:
            gem.move(vel)
            if collide(gem, player):
                score.increase_score(200)
                gem_sound.play()
                gems.remove(gem)
            elif gem.y + gem.get_height() - 48 > height:
                gems.remove(gem)

        player.move_lasers(- 4, enemies, score)
        player.move_lasers(- 4, astriods, score)

        timer.update()
        if timer.started:
            timer.draw(win)
        clock.tick(FPS)
        pygame.display.update()


def main_menu():
    title_font = pygame.font.SysFont("Times New Roman", 70)
    game_rules_font = pygame.font.SysFont("Times New Roman", 30)
    run = True
    while run:
        win.blit(pygame.transform.scale(pygame.image.load('Menu bg.png'), (1200, 675)), (0, 0))
        title_label = title_font.render("Press the mouse to begin", True, (255, 255, 255))
        game_rules = game_rules_font.render('Game Rules', True, (255, 255, 255))
        game_rules_1 = game_rules_font.render('1.You Lose 1 health if you collide with an asteroid or an enemy ship',
                                              True, (255, 255, 255))
        game_rules_2 = game_rules_font.render('2.If a bullet from an enemy ship hits you, you lose 1 health', True,
                                              (255, 255, 255))
        game_rules_3 = game_rules_font.render(
            '3.Collect heart power up to increase your health, it only works if you have less than 3 Health', True,
            (255, 255, 255))
        game_rules_4 = game_rules_font.render('4.Collect the shield to become invincible for 3 seconds', True,
                                              (255, 255, 255))
        game_rules_5 = game_rules_font.render('5.Collect the gems to gain 200 points', True, (255, 255, 255))
        game_rules_6 = game_rules_font.render('6.If you shoot an asteroid or an enemy ship you gain 100 points', True,
                                              (255, 255, 255))
        game_rules_7 = game_rules_font.render('7.You can shoot after every 2 second.', True,(255, 255, 255))
        win.blit(title_label, (width / 2 - title_label.get_width() / 2, 60))
        win.blit(game_rules, (width / 2 - game_rules.get_width() / 2, 150))
        win.blit(game_rules_1, (width / 2 - game_rules_1.get_width() / 2, 200))
        win.blit(game_rules_2, (width / 2 - game_rules_2.get_width() / 2, 250))
        win.blit(game_rules_3, (width / 2 - game_rules_3.get_width() / 2, 300))
        win.blit(game_rules_4, (width / 2 - game_rules_4.get_width() / 2, 350))
        win.blit(game_rules_5, (width / 2 - game_rules_5.get_width() / 2, 400))
        win.blit(game_rules_6, (width / 2 - game_rules_6.get_width() / 2, 450))
        win.blit(game_rules_7, (width / 2 - game_rules_7.get_width() / 2, 500))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
