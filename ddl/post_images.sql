create table post_images (
  id bigint unsigned primary key auto_increment,
  post_id bigint unsigned not null,
  image mediumblob not null
);
