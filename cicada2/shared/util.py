from datetime import datetime


def get_runtime_ms(start: datetime, end: datetime) -> int:
    return int((end - start).seconds * 1000 + (end - start).microseconds / 1000)
