# 音声を入れる
# 壁に当たったら音が出るようにしてみる
# _*_ coding: utf-8 _*_
import pygame
from pygame.locals import *
import sys

SCR_W = 640
SCR_H = 480
SCREEN_SIZE = (SCR_W, SCR_H)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(u"サウンドテスト")

# 画像をロードする
backImg = pygame.image.load("usausa.JPG").convert()
img = pygame.image.load("blue.jpg").convert()
img.set_colorkey(img.get_at((0, 0)), RLEACCEL)
img_rect = img.get_rect()

# サウンドをロードする
hit_sound = pygame.mixer.Sound("hit005.wav")

vx = vy = 300  # 1秒間の移動ピクセル
clock = pygame.time.Clock()

# BGMを再生（-1指定でループ再生する）
pygame.mixer.music.load("koyaaan.mp3")
pygame.mixer.music.play(-1)

while True:
    time_passed = clock.tick(60)
    time_passed_seconds = time_passed / 1000.0

    # 画像の移動
    img_rect.x += vx * time_passed_seconds
    img_rect.y += vy * time_passed_seconds

    # 壁にぶつかると跳ね返る
    if img_rect.left < 0 or img_rect.right > SCR_W:
        hit_sound.play()   # サウンドを再生
        vx = -vx
    if img_rect.top < 0 or img_rect.bottom > SCR_H:
        hit_sound.play()   # サウンドを再生
        vy = -vy

    screen.blit(backImg, (0, 0))
    screen.blit(img, img_rect)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT: sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()








    
