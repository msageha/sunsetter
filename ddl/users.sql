CREATE TABLE users (
  id int unsigned primary key auto_increment,
  introduction varchar(500),
  image_id int,
  screen_name varchar(20) NOT NULL,
  user_name varchar(20) NOT NULL,
  password_hash varchar(256) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
