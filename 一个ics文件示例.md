一个ics文件简单示例
```
 BEGIN:VCALENDAR                             # 日历主体
 
 VERSION:2.0                                 # 必须提供
 PRODID:-//hacksw/handcal//NONSGML v1.0//EN  # 必须提供
 X-WR-CALNAME:课表                            # （可选）
 
BEGIN:VTIMEZONE                               # 时区配置（可选）
TZID:China Standard Time
BEGIN:STANDARD
DTSTART:16010101T000000
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:16010101T000000
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
END:DAYLIGHT
END:VTIMEZONE
 
 
BEGIN:VEVENT                                # 一个事件

UID:19970610T172345Z-AF23B2@example.com     # UID 确保该事件是唯一的（测试时发现没用）
DTSTAMP:20200610T172345                     # 时间 确保该事件是唯一的（测试时发现没用）
DTSTART:20200714T170000                     # 开始时间
DTEND:20200715T040000                       # 结束时间
SUMMARY:Bastille Day Party                  # 主题
DESCRIPTION:xxxxxxxxxx                      # 描述
DESCRIPTION:Breakfast meeting with executive\n
 
BEGIN:VALARM                                 # 提醒
TRIGGER:-PT30M                               # 何时触发
REPEAT:2                                     # 重复次数
DURATION:PT15M                               # 隔多久重复
ACTION:DISPLAY                               # 提醒选项
DESCRIPTION:Breakfast meteam at 8:30 AM EST.
END:VALARM
 
END:VEVENT
 

 
END:VCALENDAR
```

 DTSTART:19960415T133000Z    # UTC时间
 DTSTART:19960415T133000      # 本地时间
 DTSTART;TZID=China Standard Time:20200612T140000 # 指定时区时间