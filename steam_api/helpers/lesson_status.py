from datetime import datetime, timedelta
from typing import Dict, Optional
from django.utils import timezone
from zoneinfo import ZoneInfo

def get_lesson_date(start_date: datetime.date, schedule: Dict[str, str], lesson_sequence: int) -> Optional[datetime.date]:
    day_mapping = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    class_days = []
    for day in schedule.keys():
        day = day.lower()
        if day in day_mapping:
            class_days.append(day_mapping[day])
    class_days.sort()
    
    if not class_days:
        return None
        
    total_days_needed = lesson_sequence - 1
    weeks = total_days_needed // len(class_days)
    remaining_days = total_days_needed % len(class_days)
    
    current_date = start_date
    
    current_date += timedelta(weeks=weeks)
    
    start_weekday = start_date.weekday()
    first_class_day = None
    for day in class_days:
        if day >= start_weekday:
            first_class_day = day
            break
    if first_class_day is None:
        first_class_day = class_days[0]
        current_date += timedelta(days=7-start_weekday+first_class_day)
    else:
        current_date += timedelta(days=first_class_day-start_weekday)
    
    if remaining_days > 0:
        days_to_add = 0
        current_weekday = current_date.weekday()
        days_added = 0
        
        while days_added < remaining_days:
            next_day_index = (class_days.index(current_weekday) + 1) % len(class_days)
            next_day = class_days[next_day_index]
            
            if next_day <= current_weekday:
                days_to_add += 7 - current_weekday + next_day
            else:
                days_to_add += next_day - current_weekday
                
            current_weekday = next_day
            days_added += 1
            
        current_date += timedelta(days=days_to_add)
    
    return current_date

def calculate_lesson_status(
    start_date: datetime.date,
    end_date: datetime.date,
    schedule: Dict[str, str],
    lesson_sequence: int
) -> str:
    vn_tz = ZoneInfo('Asia/Ho_Chi_Minh')
    now = timezone.localtime(timezone.now(), vn_tz)
    today = now.date()
    
    if today < start_date:
        return 'not_started'
        
    if today > end_date:
        return 'completed'
    
    lesson_date = get_lesson_date(start_date, schedule, lesson_sequence)
    if not lesson_date:
        return 'not_started'
        
    if lesson_date > today:
        return 'not_started'
    
    if lesson_date == today:
        weekday = lesson_date.strftime('%A').lower()
        time_range = schedule.get(weekday)
        if time_range:
            start_time = datetime.strptime(time_range.split('-')[0], '%H:%M').time()
            end_time = datetime.strptime(time_range.split('-')[1], '%H:%M').time()
            current_time = now.time()
            
            if current_time < start_time:
                return 'not_started'
            elif current_time > end_time:
                return 'completed'
            else:
                return 'in_progress'
    
    return 'completed' 