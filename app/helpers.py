from datetime import datetime

def format_timestamp(ts):
  dt = datetime.fromtimestamp(ts)
  return dt.strftime("%d %B %Y")
