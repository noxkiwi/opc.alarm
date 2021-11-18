# I am the AlarmGroup database item.
class AlarmGroupItem:
    # I am the ID for identification.
    alarm_group_id       = None
    # I state when the group has been created.
    alarm_group_created  = None
    # I am the last modification of the alarm group.
    alarm_group_modified = None
    # I am the flags integer field.
    alarm_group_flags    = None
    # I am the group name.
    alarm_group_name     = None
    # I am a reference to the BaseServer.
    baseClient           = None

    # I will create the AlarmGroup item.
    def __init__(self, alarmGroupRow, baseClient):
        self.alarm_group_id       = alarmGroupRow[0]
        self.alarm_group_created  = alarmGroupRow[1]
        self.alarm_group_modified = alarmGroupRow[2]
        self.alarm_group_flags    = alarmGroupRow[3]
        self.alarm_group_name     = alarmGroupRow[4]
        self.baseClient           = baseClient
