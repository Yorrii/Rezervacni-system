/*SQL script pokud bude potřeba resetovat databázi*/

CREATE DATABASE IF NOT EXISTS resymost;

USE resymost;
/* Tabulky */
CREATE TABLE `terminy` (
  `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `datum` date,
  `active_flag` enum('Y','N','R') DEFAULT 'N',
  `max_ridicu` tinyint
);

CREATE TABLE `autoskoly` (
  `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `nazev` varchar(50),
  `datova_schranka` varchar(100),
  `email` varchar(70),
  `heslo` varchar(70),
  `adresa_ucebny` varchar(100)
) AUTO_INCREMENT=1;

CREATE TABLE `logy` (
  `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `druh` enum('zápis','odpis','přidání','odebrání', 'přihlásil se', 'odhlásil se'),
  `kdy` datetime,
  `zprava` text,
  `id_autoskoly` INT,
  CONSTRAINT `fk_logy_autoskoly` FOREIGN KEY (`id_autoskoly`) REFERENCES `autoskoly` (`id`)
);

CREATE TABLE `komisari` (
  `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `email` varchar(70),
  `heslo` varchar(70),
  `jmeno` varchar(30),
  `prijmeni` varchar(30),
  `isAdmin` BOOLEAN NULL,
  `start_isAdmin` DATE,
  `end_isAdmin` DATE
) AUTO_INCREMENT=100001;

CREATE TABLE `superadmini` (
  `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `email` varchar(70),
  `heslo` varchar(70),
  `jmeno` varchar(30),
  `prijmeni` varchar(30)
) AUTO_INCREMENT=1000001;

CREATE TABLE `vozidla` (
    `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `znacka` VARCHAR(100) NOT NULL,
    `model` VARCHAR(100) NOT NULL,
    `spz` VARCHAR(10),
    `vozidla_id_autoskoly` INT,
    CONSTRAINT `fk_vozidla_autoskoly` FOREIGN KEY (`vozidla_id_autoskoly`) REFERENCES `autoskoly` (`id`)
);

CREATE TABLE `zaci` (
  `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `evidencni_cislo` varchar(30),
  `jmeno` varchar(30),
  `prijmeni` varchar(30),
  `datum_narozeni` date,
  `adresa` varchar(255),
  `cislo_prukazu` varchar(20),
  `splnil` DATE,
  `zacatek_vycviku` DATE,
  `zaci_id_autoskoly` INT,
  CONSTRAINT `fk_zaci_autoskoly` FOREIGN KEY (`zaci_id_autoskoly`) REFERENCES `autoskoly` (`id`)
);

CREATE TABLE `zapsani_zaci` (
  `potvrzeni` enum('Y','N','W') DEFAULT 'W',
  `typ_zkousky` enum('A','B','C','C+E','D','D+E','T'),
  `druh_zkousky` enum('Řádná zkouška','Opravná zkouška-test+jízda','Opravná zkouška-jízda','Opravná zkouška-technika','Opravná zkouška-technika+jízda','Profesní způsobilost-test'),
  `zaver` enum('Y', 'N', 'W') DEFAULT 'W',
  `zacatek` time,
  `id_terminu` INT,
  `id_komisare` INT,
  `z_zaci_id_autoskoly` INT,
  `id_zaka` INT,
  PRIMARY KEY (`id_terminu`, `id_zaka`),
  CONSTRAINT `fk_zapsani_zaci_terminy` FOREIGN KEY (`id_terminu`) REFERENCES `terminy` (`id`),
  CONSTRAINT `fk_zapsani_zaci_komisari` FOREIGN KEY (`id_komisare`) REFERENCES `komisari` (`id`),
  CONSTRAINT `fk_zapsani_zaci_autoskoly` FOREIGN KEY (`z_zaci_id_autoskoly`) REFERENCES `autoskoly` (`id`),
  CONSTRAINT `fk_zapsani_zaci_zaci` FOREIGN KEY (`id_zaka`) REFERENCES `zaci` (`id`)
);

CREATE TABLE `upozorneni` (
    `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `zprava` VARCHAR(200) NOT NULL,
    `datum_vytvoreni` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `stav` ENUM('Y', 'N') DEFAULT 'N',
    `upozorneni_id_autoskoly` INT,
    CONSTRAINT `fk_upozorneni_autoskoly` FOREIGN KEY (`upozorneni_id_autoskoly`) REFERENCES `autoskoly` (`id`) 
);


