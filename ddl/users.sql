CREATE TABLE users (
  id int unsigned primary key auto_increment,
  introduction varchar(500),
  image_id int,
  screen_name varchar(20) NOT NULL,
  user_name varchar(20) NOT NULL,
  create_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  password_hash varchar(256) NOT NULL
);
