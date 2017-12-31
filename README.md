# othello

<b>動作環境：</b><br>
Python2.7 + pygame

<b>対戦方法：</b><br>
cd src<br>
python othello.py<br>

<b>強化学習の実行方法：</b><br>
cd src/learn<br>
\# python initWeight.py<br>
python learn.py<br>

<b>Boardクラス：</b><br>
インデックスによるオセロ盤の表現<br>
http://sealsoft.jp/thell/algorithm.html<br>

<b>AIクラス：</b><br>
Brainクラスの管理とAIによる着手処理<br>
BrainBook -> BrainMid -> BrainFin<br>

<b>BrainBookクラス：</b><br>
OpeningBookを読みつつゲームを進行<br>

<b>BrainMidクラス：</b><br>
AlphaBeta法によるゲーム木探索
MoveOrdering: 一手先の盤面評価値の高い順<br>
盤面評価関数: 盤面の各インデックスの評価+着手可能手数差(近似値)+確定石数差(近似値)<br>
各インデックスの評価: インデックスの全パターンの評価値は強化学習によって事前計算済み<br>

<b>BrainFinクラス：</b><br>
NegaScout法+AlphaBeta法による終盤読み切り<br>
MoveOrdering: 一手先の相手の着手可能手数(真値)の少ない順<br>
盤面評価関数: 石差<br>

<b>Youクラス：</b><br>
プレイヤーの着手処理<br>

<b>Gameクラス：</b><br>
ゲームの進行<br>
