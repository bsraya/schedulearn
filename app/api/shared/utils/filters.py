from babel.dates import format_datetime

def format_date(value, format = "medium"):
    if format == "short":
        format = "MMM d, y 'at' h:mm a"
    elif format == "full":
        format = "EEEE, MMMM d, y 'at' h:mm a"
    return format_datetime(value, format, locale="en")