#_*_ coding:utf-8 _*_
# ヘビの仕様。
# 左右移動、ジャンプ、壁ジャンプ、
# ブロックとの衝突判定、リフトの乗降判定。

# ヘビのスピード処理を加速システムに変更したい。
# Bボタンで横方向の速度2倍。加速度0.25(もっと小さいといいかも？)。
# 穴に落ちて死ぬ仕様作りたい。

import pygame
from pygame.locals import *
import os
import sys
from Lift_17_8 import *

class Snake(pygame.sprite.Sprite):
    """スネーク"""
    MOVE_ACCELL = 0.25  # 移動加速度

    """ジャンプの実装"""
    JUMP_SPEED = 6.0    # ジャンプ時の初速度
    GRAVITY = 0.2       # 重力加速度

    def __init__(self, pos, blocks, lifts):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.right_image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        # blocks, liftsの定義
        self.blocks = blocks
        self.lifts = lifts
        self.mylift = Lift(-64.0, -64.0, 'X')  # デフォルトリフト
        self.mylift.visible = False   # スルー
        self.fromlift_x = 0.0
        self.fromlift_y = 0.0

        # 壁押し判定
        self.on_left = False
        self.on_right = False

        # 浮動小数点の位置と速度
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.fpvx = 0.0
        self.fpvy = 0.0

        # 地面とリフトの判定
        self.on_floor = False
        self.on_lift = False

        # やられた判定
        self.live = True
        self.outanim_on = False

        # やられる判定に使う処理変数
        self.ground_zero = 0.0   # 一番下のライン

    def update(self):
        """スプライトの更新"""
        # キー入力取得
        pressed_keys = pygame.key.get_pressed()

        # リフトに乗っている場合の位置修正
        if self.on_lift:
            self.fpx = self.mylift.fpx + self.fromlift_x
            self.fpy = self.mylift.fpy + self.fromlift_y

        # 左右移動（修正版）
        if not pressed_keys[K_RIGHT] or not pressed_keys[K_LEFT]:
            if pressed_keys[K_RIGHT]: self.move_r()
            elif pressed_keys[K_LEFT]: self.move_l()
            else: self.move_zero()
        elif not self.prev_LEFT or not self.prev_RIGHT:
            if self.prev_LEFT: self.move_r()
            elif self.prev_RIGHT: self.move_l()
            else: self.move_zero()
        else:
            if self.fpvx > 0: self.move_r()
            elif self.fpvx < 0: self.move_l()
            else: self.move_zero()                            

        # ジャンプ（ジャンプ中はジャンプ不可。そのためにon_floorがある）
        if pressed_keys[K_SPACE]:
            if self.on_floor or self.on_lift:
                self.fpvy = -self.JUMP_SPEED  # 上向きに初速度を与える
                self.on_floor = False
                self.on_lift = False   # リフトから外れる
                self.mylift.ridden = False
            elif self.on_left and pressed_keys[K_RIGHT]:
                self.fpvy = -self.JUMP_SPEED
            elif self.on_right and pressed_keys[K_LEFT]:
                self.fpvy = -self.JUMP_SPEED

        # 速度を更新
        if not self.on_floor and not self.on_lift:
            self.fpvy += self.GRAVITY  # 下向きに重力をかける

        if pressed_keys[K_b]:   # Bダッシュ（計算時のみ倍）
            self.fpvx *= 2.0;

        # x方向衝突判定する。
        # 浮動小数点の位置を更新(x方向)
        self.collision_x()
        
        # y方向の更新はリフト判定で行う。
        # リフトに乗らなかった場合にy方向衝突判定する。
        if not self.ridelift():
            self.on_lift = False
            self.mylift.ridden = False
            self.collision_y()

        # 浮動小数点の位置を整数座標に戻す
        # スプライトを動かすにはself.rectの更新が必要！
        self.rect.topleft = (int(self.fpx), int(self.fpy))

        # ボタンの左右キー、ジャンプキーの状態を取得
        self.prev_SPACE = pressed_keys[K_SPACE]
        self.prev_LEFT = pressed_keys[K_LEFT]
        self.prev_RIGHT = pressed_keys[K_RIGHT]

        if pressed_keys[K_b]:   # 位置計算が終わったら速度を元に戻す。
            self.fpvx /= 2.0

        # やられた判定（転落）
        # ここでは判定できない。あっちで。
        if self.fpy > self.ground_zero:
            self.fpy = self.ground_zero
            self.knock_out()

    def move_r(self):
        self.image = self.right_image
        if self.fpvx < 2.5:
            self.fpvx += self.MOVE_ACCELL

    def move_l(self):
        self.image = self.left_image
        if self.fpvx > -2.5:
            self.fpvx -= self.MOVE_ACCELL

    def move_zero(self):
        if self.fpvx > 0:
            self.fpvx -= self.MOVE_ACCELL
        elif self.fpvx < 0:
            self.fpvx += self.MOVE_ACCELL
        else:
            self.fpvx = 0

    def collision_x(self):
        width = self.rect.width
        height = self.rect.height
        newx = self.fpx + self.fpvx

        col_x = False
        # ブロックとの(横方向)衝突判定
        for block in self.blocks:
            flag3 = (self.fpy < float(block.rect.bottom))
            flag4 = (float(block.rect.top - height) < self.fpy)
            if not (flag3 and flag4): continue

            flag1 = (block.rect.left < newx < block.rect.right)
            flag2 = (block.rect.left < newx + float(width) < block.rect.right)
            if flag1:
                self.fpx = float(block.rect.right)
                self.on_left = True
            if flag2:
                self.fpx = float(block.rect.left - width)
                self.on_right = True
            if flag1 or flag2:
                col_x = True
                self.fpvx = 0
                break  # 1個調べれば充分
        if not col_x:
            self.fpx = newx
            self.on_left = False
            self.on_right = False

    # y方向はまた今度。

    def ridelift(self):
        # y方向の更新で工夫する
        newy = self.fpy + self.fpvy
        prebot = self.fpy + float(self.rect.height)
        newbot = prebot + self.fpvy

        ride = False  # リフトに乗れたかどうか
        for lift in self.lifts:

            if not lift.visible: continue  # visibleでなければスルー
            
            flag1 = (newbot >= lift.fpy)
            flag2 = (prebot <= lift.fpy)
            if flag1 and not flag2:
                if lift.prefpy >= prebot >= lift.fpy: flag2 = True
            if self.on_lift and lift == self.mylift: # 自分のリフトかどうか？
                flag1 = True; flag2 = True
            if not(flag1 and flag2): continue

            flag3 = (lift.fpx < self.fpx + float(self.rect.width))
            flag4 = (self.fpx < lift.fpx + float(lift.rect.width))
            if flag3 and flag4:
                self.on_lift = True
                self.mylift = lift
                self.mylift.ridden = True
                self.fpy = lift.fpy - float(self.rect.height)
                self.fromlift_x = self.fpx - lift.fpx
                self.fromlift_y = -float(self.rect.height)
                ride = True
                break  # 1個調べれば充分
        return ride

    def collision_y(self):
        width = self.rect.width
        height = self.rect.height
        newy = self.fpy + self.fpvy

        # col_yはいらないのか。？いや違う。y座標の変更有無と別。
        col_y = False
        for block in self.blocks:
            flag3 = float(block.rect.left - width) < self.fpx
            flag4 = self.fpx < float(block.rect.right)
            if not(flag3 and flag4): continue

            flag1 = (block.rect.top < newy < block.rect.bottom)
            flag2 = (block.rect.top <= newy + float(height) < block.rect.bottom)
            if flag1:
                self.fpy = float(block.rect.bottom)
            if flag2:
                self.fpy = float(block.rect.top - height)
                self.on_floor = True    # 地面に衝突した場合
            if flag1 or flag2:
                col_y = True
                self.fpvy = 0
        if not col_y:
            self.fpy = newy
            self.on_floor = False  # どのブロックにも乗っていない。

    def knock_out(self):
        # やられたときの処理(統一的な記述)
        self.live = False   # 死亡（こら
        self.outanim_on = True  # お葬式の準備（こら
        self.on_lift = False     # リフト関係の処理
        # 画像がひっくりカエル
        self.image = pygame.transform.flip(self.image, 0, 1)
        self.fpvy = -self.JUMP_SPEED  # 昇天スピード（（

    def reset(self, start_pos):
        # 再スタート処理
        self.fpx = float(start_pos[0])
        self.fpy = float(start_pos[1])
        self.image = self.right_image

    def outanim(self):
        # 逆さになってぽーんとかいうやつ
        self.fpvy += self.GRAVITY
        self.fpy += self.fpvy
        if self.fpy > self.ground_zero: self.outanim_on = False
        # こちらではSCR_RECTが使えないので、判定はメインの方でやる。
        self.rect.topleft = (int(self.fpx), int(self.fpy))
