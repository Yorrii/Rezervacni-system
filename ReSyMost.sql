CREATE TABLE `Terminy` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `datum` date,
  `active_flag` enum('Y','N','R') DEFAULT 'N',
  `max_ridicu` tinyint
);

CREATE TABLE `Autoskoly` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `nazev` varchar(50),
  `datova_schranka` varchar(100),
  `email` varchar(70),
  `heslo` varchar(70),
  `adresa_ucebny` varchar(100)
) AUTO_INCREMENT=1;

CREATE TABLE `Zaznamy` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `druh` enum('zápis','odpis','přidání','odebrání', 'přihlásil se', 'odhlásil se'),
  `kdy` datetime,
  `zprava` text,
  `id_autoskoly` int
);

CREATE TABLE `Komisari` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `email` varchar(70),
  `heslo` varchar(70),
  `jmeno` varchar(30),
  `prijmeni` varchar(30)
) AUTO_INCREMENT=100001;

CREATE TABLE `Zaci` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `evidencni_cislo` varchar(30),
  `jmeno` varchar(30),
  `prijmeni` varchar(30),
  `datum_narozeni` date,
  `adresa` varchar(255),
  `cislo_prukazu` varchar(20),
  `id_autoskoly` int
);

CREATE TABLE `Zapsani_zaci` (
  `potvrzeni` enum('Y','N','W') DEFAULT 'W',
  `typ_zkousky` enum('A','B','C','C+E','D','D+E','T'),
  `druh_zkousky` enum('Řádná zkouška','Opravná zkouška-test+jízda','Opravná zkouška-jízda','Opravná zkouška-technika','Opravná zkouška-technika+jízda','Profesní způsobilost-test'),
  `zaver` enum('Y', 'N', 'W') DEFAULT 'W',
  `zacatek` time,
  `id_terminu` int,
  `id_komisare` int,
  `id_autoskoly` int,
  `id_zaka` int
  PRIMARY KEY (`id_terminu`, `id_zaka`)
);

CREATE TABLE `Vozidla` (
    `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `znacka` VARCHAR(100) NOT NULL,
    `model` VARCHAR(100) NOT NULL,
    `spz` VARCHAR(10),
    `id_autoškoly` INT,
    FOREIGN KEY (id_autoškoly) REFERENCES autoškoly(id)
);


ALTER TABLE `Zaznamy` ADD FOREIGN KEY (`id_autoskoly`) REFERENCES `Autoskoly` (`id`);

ALTER TABLE `Zaci` ADD FOREIGN KEY (`id_autoskoly`) REFERENCES `Autoskoly` (`id`);

ALTER TABLE `Zapsani_zaci` ADD FOREIGN KEY (`id_terminu`) REFERENCES `Terminy` (`id`);

ALTER TABLE `Zapsani_zaci` ADD FOREIGN KEY (`id_komisare`) REFERENCES `Komisari` (`id`);

ALTER TABLE `Zapsani_zaci` ADD FOREIGN KEY (`id_autoskoly`) REFERENCES `Autoskoly` (`id`);

ALTER TABLE `Zapsani_zaci` ADD FOREIGN KEY (`id_zaka`) REFERENCES `Zaci` (`id`);

ALTER TABLE `Vozidla` ADD FOREIGN KEY (`id_autoskoly`) REFERENCES `Autoskoly` (`id`);

SET GLOBAL event_scheduler = ON;

CREATE EVENT IF NOT EXISTS `aktualizace_active_flag`
ON SCHEDULE EVERY 1 DAY
DO
  UPDATE `Terminy`
  SET `active_flag` = 'Y'
  WHERE `datum` BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 14 DAY)
  AND `active_flag` != 'Y';

CREATE EVENT IF NOT EXISTS `nastavit_flag_na_R`
ON SCHEDULE EVERY 1 DAY
DO
  UPDATE `Terminy`
  SET `active_flag` = 'R'
  WHERE `datum` < CURDATE()
  AND `active_flag` != 'R';