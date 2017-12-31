# -*- coding:utf-8 -*-

import othello

#######################################################################################################################
# 序盤戦用探索アルゴリズム
# 定石集を用いた着手位置の選択
class BrainBook():
  def __init__(self, board, color, opening_book):
    self.__board = board  # boardへの参照
    self.__color = color  # 自分の色
    self.__opening_book = opening_book

  # OpeningBookを参照して次の手を返す
  def evaluate(self, _):
    x, y = self.__opening_book.read()
    return x + y * 8

  def is_valid(self, _):
    return self.__opening_book.is_valid()


#######################################################################################################################
# 中盤戦用探索アルゴリズム
# 探索:AlphaBeta, 盤面評価:位置+着手可能手数+確定石数, MoveOrdering:1手先の盤面評価値
class BrainMid():
  NUM_STAGES = 60/4
  NUM_FEATURES = 11
  NUM_PATTARNS = [3**8]*3 + [3**4, 3**5, 3**6, 3**7, 3**8] + [3**10]*2 + [3**9]

  def __init__(self, board, color, weight=None):
    self.__board = board  # boardへの参照
    self.__color = color  # 自分の色
    if weight is None:
      self.__weight = self.__load_weights()
    else:
      self.__weight = weight  # Logistello重み
    self.__stage = None       # 盤面評価関数で使用するステージ

  # 現盤面の全着手可能位置をそれぞれ評価し,評価値が最大となる位置を返す.
  def evaluate(self, num_discs):
    # 探索関数にnum_discsを渡してincするのはだるいので,
    # num_discs+探索木の高さ から盤面評価関数が呼び出された時点での盤面でのstageを計算してしまう。
    # 途中パスでゲーム終了してしまうような場合には誤った値となるが、まぁそれはいいとする。
    self.__stage = (num_discs + othello.Config.MID_HEIGHT) / 4
    placeable_cells = self.__board.placeable_cells(self.__color)
    placeable_cells = self.__move_ordering(placeable_cells, self.__color)

    state_cpy = self.__board.get_state()  # 盤面コピー
    max_val = -othello.Config.INF
    a = -othello.Config.INF
    for placeable_cell in placeable_cells:
      self.__board.put[placeable_cell](self.__color)
      value = -self.__alphaBeta(not self.__color, othello.Config.MID_HEIGHT-1, -othello.Config.INF, -a, False)
      self.__board.restore_state(state_cpy)
      if value > max_val:
        a = max(a, value)
        max_val = value
        res = placeable_cell
    return res

  def is_valid(self, num_discs):
    return num_discs < othello.Config.FIN_PHASE

  def set_weight(self, weight):
    self.__weight = weight

  """
  def __negaScout(self, color, height, alpha, beta, passed):
    placeable_cells = self.__board.placeable_cells(color)
    if not len(placeable_cells):
      if passed:
        return self.__evaluate_leaf(color) # 連続パスでゲーム終了 TODO
      return -self.__negaScout(not color, height, -beta, -alpha, True)  # パス
    state_cpy = self.__board.get_state()

    if height >= 5:
      placeable_cells = self.__move_ordering(placeable_cells, color)
      self.__board.put[placeable_cells[0]](color)
      maxValue = value = -self.__negaScout(not color, height - 1, -beta, -alpha, False)
      self.__board.restore_state(state_cpy)
      if value >= beta:
        return value
      if value > alpha:
        alpha = value
      for placeable_cell in placeable_cells[1:]:
        self.__board.put[placeable_cell](color)
        value = -self.__negaScout(not color, height - 1, (-alpha) - 1, -alpha, False)
        self.__board.restore_state(state_cpy)
        if value >= beta:
          return value
        if value > alpha:
          alpha = value
          self.__board.put[placeable_cell](color)
          value = -self.__negaScout(not color, height - 1, -beta, -alpha, False)
          self.__board.restore_state(state_cpy)
          if value >= beta:
            return value
          if value > alpha:
            alpha = value
        maxValue = max(maxValue, value)
      return maxValue

    else:
      maxValue = -othello.Config.INF
      for placeable_cell in placeable_cells:
        self.__board.put[placeable_cell](color)
        value = -self.__alphaBeta(not color, height - 1, -beta, -alpha, False)
        self.__board.restore_state(state_cpy)
        if value >= beta:
          return value  # カット
        if value > maxValue:
          alpha = max(alpha, value)
          maxValue = value
      return maxValue
  """

  # アルファベータ法： http://uguisu.skr.jp/othello/alpha-beta.html
  # <引数> board:Board型, color:int(0~1), height:(1~MAX_SEARCH_HEIGHT), alpha:int, beta:int
  # <返値> int
  def __alphaBeta(self, color, height, alpha, beta, passed):
    # 設定した深さまでたどり着いたら(height=0)再帰終了
    if not height:
      return self.__evaluate_leaf(color)

    # 着手可能位置の取得
    placeable_cells = self.__board.placeable_cells(color)
    if not len(placeable_cells):
      if passed:
        return self.__evaluate_leaf(color) # 連続パスで終了
      return -self.__alphaBeta(not color, height, -beta, -alpha, True)  # パス
    if height >= 3:
      placeable_cells = self.__move_ordering(placeable_cells, color)

    # 探索
    state_cpy = self.__board.get_state()
    max_val = -othello.Config.INF
    for placeable_cell in placeable_cells:
      self.__board.put[placeable_cell](color)
      value = -self.__alphaBeta(not color, height - 1, -beta, -alpha, False)
      self.__board.restore_state(state_cpy)
      if value >= beta:
        return value  # 枝刈り
      if value > max_val:
        alpha = max(alpha, value)
        max_val = value
    return max_val

  # ゲーム木探索中の枝刈り回数増加のために,与えられた次手候補リストを評価値の見込みが高い順にソートする.
  def __move_ordering(self, list_pos, color):
    state_cpy = self.__board.get_state()  # 盤面コピー
    values = [0] * len(list_pos)
    for i, pos in enumerate(list_pos):
      self.__board.put[pos](color)
      values[i] = self.__evaluate_leaf(color)
      self.__board.restore_state(state_cpy)
    return [pos for _, pos in sorted(zip(values, list_pos),reverse=True)]

  # <概要> logistelloパターン+着手可能数差による評価
  def __evaluate_leaf(self, color):
    feature = self.__board.get_features()
    if color:
      return -(
        self.__weight[self.__stage][0][feature[0]]+self.__weight[self.__stage][0][feature[1]]+self.__weight[self.__stage][0][feature[2]]+self.__weight[self.__stage][0][feature[3]]+
        self.__weight[self.__stage][1][feature[4]]+self.__weight[self.__stage][1][feature[5]]+self.__weight[self.__stage][1][feature[6]]+self.__weight[self.__stage][1][feature[7]]+
        self.__weight[self.__stage][2][feature[8]]+self.__weight[self.__stage][2][feature[9]]+self.__weight[self.__stage][2][feature[10]]+self.__weight[self.__stage][2][feature[11]]+
        self.__weight[self.__stage][3][feature[12]]+self.__weight[self.__stage][3][feature[13]]+self.__weight[self.__stage][3][feature[14]]+self.__weight[self.__stage][3][feature[15]]+
        self.__weight[self.__stage][4][feature[16]]+self.__weight[self.__stage][4][feature[17]]+self.__weight[self.__stage][4][feature[18]]+self.__weight[self.__stage][4][feature[19]]+
        self.__weight[self.__stage][5][feature[20]]+self.__weight[self.__stage][5][feature[21]]+self.__weight[self.__stage][5][feature[22]]+self.__weight[self.__stage][5][feature[23]]+
        self.__weight[self.__stage][6][feature[24]]+self.__weight[self.__stage][6][feature[25]]+self.__weight[self.__stage][6][feature[26]]+self.__weight[self.__stage][6][feature[27]]+
        self.__weight[self.__stage][7][feature[28]]+self.__weight[self.__stage][7][feature[29]]+
        self.__weight[self.__stage][8][feature[30]]+self.__weight[self.__stage][8][feature[31]]+self.__weight[self.__stage][8][feature[32]]+self.__weight[self.__stage][8][feature[33]]+
        self.__weight[self.__stage][9][feature[34]]+self.__weight[self.__stage][9][feature[35]]+self.__weight[self.__stage][9][feature[36]]+self.__weight[self.__stage][9][feature[37]]+self.__weight[self.__stage][9][feature[38]]+self.__weight[self.__stage][9][feature[39]]+self.__weight[self.__stage][9][feature[40]]+self.__weight[self.__stage][9][feature[41]]+
        self.__weight[self.__stage][10][feature[42]]+
        self.__weight[self.__stage][10][feature[43]]+
        self.__weight[self.__stage][10][feature[44]]+
        self.__weight[self.__stage][10][feature[45]]+
        self.__board.get_mobility(0))
    else:
      return (
        self.__weight[self.__stage][0][feature[0]]+self.__weight[self.__stage][0][feature[1]]+self.__weight[self.__stage][0][feature[2]]+self.__weight[self.__stage][0][feature[3]]+
        self.__weight[self.__stage][1][feature[4]]+self.__weight[self.__stage][1][feature[5]]+self.__weight[self.__stage][1][feature[6]]+self.__weight[self.__stage][1][feature[7]]+
        self.__weight[self.__stage][2][feature[8]]+self.__weight[self.__stage][2][feature[9]]+self.__weight[self.__stage][2][feature[10]]+self.__weight[self.__stage][2][feature[11]]+
        self.__weight[self.__stage][3][feature[12]]+self.__weight[self.__stage][3][feature[13]]+self.__weight[self.__stage][3][feature[14]]+self.__weight[self.__stage][3][feature[15]]+
        self.__weight[self.__stage][4][feature[16]]+self.__weight[self.__stage][4][feature[17]]+self.__weight[self.__stage][4][feature[18]]+self.__weight[self.__stage][4][feature[19]]+
        self.__weight[self.__stage][5][feature[20]]+self.__weight[self.__stage][5][feature[21]]+self.__weight[self.__stage][5][feature[22]]+self.__weight[self.__stage][5][feature[23]]+
        self.__weight[self.__stage][6][feature[24]]+self.__weight[self.__stage][6][feature[25]]+self.__weight[self.__stage][6][feature[26]]+self.__weight[self.__stage][6][feature[27]]+
        self.__weight[self.__stage][7][feature[28]]+self.__weight[self.__stage][7][feature[29]]+
        self.__weight[self.__stage][8][feature[30]]+self.__weight[self.__stage][8][feature[31]]+self.__weight[self.__stage][8][feature[32]]+self.__weight[self.__stage][8][feature[33]]+
        self.__weight[self.__stage][9][feature[34]]+self.__weight[self.__stage][9][feature[35]]+self.__weight[self.__stage][9][feature[36]]+self.__weight[self.__stage][9][feature[37]]+self.__weight[self.__stage][9][feature[38]]+self.__weight[self.__stage][9][feature[39]]+self.__weight[self.__stage][9][feature[40]]+self.__weight[self.__stage][9][feature[41]]+
        self.__weight[self.__stage][10][feature[42]]+
        self.__weight[self.__stage][10][feature[43]]+
        self.__weight[self.__stage][10][feature[44]]+
        self.__weight[self.__stage][10][feature[45]]+
        self.__board.get_mobility(0))

  # <概要> 重みをロードする
  def __load_weights(self):
    weight = [[[0 for i in range(BrainMid.NUM_PATTARNS[j])] for j in range(BrainMid.NUM_FEATURES)] for k in range(BrainMid.NUM_STAGES)]
    for stage in range(BrainMid.NUM_STAGES):
      f = open("../wei/w"+str(stage)+".txt", "r")
      for feature, line in enumerate(f):
        value = line.split(' ')
        for pattern in range(BrainMid.NUM_PATTARNS[feature]):
          weight[stage][feature][pattern] = float(value[pattern])
      f.close()
    return weight


