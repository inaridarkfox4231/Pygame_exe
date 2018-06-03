# Pygame_exe
Pythonで作ったゲームをexeファイルにしてみた。dist→downloadからZIP形式でダウンロードできる。  
twitter:https://twitter.com/inaba_darkfox?lang=ja
## snake_Action
　ヘビが動くアクションゲーム。左右キーで移動、スペースキーでジャンプ。右端に行ったら終わり、特に終わる感じはない。途中、壁に当たりながら反対のキーを押してスペースキーを押す「壁ジャンプ」を使わないといけないところがある。bボタンを押しながら移動するとダッシュできる。  
 ![sampleimage](https://github.com/inaridarkfox4231/Pygame_exe/blob/sample/sampleimages/snake_Action.PNG)
## tetris3
　3つのモードが用意されたテトリス。基本的な操作は、上キーで回転、左右キーで移動、下キーで確定。強制的に確定させるごとに5点。1列消すと1000点、2列で3000点、3列で5000点、4列で10000点入る。タイトル画面で3つのゲームモードと、ランキング閲覧画面を選択できる。
1. STAGE CLEAR  
　4つのステージを順にクリアしていく。順に10, 20, 30, 50ラインがノルマ。後の方に行くほど落ちるのが速くなる。  
2. SCORE ATTACK  
　10ライン消すごとにスピードが上がる。積むまでのスコアを競うモード。  
3. JUNK MODE  
　あらかじめランダムに配置された灰色のブロック(ジャンク)を全て消すとクリア。5つのステージがある。  
4. RANK MODE  
　ランキングを見ることができる。スコアの登録は各モードクリア時に行うことができる。  
 ![sampleimage](https://github.com/inaridarkfox4231/Pygame_exe/blob/sample/sampleimages/tetris3.PNG)
 ## fox_and_ball
　ボールが跳ね回るだけ。狐の鳴き声、謎のウサギ、壁に当たると打撃音。つまりゲームではない。  
 ![sampleimage](https://github.com/inaridarkfox4231/Pygame_exe/blob/sample/sampleimages/fox_and_ball.PNG)
