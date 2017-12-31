# -*- coding:utf-8 -*-

# OpeningBook : 序盤の最善手(定石)を木構造で記録したもの.
#               相手が定石通りにゲームを進めている間はOpeningBookの記述通りにコマを置く.
#               定石から外れた時点でOpeningBookを放棄してゲーム木探索を開始する.
# OpeningBookについて詳しくは https://skatgame.net/mburo/ps/book.pdf
# Bookのソースファイルは http://www.amy.hi-ho.ne.jp/okuhara/edax.htm のリンク先から.
# リンク先にある Wzebraの Extra-large book テキストデータ は解析しやすそう
# (http://tosapy.merrymall.net/othello/wzebra/extra-large-txt-20080301.zip)

import othello

# 序盤の最善手(定石)を記録したもの.相手が定石通りにゲームを進めている間はOpeningBookの記述通りにコマを置く.
# 定石から外れた時点でOpeningBookを放棄してゲーム木探索を開始する.詳しくは https://skatgame.net/mburo/ps/book.pdf
# Bookのソースファイルは http://www.amy.hi-ho.ne.jp/okuhara/edax.htm のリンク先から.
# リンク先にある Wzebraの Extra-large book テキストデータ は解析しやすそう (<追記> 現在公開終了した模様)
# <メンバ> __current_node:
#          __valid:ゲームが定石通りに進行中か否か
#          __symm:
class OpeningBook(object):

  # 木のNode
  class Node(object):
    __slots__ = ['child', 'score']
    def __init__(self, score=0):
      self.child = {} # key=位置,val=Nodeの辞書型?
      self.score = score

  def __init__(self):
    # 現盤面を表すNode
    self.__current_node = self.__root = self.__init_book()  # 木のrootで初期化

    # ゲームが定石通りに進行中か否か
    self.__valid = True

    # 鏡像対称性
    self.__symm = False

    # 180°回転対称性
    self.__rote = False   # for 回転対称性

  # Bookを構築する
  def __init_book(self):
    file_name = "../book/book_test.txt"
    #file_name = "../book/extra-large-20080301.txt"
    total_line = sum(1 for line in open(file_name))
    input_file = open(file_name)
    root = OpeningBook.Node()
    for i, row in enumerate(input_file):
      nodes = self.__row2nodes(row)
      self.__add_nodes(root, nodes)
      print round(float(i)/total_line, 3) * 100,"% completed"
    print "OpeningBook Completed"
    return root

  def __pos2key(self, x, y):
    return x + y * 8

  def __key2pos(self, key):
    return (key % 8, key / 8)

  def __correct_pos(self, x, y):
    if self.__symm:
      x,y = y,x
    if self.__rote:
      x,y = 8-1-x, 8-1-y
    return x,y

  def __pos2correctedKey(self, x, y):
    x,y = self.__correct_pos(x,y)
    return self.__pos2key(x,y)

  def __key2correctedPos(self, key):
    x,y = self.__key2pos(key)
    return self.__correct_pos(x,y)

  # "C4"等 --> key
  def __charpos2key(self, charpos):
    alphabets = ['A','B','C','D','E','F','G','H']
    x = alphabets.index(charpos[0])
    y = int(charpos[1])-1
    return self.__pos2key(x, y)

  # 文字列row --> (key, score)のリスト
  def __row2nodes(self, row):
    sep = row.split(" ; ")
    nodes = [(self.__charpos2key(sep[0][i: i+2]), 0) for i in range(0, len(sep[0]), 2)]
    nodes[-1] = (nodes[-1][0], float(sep[1]))
    return nodes

  # 引数parent_nodeに子Nodeを追加
  # <返値> 新規追加した子Node
  def __add_child(self, parent_node, key, score=0):
    parent_node.child[key] = OpeningBook.Node(score)
    return parent_node.child[key]

  def __check(self):
    if not len(self.__current_node.child):
        self.__valid = False  # 葉Nodeに到達 -> Bookの参照終了

  def __add_nodes(self, parent_node, nodes):
    current_node = parent_node
    for node in nodes:
      keys = current_node.child.keys()
      if not node[0] in keys:
        current_node = self.__add_child(current_node, node[0], node[1])
      else:
        current_node = current_node.child[node[0]]

  # 相手(You)が定石通りにコマを置いているか判定しながらbookを読み進める
  # この関数は,Youクラスのtake_turn()内でboard.put()が呼ばれた後に実行される
  def proceed(self, x, y):
    if self.__current_node is self.__root:   # 相手が黒の一手目を打ったらbookとの対称性を記録する
      key = self.__pos2key(x, y)
      if key == 19: # = D3 = (3,2)
        self.__symm = True
      elif key == 37:  # = F5 = (5,4)
        self.__rote = True
      elif key == 44: # = E6 = (4,5)
        self.__symm = True
        self.__rote = True

    key = self.__pos2correctedKey(x,y)
    if key in self.__current_node.child:
      self.__current_node = self.__current_node.child[key]  # 相手(You)が定石通り(bookに載ってるパターン)に打ってきたら先に進む
      self.__check()
    else:
      self.__valid = False  # 相手(You)が定石から外れたらOpenBookを捨てて次のphaseへ

  # bookを読んでコマを置くべき位置を得る
  def read(self):
    key = max(self.__current_node.child.items(), key=lambda x:x[1].score)[0] # score最大ノードのキーを返す
    self.__current_node = self.__current_node.child[key]
    self.__check()
    return self.__key2correctedPos(key)

  # <概要> 現状定石通りかどうかの真偽値を返す
  def is_valid(self):
    return self.__valid
