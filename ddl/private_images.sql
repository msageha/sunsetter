CREATE TABLE private_images (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    private_message_id BIGINT UNSIGNED NOT NULL,
    image MEDIUMBLOB NOT NULL,
    INDEX idx_private_message_id(private_message_id)
);
