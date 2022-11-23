USE `patient_portal`;

CREATE TABLE IF NOT EXISTS `production_patient_photos` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `mrn` varchar(50) NULL,
    `photo_data` longblob NOT NULL,
    `photo_data_rendered` longblob NOT NULL,
    PRIMARY KEY (`id`)
);
