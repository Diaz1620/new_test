-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema magazines
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema magazines
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `magazines` DEFAULT CHARACTER SET utf8 ;
USE `magazines` ;

-- -----------------------------------------------------
-- Table `magazines`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `magazines`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL,
  `last_name` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  `created_at` DATETIME NULL DEFAULT Now(),
  `updated_at` DATETIME NULL DEFAULT Now(),
  `userscol` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `magazines`.`magazines`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `magazines`.`magazines` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NULL,
  `description` VARCHAR(255) NULL,
  `created_at` DATETIME NULL DEFAULT Now(),
  `updated_at` DATETIME NULL DEFAULT Now(),
  `users_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_magazines_users_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_magazines_users`
    FOREIGN KEY (`users_id`)
    REFERENCES `magazines`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `magazines`.`Subscribers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `magazines`.`Subscribers` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `magazine_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Subscribers_magazines1_idx` (`magazine_id` ASC) VISIBLE,
  INDEX `fk_Subscribers_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_Subscribers_magazines1`
    FOREIGN KEY (`magazine_id`)
    REFERENCES `magazines`.`magazines` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Subscribers_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `magazines`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