#######################################################################################################################
# 終盤戦用探索アルゴリズム
# 探索:NegaScout + AlphaBeta, 盤面評価:石差, MoveOrdering:着手可能手数の少ない順
class BrainFin():
  def __init__(self, board, color):
    self.__board = board  # boardへの参照
    self.__color = color  # 自分の色

  # 現盤面の全着手可能位置をそれぞれ評価し,評価値が最大となる位置を返す.
  def evaluate(self, turnCounter):
    placeable_cells = self.__move_ordering(self.__board.placeable_cells(self.__color), not self.__color)
    state_cpy = self.__board.get_state()
    maxValue = -othello.Config.INF
    a = -othello.Config.INF
    for placeable_cell in placeable_cells:
      self.__board.put[placeable_cell](self.__color)
      value = -self.__negaScout(not self.__color, 59 - turnCounter, -othello.Config.INF, -a, False)
      self.__board.restore_state(state_cpy)
      if value > maxValue:
        a = max(a, value)
        maxValue = value
        res = placeable_cell
    return res

  def is_valid(self, turnCounter):
    return True

  def __negaScout(self, color, height, alpha, beta, passed):
    placeable_cells = self.__board.placeable_cells(color)
    if not len(placeable_cells):
      if passed:
        return self.__evaluate_leaf(color) # 連続パスでゲーム終了 TODO
      return -self.__negaScout(not color, height, -beta, -alpha, True)  # パス
    state_cpy = self.__board.get_state()

    if height >= 5:
      placeable_cells = self.__move_ordering(placeable_cells, color)
      self.__board.put[placeable_cells[0]](color)
      maxValue = value = -self.__negaScout(not color, height - 1, -beta, -alpha, False)
      self.__board.restore_state(state_cpy)
      if value >= beta:
        return value
      if value > alpha:
        alpha = value
      for placeable_cell in placeable_cells[1:]:
        self.__board.put[placeable_cell](color)
        value = -self.__negaScout(not color, height - 1, (-alpha) - 1, -alpha, False)
        self.__board.restore_state(state_cpy)
        if value >= beta:
          return value
        if value > alpha:
          alpha = value
          self.__board.put[placeable_cell](color)
          value = -self.__negaScout(not color, height - 1, -beta, -alpha, False)
          self.__board.restore_state(state_cpy)
          if value >= beta:
            return value
          if value > alpha:
            alpha = value
        maxValue = max(maxValue, value)
      return maxValue

    else:
      maxValue = -othello.Config.INF
      for placeable_cell in placeable_cells:
        self.__board.put[placeable_cell](color)
        value = -self.__alphaBeta(not color, height - 1, -beta, -alpha, False)
        self.__board.restore_state(state_cpy)
        if value >= beta:
          return value  # カット
        if value > maxValue:
          alpha = max(alpha, value)
          maxValue = value
      return maxValue

  # <概要> http://uguisu.skr.jp/othello/alpha-beta.html
  # <引数> board:Board型, color:int(0~1), height:(1~MAX_SEARCH_HEIGHT), alpha:int, beta:int
  # <返値> int
  def __alphaBeta(self, color, height, alpha, beta, passed):
    if not height: # 設定した深さまでたどり着いたら再帰終了
      return self.__evaluate_leaf(color)
    placeable_cells = self.__board.placeable_cells(color)
    if not len(placeable_cells):
      if passed:
        return self.__evaluate_leaf(color)
      return -self.__alphaBeta(not color, height, -beta, -alpha, True)
    state_cpy = self.__board.get_state()
    maxValue = -othello.Config.INF
    a = alpha
    for placeable_cell in placeable_cells:
      self.__board.put[placeable_cell](color)
      value = -self.__alphaBeta(not color, height - 1, -beta, -a, False)
      self.__board.restore_state(state_cpy)
      if value >= beta:
        return value
      if value > maxValue:
        a = max(a, value)
        maxValue = value
    return maxValue

  # <概要> 相手の置ける場所が少なくなる順にソート
  def __move_ordering(self, list_pos ,color):
    state_cpy = self.__board.get_state()  # 盤面コピー
    values = [0] * len(list_pos)
    for i, pos in enumerate(list_pos):
      self.__board.put[pos](color)
      values[i] = self.__board.placeable_cells_num(not color)
      self.__board.restore_state(state_cpy)
    return [pos for value, pos in sorted(zip(values, list_pos))]

  # <概要> 石差で評価
  def __evaluate_leaf(self, color):
    return self.__board.get_difference(color)
