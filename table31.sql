# MySQL script
# create table for KAMSTRUP smart electricity meter readings

USE domotica;

DROP TABLE IF EXISTS kamstrup;

CREATE TABLE `kamstrup` (
  `sample_time`   datetime,
  `sample_epoch`  bigint(20) unsigned,
  `T1in`          int(11),
  `T2in`          int(11),
  `powerin`       int(11),
  `T1out`         int(11),
  `T2out`         int(11),
  `powerout`      int(11),
  `tarif`         int(11),
  `swits`         int(11),
  PRIMARY KEY (`sample_time`)
  ) ENGINE=InnoDB DEFAULT CHARSET=latin1 ;
