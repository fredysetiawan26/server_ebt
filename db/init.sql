CREATE DATABASE if not exists `db_monitoring_ebt`;
use db_monitoring_ebt;
CREATE TABLE if not exists `monitoring_ebt` (
    `data_id` int NOT NULL AUTO_INCREMENT,
    `client_id` int NOT NULL,
    `db_created_at` datetime(6) DEFAULT NULL,
    `send_to_db_at` datetime(6) DEFAULT NULL,
    `processing_time` time(6) DEFAULT NULL,
    `voltage` float DEFAULT NULL,
    `current` float DEFAULT NULL,
    `power` float DEFAULT NULL,
    `energy` float DEFAULT NULL,
    `power_factor` float DEFAULT NULL,
    PRIMARY KEY (`data_id`)
)