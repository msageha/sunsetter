## 設計
命名規則：テーブル名はsnake case＆複数形

### User.Image
* 復旧を早くするため外部へ
* password_hahは使用可否に関わるためSLA直結
* バックアップを常時取りたい
* あくまで見た目，非同期で取ってくることもできる
* 長めのcacheが聞く

### PostImage/PrivateImageの分離
* 基本的に別エンティティ
* Private側は，セキュリティ上，暗号化する可能性あり．

### データベースを直近１週間のものと，それ以前ので分けるか
PostのSharding→APでやる（できるものとして）

## トラフィック分析
### 投稿数
* Average 15,000,000 Post/day
* Average 173 Post/sec
* Average 3,000,000 Image/day

DAU数 300000人
ユーザの滞在時間 4[h] = 14400[sec]
ユーザの一日当たりのアクセス数 480[回]
DAU全体の一日あたりの総アクセス数 300000 * 480 = 144000000[回]

# memcache

| key | value |
|-----|-------|
| users.id | screen_name |

# SQL Queries

## ログイン画面

* ログイン
```sql
SELECT screen_name, password_hash FROM users WHERE password_hash = 'ipmL0m0g4UEqw9gdwDW8BcTvqVB69rZ3ik6Y0KVR1TpMMwqyi33ITKhD8eQMTZgQSwjCmwqrycEe6PXIjOjfTRVctlxgwZvUiiPi6eOWg5XUnTaV9KIhn9IDw5vgQvPgF9P882ee5Mka59k8EJyIDZZsW7ItePOCspI99qfwAohjF6CYAMSJ6zKl3BTBCTJoM3OwIdWsqErKZqCflT052qGDjrUsVjh1AXn5fNdVuJ2XfNjzy6P5XAhoqz0ZIYnk';
```

