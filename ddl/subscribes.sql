CREATE TABLE subscribes
  (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT, 
    user_id INT UNSIGNED NOT NULL,
    group_id BIGINT UNSIGNED NOT NULL,
    INDEX idx_user_id(user_id),
    INDEX idx_group_id(group_id)
  );
