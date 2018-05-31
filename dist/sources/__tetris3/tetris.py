"""
TETRIS.
左右のキーで移動、↑キーで回転。
"""
import pygame
from pygame.locals import *
import os
import sys
import random

BLACK, WHITE = ((0, 0, 0), (255, 255, 255))

GS = 20
SCR_RECT = Rect(0, 0, 500, 440)
SCR_W = SCR_RECT.width
SCR_H = SCR_RECT.height

JUNK = (1 << 5)  # ジャンクフラグ

dx = [0, -1, 0, 1]
dy = [1, 0, -1, 0]
next = []  # 次のブロック表示用
next.append([2, 1, 2, 2, 2, 3, 2, 4])
next.append([2, 3, 2, 4, 3, 2, 3, 3])
next.append([2, 2, 2, 3, 3, 3, 3, 4])
next.append([2, 2, 2, 3, 2, 4, 3, 2])
next.append([2, 2, 3, 2, 3, 3, 3, 4])
next.append([2, 2, 2, 3, 2, 4, 3, 3])
next.append([2, 2, 2, 3, 3, 2, 3, 3])

LINE_SCORE = [1000, 3000, 5000, 10000] # ライン消去時スコア

TITLE, START, PLAY, PAUSE, FREEZE, GAMEOVER, CLEAR, RANK = (0, 1, 2, 3, 4, 5, 6, 7)

