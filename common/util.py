from decimal import Decimal
from datetime import datetime, date, time, timezone

def default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        type(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

def getDatetime():
    return datetime.now(timezone.utc).isoformat()
