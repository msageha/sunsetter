# User 100万人
class User:
  def __init__(self): pass
  def introduction(self):
    moji = 'ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわをん'
    chars = ''.join([random.choice(moji) for i in range(random.randint(0, 500))])
    return chars
  def screen_name(self):
    moji = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    chars = ''.join([random.choice(moji) for i in range(random.randint(8, 20))])
    return chars
  def user_name(self):
    moji = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    chars = ''.join([random.choice(moji) for i in range(random.randint(8, 20))])
    return chars
  def password_hash(self):
    moji = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    chars = ''.join([random.choice(moji) for i in range(256)])
    return chars
  #50万人が画像をつけていると仮定
  def image_id(self): return random.randint(0, 500000)

#Post
class Post:
  def __init__(self): pass
  def message(self):
    moji = 'ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわをん'
    chars = ''.join([random.choice(moji) for i in range(random.randint(0, 200))])
    return chars
  def user_id(self):
    if random.randint(0, 3):
      return random.randint(300001, 1000000)
    else:
      return random.randint(0, 300000)

class PostImage:
  def __init__(self):
    self.images = os.listdir('./img')
    self.img_array = np.zeros(4500000)
  def post_id(self):
    num = int(random.randint(0, 4500000)/5)*5
    self.img_array[num] += 1
    while self.img_array[num] > 4:
      num = int(random.randint(0, 4500000)/5)*5
      self.img_array[num] += 1
    return num
  def image(self):
    image = random.choice(self.images)
    with open(f'img/{image}', 'rb') as f:
      photo = f.read()
    return photo
  def imgpath(self):
    image = random.choice(self.images)
    path = f'/home/demouser/img/{image}'
    return path

#PrivateMessage
class PrivateMessage:
  def __init__(self): pass
  def message(self):
    moji = 'ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわをん'
    chars = ''.join([random.choice(moji) for i in range(random.randint(0, 200))])
    return chars
  def user_id(self):
    if random.randint(0, 3):
      return random.randint(300001, 1000000)
    else:
      return random.randint(0, 300000)
  def group_id(self): return random.randint(0, 50000)

class Subscribe:
  def __init__(self): pass
  def group_id(self):
    return random.randint(0, 50000)
  def user_id(self):
    if random.randint(0, 3):
      return random.randint(300001, 1000000)
    else:
      return random.randint(0, 300000)

class Group:
  def __init__(self): pass
  def name(self):
    moji = 'ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわをん'
    chars = ''.join([random.choice(moji) for i in range(random.randint(8, 20))])
    return chars

class PrivateImage:
  def __init__(self):
    self.images = os.listdir('./img')
    self.img_array = np.zeros(150000)
  def image(self):
    image = random.choice(self.images)
    with open(f'img/{image}', 'rb') as f:
      photo = f.read()
    return photo
  def private_message_id(self):
    num = int(random.randint(0, 150000)/5)*5
    self.img_array[num] += 1
    while self.img_array[num] > 4:
      num = int(random.randint(0, 150000)/5)*5
      self.img_array[num] += 1
    return num
  def imgpath(self):
    image = random.choice(self.images)
    path = f'/home/demouser/img/{image}'
    return path

class UserImage:
  def __init__(self): self.images = os.listdir('./img')
  def image(self):
    image = random.choice(self.images)
    with open(f'img/{image}', 'rb') as f:
      photo = f.read()
    return binascii.unhexlify(bytes(photo))
  def imgpath(self):
    image = random.choice(self.images)
    path = f'/home/demouser/img/{image}'
    return path

class Follow:
  def __init__(self):
    self.num = random.randint(0, 300000)
    if random.randint(0, 3):
      self.num = random.randint(300001, 1000000)
  def src_user_id(self):
    return self.num
  def dst_user_id(self):
    num = random.randint(0, 300000)
    if random.randint(0, 3):
        num = random.randint(300001, 1000000)
    while num == self.num:
      num = random.randint(0, 300000)
      if random.randint(0, 3):
        num = random.randint(300001, 1000000)
    return num

