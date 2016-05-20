DROP DATABASE `sim`;
CREATE DATABASE `sim`;
USE `sim`;

CREATE TABLE `author`(
    `authorid` INT PRIMARY KEY AUTO_INCREMENT  NOT NULL,
    `author` VARCHAR (50) UNIQUE NOT NULL
    )DEFAULT CHARSET=`utf8` AUTO_INCREMENT=1;

CREATE TABLE `journal`(
    `journalid` INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    `journal` VARCHAR (50) UNIQUE NOT NULL
    )DEFAULT CHARSET=`utf8` AUTO_INCREMENT=1;


CREATE TABLE `article`(
    `articleid` INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    `title` VARCHAR (200) ,
    `year` INT DEFAULT null NULL ,
    `journalid` INT 
    ) DEFAULT CHARSET=`utf8` AUTO_INCREMENT=1;


CREATE TABLE `author_article`(
    `aaid` INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    `authorid` INT,
    `articleid` INT
    )DEFAULT CHARSET=`utf8` AUTO_INCREMENT=1;

CREATE TABLE `article_article`(
    `aaid` INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    `articlereferred` INT,
    `articlereferring` INT
    )DEFAULT CHARSET=`utf8` AUTO_INCREMENT=1;
    

alter table `article` add constraint `c_article_journal_FK` foreign key (`journalid`)  references `journal` (`journalid`);
alter table `author_article` add constraint `c_author_article_article_FK` foreign key (`articleid`) references `article` (`articleid`);
alter table `author_article` add constraint `c_author_article_author_FK` foreign key (`authorid`) references `author` (`authorid`);
alter table `article_article` add constraint `c_article_article_article_FK1` foreign key (`articlereferred`) references `article` (`articleid`);
alter table `article_article` add constraint `c_article_article_article_FK2` foreign key (`articlereferring`) references `article` (`articleid`);


CREATE TABLE `nodes`(
    `id` INT PRIMARY KEY AUTO_INCREMENT NOT NULL
    )DEFAULT CHARSET=`utf8` AUTO_INCREMENT=1;
    
CREATE TABLE `edges`(
    `id` INT PRIMARY KEY AUTO_INCREMENT NOT NULL
    )DEFAULT CHARSET=`utf8` AUTO_INCREMENT=1;
