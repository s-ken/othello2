# -*- coding:utf-8 -*-

import sys
import pygame
from pygame.locals import *

import board
import book
import AI


class Config:
  MID_HEIGHT  = 7 # 中盤ゲーム木の高さ
  FIN_HEIGHT  = 14 # 終盤ゲーム木の高さの上限
  FIN_PHASE   = 60-FIN_HEIGHT # 終盤読み切りを開始するタイミング

  CELL_WIDTH    = 80  # GUIでのマスのサイズ

  BLACK = 0
  WHITE = 1
  EMPTY = 2
  WINDOW_WIDTH  = CELL_WIDTH * 8
  WPOS          = CELL_WIDTH * 7
  INF           = sys.maxint
  POW3          = [3 ** i for i in range(8)]

class You():

  def __init__( self, board, color, opening_book ):
    self.__board = board                # boardへの参照
    self.__color = color                # 自分の色
    self.__opening_book = opening_book  # 定石集への参照

  def can_put( self ):
    return len( self.__board.placeable_cells(self.__color) ) > 0

  def __str__( self ):
    return "You"

  def take_turn( self, _ ):
    while 1:
      for event in pygame.event.get():
        if ( event.type == KEYDOWN and event.key == K_ESCAPE ):
          sys.exit()  # ESCAPEキーが押されたら終了
        if ( event.type == KEYDOWN and event.key == K_BACKSPACE ):
          raise UndoRequest() # BACKSPACEキーが押されたらUndo
        if ( event.type == MOUSEBUTTONDOWN ):
          xpos = int( pygame.mouse.get_pos()[0]/Config.CELL_WIDTH )
          ypos = int( pygame.mouse.get_pos()[1]/Config.CELL_WIDTH )
          if self.__board.placeable[xpos + ypos * 8]( self.__color ):
            self.__board.store_state()   # boardの要素のstateを書き換える前に,各stateを保存する
            self.__board.put[xpos + ypos * 8]( self.__color )  # 位置(xpos,ypos)に駒を置く
            self.__board.update_empty_cells( xpos + ypos * 8 )
            if self.__opening_book.is_valid():
              self.__opening_book.proceed( xpos, ypos )  # 定石通りかどうかチェック
            return xpos + ypos * 8
          else:
            print "ERROR: You cannot put here."   # クリック地点が置けない場所ならループ継続

class UndoRequest(Exception):
  def __init__(self): 0


class Game:
  def __init__( self ):
    self.__board  = board.Board( True )
    self.__player = [None] * 2
    self.__opening_book = book.OpeningBook()

  def init( self ):
    self.__board.init()
    self.__turn = Config.BLACK
    self.__num_discs = 0
    self.__passed = False
    self.__pos = -1
    while 1:
      st = raw_input("Choose your color. (b/w) : ")
      if st == 'b':
        self.__set_players(Config.BLACK)
      elif st == 'w':
        self.__set_players(Config.WHITE)
      else:
        continue
      break

  def __set_players( self, your_color ):
    self.__player[your_color]     = You( self.__board, your_color, self.__opening_book )
    self.__player[not your_color] = AI.AI( self.__board, not your_color, self.__opening_book, None )

  def run( self ):
    while 1:
      self.__board.print_board( self.__pos, self.__turn%2 )
      if self.__num_discs == 60:
        break
      if self.__player[self.__turn%2].can_put():  # 置ける場所があればTrue
        try:
          print "Turn:", self.__num_discs
          self.__pos    = self.__player[self.__turn%2].take_turn(self.__num_discs)
          self.__passed = False
        except UndoRequest:
          self.__undo()
          self.__num_discs -= 2
          continue
        self.__num_discs += 1
      else:
        print self.__player[self.__turn%2], " passed."
        if self.__passed:  # 二人ともパス->終了
          return
        self.__passed = True
      self.__turn += 1

  def output(self):
    self.__board.print_result()

  def __undo(self):
    self.__board.load_state()

def main():
  game = Game()
  while 1:
    game.init()
    game.run()
    game.output()

    st = raw_input("Continue? (y/n) : ")
    if st == 'n':
      break

if __name__ == "__main__":
  main()
