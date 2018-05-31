#_*_ coding:utf-8 _*_
# リフトの仕様。
# 位置の更新など。

import pygame
from pygame.locals import *
import os
import sys
from math import cos, sin, radians

class Lift(pygame.sprite.Sprite):
    """リフトの原型"""
    """初期位置とカウントとdrawメソッドだけ共通"""
    def __init__(self, c_x, c_y, kind):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = (c_x, c_y)  # 初期位置
        self.fpx = c_x
        self.fpy = c_y
        self.count = 0    # 位置制御のためのカウント
        self.prefpy = 0.0 # 直前のリフトのy方向の位置
        self.kind = kind    # リフトのタイプ
        self.visible = True   # リフトが存在しているかどうか
        self.ridden = False   # リフトに乗られているかどうか

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class lineLift(Lift):
    """直線リフト(L)"""
    """移動が直線的で行ったり来たりする"""
    def __init__(self, c_x, c_y, kind, v_x, v_y, limit):
        # lineLift(120.0, 240.0, 3.0, 0.0, 64)のように指定する
        Lift.__init__(self, c_x, c_y, kind)
        self.v_x = v_x
        self.v_y = v_y
        self.limit = limit

    def update(self):
        self.prefpy = self.fpy
        self.fpx += self.v_x
        self.fpy += self.v_y
        self.count += 1
        if self.count == self.limit:
            # limit×速度の絶対値だけ、limit数のフレーム数で移動する。
            # 同じ距離ならlimitが大きい程遅くなるということ。
            self.count = -self.count
            self.v_x = -self.v_x
            self.v_y = -self.v_y
        self.rect.topleft = (int(self.fpx), int(self.fpy))

class penduLift(Lift):
    """振り子リフト(P)"""
    """振り子のように正弦振動で移動する"""
    def __init__(self, c_x, c_y, kind, a_x, a_y):
        # penduLift(120.0, 240.0, 64.0, 32.0)のように指定する
        Lift.__init__(self, c_x, c_y, kind)
        self.c_x = c_x
        self.c_y = c_y
        self.a_x = a_x
        self.a_y = a_y

    def update(self):
        self.prefpy = self.fpy
        self.fpx = self.c_x + self.a_x * sin(radians(self.count))
        self.fpy = self.c_y + self.a_y * sin(radians(self.count))
        self.count += 1
        if self.count > 360: self.count -= 360
        # rectの匹数は整数
        self.rect.topleft = (int(self.fpx), int(self.fpy))

class circleLift(Lift):
    """円形リフト(C)"""
    """円を描くように移動する"""
    def __init__(self, c_x, c_y, kind, r_x, r_y):
        # circleLift(120.0, 240.0, 96.0, 96.0)のように指定する
        Lift.__init__(self, c_x, c_y, kind)
        self.c_x = c_x
        self.c_y = c_y
        self.r_x = r_x
        self.r_y = r_y

    def update(self):
        self.prefpy = self.fpy
        self.fpx = self.c_x + self.r_x * sin(radians(self.count))
        self.fpy = self.c_y + self.r_y * cos(radians(self.count))
        self.count += 1
        if self.count > 360: self.count -= 360
        self.rect.topleft = (int(self.fpx), int(self.fpy))

class disapLift(Lift):
    """消滅リフト(D)"""
    """一定距離進んだのち消滅する"""
    def __init__(self, c_x, c_y, kind, v_x, v_y, limit):
        # limitだけ進むと元の位置に戻って再スタート
        Lift.__init__(self, c_x, c_y, kind)
        self.c_x = c_x
        self.c_y = c_y
        self.v_x = v_x
        self.v_y = v_y
        self.limit = limit

    def update(self):
        self.prefpy = self.fpy
        if self.visible and self.count < self.limit - 1:
            self.count += 1
            self.fpx += self.v_x
            self.fpy += self.v_y
            self.rect.topleft = (int(self.fpx), int(self.fpy))
        if not self.visible and self.count > self.limit - 2:
            self.fpx = self.c_x
            self.fpy = self.c_y
            self.prefpy = self.fpy
            self.visible = True
            self.count = 0
        if self.count > self.limit - 2:
            self.visible = False
            # self.visibleがFalseのリフトには乗れない。

# この仕様だとcountが31, 32, 0, 1とかなって1つずれるな。
# そうならないためには、self.limit - 1とする必要があるな。
# うまくいったらしい。連結リフトの仕様で。
# 待ち時間を導入したい。何フレーム待つ、とかそういうの。

class fallLift(Lift):
    """落下リフト(F)"""
    """乗ると落下を始め、画面外に消えると復活する"""
    def __init__(self, c_x, c_y, kind, border):
        # borderを過ぎると消滅して元に戻る
        Lift.__init__(self, c_x, c_y, kind)
        self.c_x = c_x
        self.c_y = c_y
        self.border = border
        self.v_y = 0.0
        self.wait = 0    # 復活するまでのフレーム数。
        # 直後に復活するの何か気持ち悪いので。

    def update(self):
        self.prefpy = self.fpy
        if self.visible and (self.ridden or self.v_y > 0):
            self.v_y += 0.1
            self.fpy += self.v_y
            self.rect.top = int(self.fpy)
        if not self.visible and self.fpy > self.border:
            self.wait += 1
            if self.wait > 119:   # 2秒後に復活
                self.fpy = self.c_y
                self.prefpy = self.fpy
                self.rect.top = int(self.fpy)
                self.visible = True
                self.v_y = 0.0
                self.wait = 0
        if self.fpy > self.border:
            self.visible = False
            # これでいいのか？？→いいみたい。
        
