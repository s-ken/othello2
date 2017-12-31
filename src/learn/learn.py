# -*- coding:utf-8 -*-

import sys,os
sys.path.append(os.pardir)
import board
import AI
import random

class Learner:
  STAGE_WIDTH  = 4
  NUM_STAGES   = 60/STAGE_WIDTH
  NUM_FEATURES = 11
  NUM_PATTARNS = [3**8]*3 + [3**4, 3**5, 3**6, 3**7, 3**8] + [3**10]*2 + [3**9]
  PAT2FEA      = [0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,8,8,8,8,9,9,9,9,9,9,9,9,10,10,10,10]

  STEPSZ      = 0.01 # 重み更新のステップサイズ係数
  RANDOMBEGIN = 8    # ゲーム最初のランダム手数
  RANDOMMOVE  = 0.01 # AIがランダムにコマを打つ確率

  def __init__(self):
    self.__weight    = self.__load_weights() # Logistelloパターン重み
    self.__board     = board.Board(False)
    self.__player    = [AI.AI(self.__board, 0, None, self.__weight),AI.AI(self.__board, 1, None, self.__weight)]
    self.__symm_table = self.__init_symmTable() # 各パターンの対称形のコードを格納するテーブル

  def init(self):
    self.__board.init()
    self.__turn = 0
    self.__num_disks = 0
    self.__passed = False
    self.__board_state = [None] * 60
    self.__player[0].set_weight(self.__weight)
    self.__player[1].set_weight(self.__weight)

  # AI同士で一試合プレイする
  def run(self):
    for i in range(Learner.RANDOMBEGIN):  # 最初の数手はランダムに打つ
      pos = random.choice(self.__board.placeable_cells(self.__turn%2))
      self.__board.put[pos](self.__turn%2)
      self.__board.update_empty_cells(pos)
      self.__board_state[self.__num_disks] = self.__board.get_state()
      self.__turn += 1
      self.__num_disks += 1
    while 1:
      if self.__num_disks == 60:
        break
      if self.__player[self.__turn%2].can_put():  # 置ける場所があればTrue
        if random.random() < Learner.RANDOMMOVE:  # ある確率でランダムに打つ
          pos = random.choice(self.__board.placeable_cells(self.__turn%2))
          self.__board.put[pos](self.__turn%2)
          self.__board.update_empty_cells(pos)
        else:
          self.__player[self.__turn%2].take_turn(self.__num_disks)
        self.__passed = False
        self.__board_state[self.__num_disks] = self.__board.get_state()   # ボードの状態を保存
        self.__num_disks += 1
      else:
        if self.__passed:  # 二人ともパス->終了
          return
        self.__passed = True
      self.__turn += 1

  # <概要> 保存されている一試合分の記録(boardState)をもとにlogistello重みを更新する
  def update_weight(self):
    t = float(self.__board.get_difference(0))
    for turn in range(self.__num_disks):
      stage = turn / 4
      self.__board.restore_state(self.__board_state[turn])
      feature = self.__board.get_features()
      t_hat = (
        self.__weight[stage][0][feature[0]]+self.__weight[stage][0][feature[1]]+self.__weight[stage][0][feature[2]]+self.__weight[stage][0][feature[3]]+
        self.__weight[stage][1][feature[4]]+self.__weight[stage][1][feature[5]]+self.__weight[stage][1][feature[6]]+self.__weight[stage][1][feature[7]]+
        self.__weight[stage][2][feature[8]]+self.__weight[stage][2][feature[9]]+self.__weight[stage][2][feature[10]]+self.__weight[stage][2][feature[11]]+
        self.__weight[stage][3][feature[12]]+self.__weight[stage][3][feature[13]]+self.__weight[stage][3][feature[14]]+self.__weight[stage][3][feature[15]]+
        self.__weight[stage][4][feature[16]]+self.__weight[stage][4][feature[17]]+self.__weight[stage][4][feature[18]]+self.__weight[stage][4][feature[19]]+
        self.__weight[stage][5][feature[20]]+self.__weight[stage][5][feature[21]]+self.__weight[stage][5][feature[22]]+self.__weight[stage][5][feature[23]]+
        self.__weight[stage][6][feature[24]]+self.__weight[stage][6][feature[25]]+self.__weight[stage][6][feature[26]]+self.__weight[stage][6][feature[27]]+
        self.__weight[stage][7][feature[28]]+self.__weight[stage][7][feature[29]]+
        self.__weight[stage][8][feature[30]]+self.__weight[stage][8][feature[31]]+self.__weight[stage][8][feature[32]]+self.__weight[stage][8][feature[33]]+
        self.__weight[stage][9][feature[34]]+self.__weight[stage][9][feature[35]]+self.__weight[stage][9][feature[36]]+self.__weight[stage][9][feature[37]]+self.__weight[stage][9][feature[38]]+self.__weight[stage][9][feature[39]]+self.__weight[stage][9][feature[40]]+self.__weight[stage][9][feature[41]]+
        self.__weight[stage][10][feature[42]]+self.__weight[stage][10][feature[43]]+self.__weight[stage][10][feature[44]]+self.__weight[stage][10][feature[45]]
      )
      delta = (t - t_hat) * Learner.STEPSZ
      for f in range(46):
        self.__weight[stage][Learner.PAT2FEA[f]][feature[f]] += delta
        symm = self.__symm_table[Learner.PAT2FEA[f]][feature[f]]
        if symm != feature[f]:                                      # 対称形があれば..
          self.__weight[stage][Learner.PAT2FEA[f]][symm] += delta   # それにも同じ値を加算

  # 重みをファイル出力
  def save_weight(self):
    for stage in range(Learner.NUM_STAGES):
      f = open("../../wei/w"+str(stage)+".txt", "w")
      for feature in range(11):
        for pattern in range(Learner.NUM_PATTARNS[feature]):
          f.write(str(self.__weight[stage][feature][pattern])+" ")
        f.write("\n")
      f.close()

  # symmTableを初期化する
  def __init_symmTable(self):
    line4SymmTable   = self.__initLineSymmTable(4)
    line5SymmTable   = self.__initLineSymmTable(5)
    line6SymmTable   = self.__initLineSymmTable(6)
    line7SymmTable   = self.__initLineSymmTable(7)
    line8SymmTable   = self.__initLineSymmTable(8)
    edge2xSymmTable  = self.__initLineSymmTable(10)
    cornerSymmTable  = self.__initCorner33SymmTable()
    return [line8SymmTable,line8SymmTable,line8SymmTable,line4SymmTable,line5SymmTable,line6SymmTable,line7SymmTable,line8SymmTable,edge2xSymmTable,range(3**10),cornerSymmTable]

  def __initLineSymmTable(self, length):
    table = [0] * (3**length)
    for i in range(3**length):
      code = i
      for j in range(length):
        table[i] += (code/(3**(length-1-j))) * (3**j)
        code %= 3**(length-1-j)
    return table

  def __initCorner33SymmTable(self):
    table = [0] * (3**9)
    for i in range(3**9):
      cell = [0] * 9
      code = i
      for j in range(9):
        cell[8-j] = code/(3**(8-j))
        code %= 3**(8-j)
      table[i] = cell[0]+cell[3]*(3**1)+cell[6]*(3**2)+cell[1]*(3**3)+cell[4]*(3**4)+cell[7]*(3**5)+cell[2]*(3**6)+cell[5]*(3**7)+cell[8]*(3**8)
    return table

  # 重みをファイル入力
  def __load_weights(self):
    weight = [[[0 for i in range(Learner.NUM_PATTARNS[j])] for j in range(Learner.NUM_FEATURES)] for k in range(Learner.NUM_STAGES)]
    for stage in range(Learner.NUM_STAGES):
      f = open("../../wei/w"+str(stage)+".txt", "r")
      for feature, line in enumerate(f):
        value = line.split(' ')
        for pattern in range(Learner.NUM_PATTARNS[feature]):
          weight[stage][feature][pattern] = float(value[pattern])
      f.close()
    return weight

def main():
  learner = Learner()
  i = 1
  while True:
    print "game:", i
    learner.init()
    learner.run()
    learner.update_weight()
    if not (i % 100): # 100試合毎に重みを保存
      print ""
      learner.save_weight()
    i += 1

if __name__ == "__main__":
  main()
