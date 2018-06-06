# ブロック崩しできるのかできないのか
# 出来たみたいだけどここまでにしよ。別のゲーム作ってみたい。
# 両側に壁用意して・・あと天井も。それからスコア、
# 画面を制限して上部にスコア表示、ステージも表示、残機表示。
# タイミングよく↑キー押すとスピード上がる(フレーム300で戻る)
# スピードアップ時はボールの色が金色になってダメージ2倍。
# スピードアップ時でないと壊せないブロックを用意(壊せなくてもステージクリア可)
# タイトル画面用意する
# ステージ選択機能も付けたい(5つくらい作ろう、1, 2, 3, 4, 5で。)

import pygame
from pygame.locals import *
import sys
from math import sin, cos, atan, radians, floor, pi
from random import randint

SCR_RECT = Rect(0, 0, 480, 320)
SCR_W = SCR_RECT.width
SCR_H = SCR_RECT.height

TITLE, START, PLAY, GAMEOVER, CLEAR, NEXT, RANK = [0, 1, 2, 3, 4, 5, 6]

direction = [23, 45, 67, 113, 135, 157]

def calc_ballpos(rect, pos):
    x = pos[0]; y = pos[1]
    if y > rect.bottom:
        if x > rect.right: return 1
        elif x < rect.left: return 3
        else: return 2
    elif y < rect.top:
        if x > rect.right: return 7
        elif x < rect.left: return 5
        else: return 6
    else:
        if x > rect.right: return 0
        elif x < rect.left: return 4
        else: return -1

def calc_is_far(rect, pos):
    # 離れてるのは計算しない
    dx = abs(rect.centerx - pos[0]) - rect.width // 2
    dy = abs(rect.centery - pos[1]) - rect.height // 2
    return max(dx, dy) > 40

def calc_reflect(cornerpos, ballpos, speed):
    # 新しい速度を返す関数
    a, b = cornerpos
    theta = radians(randint(30, 60))
    newvx = 0.1 * floor(cos(theta) * 10 * speed)
    newvy = 0.1 * floor(sin(theta) * 10 * speed)
    return (newvx, newvy)

