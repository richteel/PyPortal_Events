import time


class event:
    def __init__(self, title, subtitle, year, month, day, hour, minute, imageCountDown, imageEventDay, forecolor=0xF0C810):
        self.title = title
        self.subtitle = subtitle
        self.forecolor = forecolor
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.date = time.struct_time((year, month, day,
                                      hour, minute, 0,  # we don't track seconds
                                      -1, -1, False))  # we dont know day of week/year or DST
        self.imageCountDown = imageCountDown
        self.imageEventDay = imageEventDay
        self.remainingTime = 365 * 24 * 60 * 60
        self.remainingDays = 365
        self.remainingHours = 0
        self.remainingMinutes = 0
        self.remainingSeconds = 0

    def __lt__(self, other):
        return self.date < other.date

    def __gt__(self, other):
        return self.date > other.date

    def __repr__(self):
        return "event()"

    def __str__(self):
        return f"event(title: {self.title}, subtitle: {self.subtitle}, remainingTime: {self.remainingTime}) for {self.month}/{self.day}/{self.year} {self.hour:02}:{self.minute:02}"

    def remainingUpdate(self):
        now = time.localtime()
        remaining = time.mktime(self.date) - time.mktime(now)
        self.remainingTime = remaining

        self.remainingSeconds = remaining % 60
        remaining //= 60
        self.remainingMinutes = remaining % 60
        remaining //= 60
        self.remainingHours = remaining % 24
        remaining //= 24
        self.remainingDays = remaining

        return self.remainingTime