![](https://i.imgur.com/gSLKGJ5.png)

```
mysql> explain SELECT screen_name, password_hash FROM users WHERE password_hash = 'ipmL0m0g4UEqw9gdwDW8BcTvqVB69rZ3ik6Y0KVR1TpMMwqyi33ITKhD8eQMTZgQSwjCmwqrycEe6PXIjOjfTRVctlxgwZvUiiPi6eOWg5XUnTaV9KIhn9IDw5vgQvPgF9P882ee5Mka59k8EJyIDZZsW7ItePOCspI99qfwAohjF6CYAMSJ6zKl3BTBCTJoM3OwIdWsqErKZqCflT052qGDjrUsVjh1AXn5fNdVuJ2XfNjzy6P5XAhoqz0ZIYnk';
+----+-------------+-------+------+-------------------+-------------------+---------+-------+------+-------------+
| id | select_type | table | type | possible_keys     | key               | key_len | ref   | rows | Extra       |
+----+-------------+-------+------+-------------------+-------------------+---------+-------+------+-------------+
|  1 | SIMPLE      | users | ref  | idx_password_hash | idx_password_hash | 767     | const |    1 | Using where |
+----+-------------+-------+------+-------------------+-------------------+---------+-------+------+-------------+
1 row in set (0.00 sec)
```

## プロフィール画面

* フォロー数取得
```sql
SELECT COUNT(*) from users JOIN (
    SELECT dst_user_id FROM follows WHERE src_user_id = 10
) as c ON c.dst_user_id = users.id;
```
例: src_user_id = 10と取る場合
![](https://i.imgur.com/NpNKaB1.png)

```
mysql> explain SELECT COUNT(*) from users JOIN (
    ->     SELECT dst_user_id FROM follows WHERE src_user_id = 10
    -> ) as c ON c.dst_user_id = users.id;
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------------+
| id | select_type | table      | type   | possible_keys   | key             | key_len | ref           | rows | Extra       |
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------------+
|  1 | PRIMARY     | <derived2> | ALL    | NULL            | NULL            | NULL    | NULL          |  142 | NULL        |
|  1 | PRIMARY     | users      | eq_ref | PRIMARY         | PRIMARY         | 4       | c.dst_user_id |    1 | Using index |
|  2 | DERIVED     | follows    | ref    | idx_src_user_id | idx_src_user_id | 4       | const         |  142 | NULL        |
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------------+
3 rows in set (0.00 sec)
```

* フォロー取得
```sql
SELECT screen_name, user_name FROM users JOIN (
    SELECT dst_user_id FROM follows WHERE src_user_id = 10
) AS c ON c.dst_user_id = users.id LIMIT 25;
```

例: src_user_id = 10と取る場合
![](https://i.imgur.com/rZAoGnG.png)

```
mysql> explain SELECT screen_name, user_name FROM users JOIN (
    ->     SELECT dst_user_id FROM follows WHERE src_user_id = 10
    -> ) AS c ON c.dst_user_id = users.id LIMIT 25;
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------+
| id | select_type | table      | type   | possible_keys   | key             | key_len | ref           | rows | Extra |
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------+
|  1 | PRIMARY     | <derived2> | ALL    | NULL            | NULL            | NULL    | NULL          |  142 | NULL  |
|  1 | PRIMARY     | users      | eq_ref | PRIMARY         | PRIMARY         | 4       | c.dst_user_id |    1 | NULL  |
|  2 | DERIVED     | follows    | ref    | idx_src_user_id | idx_src_user_id | 4       | const         |  142 | NULL  |
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------+
3 rows in set (0.00 sec)
```


* フォロワー数取得
```sql
SELECT COUNT(*) from users JOIN (
    SELECT src_user_id FROM follows WHERE dst_user_id = 10
) as c ON c.src_user_id = users.id;
```
例: dst_user_id = 10と取る場合
![](https://i.imgur.com/yPNOMZj.png)

```
mysql> explain SELECT COUNT(*) from users JOIN (
    ->     SELECT src_user_id FROM follows WHERE dst_user_id = 10
    -> ) as c ON c.src_user_id = users.id;
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------------+
| id | select_type | table      | type   | possible_keys   | key             | key_len | ref           | rows | Extra       |
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------------+
|  1 | PRIMARY     | <derived2> | ALL    | NULL            | NULL            | NULL    | NULL          |  172 | NULL        |
|  1 | PRIMARY     | users      | eq_ref | PRIMARY         | PRIMARY         | 4       | c.src_user_id |    1 | Using index |
|  2 | DERIVED     | follows    | ref    | idx_dst_user_id | idx_dst_user_id | 4       | const         |  172 | NULL        |
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------------+
3 rows in set (0.00 sec)
```


* フォロワー取得
```sql
SELECT screen_name, user_name FROM users JOIN (
    SELECT src_user_id FROM follows WHERE dst_user_id = 10
) AS c ON c.src_user_id = users.id LIMIT 25;
```
例: dst_user_id = 10と取る場合
![](https://i.imgur.com/eMFjxcZ.png)

```
mysql> explain SELECT screen_name, user_name FROM users JOIN (
    ->     SELECT src_user_id FROM follows WHERE dst_user_id = 10
    -> ) AS c ON c.src_user_id = users.id LIMIT 25;
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------+
| id | select_type | table      | type   | possible_keys   | key             | key_len | ref           | rows | Extra |
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------+
|  1 | PRIMARY     | <derived2> | ALL    | NULL            | NULL            | NULL    | NULL          |  172 | NULL  |
|  1 | PRIMARY     | users      | eq_ref | PRIMARY         | PRIMARY         | 4       | c.src_user_id |    1 | NULL  |
|  2 | DERIVED     | follows    | ref    | idx_dst_user_id | idx_dst_user_id | 4       | const         |  172 | NULL  |
+----+-------------+------------+--------+-----------------+-----------------+---------+---------------+------+-------+
3 rows in set (0.00 sec)
```


* プロフィール取得
```sql
SELECT introduction, image_id, screen_name, user_name
FROM users WHERE users.id = 10;
```
例: users.id = 10と取る場合
![](https://i.imgur.com/svxJGX6.png)

```
mysql> explain SELECT introduction, image_id, screen_name, user_name
    -> FROM users WHERE users.id = 10;
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref   | rows | Extra |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------+
|  1 | SIMPLE      | users | const | PRIMARY       | PRIMARY | 4       | const |    1 | NULL  |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------+
1 row in set (0.00 sec)
```


* アイコン取得
```sql
SELECT image FROM user_images WHERE id = 10;
```
image.id = 10のものを取得(バイナリが流れてほしくないため，updated_at)
![](https://i.imgur.com/xcFfEUc.png)



## メッセージ一覧
* 投稿
```sql
INSERT INTO posts (message, user_id)
VALUES ('Voyageのインターン最高', 10);
```
![](https://i.imgur.com/6XHW7xJ.png)

```
mysql> explain INSERT INTO posts (message, user_id)
    -> VALUES ('Voyageのインターン最高', 10);
+----+-------------+-------+------+---------------+------+---------+------+------+----------------+
| id | select_type | table | type | possible_keys | key  | key_len | ref  | rows | Extra          |
+----+-------------+-------+------+---------------+------+---------+------+------+----------------+
|  1 | SIMPLE      | NULL  | NULL | NULL          | NULL | NULL    | NULL | NULL | No tables used |
+----+-------------+-------+------+---------------+------+---------+------+------+----------------+
1 row in set (0.00 sec)

```

* 自メッセージ取得
```sql
SELECT message, created_at
FROM posts
WHERE user_id = 10
ORDER BY created_at desc
LIMIT 25;
```
![](https://i.imgur.com/zhPaahR.jpg)

```
mysql> explain SELECT message, created_at  FROM posts WHERE user_id = 10 ORDER BY created_at desc LIMIT 25;
+----+-------------+-------+------+---------------+-------------+---------+-------+------+-----------------------------+
| id | select_type | table | type | possible_keys | key         | key_len | ref   | rows | Extra                       |
+----+-------------+-------+------+---------------+-------------+---------+-------+------+-----------------------------+
|  1 | SIMPLE      | posts | ref  | idx_user_id   | idx_user_id | 4       | const |    9 | Using where; Using filesort |
+----+-------------+-------+------+---------------+-------------+---------+-------+------+-----------------------------+
1 row in set (0.00 sec)
```


* 削除
```sql
DELETE FROM posts WHERE id = 50;
```

```
mysql> explain DELETE FROM posts WHERE id = 60;
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref   | rows | Extra       |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------------+
|  1 | SIMPLE      | posts | range | PRIMARY       | PRIMARY | 8       | const |    1 | Using where |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------------+
1 row in set (0.00 sec)
```

## タイムライン
* 投稿
```sql
INSERT INTO posts (message, user_id)
VALUES ('Voyageのインターン最高', 10);
```
![](https://i.imgur.com/6XHW7xJ.png)
```
mysql> explain INSERT INTO posts (message, user_id) VALUES ('Voyageのインターン最高', 10);
+----+-------------+-------+------+---------------+------+---------+------+------+----------------+
| id | select_type | table | type | possible_keys | key  | key_len | ref  | rows | Extra          |
+----+-------------+-------+------+---------------+------+---------+------+------+----------------+
|  1 | SIMPLE      | NULL  | NULL | NULL          | NULL | NULL    | NULL | NULL | No tables used |
+----+-------------+-------+------+---------------+------+---------+------+------+----------------+
1 row in set (0.00 sec)
```

* 直近100メッセージの取得
```sql
SELECT * from posts
JOIN (
    SELECT id FROM users JOIN (
        SELECT src_user_id
        FROM follows
        WHERE dst_user_id = 234453
        UNION SELECT 234453
    ) AS c ON c.src_user_id = users.id
) AS d ON d.id = posts.user_id
ORDER BY created_at desc
LIMIT 100;
```

```
mysql> explain SELECT * from posts
    -> JOIN (
    ->     SELECT id FROM users JOIN (
    ->         SELECT src_user_id
    ->         FROM follows
    ->         WHERE dst_user_id = 234453
    ->         UNION SELECT 234453
    ->     ) AS c ON c.src_user_id = users.id
    -> ) AS d ON d.id = posts.user_id
    -> ORDER BY created_at desc
    -> LIMIT 100;
+----+--------------+------------+--------+-----------------+-----------------+---------+---------------+------+---------------------------------+
| id | select_type  | table      | type   | possible_keys   | key             | key_len | ref           | rows | Extra                           |
+----+--------------+------------+--------+-----------------+-----------------+---------+---------------+------+---------------------------------+
|  1 | PRIMARY      | <derived2> | ALL    | NULL            | NULL            | NULL    | NULL          |  182 | Using temporary; Using filesort |
|  1 | PRIMARY      | posts      | ref    | idx_user_id     | idx_user_id     | 4       | d.id          |    2 | NULL                            |
|  2 | DERIVED      | <derived3> | ALL    | NULL            | NULL            | NULL    | NULL          |  182 | NULL                            |
|  2 | DERIVED      | users      | eq_ref | PRIMARY         | PRIMARY         | 4       | c.src_user_id |    1 | Using where; Using index        |
|  3 | DERIVED      | follows    | ref    | idx_dst_user_id | idx_dst_user_id | 4       | const         |  181 | NULL                            |
|  4 | UNION        | NULL       | NULL   | NULL            | NULL            | NULL    | NULL          | NULL | No tables used                  |
| NULL | UNION RESULT | <union3,4> | ALL    | NULL            | NULL            | NULL    | NULL          | NULL | Using temporary                 |
+----+--------------+------------+--------+-----------------+-----------------+---------+---------------+------+---------------------------------+
7 rows in set (0.00 sec)
```

* 新規メッセージ取得
```sql
SELECT * from posts
JOIN (
    SELECT id FROM users JOIN (
        SELECT src_user_id
        FROM follows
        WHERE dst_user_id = 234453
        UNION SELECT 234453
    ) AS c ON c.src_user_id = users.id
) AS d ON d.id = posts.user_id
WHERE created_at > '2017-10-28'
ORDER BY created_at desc
LIMIT 100;
```

```
mysql> explain SELECT * from posts
    -> JOIN (
    ->     SELECT id FROM users JOIN (
    ->         SELECT src_user_id
    ->         FROM follows
    ->         WHERE dst_user_id = 234453
    ->         UNION SELECT 234453
    ->     ) AS c ON c.src_user_id = users.id
    -> ) AS d ON d.id = posts.user_id
    -> WHERE created_at > '2017-10-28'
    -> ORDER BY created_at desc
    -> LIMIT 100;
+----+--------------+------------+--------+----------------------------+-----------------+---------+---------------+------+---------------------------------+
| id | select_type  | table      | type   | possible_keys              | key             | key_len | ref           | rows | Extra                           |
+----+--------------+------------+--------+----------------------------+-----------------+---------+---------------+------+---------------------------------+
|  1 | PRIMARY      | <derived2> | ALL    | NULL                       | NULL            | NULL    | NULL          |  182 | Using temporary; Using filesort |
|  1 | PRIMARY      | posts      | ref    | idx_user_id,idx_created_at | idx_user_id     | 4       | d.id          |    2 | Using where                     |
|  2 | DERIVED      | <derived3> | ALL    | NULL                       | NULL            | NULL    | NULL          |  182 | NULL                            |
|  2 | DERIVED      | users      | eq_ref | PRIMARY                    | PRIMARY         | 4       | c.src_user_id |    1 | Using where; Using index        |
|  3 | DERIVED      | follows    | ref    | idx_dst_user_id            | idx_dst_user_id | 4       | const         |  181 | NULL                            |
|  4 | UNION        | NULL       | NULL   | NULL                       | NULL            | NULL    | NULL          | NULL | No tables used                  |
| NULL | UNION RESULT | <union3,4> | ALL    | NULL                       | NULL            | NULL    | NULL          | NULL | Using temporary                 |
+----+--------------+------------+--------+----------------------------+-----------------+---------+---------------+------+---------------------------------+
7 rows in set (0.00 sec)
```

* 過去メッセージ取得
```sql
SELECT * from posts
JOIN (
    SELECT id FROM users JOIN (
        SELECT src_user_id
        FROM follows
        WHERE dst_user_id = 234453
        UNION SELECT 234453
    ) AS c ON c.src_user_id = users.id
) AS d ON d.id = posts.user_id
WHERE created_at < '2017-10-30'
ORDER BY created_at desc
LIMIT 100;
```

```
mysql> explain SELECT * from posts
    -> JOIN (
    ->     SELECT id FROM users JOIN (
    ->         SELECT src_user_id
    ->         FROM follows
    ->         WHERE dst_user_id = 234453
    ->         UNION SELECT 234453
    ->     ) AS c ON c.src_user_id = users.id
    -> ) AS d ON d.id = posts.user_id
    -> WHERE created_at < '2017-10-30'
    -> ORDER BY created_at desc
    -> LIMIT 100;
+----+--------------+------------+--------+----------------------------+-----------------+---------+---------------+------+---------------------------------+
| id | select_type  | table      | type   | possible_keys              | key             | key_len | ref           | rows | Extra                           |
+----+--------------+------------+--------+----------------------------+-----------------+---------+---------------+------+---------------------------------+
|  1 | PRIMARY      | <derived2> | ALL    | NULL                       | NULL            | NULL    | NULL          |  182 | Using temporary; Using filesort |
|  1 | PRIMARY      | posts      | ref    | idx_user_id,idx_created_at | idx_user_id     | 4       | d.id          |    2 | Using where                     |
|  2 | DERIVED      | <derived3> | ALL    | NULL                       | NULL            | NULL    | NULL          |  182 | NULL                            |
|  2 | DERIVED      | users      | eq_ref | PRIMARY                    | PRIMARY         | 4       | c.src_user_id |    1 | Using where; Using index        |
|  3 | DERIVED      | follows    | ref    | idx_dst_user_id            | idx_dst_user_id | 4       | const         |  181 | NULL                            |
|  4 | UNION        | NULL       | NULL   | NULL                       | NULL            | NULL    | NULL          | NULL | No tables used                  |
| NULL | UNION RESULT | <union3,4> | ALL    | NULL                       | NULL            | NULL    | NULL          | NULL | Using temporary                 |
+----+--------------+------------+--------+----------------------------+-----------------+---------+---------------+------+---------------------------------+
7 rows in set (0.00 sec)
```

## (プライベート|グループ)メッセージ
* 自分の所属するグループ取得
```sql
SELECT id, name from groups JOIN (
    SELECT group_id
    FROM subscribes
    WHERE user_id = 753070
) as c ON c.group_id = groups.id;
```

```
mysql> explain SELECT id, name from groups JOIN (     SELECT group_id      FROM subscribes     WHERE user_id = 753070 ) as c ON c.group_id = groups.id;
+----+-------------+------------+--------+---------------+-------------+---------+------------+------+-------+
| id | select_type | table      | type   | possible_keys | key         | key_len | ref        | rows | Extra |
+----+-------------+------------+--------+---------------+-------------+---------+------------+------+-------+
|  1 | PRIMARY     | <derived2> | ALL    | NULL          | NULL        | NULL    | NULL       |    2 | NULL  |
|  1 | PRIMARY     | groups     | eq_ref | PRIMARY       | PRIMARY     | 8       | c.group_id |    1 | NULL  |
|  2 | DERIVED     | subscribes | ref    | idx_user_id   | idx_user_id | 4       | const      |    1 | NULL  |
+----+-------------+------------+--------+---------------+-------------+---------+------------+------+-------+
3 rows in set (0.00 sec)
```

* メッセージ参加者名取得
``` sql
SELECT user_name FROM users JOIN (
    SELECT user_id
    FROM subscribes
    WHERE group_id = 13
) as c ON c.user_id = users.id;
```

```
mysql> explain SELECT user_name FROM users JOIN (     SELECT user_id     FROM subscribes     WHERE group_id = 13 ) as c ON c.user_id = users.id;
+----+-------------+------------+--------+---------------+--------------+---------+-----------+------+-----------------------+
| id | select_type | table      | type   | possible_keys | key          | key_len | ref       | rows | Extra                 |
+----+-------------+------------+--------+---------------+--------------+---------+-----------+------+-----------------------+
|  1 | PRIMARY     | <derived2> | ALL    | NULL          | NULL         | NULL    | NULL      |    3 | NULL                  |
|  1 | PRIMARY     | users      | eq_ref | PRIMARY       | PRIMARY      | 4       | c.user_id |    1 | NULL                  |
|  2 | DERIVED     | subscribes | ref    | idx_group_id  | idx_group_id | 8       | const     |    3 | Using index condition |
+----+-------------+------------+--------+---------------+--------------+---------+-----------+------+-----------------------+
3 rows in set (0.00 sec)

```

* プライベートメッセージ取得
```sql
SELECT message, user_id, created_at
FROM private_messages
WHERE group_id = 13;
```

```
mysql> explain SELECT message, user_id, created_at FROM private_messages WHERE group_id = 13;
+----+-------------+------------------+------+---------------+--------------+---------+-------+------+-----------------------+
| id | select_type | table            | type | possible_keys | key          | key_len | ref   | rows | Extra                 |
+----+-------------+------------------+------+---------------+--------------+---------+-------+------+-----------------------+
|  1 | SIMPLE      | private_messages | ref  | idx_group_id  | idx_group_id | 8       | const |    3 | Using index condition |
+----+-------------+------------------+------+---------------+--------------+---------+-------+------+-----------------------+
1 row in set (0.00 sec)

```

* 新規のプライベートメッセージ取得
```sql
SELECT message, user_id, created_at
FROM private_messages
WHERE group_id = 13 AND created_at > '2017-10-28';
```

```
mysql> explain SELECT message, user_id, created_at
    -> FROM private_messages
    -> WHERE group_id = 13 AND created_at > '2017-10-28';
+----+-------------+------------------+------+-----------------------------+--------------+---------+-------+------+------------------------------------+
| id | select_type | table            | type | possible_keys               | key          | key_len | ref   | rows | Extra                              |
+----+-------------+------------------+------+-----------------------------+--------------+---------+-------+------+------------------------------------+
|  1 | SIMPLE      | private_messages | ref  | idx_created_at,idx_group_id | idx_group_id | 8       | const |    3 | Using index condition; Using where |
+----+-------------+------------------+------+-----------------------------+--------------+---------+-------+------+------------------------------------+
1 row in set (0.00 sec)
```

* 過去のプライベートメッセージ取得
```sql
SELECT message, user_id, created_at
FROM private_messages
WHERE group_id = 13 AND created_at < '2017-10-30';
```

```
mysql> explain SELECT message, user_id, created_at
    -> FROM private_messages
    -> WHERE group_id = 13 AND created_at < '2017-10-30';
+----+-------------+------------------+------+-----------------------------+--------------+---------+-------+------+------------------------------------+
| id | select_type | table            | type | possible_keys               | key          | key_len | ref   | rows | Extra                              |
+----+-------------+------------------+------+-----------------------------+--------------+---------+-------+------+------------------------------------+
|  1 | SIMPLE      | private_messages | ref  | idx_created_at,idx_group_id | idx_group_id | 8       | const |    3 | Using index condition; Using where |
+----+-------------+------------------+------+-----------------------------+--------------+---------+-------+------+------------------------------------+
1 row in set (0.00 sec)
```


* メッセージの送信者名取得
```sql
SELECT user_name FROM users WHERE id = 753070;
```

sunsetter データベースのテーブル詳細
```
mysql> explain SELECT user_name FROM users WHERE id = 753070;
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref   | rows | Extra |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------+
|  1 | SIMPLE      | users | const | PRIMARY       | PRIMARY | 4       | const |    1 | NULL  |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-------+
1 row in set (0.00 sec)
```

```
mysql> SHOW TABLE STATUS FROM sunsetter\G
*************************** 1. row ***************************
           Name: follows
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 197857920
 Avg_row_length: 42
    Data_length: 8452571136　# 8.4GB
Max_data_length: 0
   Index_length: 0
      Data_free: 0
 Auto_increment: 200000001
    Create_time: 2017-10-29 13:51:48
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
*************************** 2. row ***************************
           Name: groups
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 50186
 Avg_row_length: 94
    Data_length: 4734976 # 4.7MB
Max_data_length: 0
   Index_length: 0
      Data_free: 4194304
 Auto_increment: 50001
    Create_time: 2017-10-29 10:11:55
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
*************************** 3. row ***************************
           Name: posts
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 4545630
 Avg_row_length: 331
    Data_length: 1505755136 # 1.5GB
Max_data_length: 0
   Index_length: 0
      Data_free: 0
 Auto_increment: 4500006
    Create_time: 2017-10-29 14:43:08
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
*************************** 4. row ***************************
           Name: private_messages
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 143325
 Avg_row_length: 406
    Data_length: 58294272 # 58.29GB
Max_data_length: 0
   Index_length: 0
      Data_free: 2097152
 Auto_increment: 150001
    Create_time: 2017-10-29 15:32:46
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
*************************** 5. row ***************************
           Name: subscribes
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 50432
 Avg_row_length: 52
    Data_length: 2637824 # 2.63GB
Max_data_length: 0
   Index_length: 0
      Data_free: 2097152
 Auto_increment: 50001
    Create_time: 2017-10-29 15:30:25
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
*************************** 6. row ***************************
           Name: users
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 901219
 Avg_row_length: 1324
    Data_length: 1193279488 # 1.2GB
Max_data_length: 0
   Index_length: 0
      Data_free: 0
 Auto_increment: 1000001
    Create_time: 2017-10-29 13:21:03
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
6 rows in set (0.00 sec)
```

user image(ユーザ０のプロフィール写真が入ったデータベース)
```
mysql> SHOW TABLE STATUS FROM sunsetter_user_image\G
*************************** 1. row ***************************
           Name: user_images
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 459511
 Avg_row_length: 141938
    Data_length: 65222344704 # 65.22GB
Max_data_length: 0
   Index_length: 0
      Data_free: 0
 Auto_increment: 502001
    Create_time: 2017-10-29 15:07:26
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
1 row in set (0.00 sec)
```

post imageの写真が入っているデータベース
```
mysql> SHOW TABLE STATUS FROM sunsetter_post_image\G
*************************** 1. row ***************************
           Name: post_images
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 630258
 Avg_row_length: 130342
    Data_length: 82149638144 # 82.1GB
Max_data_length: 0
   Index_length: 0
      Data_free: 97517568
 Auto_increment: 626001
    Create_time: 2017-10-29 15:48:25
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
1 row in set (0.00 sec)
```

private messageの写真が入っているデータベース
```
mysql> SHOW TABLE STATUS FROM sunsetter_private_image\G
*************************** 1. row ***************************
           Name: private_images
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 28129
 Avg_row_length: 147900
    Data_length: 4160290816 # 4.16GB
Max_data_length: 0
   Index_length: 0
      Data_free: 2097152
 Auto_increment: 31001
    Create_time: 2017-10-29 15:03:24
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
1 row in set (0.00 sec)
```
