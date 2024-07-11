from datetime import datetime

def relative_time_from_string(time_string):
    parsed_time = datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
    current_time = datetime.now()
    time_difference = current_time - parsed_time
    seconds = time_difference.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minutes ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hours ago"
    else:
        days = int(seconds // 86400)
        return f"{days} days ago"

now = str(datetime.now())
parsed_time = datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')
formatted_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
#time_string = "2024-07-09 09:07:37"
print(relative_time_from_string(formatted_time))