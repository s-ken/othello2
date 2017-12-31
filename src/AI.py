# -*- coding:utf-8 -*-

import othello
import brain
import time

class AI():
  def __init__( self, board, color, opening_book, weight=None ):
    self.__board = board  # boardへの参照
    self.__color = color  # 自分の色
    self.__brain_mid = brain.BrainMid(board, color, weight)  # 中盤戦用の探索アルゴリズム
    self.__brain_fin = brain.BrainFin(board, color)          # 終盤戦用の探索アルゴリズム
    if opening_book is None:
      self.__brain = self.__brain_mid
    else:
      self.__brain = brain.BrainBook(board, color, opening_book)

  def set_weight( self, weight ):
    self.__brain_mid.set_weight(weight)
    self.__brain = self.__brain_mid

  def can_put( self ):
    return len(self.__board.placeable_cells(self.__color)) > 0

  def __str__( self ):
    return "AI"

  def take_turn( self, num_discs ):
    start = time.time()

    if not self.__brain.is_valid(num_discs):
      self.__change_brain()
    pos = self.__brain.evaluate(num_discs)  # 着手位置の選択
    self.__board.put[pos](self.__color)     # 位置posに駒を置く
    self.__board.update_empty_cells(pos)    # 空マスリストの更新
    elapsed_time = time.time() - start

    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    return pos

  def __change_brain( self ):
    if self.__brain is self.__brain_mid:
      self.__brain = self.__brain_fin
    else:
      self.__brain = self.__brain_mid
