create table posts (
  id bigint unsigned primary key auto_increment,
  message varchar(200) not null,
  user_id int unsigned not null,
  created_at datetime not null default current_timestamp,
  INDEX idx_user_id(user_id),
  INDEX idx_created_at(created_at)
);
