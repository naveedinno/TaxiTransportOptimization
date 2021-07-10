from datetime import datetime, timedelta, date, time

class Trip:
    def __init__(self, startTime, endTime, source, destination):
        startTime = startTime.strip()
        self.startTime = datetime.combine(date.today(), time(hour=int(startTime[:-2]), minute=int(startTime[-2:])))
        endTime = endTime.strip()
        self.endTime = datetime.combine(date.today(), time(hour=int(endTime[:-2]), minute=int(endTime[-2:])))
        self.source = int(source.strip())
        self.destination = int(destination.strip())

    def __str__(self):
        return f"{self.startTime}:{self.endTime}:{self.source}:{self.destination}"