# -*- coding: utf-8 -*-
# ヘビが左右に移動、ジャンプ実装、リフト実装。
# さらにリフトに乗れる。リフトを増やしたい。
# リフトをブロックと共演させたい。

# リフト列の実装
# ゴールに入って↑キーでクリア、の仕様

import pygame
from pygame.locals import *
import os
import sys
from Map_17_8 import *
from Snake_17_8 import *
from Block_16 import *
from Lift_17_8 import *

SCR_RECT = Rect(0, 0, 640, 480)
SCR_W = SCR_RECT.width
SCR_H = SCR_RECT.height

class PyAction:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("いろんなリフト")

        # 画像のロード(ヘビ)
        # 右向き
        Snake.right_image = self.load_image("snake.jpg", True)
        # 左向き
        Snake.left_image = pygame.transform.flip(Snake.right_image, 1, 0)
        # 第1引数が1だと左右、第2引数が1だと上下反転

        # 画像のロード(ブロック)
        Block.image = self.load_image("block.jpg")

        # 画像のロード(リフト)
        Lift.image = self.load_image("lift.png")

        # 画像のロード(メッセージ)
        textImages = self.load_image("texts.png")
        surfaces = [pygame.Surface((360, 60)), pygame.Surface((360, 60))]
        surfaces[0].blit(textImages, (0, 0), (0, 0, 360, 60))
        surfaces[1].blit(textImages, (0, 0), (0, 60, 360, 60))
        self.pauseWords = surfaces[0]
        self.overWords = surfaces[1]

        # スプライトのグループ化とマップ作成をmapに譲る。
        file_of_map = os.path.join("sub", "mapdata_17_8.map")
        file_of_lift = os.path.join("sub", "liftdata_17_8.txt")
        self.map = Map(file_of_map, file_of_lift)

        # Snakeをメンバ変数にする。
        self.Snake = self.map.Snake
        self.Snake.ground_zero = self.map.rect.bottom

        # メインループ
        clock = pygame.time.Clock()

        # ポーズ状態の表現
        self.pause = False

        while True:
            if not self.pause:
                clock.tick(60)
                self.update()
                self.draw(screen)
                if not self.Snake.live and not self.Snake.outanim_on:
                    # やられたテキスト
                    self.knockouttext(screen)
            else:
                # ポーズテキスト
                self.pausetext(screen)
            
            pygame.display.update()
            self.key_handler()

    def update(self):
        """スプライトの更新"""
        self.map.update()

    def draw(self, screen):
        """スプライトの描画"""
        # スプライトをマップサーファスに描画。
        # この時点では画面に表示されない！！（だからまっくろくろすけ）
        # マップの方が大きくて、その一部をメインスクリーンにごにょごにょ
        self.map.draw()
        '''
        スクロール処理書いちゃう。
        '''
        # オフセットに基づいてマップの一部を画面に描画
        offset_x, offset_y = self.map.calc_offset(SCR_W, SCR_H)
        # 端ではスクロールしない処理
        if offset_x < 0:
            offset_x = 0
        elif offset_x > self.map.width -  SCR_W:
            offset_x = self.map.width - SCR_W

        if offset_y < 0:
            offset_y = 0
        elif offset_y > self.map.height - SCR_H:
            offset_y = self.map.height - SCR_H

        # マップサーファスの一部をスクリーンに描画
        screen.blit(self.map.surface, (0, 0), (offset_x, offset_y, SCR_W, SCR_H))

    def key_handler(self):
        """キー入力処理"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # ポーズボタンでゲームの一時停止
                if event.key == K_PAUSE and self.Snake.live:
                    # 死んでる間はポーズ不可
                    self.pause = not self.pause
                # リターンキーでゲーム再開
                if event.key == K_RETURN:
                    if not self.Snake.live and not self.Snake.outanim_on:
                        self.Snake.live = True
                        self.Snake.reset(self.map.start_pos)
                        # リフトの再配置とかここに書くんじゃないかと。

    def pausetext(self, screen):
        screen.blit(self.pauseWords, (140, 200))

    def knockouttext(self, screen):
        screen.blit(self.overWords, (140, 200))

    def load_image(self, filename, flag = False):
        """画像のロード"""
        filename = os.path.join("sub", filename)
        image = pygame.image.load(filename).convert()
        if not flag: return image
        else:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image

if __name__ == "__main__":
    PyAction()
