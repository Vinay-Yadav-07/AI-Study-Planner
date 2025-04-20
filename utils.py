# Utility functions for the study planner application

import random
from datetime import datetime, timedelta

def format_time(time_obj):
    """Format time object to string"""
    if isinstance(time_obj, str):
        return time_obj
    return time_obj.strftime("%H:%M")

def parse_time(time_str):
    """Parse time string to datetime object"""
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return datetime.now().time()

def parse_date(date_str):
    """Parse date string to date object"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return datetime.now().date()

def get_date_range(start_date, end_date):
    """Get a list of dates between start_date and end_date"""
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    return date_list

def get_motivational_quote():
    """Get a random motivational quote"""
    quotes = [
        "The secret of getting ahead is getting started. – Mark Twain",
        "Don't watch the clock; do what it does. Keep going. – Sam Levenson",
        "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
        "The future depends on what you do today. – Mahatma Gandhi",
        "You don't have to be great to start, but you have to start to be great. – Zig Ziglar",
        "Believe you can and you're halfway there. – Theodore Roosevelt",
        "It always seems impossible until it's done. – Nelson Mandela",
        "The only way to do great work is to love what you do. – Steve Jobs",
        "Your time is limited, don't waste it living someone else's life. – Steve Jobs",
        "The best way to predict the future is to create it. – Abraham Lincoln"
    ]
    return random.choice(quotes)

def get_productivity_tip():
    """Get a random productivity tip"""
    tips = [
        "Try the Pomodoro Technique: 25 minutes of focused work followed by a 5-minute break.",
        "Start your day by tackling your most challenging task first.",
        "Take short breaks to maintain focus and prevent burnout.",
        "Stay hydrated and maintain a healthy diet to boost brain function.",
        "Review your notes before sleeping to improve retention.",
        "Create a dedicated study space free from distractions.",
        "Use active recall instead of passive re-reading to improve memory.",
        "Set specific, measurable goals for each study session.",
        "Try studying at different times of day to find your peak productivity hours.",
        "Use spaced repetition to review material at optimal intervals for retention."
    ]
    return random.choice(tips)

def validate_input(input_text, input_type):
    """Validate user input based on input type"""
    if input_type == "subject":
        # Subjects should be non-empty strings
        return input_text.strip() != ""
    elif input_type == "date":
        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(input_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    elif input_type == "time":
        # Validate time format (HH:MM)
        try:
            datetime.strptime(input_text, "%H:%M")
            return True
        except ValueError:
            return False
    elif input_type == "number":
        # Validate that input is a number
        try:
            float(input_text)
            return True
        except ValueError:
            return False
    else:
        # Default validation (non-empty)
        return input_text.strip() != ""

def calculate_study_distribution(subjects, days_available, difficulty_dict=None, priority_dict=None):
    """
    Calculate how to distribute study time across subjects based on difficulty and priority
    
    Args:
        subjects (list): List of subject names
        days_available (int): Number of days available for studying
        difficulty_dict (dict, optional): Dictionary mapping subjects to difficulty ratings (1-5)
        priority_dict (dict, optional): Dictionary mapping subjects to priority levels (High, Medium, Low)
        
    Returns:
        dict: Dictionary mapping subjects to number of days to spend on them
    """
    if difficulty_dict is None:
        difficulty_dict = {subject: 3 for subject in subjects}  # Default medium difficulty
        
    if priority_dict is None:
        priority_dict = {subject: "Medium" for subject in subjects}  # Default medium priority
    
    # Convert priority to numerical value
    priority_values = {"High": 1.5, "Medium": 1.0,_values = {"High": 1.5, "Medium": 1.0, "Low": 0.5}
    
    # Calculate weighted difficulty based on priority
    weighted_difficulties = {}
    total_weighted_difficulty = 0
    
    for subject in subjects:
        difficulty = difficulty_dict.get(subject, 3)
        priority = priority_dict.get(subject, "Medium")
        priority_value = priority_values.get(priority, 1.0)
        
        weighted_difficulty = difficulty * priority_value
        weighted_difficulties[subject] = weighted_difficulty
        total_weighted_difficulty += weighted_difficulty
    
    # Distribute days based on weighted difficulty
    days_per_subject = {}
    remaining_days = days_available
    
    for subject in subjects:
        # Calculate proportion of days based on weighted difficulty
        proportion = weighted_difficulties[subject] / total_weighted_difficulty
        days = max(1, round(proportion * days_available))
        
        # Ensure we don't exceed available days
        if days > remaining_days:
            days = remaining_days
        
        days_per_subject[subject] = days
        remaining_days -= days
    
    # Distribute any remaining days to highest priority subjects
    sorted_subjects = sorted(
        subjects,
        key=lambda s: (priority_values.get(priority_dict.get(s, "Medium"), 1.0), weighted_difficulties[s]),
        reverse=True
    )
    
    i = 0
    while remaining_days > 0 and i < len(sorted_subjects):
        days_per_subject[sorted_subjects[i]] += 1
        remaining_days -= 1
        i = (i + 1) % len(sorted_subjects)
    
    return days_per_subject