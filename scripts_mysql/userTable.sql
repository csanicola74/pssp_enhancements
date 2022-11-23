USE `patient_portal`;

CREATE TABLE IF NOT EXISTS `production_accounts` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
  	`username` varchar(50) NOT NULL,
  	`password` varchar(255) NOT NULL,
  	`email` varchar(100) NOT NULL,
    `account_type` varchar(50) NOT NULL,
    `mrn` varchar(50) NULL,
    `date_created` datetime NULL,
    `last_login` datetime NULL,
    PRIMARY KEY (`id`)
);

INSERT INTO `production_accounts` (`id`, `username`, `password`, `email`, `account_type`) VALUES (1, 'admin', 'admin', 'admin@admin.com', 'admin');