class Play:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("tetris ver2.0")
        pygame.key.set_repeat(60)   # 押しっぱなしで繰り返し反応

        self.M = []  # ブロックの積み上げ状況。
        for i in range(25):
            line = []
            for j in range(12):
                line.append(0)
            self.M.append(line)

        # 画像処理関係
        self.tileimg = []    # タイル画像
        self.label = []      # LEVEL～とか。
        self.mode = []       # モード表示と白抜き。
        self.num = []        # 数字とか
        self.letter = []     # アルファベットとか。ドットとか。
        self.order = []      # 順位表示(1stとか2ndとか)
        self.explain = []    # キー操作説明など。
        self.config = self.load_image("KEY_CONFIG.png")  # 140×130.
        self.loading_images()

        self.frame = 0  # 落下時間管理
        self.State = TITLE  # ついに待望のタイトル画面が(おい

        # テトリミノ関係
        self.x = [0, 0, 0, 0]  # 操作するブロックの位置座標
        self.y = [0, 0, 0, 0]
        self.phase = 0
        self.type = 0
        self.next_type = random.randint(1, 7)  # 次のブロック。

        # ステータス関係
        self.score = 0  # スコア。
        self.scoreimg = []  # スコア表示用の画像格納用配列
        for i in range(7):
            self.scoreimg.append(self.num[0])  # とりあえず0を7個入れとく。
        self.level = 0  # レベル(スピードとかの制御に使う）。
        # 1, 2, 3, 4: ノルムが10, 20, 30, 50 落下時間が32, 24, 16, 8.
        self.norm = 0   # 達成すべき課題、もしくは消したライン数
        self.fall_time = 0   # 基本32→8と推移する。
        self.erase_line = []  # 消去するラインの行番号を格納。

        # ランキング関係
        self.ranking = []     # ランクスコアを入れる（(スコア,名前)って感じで。）
        self.rankingimg = []  # ランキングをポップ表示するための画像格納用配列。
        self.name = [-1, -1, -1]   # 名前入力用
        self.cursol = 0            # カーソル。3のときRANKでスペースでリセットする。
        # タイトル画面でのモード決定及びゲーム中の細かいモード仕様の違いとか
        # 検出に使う。

        # ファイル名テキスト
        self.file = []
        self.file.append(self.load_rank("RANK_STCL"))
        self.file.append(self.load_rank("RANK_SCAT"))
        self.file.append(self.load_rank("RANK_JUNK"))

        clock = pygame.time.Clock()
        
        while True:
            screen.fill(BLACK)
            clock.tick(60)
            if self.State == START:
                self.tetris_init()
                self.State = PLAY
            self.update()  # 落下処理など
            self.draw(screen)    # STARTでなければ常にdrawする。
            pygame.display.update()
            self.key_handler()   # ブロックの回転はPLAY時のみ可能。

    def tetris_init(self):
        # 各種初期化
        for i in range(25):
            for j in range(12):
                self.M[i][j] = 0  # すべて0にする。
        for i in range(25):
            self.M[i][0] = 8; self.M[i][11] = 6
        for j in range(12): self.M[24][j] = 8   # 周囲を8にする(判定用)

        self.make_block() # ブロック生成

        # STAGE CLEARモード。
        if self.cursol == 0:
            self.level += 1
            self.norm = self.level * 10 + (self.level // 4) * 10
            self.fall_time = 40 - self.level * 8
        # SCORE ATTACKモード。
        if self.cursol == 4:
            self.norm = 0        # 0から増えていく(消したライン数)
            self.fall_time = 32  # 32から減っていく
        # JUNK MODEモード.
        if self.cursol == 8:
            self.level += 1
            self.fall_time = 38 - self.level * 6
            # ジャンクは2行～6行で各行につき5～7個。normは常に0からスタートする。
            for i in range(23 - self.level, 24):
                a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                n = random.randint(5, 7)
                self.norm += 1
                self.M[i][11] = ((n + 6)|JUNK)
                for k in range(n):
                    p = random.randrange(10 - k)
                    self.M[i][a[p]] = 8
                    del a[p]

    def loading_images(self):
        # 各種画像、文字データのロード。
        # タイル画像のロード
        tiles = self.load_image("TILES.png")
        for i in range(9):
            surface = pygame.Surface((20, 20))
            surface.blit(tiles, (0, 0), (i * 20, 0, 20, 20))
            self.tileimg.append(surface)

        # 各種ラベルのロード
        # 順にLEVEL, NORM, SCORE, LINE, FALL, NEXT, TETRIS.
        labels = self.load_image("LABELS.png")
        end = [93, 76, 93, 76, 76, 66, 96]
        for i in range(7):
            surface = pygame.Surface((end[i], 30))
            surface.blit(labels, (0, 0), (0, 30 * i, end[i], 30))
            self.label.append(surface)

        # 各種モード表示のロード。
        # STAGE CLEAR, SCORE ATTACK, JUNK MODE, RANKING. 白抜きも。4を足してチェンジ。
        modes = self.load_image("MODES.png")
        end = [180, 194, 148, 116, 180, 194, 148, 116]
        for i in range(8):
            surface = pygame.Surface((end[i], 32))
            surface.blit(modes, (0, 0), (0, 32 * i, end[i], 32))
            self.mode.append(surface)
            
        # 各種数字画像のロード
        nums = self.load_image("NUMBER.png")
        for i in range(10):
            surface = pygame.Surface((18, 30))
            surface.blit(nums, (0, 0), (18 * i, 0, 18, 30))
            self.num.append(surface)

        # 各種アルファベットのロード, ドットも。
        letters = self.load_image("LETTER.png")
        for i in range(27):
            surface = pygame.Surface((18, 30))
            surface.blit(letters, (0, 0), (18 * i, 0, 18, 30))
            self.letter.append(surface)

        # 順位のロード
        orders = self.load_image("ORDER.png")
        for i in range(5):
            surface = pygame.Surface((48, 30))
            surface.blit(orders, (0, 0), (48 * i, 0, 48, 30))
            self.order.append(surface)

        # 説明のロード
        explains = self.load_image("EXPLAIN.png")
        sizes = [(200, 80), (200,80), (320, 120), (320, 100), (320, 50), (200, 80)]
        coord_y = [0, 80, 160, 280, 380, 430]
        for i in range(6):
            surface = pygame.Surface((sizes[i][0], sizes[i][1]))
            surface.blit(explains, (0, 0), (0, coord_y[i], sizes[i][0], sizes[i][1]))
            self.explain.append(surface)

    def update(self):
        if self.State == PLAY:
            self.frame += 1    # PLAY中はフレームを進める。
            if self.frame > self.fall_time:
                self.frame = 0
                self.check()  # FREEZE判定

        if self.State == FREEZE and self.frame == 0:
            # frame正でFREEZEのときは消えるアニメ中
            # GAMEOVER判定。
            if self.M[4][5] > 0 or self.M[4][6] > 0:
                self.State = GAMEOVER;
                self.frame += 1; return   # GAMEOVER時のアニメをdrawで行う。
            # 必要なら行消去(del, insert)。
            if len(self.erase_line) > 0:
                L = len(self.erase_line)
                for k in range(L): del self.M[self.erase_line[k]]
                # 両側は8にして移動不可にしておかないと、端っこに移動出来てしまう。
                for k in range(L): self.M.insert(0, [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6])
                self.erase_line = []  # リセット。
                # self.score += LINE_SCORE[L - 1]  # 消した行の数に応じてスコアを与える。
                self.scoreimg_update(self.score + LINE_SCORE[L - 1])

                if self.cursol == 0:
                    self.norm = max(self.norm - L, 0)
                    # この「ノルマ達成でCLEAR」ってのはSTAGE CLEARモード限定なので、
                    # 今回の仕様変更で変えないといけないところ。
                    if self.norm == 0: self.State = CLEAR; return
                elif self.cursol == 4:
                    # SCORE ATTACKでは10ライン消すごとにfall_time -2. (最低で8まで下がる。)
                    for i in range(L):  # とばすとマズいので1をL回足す。
                        self.norm += 1
                        if not self.norm < 1000: self.norm = 999  # カンスト対策
                        if self.norm % 10 == 0 and self.norm > 0:
                            self.fall_time = max(self.fall_time - 2, 8)
                elif self.cursol == 8:
                    # ジャンクモードではもうジャンク減らしてあるので0かどうかチェックするだけ。
                    if self.norm == 0: self.State = CLEAR; return  # normはもう減らしてある(はず)
                
            self.make_block()  # ブロックを作る。
            self.State = PLAY  # StateをPLAYに戻す。

    def scoreimg_update(self, b):
        if not b < 10000000: return  # カンスト対策
        # 新しいスコアをもとにしてscoreimgの内容を更新する。bは新しいスコア。
        a = self.score  # 元のスコア。
        new_score = b   # 新しいスコア。
        r = 0  # 桁。
        while a != b:   # 途中から同じになるようなら終了
            if b % 10 != a % 10:
                self.scoreimg[r] = self.num[b % 10]  # 違う桁のとこだけ更新
            a = a // 10
            b = b // 10
            r += 1      # rを増やす。
        self.score = new_score  # スコアの更新

    def draw(self, screen):
        if self.State == TITLE:
            if self.cursol & 12 == 0:
                # 上位2bitが0のときTITLE.
                self.draw_title(screen); return
            else:
                # 上位2bitが4, 8, 12のときランキング閲覧モード
                self.draw_rank(screen); return

        if self.State == RANK:
            self.draw_rank(screen); return

        # ブロックの描写
        pygame.draw.rect(screen, (255, 255, 255), (145, 15, 210, 410))
        pygame.draw.rect(screen, (235, 235, 235), (150, 20, 200, 400))

        for i in range(4, 24):
            for j in range(1, 11):
                if self.M[i][j] > 0:
                    screen.blit(self.tileimg[self.M[i][j]], (130 + 20 * j, -60 + 20 * i))

        self.draw_status(screen)   # ステータス表示, NEXT BLOCKの表示。

        # 落下中のブロックの描写。
        if self.State == PLAY or self.State == PAUSE:
            for k in range(4):
                j = self.x[k]; i = self.y[k]
                if i > 3:
                    screen.blit(self.tileimg[self.type], (130 + 20 * j, -60 + 20 * i))
        if self.State == PAUSE:
            # PAUSE表示。
            screen.blit(self.explain[5], (150, 180))
        
        # FREEZE中の行消去アニメ
        if self.State == FREEZE:
            if self.frame > 0:
                self.frame += 1  # アニメ中はフレームを進める。
                if self.frame // 4 % 2 == 0:
                    for i in self.erase_line:
                        pygame.draw.rect(screen, (235, 235, 235), (150, -60 + 20 * i, 200, 20))
            if self.frame > 64:  # 64フレームで終了
                self.frame = 0   # このあとupdateに戻り消去処理を行う。
                # なお、消去が起こる場合GAMEOVERにはならない.

        if self.State == GAMEOVER:  # GAMEOVERアニメ。
            if self.frame > 0:
                self.frame += 1   # フレームを進める。
                if self.frame % 2 == 0:
                    # 2フレームごとに灰色にしていく。
                    for j in range(1, 11):
                        if self.M[(self.frame // 2) + 3][j] > 0: self.M[(self.frame // 2) + 3][j] = 8
            if self.frame > 40:
                self.frame = 0  # 40フレームで終了
            if self.frame == 0:
                # GAMEOVERのテキスト。
                screen.blit(self.explain[0], (150, 180))

        if self.State == CLEAR:
            # CLEARのテキスト。
            screen.blit(self.explain[1], (150, 180))

    def draw_title(self, screen):
        # タイトル画面。3つのモードを選ぶ。
        screen.blit(self.label[6], (202, 80))
        for i in range(4):
            if self.cursol == i:
                screen.blit(self.mode[i + 4], (153, 190 + 40 * i))
            else:
                screen.blit(self.mode[i], (153, 190 + 40 * i))

    def draw_status(self, screen):
        # ステータス表示
        if self.cursol == 0 or self.cursol == 8:
            screen.blit(self.label[0], (5, 10))   # LEVEL
            screen.blit(self.num[self.level], (98, 10))
            screen.blit(self.label[1], (5, 42))   # NORM
            screen.blit(self.num[self.norm // 10], (81, 42))
            screen.blit(self.num[self.norm % 10], (99, 42))

        elif self.cursol == 4:
            screen.blit(self.label[4], (5, 10))  # FALL
            screen.blit(self.num[self.fall_time // 10], (81, 10))
            screen.blit(self.num[self.fall_time % 10], (99, 10))
            screen.blit(self.label[3], (5, 42))  # LINE
            screen.blit(self.num[self.norm // 100], (81, 42))
            screen.blit(self.num[(self.norm // 10) % 10], (99, 42))
            screen.blit(self.num[self.norm % 10], (117, 42))

        screen.blit(self.label[2], (5, 90)) # SCORE
        for i in range(7):
            screen.blit(self.scoreimg[i], (123 - 18 * i, 120))  # SCOREの数字

        # 次のブロックの表示。
        screen.blit(self.label[5], (397, 55))  # NEXT
        pygame.draw.rect(screen, (255, 255, 255), (365, 90, 130, 130))
        pygame.draw.rect(screen, (235, 235, 235), (370, 95, 120, 120))
        screen.blit(self.config, (360, 250))  # キー操作説明
        nt = self.next_type
        for i in range(4):
            screen.blit(self.tileimg[nt], (370 + next[nt - 1][2 * i] * 20, 95 + next[nt - 1][2 * i + 1] * 20))
        
    def key_handler(self):
        # キー操作
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.State == PLAY:
                    if event.key == K_DOWN:  # ↓ボタンでスコア+5.
                        self.scoreimg_update(self.score + 5)
                        self.frame = self.fall_time; return
                    if event.key == K_UP:  # ↑ボタンで回転
                        opt = [0, 1, -1, -2]  # -2は縦棒の回転用
                        for opt_x in opt:
                            if self.rollable(opt_x):
                                self.phase = (self.phase + 1) % 4
                                self.slide(opt_x); self.set_block(); return

                    if event.key == K_RIGHT: self.slide(1); return  # →←ボタンで移動
                    if event.key == K_LEFT: self.slide(-1); return
                    if event.key == K_SPACE: self.State = PAUSE; return

                if self.State == PAUSE and event.key == K_RETURN: self.State = PLAY; return

                if self.State == GAMEOVER and event.key == K_RETURN:
                    if self.frame == 0:
                        if self.cursol == 0 or self.cursol == 8:
                            self.reset(); self.State = TITLE; return
                        if self.cursol == 4:
                            self.State = RANK;
                            self.read_rank(self.file[1] + ".txt"); return

                if self.State == RANK:
                    if (self.cursol & 3) == 3 and event.key == K_SPACE:
                        self.reset()
                        self.State = TITLE  # ランク書き込み中はcursolが0, 1, 2になってて移行できない。
                    else:
                        # ランクの更新
                        self.write_rank(event.key, self.file[(self.cursol & 12) >> 2] + ".txt")
                            
                if self.State == CLEAR and event.key == K_RETURN:
                    # ステージクリアモード
                    if (self.cursol == 0 and self.level < 4) or (self.cursol == 8 and self.level < 5):
                        self.State = START; return
                    else:
                        self.State = RANK; self.read_rank(self.file[self.cursol >> 2] + ".txt")
                        return

                if self.State == TITLE:
                    # 上下キーでモード選択、エンターでSTARTに遷移。scoreが0のときのみ。
                    if self.cursol & 12 == 0:
                        # タイトル画面での操作
                        if event.key == K_DOWN:
                            self.cursol = (self.cursol + 1) % 4
                        elif event.key == K_UP:
                            self.cursol = (self.cursol + 3) % 4
                        elif event.key == K_RETURN:
                            if self.cursol < 3:
                                self.State = START
                                self.cursol <<= 2  # 0, 4, 8でモードを表す。
                            elif self.cursol == 3:
                                self.cursol |= 4  # カーソルいじる
                                self.read_rank(self.file[0] + ".txt")
                    else:
                        # ランキングモードでの操作(score正、戻るときに戻す)。
                        # 7, 11, 15でモードを表す。
                        if event.key == K_RIGHT or event.key == K_LEFT:
                            if event.key == K_RIGHT:
                                self.cursol += 4
                                if self.cursol > 15: self.cursol -= 12
                            else:
                                self.cursol -= 4
                                if self.cursol < 7: self.cursol += 12
                            self.read_rank(self.file[(self.cursol - 7) >> 2] + ".txt")
                            
                        elif event.key == K_SPACE:
                            self.cursol &= 3  # カーソルを戻す。


    def reset(self):
        # レベル0に戻す、スコアは0から、next_typeも計算し直す。
        self.level = 0
        self.norm = 0
        self.score = 0
        self.scoreimg = []  # スコア表示も初期化。
        for i in range(7):
            self.scoreimg.append(self.num[0])
        self.fall_time = 32
        self.next_type = random.randint(1, 7)
        # ランキング関連のリセット処理
        self.ranking = []
        self.name = [-1, -1, -1]
        self.cursol = 0

    def make_block(self):
        # ブロックを作る
        self.type = self.next_type  # typeを決めたよ。
        self.next_type = random.randint(1, 7)  # ここでnextを決めるとか。
        if self.type == 5: self.x[0] = 6  # nextはスタンダードなやつをnext blockとかして右に表示する感じで。
        else: self.x[0] = 5
        if self.type == 1: self.y[0] = 2
        elif self.type == 7: self.y[0] = 4
        else: self.y[0] = 3
        self.phase = 0
        self.set_block()

    def set_block(self):
        # typeとphaseに応じてブロックの形状(各パーツの位置)を指定。
        a = self.x[0]; b = self.y[0]; t = self.type; p = self.phase
        if t < 4:
            q = p % 2
            if t == 1:
                self.x[1] = a - q; self.x[2] = a + q; self.x[3] = a + 2 * q
                self.y[1] = b - 1 + q; self.y[2] = b + 1 - q; self.y[3] = b + 2 * (1 - q); return
            if t == 2:
                self.x[1] = a; self.x[2] = a + 1 - 2 * q; self.x[3] = a + 1
                self.y[1] = b + 1; self.y[2] = b; self.y[3] = b - 1 + 2 * q; return
            if t == 3:
                self.x[1] = a + 1; self.x[2] = a; self.x[3] = a + 1 - 2 * q
                self.y[1] = b; self.y[2] = b - 1 + 2 * q; self.y[3] = b + 1; return
        if t < 7:
            self.x[1] = a + dx[p]; self.x[2] = a - dx[p]
            self.y[1] = b + dy[p]; self.y[2] = b - dy[p]
            if t == 4:
                self.x[3] = a + dy[p] - dx[p]; self.y[3] = b - dx[p] - dy[p]; return
            if t == 5:
                self.x[3] = a - dx[p] - dy[p]; self.y[3] = b + dx[p] - dy[p]; return
            if t == 6:
                self.x[3] = a + dy[p]; self.y[3] = b - dx[p]; return
        if t == 7:
            self.x[1] = a; self.x[2] = a + 1; self.x[3] = a + 1
            self.y[1] = b - 1; self.y[2] = b; self.y[3] = b - 1; return

    def is_zero(self, a, b):
        # 空いてるかどーか。端っこの処理のためにメソッド化した。
        if a < 0 or a > 11: return False
        return self.M[b][a] == 0

    def rollable(self, opt_x):
        # 回転可能か調べる。これがTrueを返すならphaseを変えたうえでself.set_block()を呼び出す。
        if self.type == 7: return True  # 正方形。
        # opt_xだけずらした場合の回転可能性を調べることでずらせば回転できないか調べる。
        # opt_x > 0なら右ずらし、opt_x < 0なら左ずらし。
        a = self.x[0] + opt_x; b = self.y[0]; t = self.type; p = self.phase
        if t < 4:
            q = (p + 1) % 2  # qは次の位相で計算。
            if t == 1:
                return self.is_zero(a - q, b - 1 + q) and self.is_zero(a + q, b + 1 - q) and self.is_zero(a + 2 * q, b + 2 * (1 - q))
            if t == 2:
                return self.is_zero(a + 1 - 2 * q, b) and self.is_zero(a + 1, b - 1 + 2 * q)
            if t == 3:
                return self.is_zero(a, b - 1 + 2 * q) and self.is_zero(a + 1 - 2 * q, b + 1)
        if t < 7:
            q = (p + 1) % 4  # qは次の位相で計算。
            x1 = a + dx[q]; x2 = a - dx[q]; y1 = b + dy[q]; y2 = b - dy[q]
            if self.is_zero(x1, y1) and self.is_zero(x2, y2):
                if t == 4:
                    return self.is_zero(a + dy[q] - dx[q], b - dx[q] - dy[q])
                if t == 5:
                    return self.is_zero(a - dx[q] - dy[q], b + dx[q] - dy[q])
                if t == 6:
                    return self.is_zero(a + dy[q], b - dx[q])

    def slide(self, d):
        if d == 0: return
        # 左右移動する。不可能なら何もしない。
        for i in range(4):
            if not self.is_zero(self.x[i] + d, self.y[i]): return
        for i in range(4): self.x[i] += d

    def check(self):
        # この時点で落とせないならStateをFREEZEに。落とせるなら1段落とす。
        for i in range(4):
            if self.M[self.y[i] + 1][self.x[i]] > 0:
                self.State = FREEZE;
                self.write(); return  # マップへの書き込み処理と必要ならeraseの準備。
        for i in range(4):
            self.y[i] += 1  # 1段落とす。

    def write(self):
        # マップに書き込み(はみ出てたら0にする), 消去する行があればチェックする。
        # ジャンクモードではジャンクの数を減らす。
        for i in range(4):
            if self.y[i] < 4: self.M[self.y[i]][self.x[i]] = 0
            else:
                self.M[self.y[i]][self.x[i]] = self.type
                self.M[self.y[i]][11] += 1  # 行単位でブロックの個数を更新

        for i in range(4, 24):
            if self.M[27 - i][11] & 16:
                self.erase_line.append(27 - i)
                if self.M[27 - i][11] & JUNK: self.norm -= 1
            if self.M[27 - i][11] ^ 6 == 0: break  # 空の行は浮かない。

        if len(self.erase_line) > 0: self.frame += 1   # 消去する行があればフレーム処理でアニメ作る。

    def read_rank(self, filename):
        # ランキングデータの読み込み
        self.ranking = []  # 一旦空にする。
        self.rankingimg = []  # 画像。
        data = []
        fp = open(filename, "r")
        for row in fp:
            row = row.rstrip()  # 改行除去
            data.append(row.split(' '))
        fp.close()
        for i in range(5):
            self.ranking.append((int(data[0][5 + i]), data[0][i]))

        self.make_rankingimg()  # rankingimgの作成。

        # TITLEのときは読み込むだけ(key_handlerで行う感じ).
        if self.State == RANK:
            # 最下位スコア(int(self.ranking[4][0])よりスコアが大きければcursolを0にする。
            if self.ranking[4][0] <= self.score:
                # self.cursol = 0   # 記入準備。
                self.name[0] = 0  # 一文字目をAに。
            else:
                self.cursol |= 3   # さもなくば3を立てる

    def make_rankingimg(self):
        # rankingimgの作成。
        for i in range(5):
            data = []
            for k in range(3):  # 名前
                o = ord(self.ranking[i][1][k])
                if o > 60: data.append(self.letter[o - 65])
                else: data.append(self.letter[26])  # ドットを許したので場合分け。
            n = self.ranking[i][0]  # スコア 
            for k in range(7):
                data.append(self.num[n % 10])
                n = (n // 10)
            self.rankingimg.append(data)  # これをいくつも作る。

    def write_rank(self, key, filename):
        # ランキングデータの更新
        # カーソル位置が0,1,2の時は上下キーでアルファベット選択.
        # cursolが3のときは何もすることが無い。
        # リターンキーを押してカーソルが3になった時にファイル書き込みとrankingの更新を行う。
        # あと、リセットの所にranking = []を忘れずに。
        if key == K_UP:
            self.name[self.cursol & 3] = (self.name[self.cursol & 3] + 1) % 27
        elif key == K_DOWN:
            self.name[self.cursol & 3] = (self.name[self.cursol & 3] + 26) % 27
        elif key == K_BACKSPACE and (self.cursol & 3) > 0:
            self.name[self.cursol & 3] = -1
            self.cursol -= 1
        elif key == K_RETURN:
            self.cursol += 1 
            if (self.cursol & 3) == 3:  # 3になったときに一回だけ行われる。
                self.ranking_update(filename)
            else:
                self.name[self.cursol & 3] = 0  # なんかアットマーク出ちゃうから修正。

    def ranking_update(self, filename):
        # ランキングのアップデート
        new_name = []
        for i in range(3):
            let = chr(65 + self.name[i])
            if self.name[i] < 26:
                new_name.append(let)
            else:
                new_name.append(".")  # ドット処理
        self.ranking.append((self.score, new_name[0] + new_name[1] + new_name[2]))
        self.ranking.sort()
        self.ranking.reverse()
        # ここで中身が変わったので、再びself.rankingimgを作成しなければならない。
        self.rankingimg = []
        self.make_rankingimg()
        
        # ファイル書き込み操作。
        fp = open(filename, "w")
        for i in range(5):
            fp.write(self.ranking[i][1] + " ")
        for i in range(5):
            fp.write(str(self.ranking[i][0]) + " ")
        fp.close()

    def draw_rank(self, screen):
        # 元ランキング表示部分
        for i in range(5):
            screen.blit(self.order[i], (113, 140 + 35 * i))
            for k in range(3):
                screen.blit(self.rankingimg[i][k], (181 + 18 * k, 140 + 35 * i))
            for k in range(7):
                screen.blit(self.rankingimg[i][9 - k], (255 + 18 * k, 140 + 35 * i))
            
        # TITLEモードのモード名表示
        if self.State == TITLE:
            screen.blit(self.mode[(self.cursol - 7) >> 2], (160, 40))
            # キー操作。
            screen.blit(self.explain[3], (80, 315))

        if self.State == RANK:
            # モード名表示
            screen.blit(self.mode[(self.cursol & 12) >> 2], (160, 30)) 

            # スコアと名前入力部分(RANKモードのみ)
            for i in range(7):
                screen.blit(self.scoreimg[6 - i], (255 + 18 * i, 80))

            if self.cursol & 3 < 3:
                for i in range(3):
                    # アルファベットを置く場所
                    pygame.draw.rect(screen, (255, 255, 255), (182 + 18 * i, 111, 16, 3))
                for i in range((self.cursol & 3) + 1):
                    # アルファベット表示(self.letter[]の出番)
                    screen.blit(self.letter[self.name[i]], (181 + 18 * i, 80))
                # キー操作説明(スコア入力用)
                screen.blit(self.explain[2], (80, 315))
            else:
                # スコア入力後。
                screen.blit(self.explain[4], (80, 320))

    def load_image(self, filename):
        filename = os.path.join("images", filename)
        image = pygame.image.load(filename).convert()
        return image

    def load_rank(self, filename):
        filename = os.path.join("rankdata", filename)
        return filename

if __name__ == "__main__":
    Play()

        