class Play():
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("blockbreak_1")

        self.blocks = pygame.sprite.RenderUpdates()
        block.containers = self.blocks
        block.sound_break = pygame.mixer.Sound("break.wav")  # 破壊音

        self.loading();

        self.State = PLAY
        clock = pygame.time.Clock()
        self.frame = 0

        for j in range(5):
            for i in range(3):
                block((60 + 60 * i, 40 + 40 * j), j)
                block((260 + 60 * i, 40 + 40 * j), j)
        
        self.paddle = paddle((200, 300))
        self.ball = ball((232, 288), self.blocks, self.paddle)

        while True:
            screen.fill((0, 0, 0))
            clock.tick(60)
            self.update()
            self.draw(screen)
            pygame.display.update()

            self.key_handler()
            
    def loading(self):
        imageList = pygame.image.load("blockimages.png")
        for i in range(5):
            surface = pygame.Surface((40, 20))
            surface.blit(imageList, (0, 0), (0, 20 * i, 40, 20))
            block.images.append(surface)

        imageList = pygame.image.load("paddleimages.png")
        for i in range(2):
            surface = pygame.Surface((80, 20))
            surface.blit(imageList, (0, 0), (0, 20 * i, 80, 20))
            paddle.images.append(surface)

        imageList = pygame.image.load("ballimages.png")
        for i in range(2):
            surface = pygame.Surface((16, 16))
            surface.blit(imageList, (0, 0), (16 * i, 0, 16, 16))
            surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
            ball.images.append(surface)

        self.dirimage = pygame.image.load("pointerimage.png")

    def update(self):
        for block in self.blocks:
            block.update()
            block.far = calc_is_far(block.rect, self.ball.rect.center)
            if not block.far:
                block.ballpos = calc_ballpos(block.rect, self.ball.rect.center)
        self.paddle.ballpos = calc_ballpos(self.paddle.rect, self.ball.rect.center)
        self.paddle.far = calc_is_far(self.paddle.rect, self.ball.rect.center)
        self.paddle.update()
        self.ball.update()
        

    def draw(self, screen):
        if self.ball.set_on:
            self.frame += 1
            if self.frame > 191: self.frame = 0
            x, y = self.ball.rect.center
            dx = floor(cos(radians(direction[self.frame // 32])) * 20)
            dy = -floor(sin(radians(direction[self.frame // 32])) * 20)
            screen.blit(self.dirimage, (x + dx, y + dy))
            
        self.blocks.draw(screen)
        self.paddle.draw(screen)
        self.ball.draw(screen)

    def key_handler(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                self.keydown_event(event.key, self.State)

    def keydown_event(self, key, state):
        if key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        if state == PLAY:
            if key == K_SPACE and self.ball.set_on:
                dx = cos(radians(direction[self.frame // 32]))
                dy = sin(radians(direction[self.frame // 32]))
                self.ball.fpvx = 0.1 * floor(dx * self.ball.speed * 10)
                self.ball.fpvy = 0.1 * floor(dy * self.ball.speed * 10)
                self.frame = 0
                self.ball.set_on = False  # ボールがパドルから離れる
            if key == K_UP and not self.ball.set_on and self.paddle.count == 0:
                self.paddle.count = 16
                self.paddle.image = paddle.images[1]
            

class block(pygame.sprite.Sprite):
    images = []
    sound_break = None
    def __init__(self, pos, kind):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.kind = kind
        self.image = self.images[self.kind]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.tough = kind + 1  # いずれkindにより種別する
        self.ballpos = -1  # 衝突判定用
        self.far = True    # ボールが遠くにあるときに判定しない

    def break_off(self, dmg):
        self.tough = max(self.tough - dmg, 0)
        if self.tough > 0:
            self.kind -= dmg
            self.image = self.images[self.kind]

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.tough == 0:
            self.sound_break.play()
            self.kill()



class paddle:
    images = []
    def __init__(self, pos):
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.vx = 0
        self.ballpos = -1 # 衝突判定用
        self.far = False  # ボールが遠くにあるときに判定しない
        self.count = 0    # 0～32の範囲で動く、32～16のときに赤く光る

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT]:
            self.vx = 8
        elif keys[K_LEFT]:
            self.vx = -8
        else:
            self.vx = 0
        if self.rect.left + self.vx < 0: self.vx = 0
        if self.rect.right + self.vx > SCR_W: self.vx = 0
        self.rect.x += self.vx
        # カウントは16～0で、16～8のときに光ってる感じ。
        if self.count > 0:
            self.count -= 1
            if self.count < 8: self.image = self.images[0]

class ball:
    r = 8
    speed = 4.0  # スピードアップ時は6.0にする。クラス変数は変更可能。
    images = []
    def __init__(self, pos, blocks, paddle):
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0], pos[1])
        self.blocks = blocks  # 衝突判定用
        self.paddle = paddle
        self.fpvx = 0.0
        self.fpvy = 0.0
        self.fpx = float(pos[0])
        self.fpy = float(pos[1])
        self.set_on = True
        self.count = 0   # 強化してる時用のカウント

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.set_on:
            self.rect.x = self.paddle.rect.x + self.paddle.rect.width // 2 - self.r
            self.rect.y = self.paddle.rect.y - self.rect.height
            self.fpx = float(self.rect.x)
            self.fpy = float(self.rect.y)
            return

        # ブロック、パドル、床のうち衝突するのはひとつだけ。
        
        # ブロックと衝突判定
        # 1. farなのはスルー。2. 移動後の座標で衝突しないものはスルー。
        # 3. 衝突するならフラグに従って、偶数フラグなら値により速度反転、
        # 奇数フラグ(角っちょ)の場合は当たり方によって方向をいじる感じ。
        self.collideblock()                
        
        # パドルと衝突判定
        self.collidepaddle()

        # 天井、右床、左床と衝突判定
        if self.fpy + self.fpvy < 0: self.fpvy = -self.fpvy
        elif self.fpx + self.fpvx < 0: self.fpvx = -self.fpvx
        elif self.fpx + self.fpvx + self.r * 2.0 > SCR_W * 1.0: self.fpvx = -self.fpvx

        # 位置更新
        self.fpx += self.fpvx
        self.fpy += self.fpvy
        self.rect.x = int(self.fpx)
        self.rect.y = int(self.fpy)
        
        # 落下判定
        if self.rect.top > SCR_H:
            self.reset()

        if self.count > 0:
            self.count -= 1
            if self.count == 0:
                self.speed = 4.0
                self.fpvx = floor(self.fpvx * 6.6) * 0.1
                self.fpvy = floor(self.fpvy * 6.6) * 0.1
                self.image = self.images[0]

    def collideblock(self):
        newrect = Rect(int(self.rect.x + self.fpvx), int(self.rect.y + self.fpvy), 16, 16)
        for block in self.blocks:
            if block.far: continue
            if newrect.colliderect(block.rect):
                phase = block.ballpos
                if phase == 0 or phase == 4: self.fpvx = -self.fpvx
                if phase == 2 or phase == 6: self.fpvy = -self.fpvy
                if phase & 1 == 0: block.break_off(1); break
                newv = (0, 0)
                if phase == 1:
                    newv = calc_reflect(block.rect.bottomright, newrect.center, self.speed)
                    self.fpvx = newv[0]; self.fpvy = newv[1]
                elif phase == 3:
                    newv = calc_reflect(block.rect.bottomleft, newrect.center, self.speed)
                    self.fpvx = -newv[0]; self.fpvy = newv[1]
                elif phase == 5:
                    newv = calc_reflect(block.rect.topleft, newrect.center, self.speed)
                    self.fpvx = -newv[0]; self.fpvy = -newv[1]
                elif phase == 7:
                    newv = calc_reflect(block.rect.topright, newrect.center, self.speed)
                    self.fpvx = newv[0]; self.fpvy = -newv[1]
                block.break_off(1)  # ブロックが消える
                break  # ひとつで充分

    def collidepaddle(self):
        if self.paddle.far: return
        newrect = Rect(int(self.rect.x + self.fpvx), int(self.rect.y + self.fpvy), 16, 16)
        if not newrect.colliderect(self.paddle.rect): return
        phase = self.paddle.ballpos
        if phase == 6:
            self.fpvy = -self.fpvy
            if self.paddle.count & 8 and self.count == 0:  # 強化
                self.count = 300; self.speed = 6.0;
                self.fpvx = floor(self.fpvx * 15) * 0.1
                self.fpvy = floor(self.fpvy * 15) * 0.1
                self.image = self.images[1]
            return
        if phase == 0 or phase == 4: self.fpvx = -self.fpvx; return
        if phase == 5:
            newv = calc_reflect(self.paddle.rect.topleft, newrect.center, self.speed)
            self.fpvx = -newv[0]; self.fpvy = -newv[1]
        elif phase == 7:
            newv = calc_reflect(self.paddle.rect.topright, newrect.center, self.speed)
            self.fpvx = newv[0]; self.fpvy = -newv[1]


    def reset(self):
        self.set_on = True
        self.speed = 4.0
        self.image = self.images[0]

if __name__ =="__main__":
    Play()
