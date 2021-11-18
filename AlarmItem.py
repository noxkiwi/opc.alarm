import time

from noxLogger import noxLogger

# I am an alarm item.
class AlarmItem:
    # I am the ID of the alarm for Identification.
    alarm_item_id = None
    # When was the alarm created?
    alarm_item_created = None
    # When was the alarm modified?
    alarm_item_modified = None
    # Flags 'n stuff.
    alarm_item_flags = None
    # The name of the alarm. Unique per group.
    alarm_item_name = None
    # I am the OPC address that will be read to compare the value.
    alarm_address_read = None
    # I am the OPC address the real alarm value will be written to. Write addresses are unique.
    alarm_address_write = None
    # I am the OPC address the CAME date and time will be written to. Write addresses are unique.
    alarm_address_came = None
    # I am the OPC address that the GONE statement will be written to. Write addresses are unique.
    alarm_address_gone = None
    # I am the OPC address the acknowledgement will be written to. Write addresses are unique.
    alarm_address_ack = None
    # I am the hysteresis time, to allow the read value to exceed the threshold for some time.
    alarm_item_hysteresis_seconds = None
    # I am the hysteresis value, to allow the read value to exceed the threshold for some time.
    alarm_item_hysteresis_value = None
    # I am the comparison type (less, greater, equals, etc.)
    alarm_item_comparison_type = None
    # I am the threshold value for the comparison.
    alarm_item_compare_value = None
    # I am the value written to the alarm address, if the alarm is engaged.
    alarm_item_valence_on = None
    # I am the value written to the alarm address, if the alarm is disengaged.
    alarm_item_valence_off = None
    # OPC Node of the readable item.
    node_read = None
    # OPC Node of the ALARM item
    node_write = None
    # OPC Node of the CAME item
    node_came = None
    # OPC Node of the GONE item
    node_gone = None
    # OPC Node of the ACK item
    node_ack = None
    # OTHER
    server = None
    hysteresis_start = None
    hysteresis_direction = None
    alarmGroupItem = None
    hysteresisValue = None

    # Creates the AlarmItem.
    def __init__(self, alarm_item_row, server, alarm_group_item):
        self.alarm_item_id = alarm_item_row[0]
        self.alarm_item_created = alarm_item_row[1]
        self.alarm_item_modified = alarm_item_row[2]
        self.alarm_item_flags = alarm_item_row[3]
        self.alarm_item_name = alarm_item_row[4]
        self.alarm_address_read = alarm_item_row[5]
        self.alarm_address_write = alarm_item_row[6]
        self.alarm_address_came = alarm_item_row[7]
        self.alarm_address_gone = alarm_item_row[8]
        self.alarm_address_ack = alarm_item_row[9]
        self.alarm_item_hysteresis_seconds = alarm_item_row[10]
        self.alarm_item_hysteresis_value = alarm_item_row[11]
        self.alarm_item_comparison_type = alarm_item_row[12]
        self.alarm_item_compare_value = alarm_item_row[13]
        self.alarm_item_valence_on = alarm_item_row[14]
        self.alarm_item_valence_off = alarm_item_row[15]
        self.server = server
        self.alarmGroupItem = alarm_group_item
        self.hysteresisValue = float(self.alarm_item_compare_value) + float(self.alarm_item_hysteresis_value)

    # I will run the comparison, check for hysteresis time and make alarms come and leave.
    def work(self):
        noxLogger.debug("[0x01000000] START alarm checking for " + self.alarm_address_read)
        noxLogger.debug("     ---     Current value is " + str(self.node_read.get_value()))
        if self.comparisonMatch(self.node_read.get_value()):
            noxLogger.debug("     ---     Value out of boundaries.")
            if self.hysteresisExceeded("come"):
                self.come()
        else:
            noxLogger.debug("     ---     Value within boundaries.")
            if self.hysteresisExceeded("leave"):
                self.leave()

    # I will return whether the configured comparison matches or not.
    def comparisonMatch(self, val):
        if self.alarm_item_comparison_type == "EQ":
            result = val == self.hysteresisValue
        if self.alarm_item_comparison_type == "NEQ":
            result = val != self.hysteresisValue
        if self.alarm_item_comparison_type == "LT":
            result = val < self.hysteresisValue
        if self.alarm_item_comparison_type == "LTE":
            result = val <= self.hysteresisValue
        if self.alarm_item_comparison_type == "GT":
            result = val > self.hysteresisValue
        if self.alarm_item_comparison_type == "GTE":
            result = val >= self.hysteresisValue
        noxLogger.debug("     ---     COMPARISON: ")
        noxLogger.debug("     ---       └───Type: " + self.alarm_item_comparison_type)
        noxLogger.debug("     ---       └──Value: " + str(self.alarm_item_compare_value))
        noxLogger.debug("     ---       └─HValue: " + str(self.hysteresisValue))
        noxLogger.debug("     ---     RESULT:")
        noxLogger.debug("     ---       └──Value: " + str(result))
        return result

    # I will restart the hysteresis time for the given direction.
    def hysteresisReset(self, direction):
        self.hysteresis_start = time.time()
        self.hysteresis_direction = direction

    # I will return whether the hysteresis time has exceeded.
    def hysteresisExceeded(self, direction):
        noxLogger.debug("     ---     HYSTERESIS: ")
        noxLogger.debug("     ---       └───Type: " + str(self.alarm_item_hysteresis_value))
        noxLogger.debug("     ---       └──Value: " + str(self.hysteresisValue))
        if self.alarm_item_hysteresis_seconds is None:
            return True
        if self.hysteresis_start is None or self.hysteresis_direction != direction:
            self.hysteresisReset(direction)
            return False
        hysteresisElapsed = time.time() - self.hysteresis_start

        noxLogger.debug("     ---       └──Start: " + str(self.hysteresis_start))
        noxLogger.debug("     ---       └───Time: " + str(self.alarm_item_hysteresis_seconds))
        if hysteresisElapsed < self.alarm_item_hysteresis_seconds:
            hysteresisRemains = self.alarm_item_hysteresis_seconds - hysteresisElapsed
            noxLogger.debug("     ---       └────Elapsed: " + str(hysteresisElapsed))
            noxLogger.debug("     ---       └──Remaining: " + str(hysteresisRemains))
            return False
        return True

    # I will make the alarm come up.
    def come(self):
        if self.node_write.get_value() == self.alarm_item_valence_on:
            return None
        noxLogger.debug("     ---     Engaging Alarm.")
        self.server.increaseCounter()
        self.node_came.set_value(time.strftime('%Y-%m-%d %H:%M:%S'))
        self.node_gone.set_value("")
        self.node_ack.set_value("")
        self.node_write.set_value(self.alarm_item_valence_on)

    # I will make the alarm leave.
    def leave(self):
        if self.node_write.get_value() == self.alarm_item_valence_off:
            return None
        noxLogger.debug("     ---     Disengaging Alarm.")
        self.server.increaseCounter()
        self.node_gone.set_value(time.strftime('%Y-%m-%d %H:%M:%S'))
        self.node_write.set_value(self.alarm_item_valence_off)

    # I will acknowledge the given alarm.
    def acknowledge(self):
        noxLogger.debug("     ---     Alarm is now acknowledged.")
        self.server.increaseCounter()
        self.node_ack.set_value(time.strftime('%Y-%m-%d %H:%M:%S'))

    # I will return all current data.
    def getData(self):
        return {
            "name": self.alarm_item_name,
            "address": self.alarm_address_write,
            "came": self.node_came.get_value(),
            "gone": self.node_gone.get_value(),
            "ack": self.node_ack.get_value()
        }
