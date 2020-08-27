import datetime
from datetime import datetime as dt
from datetime import timezone, timedelta
from typing import Optional


def date_to_datetime(date_str: Optional[str] = None):
    """
    Takes a vaild date string and converts it into
    a datetime object
    """
    if date_str is None:
        return dt.now()
    day = dt.strptime(date_str, "%Y-%m-%d").date()
    timestamp = dt(
        year=day.year,
        month=day.month,
        day=day.day,
        tzinfo=timezone(timedelta(minutes=0)),
    )
    return timestamp
