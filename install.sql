DROP TABLE IF EXISTS `alarm_item`;
DROP TABLE IF EXISTS `alarm_group`;

CREATE TABLE `alarm_group` (
	`alarm_group_id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`alarm_group_created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`alarm_group_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`alarm_group_flags` TINYINT(4) NOT NULL DEFAULT '0' COMMENT 'Flags: 1: enable/disable',
	`alarm_group_name` VARCHAR(128) NOT NULL COMMENT 'I am the name of the alarm group. I am unique.' COLLATE 'utf8_general_ci',
	PRIMARY KEY (`alarm_group_id`) USING BTREE,
	UNIQUE INDEX `alarm_group_name_unique` (`alarm_group_name`) USING BTREE
) COLLATE='utf8_general_ci' ENGINE=INNODB;

CREATE TABLE `alarm_item` (
	`alarm_item_id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`alarm_item_created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`alarm_item_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`alarm_item_flags` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Flags: 1: enable/disable',
	`alarm_item_name` VARCHAR(64) NOT NULL COMMENT 'The name of the alarm. Unique per group.' COLLATE 'utf8_general_ci',
	`alarm_item_valence_on` VARCHAR(16) NOT NULL COMMENT 'I am the value written to the alarm address, if the alarm is engaged.' COLLATE 'utf8_general_ci',
	`alarm_item_valence_off` VARCHAR(16) NOT NULL COMMENT 'I am the value written to the alarm address, if the alarm is disengaged.' COLLATE 'utf8_general_ci',
	`alarm_item_hysteresis_seconds` TINYINT(3) UNSIGNED NOT NULL COMMENT 'I am the hysteresis time, to allow the read value to exceed the threshold for some time.',
	`alarm_item_hysteresis_value` VARCHAR(16) NOT NULL COMMENT 'I am the hysteresis value, to allow the read value to exceed the threshold for some time.' COLLATE 'utf8_general_ci',
	`alarm_item_comparison_type` VARCHAR(8) NOT NULL COMMENT 'I am the comparison type (less, greater, equals, etc.)' COLLATE 'utf8_general_ci',
	`alarm_item_compare_value` VARCHAR(16) NOT NULL COMMENT 'I am the threshold value for the comparison.' COLLATE 'utf8_general_ci',
	`alarm_group_id` INT(10) UNSIGNED NOT NULL COMMENT 'I am the alarm group this alarm is located in.',
	`opc_item_id_read` INT(10) UNSIGNED NOT NULL COMMENT 'I am the OPC address that will be read to compare the value.',
	`opc_item_id_disengaged` INT(10) UNSIGNED NOT NULL COMMENT 'I am the OPC address that the DISENGAGED statement will be written to. Write addresses are unique.',
	`opc_item_id_alarm` INT(10) UNSIGNED NOT NULL COMMENT 'I am the OPC address the real alarm value will be written to. Write addresses are unique.',
	`opc_item_id_ack` INT(10) UNSIGNED NOT NULL COMMENT 'I am the OPC address the acknowledgement will be written to. Write addresses are unique.',
	`opc_item_id_engaged` INT(10) UNSIGNED NOT NULL COMMENT 'I am the OPC address the engaged date and time will be written to. Write addresses are unique.',
	PRIMARY KEY (`alarm_item_id`) USING BTREE,
	UNIQUE INDEX `alarm_item_to_opc_item_disengaged_unique` (`opc_item_id_disengaged`) USING BTREE,
	UNIQUE INDEX `alarm_item_to_opc_item_alarm_unique` (`opc_item_id_alarm`) USING BTREE,
	UNIQUE INDEX `alarm_item_to_opc_item_ack_unique` (`opc_item_id_ack`) USING BTREE,
	UNIQUE INDEX `alarm_item_to_opc_item_engaged_unique` (`opc_item_id_engaged`) USING BTREE,
	UNIQUE INDEX `alarm_group_id_alarm_name_unique` (`alarm_group_id`, `alarm_item_name`) USING BTREE,
	INDEX `opc_item_read` (`opc_item_id_read`) USING BTREE,
	INDEX `opc_item_alarm` (`opc_item_id_alarm`) USING BTREE,
	INDEX `opc_item_engaged` (`opc_item_id_engaged`) USING BTREE,
	INDEX `opc_item_disengaged` (`opc_item_id_disengaged`) USING BTREE,
	INDEX `opc_item_ack` (`opc_item_id_ack`) USING BTREE,
	INDEX `alarm_group_id` (`alarm_group_id`) USING BTREE,
	CONSTRAINT `alarm_item_to_alarm_group` FOREIGN KEY (`alarm_group_id`) REFERENCES `alarm_group` (`alarm_group_id`) ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT `alarm_item_to_opc_item_ack` FOREIGN KEY (`opc_item_id_ack`) REFERENCES `opc_item` (`opc_item_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
	CONSTRAINT `alarm_item_to_opc_item_alarm` FOREIGN KEY (`opc_item_id_alarm`) REFERENCES `opc_item` (`opc_item_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
	CONSTRAINT `alarm_item_to_opc_item_engaged` FOREIGN KEY (`opc_item_id_engaged`) REFERENCES `opc_item` (`opc_item_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
	CONSTRAINT `alarm_item_to_opc_item_disengaged` FOREIGN KEY (`opc_item_id_disengaged`) REFERENCES `opc_item` (`opc_item_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
	CONSTRAINT `alarm_item_to_opc_item_read` FOREIGN KEY (`opc_item_id_read`) REFERENCES `opc_item` (`opc_item_id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) COLLATE='utf8_general_ci' ENGINE=INNODB;
