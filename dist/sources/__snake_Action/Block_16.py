#_*_ coding:utf-8 _*_
# ブロックの仕様。
# 今んとこは設置するだけ。

import pygame
from pygame.locals import *
import os
import sys
from math import cos, sin, radians

class Block(pygame.sprite.Sprite):
    """ブロック"""
    """すごく簡単なクラス。位置指定だけ。"""
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
