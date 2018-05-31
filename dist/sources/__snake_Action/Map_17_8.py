# Mapクラスの作成(リフトも作ろうバージョン)
# スタートとゴールを作りました。

# _*_ coding:utf-8 _*_
import pygame
from pygame.locals import *
import os
import sys

from Snake_17_8 import *
from Block_16 import *
from Lift_17_8 import *

class Map:
    """マップ（プレイヤーや内部のスプライト含む"""
    GS = 32  # グリッドサイズ

    def __init__(self, file_map, file_lift):

        # スプライトグループの登録
        self.all = pygame.sprite.RenderUpdates()
        self.blocks = pygame.sprite.Group()
        self.lifts = pygame.sprite.Group()
        Snake.containers = self.all
        Block.containers = self.all, self.blocks
        Lift.containers = self.lifts

        # マップをロードしてマップ内スプライトの作成(リフトは後)
        self.load(file_map, file_lift)

        self.Snake = Snake(self.start_pos, self.blocks, self.lifts)   # ヘビの作成

        # マップサーファスを作成
        self.surface = pygame.Surface((self.col * self.GS, self.row * self.GS)).convert()
        self.rect = self.surface.get_rect()
        file_of_start = os.path.join("sub", "start.png")
        file_of_goal = os.path.join("sub", "goal.png")
        self.startimage = pygame.image.load(file_of_start).convert()
        self.goalimage = pygame.image.load(file_of_goal).convert()

        # こっちのサーファスにより大きいマップ画像を用意しておいて
        # PyActionの方で部分的に描画っていうのを後でやる（スクロール）。

    def update(self):
        """マップ内スプライトを更新"""
        # やられてる間は他のupdateは復活するまでキャンセル
        if self.Snake.live:
            self.lifts.update()
            self.all.update()
        elif self.Snake.outanim_on:
            self.Snake.outanim()   # 逆さポーン

    def draw(self):
        """マップサーファスにマップ内スプライトを描画"""
        self.surface.fill((0, 0, 0))
        self.lifts.draw(self.surface)
        self.surface.blit(self.startimage, self.start_pos)
        self.surface.blit(self.goalimage, self.goal_pos)
        self.all.draw(self.surface)

    def calc_offset(self, w, h):
        """オフセットを計算（マップスクロールのためプレイヤーの位置を計算"""
        # SCR_RECTからスクリーンの幅の情報を読み込む。
        offset_x = self.Snake.rect.topleft[0] - w/2
        offset_y = self.Snake.rect.topleft[1] - h/2
        return offset_x, offset_y

    def load(self, file_map, file_lift):
        """マップをロードしてスプライトを作成"""
        map = []  # マップは1行ごとをリストとするリスト成分の配列
        fp = open(file_map, "r")
        for line in fp:
            line = line.rstrip()   # 改行除去
            map.append(list(line))
        self.row = len(map)    # mapの配列としての長さ、つまり縦のグリッドの個数
        self.col = len(map[0]) # mapの第1成分のリストの長さ、つまり横のグリッドの個数
        self.width = self.col * self.GS
        self.height = self.row * self.GS
        fp.close()

        # マップからスプライトを作成
        # リフトは速さだけ別のファイルから読み込む。場所だけ書いておく。
        lpos = []
        start_pos = (0, 0)
        goal_pos = (0, 0)
        for i in range(self.row):
            for j in range(self.col):
                if map[i][j] == 'B':
                    Block((j * self.GS, i * self.GS))   # ブロックの作成
                if map[i][j] == 'L':
                    lpos.append((j * self.GS, i * self.GS))  # リフトの作成
                if map[i][j] == 'S':
                    start_pos = (j * self.GS, i * self.GS) # スタート
                if map[i][j] == 'G':
                    goal_pos = (j * self.GS, i * self.GS)  # ゴール
        self.start_pos = start_pos   # スタート位置のメンバ変数を定義
        self.goal_pos = goal_pos     # ゴール位置のメンバ変数を定義
        lv = []
        fp = open(file_lift, 'r')
        for row in fp:
            lv.append(row.split(' '))   # 読み込んだLの順に速さのデータを読み込む。
        fp.close()
        
        n = len(lv)
        x, y = (0.0, 0.0)
        for i in range(n):
            x = lpos[i][0]; y = lpos[i][1]
            if lv[i][0] == 'L':
                # 直線リフト
                lineLift(x, y, 'L', float(lv[i][1]), float(lv[i][2]), float(lv[i][3]) * self.GS)
            if lv[i][0] == 'P':
                # 振り子リフト
                penduLift(x, y, 'P', float(lv[i][1]) * self.GS, float(lv[i][2]) * self.GS)
            if lv[i][0] == 'C':
                # 円形リフト
                circleLift(x, y, 'C', float(lv[i][1]) * self.GS, float(lv[i][2]) * self.GS)
            if lv[i][0] == 'D':
                # 消滅リフト
                disapLift(x, y, 'D', float(lv[i][1]), float(lv[i][2]), float(lv[i][3]) * self.GS)
            if lv[i][0] == 'F':
                # 落下リフト
                fallLift(x, y, 'F', self.height + self.GS)
            if lv[i][0] == 'H':
                # 連続リフト（消滅リフトが連なったもの）
                num = int(lv[i][5])
                newx = x - float(lv[i][1]) * self.GS * float(lv[i][4])
                newy = y - float(lv[i][2]) * self.GS * float(lv[i][4])
                dx = x - newx
                dy = y - newy
                for k in range(0, num):
                    lift = disapLift(newx, newy, 'D', float(lv[i][1]), float(lv[i][2]), float(lv[i][3]) * self.GS)
                    lift.count = int(k * float(lv[i][4]) * self.GS)
                    lift.fpx = newx + k * dx
                    lift.fpy = newy + k * dy
                    lift.rect.topleft = (int(lift.fpx), int(lift.fpy))
                    lift.prefpy = lift.fpy
                