/* EVENTY */
/*Mění neaktivní termín na aktivní*/
CREATE EVENT IF NOT EXISTS `aktualizace_active_flag`
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 1 HOUR + INTERVAL 5 MINUTE
DO
  UPDATE `Terminy`
  SET `active_flag` = 'Y'
  WHERE `datum` BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 28 DAY)
  AND `active_flag` != 'Y';

/*Mění termín, který už proběhl na proběhlí termín*/
CREATE EVENT IF NOT EXISTS `nastavit_flag_na_R`
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 1 HOUR
DO
  UPDATE `Terminy`
  SET `active_flag` = 'R'
  WHERE `datum` < CURDATE()
  AND `active_flag` != 'R';

/* smaže studenty, kteří splnili zkoušku */
CREATE EVENT delete_old_students
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 1 HOUR + INTERVAL 15 MINUTE
DO
  DELETE FROM zaci
  WHERE splnil < CURDATE() - INTERVAL 7 DAY;

CREATE EVENT update_isAdmin
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 2 HOUR
DO
BEGIN
    UPDATE komisari
    SET isAdmin = TRUE
    WHERE CURDATE() BETWEEN start_isAdmin AND end_isAdmin;

    UPDATE komisari
    SET isAdmin = FALSE
    WHERE CURDATE() NOT BETWEEN start_isAdmin AND end_isAdmin;
END;

/*vstupní data*/
INSERT INTO `Superadmini` (`email`, `heslo`, `jmeno`, `prijmeni`) VALUES ('martina.pokorna@mesto-most.cz', '2eca8004994d2eded136286454ba7262c21b8c3cb9a3cd571d54a45f128114db', 'Martina', 'Pokorná');
INSERT INTO `Superadmini` (`email`, `heslo`, `jmeno`, `prijmeni`) VALUES ('resymost.sprava@mesto-most.cz', 'ac28112903580c5322fbda7ae7c9bbc5e76cc9bb7f5943f14da36b2bb988bd08', '-', '-');
INSERT INTO `Komisari` (`email`, `heslo`, `jmeno`, `prijmeni`) VALUES ('lubos.manak@mesto-most.cz', 'c10d22529eb52bb89fce8520db878c7d77b74cc3f60c898f6007e0896e08a349', 'Luboš', 'Maňák');
INSERT INTO `Komisari` (`email`, `heslo`, `jmeno`, `prijmeni`) VALUES ('jiri.tichy@mesto-most.cz', '74f4dd58456fc8be7f0f2940e6f37c89a820ae84a40a65acc7fe47053df56333', 'Jiří', 'Tichý');
INSERT INTO `Komisari` (`email`, `heslo`, `jmeno`, `prijmeni`) VALUES ('lenka.mrnkova@mesto-most.cz', 'e7c894d57decd939aff53a50013fd62bb561d47148b48aa2031edc04ba908fbb', 'Lenka', 'Mrnková');
INSERT INTO `Komisari` (`email`, `heslo`, `jmeno`, `prijmeni`) VALUES ('komisar@mesto-most.cz', '2b01b43a133fb76ebe95416c8061e9f4d2a476cec13c249acbddf7de04dc9a5f', 'Komisař', '-');
INSERT INTO `Autoskoly` (`nazev`, `datova_schranka`, `email`, `heslo`, `adresa_ucebny`) VALUES ('Autoškola Heger', '0000000', 'hegerit@seznam.cz', 'c794c11a0ed90fa94d1b1212b1ebd490de7b15d0eebf223b28241b496ec591a2', 'Židovická 119');
INSERT INTO `Autoskoly` (`nazev`, `datova_schranka`, `email`, `heslo`, `adresa_ucebny`) VALUES ('Autoškola Mlejnek', '0000000', 'MlejnekAS@autoskola.cz', 'e31547c80c3777a27357f76b2b2ab4626334d4d0986d880882528468528e08eb', 'Radniční 1/2');

SET GLOBAL event_scheduler = ON;