import random
import os
import mysql.connector
import numpy as np
conn = mysql.connector.connect(user='demouser', password='demopass', host='localhost', database='sunsetter')
# conn = mysql.connector.connect(user='demouser', password='demopass', host='localhost', database='sunsetter_user_image')
# conn = mysql.connector.connect(user='demouser', password='demopass', host='localhost', database='sunsetter_post_image')
# conn = mysql.connector.connect(user='demouser', password='demopass', host='localhost', database='sunsetter_private_image')
cur = conn.cursor()

#Create User
users = User()
for i in range(1000):
  sql = 'INSERT INTO users (introduction, image_id, screen_name, user_name, password_hash, created_at, updated_at) VALUES'
  for j in range(1000):
    sql += f'''('{users.introduction()}', {users.image_id()}, '{users.screen_name()}', '{users.user_name()}', '{users.password_hash()}', DEFAULT, DEFAULT),'''
  sql = sql[:-1]+';'
  cur.execute(sql)
  conn.commit()
  print(i)
cur.close()
conn.close()

#Create Post
posts = Post
for i in range(4500):
  sql = 'INSERT INTO posts (message, user_id, created_at) VALUES'
  for j in range(1000):
    sql += f'''('{posts.message()}', {posts.user_id()}, DEFAULT),'''
  sql = sql[:-1]+';'
  cur.execute(sql)
  conn.commit()
  print(i)
cur.close()
conn.close()

#Private Message
pm = PrivateMessage
for i in range(150):
  sql = 'INSERT INTO private_messages (message, user_id, group_id, created_at, updated_at) VALUES'
  for j in range(1000):
    sql += f'''('{pm.message()}', {pm.user_id()}, {pm.group_id()}, DEFAULT, DEFAULT),'''
  sql = sql[:-1]+';'
  cur.execute(sql)
  conn.commit()
  print(i)
cur.close()
conn.close()

#Follow
for i in range(1000):
  sql = 'INSERT INTO follows (src_user_id, dst_user_id) VALUES'
  for j in range(1000):
    for k in range(200):
      follow = Follow()
      sql += f'''({follow.src_user_id()}, {follow.dst_user_id()}),'''
  sql = sql[:-1]+';'
  cur.execute(sql)
  conn.commit()
  print(i)
cur.close()
conn.close()

#Subscribe
subscribes = Subscribe()
for i in range(50):
  sql = 'INSERT INTO subscribes (user_id, group_id) VALUES'
  for j in range(1000):
    sql += f'({subscribes.user_id()}, {subscribes.group_id()}),'
  sql = sql[:-1]+';'
  cur.execute(sql)
  conn.commit()
  print(i)
cur.close()
conn.close()

#Group
group = Group()
for i in range(50):
  sql = 'INSERT INTO groups (name) VALUES'
  for j in range(1000):
    sql += f'''('{group.name()}'),'''
  sql = sql[:-1]+';'
  cur.execute(sql)
  conn.commit()
  print(i)
cur.close()
conn.close()

#UserImage 別のサーバー
ui = UserImage()
for i in range(240):
  sql = 'INSERT INTO user_images (image, updated_at) VALUES'
  for j in range(1000):
    sql += f'''(LOAD_FILE('{ui.imgpath()}'), DEFAULT),'''
  sql = sql[:-1]+';'
  cur.execute(sql)
  conn.commit()
  print(i)
cur.close()
conn.close()

#PostImage 別のサーバー
pi = PostImage()
for i in range(900):
  sql = 'INSERT INTO post_images (post_id, image) VALUES'
  for j in range(1000):
    sql += f'''({pi.post_id()}, LOAD_FILE('{pi.imgpath()}')),'''
  sql = sql[:-1]+';'
  cur.execute(sql)
  conn.commit()
  print(i)
cur.close()
conn.close()

#PrivateMessageImage 別のサーバー
pi = PrivateImage()
for i in range(15):
  sql = 'INSERT INTO private_images (private_message_id, image) VALUES'
  for j in range(1000):
    sql += f'''({pi.private_message_id()}, LOAD_FILE('{pi.imgpath()}')),'''
  sql = sql[:-1]+';'
  cur.execute(sql)
  conn.commit()
  print(i)

cur.close()
conn.close()