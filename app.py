import streamlit as st
import pandas as pd
import datetime
import json
import os
import random
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from ai import generate_study_plan, generate_resource_recommendations, generate_study_technique
from database import Database

# Set page configuration
st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #4CAF50, #8BC34A);
    }
    .task-complete {
        color: #4CAF50;
    }
    .priority-high {
        border-left: 4px solid #FF5252;
        padding-left: 10px;
    }
    .priority-medium {
        border-left: 4px solid #FFC107;
        padding-left: 10px;
    }
    .priority-low {
        border-left: 4px solid #2196F3;
        padding-left: 10px;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .light-mode {
        background-color: #ffffff;
        color: #333333;
    }
    .dark-mode {
        background-color: #1E1E1E;
        color: #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = Database()

# Initialize session state
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
if 'view_plan_id' not in st.session_state:
    st.session_state.view_plan_id = None

# Helper functions
def get_motivational_quote():
    quotes = [
        "The secret of getting ahead is getting started. – Mark Twain",
        "Don't watch the clock; do what it does. Keep going. – Sam Levenson",
        "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
        "The future depends on what you do today. – Mahatma Gandhi",
        "You don't have to be great to start, but you have to start to be great. – Zig Ziglar"
    ]
    return random.choice(quotes)

def get_productivity_tip():
    tips = [
        "Try the Pomodoro Technique: 25 minutes of focused work followed by a 5-minute break.",
        "Start your day by tackling your most challenging task first.",
        "Take short breaks to maintain focus and prevent burnout.",
        "Stay hydrated and maintain a healthy diet to boost brain function.",
        "Review your notes before sleeping to improve retention."
    ]
    return random.choice(tips)

# Main application
def main():
    st.sidebar.title("AI Study Planner 📚")
    
    # Main navigation
    page = st.sidebar.selectbox("Navigation", 
                               ["Create Plan", "View Plans", "Calendar", "Insights"])
    
    # Display motivational content in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Daily Motivation")
    st.sidebar.info(get_motivational_quote())
    st.sidebar.subheader("Productivity Tip")
    st.sidebar.success(get_productivity_tip())
    
    # Page routing
    if page == "Create Plan":
        create_plan_page()
    elif page == "View Plans":
        view_plans_page()
    elif page == "Calendar":
        calendar_page()
    elif page == "Insights":
        insights_page()

def create_plan_page():
    st.title("Create Your Study Plan")
    
    # Plan type selection
    plan_type = st.selectbox(
        "Select Plan Type",
        ["Quick Study", "Exam Time", "Submissions"]
    )
    
    # Different forms based on plan type
    if plan_type == "Quick Study":
        quick_study_form()
    elif plan_type == "Exam Time":
        exam_time_form()
    elif plan_type == "Submissions":
        submissions_form()

def quick_study_form():
    st.subheader("Quick Study Plan")
    st.write("Create a daily study plan to complete topics within 2 days")
    
    with st.form("quick_study_form"):
        # Basic inputs
        subjects = st.text_area("Enter subjects (one per line)")
        topics_per_subject = st.text_area("Enter topics for each subject (format: Subject: Topic1, Topic2)")
        
        # Customization tab
        with st.expander("Customizations"):
            st.subheader("Personalize Your Plan")
            
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.time_input("Study start time", datetime.strptime("08:00", "%H:%M").time())
                end_time = st.time_input("Study end time", datetime.strptime("20:00", "%H:%M").time())
                break_duration = st.slider("Break duration (minutes)", 5, 30, 15)
                
            with col2:
                break_frequency = st.slider("Study session duration (minutes)", 25, 120, 50)
                preferred_activities = st.multiselect(
                    "Break activities",
                    ["Stretching", "Walking", "Meditation", "Snack", "Social Media", "Power Nap"]
                )
                
            special_events = st.text_area("Any special events to consider? (format: Event, Date, Duration)")
            learning_style = st.radio("Your learning style", ["Visual", "Reading", "Mixed"], horizontal=True)
        
        # Priority settings
        with st.expander("Task Priorities"):
            st.subheader("Set Task Priorities")
            priority_settings = st.text_area(
                "Set priorities for subjects/topics (format: Subject/Topic: High/Medium/Low)",
                placeholder="Example:\nMath/Calculus: High\nHistory/World War II: Medium"
            )
        
        submitted = st.form_submit_button("Generate Plan")
        
        if submitted:
            if not subjects or not topics_per_subject:
                st.error("Please enter at least one subject and topic")
            else:
                # Process the inputs
                subject_list = [s.strip() for s in subjects.split('\n') if s.strip()]
                
                # Parse topics
                topics_dict = {}
                for line in topics_per_subject.split('\n'):
                    if ':' in line:
                        subj, topics = line.split(':', 1)
                        topics_dict[subj.strip()] = [t.strip() for t in topics.split(',')]
                
                # Generate plan using AI
                plan = generate_quick_study_plan(subject_list, topics_dict, start_time, end_time, 
                                               break_duration, break_frequency, preferred_activities,
                                               special_events, learning_style, priority_settings)
                
                # Save the plan
                st.session_state.current_plan = plan
                st.session_state.db.add_plan(plan)
                
                # Initialize progress tracking for this plan
                st.session_state.db.update_progress(plan['id'], {
                    'completed_tasks': [],
                    'total_tasks': len(plan['tasks']),
                    'completion_percentage': 0
                })
                
                # Show success message
                st.success("Your study plan has been generated!")
                
                # Display the plan
                display_plan(plan, show_progress=False)

def exam_time_form():
    st.subheader("Exam Time Plan")
    st.write("Create a study plan to finish all subjects before your exam")
    
    with st.form("exam_time_form"):
        # Basic inputs
        subjects = st.text_area("Enter subjects (one per line)")
        min_exam_date = datetime.now().date() + timedelta(days=1)
        exam_date = st.date_input("Exam date", value=min_exam_date, min_value=min_exam_date)

        
        # Customization tab
        with st.expander("Customizations"):
            st.subheader("Personalize Your Plan")
            
            col1, col2 = st.columns(2)
            with col1:
                daily_hours = st.slider("Hours available per day", 1, 12, 4)
                difficulty_ratings = st.text_area(
                    "Subject difficulty (1-5, format: Subject: Rating)",
                    placeholder="Example:\nMath: 4\nHistory: 2"
                )
                
            with col2:
                preferred_time = st.multiselect(
                    "Preferred study time",
                    ["Morning", "Afternoon", "Evening", "Night"]
                )
                special_events = st.text_area("Any special events to consider? (format: Event, Date)")
            
            learning_style = st.radio("Your learning style", ["Visual", "Reading", "Mixed"], horizontal=True)
        
        # Priority settings
        with st.expander("Task Priorities"):
            st.subheader("Set Subject Priorities")
            priority_settings = st.text_area(
                "Set priorities for subjects (format: Subject: High/Medium/Low)",
                placeholder="Example:\nMath: High\nHistory: Medium"
            )
        
        submitted = st.form_submit_button("Generate Plan")
        
        if submitted:
            if not subjects or not exam_date:
                st.error("Please enter at least one subject and the exam date")
            else:
                # Process the inputs
                subject_list = [s.strip() for s in subjects.split('\n') if s.strip()]
                
                # Parse difficulty ratings
                difficulty_dict = {}
                if difficulty_ratings:
                    for line in difficulty_ratings.split('\n'):
                        if ':' in line:
                            subj, rating = line.split(':', 1)
                            try:
                                difficulty_dict[subj.strip()] = int(rating.strip())
                            except ValueError:
                                pass
                
                # Generate plan using AI
                plan = generate_exam_time_plan(subject_list, exam_date, daily_hours, 
                                             difficulty_dict, preferred_time, special_events,
                                             learning_style, priority_settings)
                
                # Save the plan
                st.session_state.current_plan = plan
                st.session_state.db.add_plan(plan)
                
                # Initialize progress tracking for this plan
                st.session_state.db.update_progress(plan['id'], {
                    'completed_tasks': [],
                    'total_tasks': len(plan['tasks']),
                    'completion_percentage': 0
                })
                
                # Show success message
                st.success("Your exam preparation plan has been generated!")
                
                # Display the plan
                display_plan(plan, show_progress=False)

def submissions_form():
    st.subheader("Submissions Plan")
    st.write("Schedule assignment completion throughout the week")
    
    with st.form("submissions_form"):
        # Basic inputs
        assignments = st.text_area("Enter assignments (one per line)")
        due_dates = st.text_area("Enter due dates for each assignment (format: Assignment: YYYY-MM-DD)")
        
        # Customization tab
        with st.expander("Customizations"):
            st.subheader("Personalize Your Plan")
            
            col1, col2 = st.columns(2)
            with col1:
                daily_hours = st.slider("Hours available per day", 1, 12, 3)
                complexity_ratings = st.text_area(
                    "Assignment complexity (1-5, format: Assignment: Rating)",
                    placeholder="Example:\nResearch Paper: 5\nQuiz: 2"
                )
                
            with col2:
                preferred_time = st.multiselect(
                    "Preferred work time",
                    ["Morning", "Afternoon", "Evening", "Night"]
                )
                special_events = st.text_area("Any special events to consider? (format: Event, Date)")
            
            work_style = st.radio("Your work style", ["Focused Sessions", "Spread Out", "Deadline Driven"], horizontal=True)
        
        # Priority settings
        with st.expander("Task Priorities"):
            st.subheader("Set Assignment Priorities")
            priority_settings = st.text_area(
                "Set priorities for assignments (format: Assignment: High/Medium/Low)",
                placeholder="Example:\nResearch Paper: High\nQuiz: Low"
            )
        
        submitted = st.form_submit_button("Generate Plan")
        
        if submitted:
            if not assignments or not due_dates:
                st.error("Please enter at least one assignment and its due date")
            else:
                # Process the inputs
                assignment_list = [a.strip() for a in assignments.split('\n') if a.strip()]
                
                # Parse due dates
                due_date_dict = {}
                for line in due_dates.split('\n'):
                    if ':' in line:
                        assign, date_str = line.split(':', 1)
                        try:
                            due_date_dict[assign.strip()] = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
                        except ValueError:
                            st.warning(f"Invalid date format for {assign.strip()}")
                
                # Parse complexity ratings
                complexity_dict = {}
                if complexity_ratings:
                    for line in complexity_ratings.split('\n'):
                        if ':' in line:
                            assign, rating = line.split(':', 1)
                            try:
                                complexity_dict[assign.strip()] = int(rating.strip())
                            except ValueError:
                                pass
                
                # Generate plan using AI
                plan = generate_submissions_plan(assignment_list, due_date_dict, daily_hours, 
                                               complexity_dict, preferred_time, special_events,
                                               work_style, priority_settings)
                
                # Save the plan
                st.session_state.current_plan = plan
                st.session_state.db.add_plan(plan)
                
                # Initialize progress tracking for this plan
                st.session_state.db.update_progress(plan['id'], {
                    'completed_tasks': [],
                    'total_tasks': len(plan['tasks']),
                    'completion_percentage': 0
                })
                
                # Show success message
                st.success("Your submissions plan has been generated!")
                
                # Display the plan
                display_plan(plan, show_progress=False)

def display_plan(plan, show_progress=True):
    st.subheader("Your Personalized Study Plan")
    
    # Get progress tracking for this plan
    progress = st.session_state.db.get_progress(plan['id'])
    
    # Display plan details
    st.markdown(f"**Plan Type:** {plan['type']}")
    st.markdown(f"**Created:** {plan['created_at']}")
    
    # Display progress only if show_progress is True
    if show_progress:
        completion_percentage = progress['completion_percentage']
        
        st.subheader("Progress")
        progress_bar = st.progress(completion_percentage / 100)
        st.markdown(f"**{completion_percentage:.1f}%** completed")
    
    # Display tasks with checkboxes
    st.subheader("Tasks")
    
    # Create a container for task updates to avoid rerunning the whole app
    task_container = st.container()
    
    with task_container:
        for i, task in enumerate(plan['tasks']):
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            
            with col1:
                # Check if task is already completed
                is_completed = i in progress['completed_tasks']
                task_key = f"task_{plan['id']}_{i}"
                checked = st.checkbox("", value=is_completed, key=task_key)
                
                # Update progress if checkbox state changed
                if checked != is_completed:
                    # Create a copy of the completed tasks list
                    completed_tasks = progress['completed_tasks'].copy()
                    
                    if checked:
                        if i not in completed_tasks:
                            completed_tasks.append(i)
                    else:
                        if i in completed_tasks:
                            completed_tasks.remove(i)
                    
                    # Calculate new completion percentage
                    new_percentage = (len(completed_tasks) / progress['total_tasks']) * 100
                    
                    # Update progress in the database
                    st.session_state.db.update_progress(plan['id'], {
                        'completed_tasks': completed_tasks,
                        'total_tasks': progress['total_tasks'],
                        'completion_percentage': new_percentage
                    })
                    
                    # Refresh the progress display if showing progress
                    if show_progress:
                        progress_bar.progress(new_percentage / 100)
                        st.markdown(f"**{new_percentage:.1f}%** completed")
                    
                    # Rerun the app to update all views
                    st.experimental_rerun()
            
            with col2:
                # Display task with appropriate styling based on priority and completion
                priority_class = ""
                if 'priority' in task:
                    if task['priority'] == 'High':
                        priority_class = "priority-high"
                    elif task['priority'] == 'Medium':
                        priority_class = "priority-medium"
                    elif task['priority'] == 'Low':
                        priority_class = "priority-low"
                
                task_time = f"{task['start_time']} - {task['end_time']}" if 'start_time' in task and 'end_time' in task else ""
                
                st.markdown(
                    f"<div class='{priority_class}'>"
                    f"{task['subject']}: {task['description']} ({task_time})"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            with col3:
                # Display emoji based on task type
                if 'type' in task:
                    if task['type'] == 'study':
                        st.markdown("📚")
                    elif task['type'] == 'break':
                        st.markdown("☕")
                    elif task['type'] == 'review':
                        st.markdown("🔍")
    
    # Display study techniques and resources in separate containers to avoid nesting expanders
    st.subheader("Study Techniques")
    for technique in plan.get('study_techniques', []):
        st.markdown(f"**{technique['name']}**: {technique['description']}")
    
    st.subheader("Resources")
    for resource in plan.get('resources', []):
        st.markdown(f"**{resource['subject']}**: [{resource['title']}]({resource['url']})")
        st.markdown(f"Type: {resource['type']} | Difficulty: {resource['difficulty']}")

def view_plans_page():
    st.title("Your Study Plans")
    
    # Get all plans from the database
    plans = st.session_state.db.get_plans()
    
    if not plans:
        st.info("You haven't created any study plans yet. Go to 'Create Plan' to get started!")
        return
    
    # Check if we need to view a specific plan
    if st.session_state.view_plan_id:
        plan = st.session_state.db.get_plan(st.session_state.view_plan_id)
        if plan:
            # Add a back button
            if st.button("← Back to Plans"):
                st.session_state.view_plan_id = None
                st.experimental_rerun()
            
            # Display the plan
            display_plan(plan)
            return
        else:
            # Plan not found, reset view_plan_id
            st.session_state.view_plan_id = None
    
    # Display list of plans
    for i, plan in enumerate(plans):
        with st.expander(f"{plan['type']} Plan - {plan['created_at']}"):
            # Display plan details
            st.markdown(f"**Plan Type:** {plan['type']}")
            st.markdown(f"**Created:** {plan['created_at']}")
            
            # Calculate and display progress
            progress = st.session_state.db.get_progress(plan['id'])
            completion_percentage = progress['completion_percentage']
            st.progress(completion_percentage / 100)
            st.markdown(f"**{completion_percentage:.1f}%** completed")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("View Details", key=f"view_{i}"):
                    st.session_state.view_plan_id = plan['id']
                    st.experimental_rerun()
            
            with col2:
                if st.button("Edit Plan", key=f"edit_{i}"):
                    st.info("Edit functionality would be implemented here")
            
            with col3:
                if st.button("Delete Plan", key=f"delete_{i}"):
                    # Store the plan ID to delete
                    st.session_state[f"delete_plan_{i}"] = True
    
    # Handle plan deletion with confirmation
    for i, plan in enumerate(plans):
        if st.session_state.get(f"delete_plan_{i}", False):
            st.warning(f"Are you sure you want to delete this plan?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Delete", key=f"confirm_delete_{i}"):
                    # Delete the plan
                    st.session_state.db.delete_plan(plan['id'])
                    # Reset the flag
                    st.session_state[f"delete_plan_{i}"] = False
                    # If this was the viewed plan, reset view_plan_id
                    if st.session_state.view_plan_id == plan['id']:
                        st.session_state.view_plan_id = None
                    st.success("Plan deleted successfully!")
                    st.experimental_rerun()
            with col2:
                if st.button("Cancel", key=f"cancel_delete_{i}"):
                    # Reset the flag
                    st.session_state[f"delete_plan_{i}"] = False
                    st.experimental_rerun()
    
    # Clear all plans button
    if st.button("Clear All Plans"):
        st.session_state["confirm_clear_all"] = True
    
    if st.session_state.get("confirm_clear_all", False):
        st.warning("Are you sure you want to clear all plans? This cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Clear All"):
                st.session_state.db.clear_all_data()
                st.session_state.view_plan_id = None
                st.session_state["confirm_clear_all"] = False
                st.success("All plans cleared successfully!")
                st.experimental_rerun()
        with col2:
            if st.button("Cancel Clearing"):
                st.session_state["confirm_clear_all"] = False
                st.experimental_rerun()

def calendar_page():
    st.title("Study Calendar")
    
    # Calendar view
    st.subheader("Schedule Study Sessions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Add new calendar event
        with st.form("add_calendar_event"):
            st.subheader("Add New Study Session")
            event_title = st.text_input("Title")
            event_date = st.date_input("Date")
            event_start_time = st.time_input("Start Time")
            event_end_time = st.time_input("End Time")
            event_description = st.text_area("Description")
            
            submitted = st.form_submit_button("Add to Calendar")
            
            if submitted:
                if not event_title:
                    st.error("Please enter a title for the event")
                elif event_end_time <= event_start_time:
                    st.error("End time must be after start time")
                else:
                    # Create new calendar event
                    new_event = {
                        'id': f"event_{datetime.now().timestamp()}",
                        'title': event_title,
                        'date': event_date.strftime("%Y-%m-%d"),
                        'start_time': event_start_time.strftime("%H:%M"),
                        'end_time': event_end_time.strftime("%H:%M"),
                        'description': event_description
                    }
                    
                    st.session_state.db.add_calendar_event(new_event)
                    st.success("Event added to calendar!")
                    st.experimental_rerun()
    
    with col2:
        # Display upcoming events
        st.subheader("Upcoming Study Sessions")
        
        calendar_events = st.session_state.db.get_calendar_events()
        
        if not calendar_events:
            st.info("No upcoming study sessions scheduled")
        else:
            # Sort events by date
            sorted_events = sorted(
                calendar_events,
                key=lambda x: (x['date'], x['start_time'])
            )
            
            # Display events
            for event in sorted_events:
                event_date = datetime.strptime(event['date'], "%Y-%m-%d").date()
                
                # Only show future events
                if event_date >= datetime.now().date():
                    with st.expander(f"{event['date']} - {event['title']}"):
                        st.markdown(f"**Time:** {event['start_time']} - {event['end_time']}")
                        st.markdown(f"**Description:** {event['description']}")
                        
                        # Delete button
                        if st.button("Remove", key=f"remove_event_{event['id']}"):
                            st.session_state.db.delete_calendar_event(event['id'])
                            st.success("Event removed from calendar!")
                            st.experimental_rerun()
    
    # Calendar visualization
    st.subheader("Monthly Calendar View")
    
    # Get current month and year
    today = datetime.now()
    month = st.selectbox("Month", range(1, 13), index=today.month - 1)
    year = st.selectbox("Year", range(today.year, today.year + 5), index=0)
    
    # Create calendar data
    cal_data = []
    
    # Get the first day of the month and the number of days
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    
    num_days = last_day.day
    
    # Create calendar grid
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Create a 6x7 grid for the calendar
    calendar_grid = []
    
    # Fill in the calendar grid
    day = 1
    for week in range(6):
        week_row = []
        for weekday in range(7):
            if week == 0 and weekday < first_day.weekday():
                # Empty cells before the first day of the month
                week_row.append({"day": "", "events": []})
            elif day > num_days:
                # Empty cells after the last day of the month
                week_row.append({"day": "", "events": []})
            else:
                # Regular day cells
                date_str = f"{year}-{month:02d}-{day:02d}"
                events = [e for e in calendar_events if e['date'] == date_str]
                week_row.append({"day": day, "events": events})
                day += 1
        calendar_grid.append(week_row)
    
    # Display the calendar
    st.markdown("### Calendar")
    
    # Create a table for the calendar
    cal_html = '<table style="width:100%; border-collapse: collapse;">'
    
    # Add header row with day names
    cal_html += '<tr>'
    for day_name in day_names:
        cal_html += f'<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">{day_name}</th>'
    cal_html += '</tr>'
    
    # Add calendar days
    for week in calendar_grid:
        cal_html += '<tr>'
        for day_cell in week:
            if day_cell["day"] == "":
                # Empty cell
                cal_html += '<td style="border: 1px solid #ddd; padding: 8px; height: 80px;"></td>'
            else:
                # Day cell with events
                cell_style = 'border: 1px solid #ddd; padding: 8px; height: 80px; vertical-align: top;'
                
                # Highlight today
                if day_cell["day"] == today.day and month == today.month and year == today.year:
                    cell_style += 'background-color: #e6f7ff;'
                
                cal_html += f'<td style="{cell_style}">'
                cal_html += f'<div style="font-weight: bold;">{day_cell["day"]}</div>'
                
                # Add events for this day
                for event in day_cell["events"]:
                    cal_html += f'<div style="margin-top: 2px; padding: 2px; background-color: #4CAF50; color: white; border-radius: 3px; font-size: 0.8em;">{event["title"]}</div>'
                
                cal_html += '</td>'
        cal_html += '</tr>'
    
    cal_html += '</table>'
    
    st.markdown(cal_html, unsafe_allow_html=True)

def insights_page():
    st.title("Study Insights")
    
    plans = st.session_state.db.get_plans()
    
    if not plans:
        st.info("You haven't created any study plans yet. Go to 'Create Plan' to get started!")
        return
    
    # Calculate insights
    total_tasks = sum(len(plan['tasks']) for plan in plans)
    completed_tasks = sum(len(st.session_state.db.get_progress(plan['id']).get('completed_tasks', [])) 
                         for plan in plans)
    
    completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    
    # Display overall statistics
    st.subheader("Overall Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Plans", len(plans))
    with col2:
        st.metric("Total Tasks", total_tasks)
    with col3:
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Subject breakdown
    st.subheader("Subject Breakdown")
    
    # Collect subject data
    subject_data = {}
    for plan in plans:
        for task in plan['tasks']:
            if 'subject' in task and task['subject'] != 'Break':
                subject = task['subject']
                if subject not in subject_data:
                    subject_data[subject] = {'total': 0, 'completed': 0}
                
                subject_data[subject]['total'] += 1
                
                # Check if task is completed
                progress = st.session_state.db.get_progress(plan['id'])
                task_index = plan['tasks'].index(task)
                if task_index in progress.get('completed_tasks', []):
                    subject_data[subject]['completed'] += 1
    
    # Create subject breakdown chart
    if subject_data:
        subjects = list(subject_data.keys())
        total_counts = [data['total'] for data in subject_data.values()]
        completed_counts = [data['completed'] for data in subject_data.values()]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=subjects,
            y=total_counts,
            name='Total Tasks',
            marker_color='#2196F3'
        ))
        fig.add_trace(go.Bar(
            x=subjects,
            y=completed_counts,
            name='Completed Tasks',
            marker_color='#4CAF50'
        ))
        
        fig.update_layout(
            title='Tasks by Subject',
            xaxis_title='Subject',
            yaxis_title='Number of Tasks',
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No subject data available yet")
    
    # Time management insights
    st.subheader("Time Management Insights")
    
    # Simulate time management data
    # In a real app, this would be based on actual user behavior
    time_slots = ["Morning (6AM-12PM)", "Afternoon (12PM-5PM)", "Evening (5PM-9PM)", "Night (9PM-6AM)"]
    productivity_scores = [85, 65, 90, 40]  # Example scores
    
    fig = px.bar(
        x=time_slots,
        y=productivity_scores,
        labels={'x': 'Time of Day', 'y': 'Productivity Score'},
        title='Productivity by Time of Day',
        color=productivity_scores,
        color_continuous_scale='Viridis'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommended study times
    st.subheader("Recommended Study Times")
    st.markdown("""
    Based on your study patterns, here are your most productive times:
    
    1. **Evening (5PM-9PM)** - Your highest productivity period
    2. **Morning (6AM-12PM)** - Also very productive
    3. **Afternoon (12PM-5PM)** - Moderate productivity
    
    Consider scheduling your most challenging tasks during your peak productivity periods.
    """)
    
    # Study technique effectiveness
    st.subheader("Study Technique Effectiveness")
    
    techniques = ["Pomodoro", "Spaced Repetition", "Feynman Technique", "Mind Mapping", "Active Recall"]
    effectiveness = [92, 88, 75, 70, 85]  # Example scores
    
    fig = px.pie(
        names=techniques,
        values=effectiveness,
        title='Study Technique Effectiveness',
        hole=0.4
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Personalized recommendations
    st.subheader("Personalized Recommendations")
    st.markdown("""
    Based on your study patterns and performance, here are some personalized recommendations:
    
    1. **Try the Pomodoro Technique** - This seems to work well for your study style
    2. **Schedule difficult subjects in the evening** - Your peak productivity time
    3. **Take regular breaks** - Your completion rate drops after 90 minutes of continuous study
    4. **Use active recall** - This technique has shown good results for your learning style
    """)

# Simulated AI functions
def generate_quick_study_plan(subjects, topics, start_time, end_time, break_duration, 
                            break_frequency, preferred_activities, special_events, 
                            learning_style, priority_settings):
    # In a real app, this would use AI to generate a personalized plan
    # For this example, we'll create a simulated plan
    
    plan_id = f"plan_{datetime.now().timestamp()}"
    
    # Parse priorities
    priorities = {}
    if priority_settings:
        for line in priority_settings.split('\n'):
            if ':' in line:
                item, priority = line.split(':', 1)
                priorities[item.strip()] = priority.strip()
    
    # Create tasks
    tasks = []
    current_time = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)
    
    task_id = 0
    
    # Generate more tasks by creating multiple subtasks for each topic
    for subject in subjects:
        if subject in topics:
            for topic in topics[subject]:
                # Determine priority
                priority = "Medium"  # Default
                for key in priorities:
                    if key == subject or key == f"{subject}/{topic}":
                        priority = priorities[key]
                
                # Create multiple subtasks for each topic (3-4 subtasks)
                subtasks = [
                    f"Read about {topic}",
                    f"Take notes on {topic}",
                    f"Practice problems on {topic}",
                    f"Review {topic} concepts"
                ]
                
                for subtask in subtasks:
                    # Study session
                    session_end = current_time + timedelta(minutes=break_frequency // 2)  # Shorter sessions
                    if session_end > end_datetime:
                        session_end = end_datetime
                    
                    tasks.append({
                        'id': task_id,
                        'subject': subject,
                        'description': subtask,
                        'start_time': current_time.strftime("%H:%M"),
                        'end_time': session_end.strftime("%H:%M"),
                        'type': 'study',
                        'priority': priority
                    })
                    task_id += 1
                    
                    current_time = session_end
                    
                    # Break
                    if current_time < end_datetime:
                        break_end = current_time + timedelta(minutes=break_duration)
                        if break_end > end_datetime:
                            break_end = end_datetime
                        
                        # Choose a random break activity
                        activity = "Take a break"
                        if preferred_activities:
                            activity = f"{random.choice(preferred_activities)}"
                        
                        tasks.append({
                            'id': task_id,
                            'subject': 'Break',
                            'description': activity,
                            'start_time': current_time.strftime("%H:%M"),
                            'end_time': break_end.strftime("%H:%M"),
                            'type': 'break'
                        })
                        task_id += 1
                        
                        current_time = break_end
                    
                    if current_time >= end_datetime:
                        break
                
                if current_time >= end_datetime:
                    break
            
            if current_time >= end_datetime:
                break
    
    # Generate study techniques based on learning style
    study_techniques = generate_study_technique(learning_style)
    
    # Generate resource recommendations
    resources = generate_resource_recommendations(subjects, learning_style)
    
    # Create the plan
    plan = {
        'id': plan_id,
        'type': 'Quick Study',
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'tasks': tasks,
        'study_techniques': study_techniques,
        'resources': resources
    }
    
    return plan

def generate_exam_time_plan(subjects, exam_date, daily_hours, difficulty_dict, 
                          preferred_time, special_events, learning_style, priority_settings):
    # In a real app, this would use AI to generate a personalized plan
    # For this example, we'll create a simulated plan
    
    plan_id = f"plan_{datetime.now().timestamp()}"
    
    # Parse priorities
    priorities = {}
    if priority_settings:
        for line in priority_settings.split('\n'):
            if ':' in line:
                item, priority = line.split(':', 1)
                priorities[item.strip()] = priority.strip()
    
    # Calculate days until exam
    today = datetime.now().date()
    days_until_exam = max(1, (exam_date - today).days)
    
    # Create tasks
    tasks = []
    task_id = 0
    
    # Distribute study time based on difficulty and priority
    total_difficulty = sum(difficulty_dict.get(subject, 3) for subject in subjects)
    
    # Ensure we have at least 7-8 tasks
    min_tasks = 8
    current_task_count = 0
    
    for subject in subjects:
        # Determine priority
        priority = priorities.get(subject, "Medium")
        
        # Determine difficulty
        difficulty = difficulty_dict.get(subject, 3)
        
        # Calculate study days based on difficulty and priority
        priority_multiplier = 1.5 if priority == "High" else (1.0 if priority == "Medium" else 0.7)
        subject_days = max(1, int((difficulty / total_difficulty) * days_until_exam * priority_multiplier))
        
        # For short time gaps, ensure we create enough tasks by adding multiple sessions per day
        sessions_per_day = 1
        if days_until_exam < 4 and len(subjects) < 4:
            sessions_per_day = max(2, 8 // (len(subjects) * days_until_exam))
        
        # Create study sessions for this subject
        for day in range(min(subject_days, days_until_exam)):
            current_date = today + timedelta(days=day)
            
            # Skip weekends if preferred
            if current_date.weekday() >= 5 and "Weekend" not in preferred_time:
                continue
            
            # Create multiple sessions per day if needed
            for session in range(sessions_per_day):
                # Determine study time based on preferences and session number
                if "Morning" in preferred_time and session == 0:
                    start_time = "08:00"
                    end_time = f"{8 + min(daily_hours // sessions_per_day, 3):02d}:00"
                elif "Afternoon" in preferred_time or session == 1:
                    start_time = "13:00"
                    end_time = f"{13 + min(daily_hours // sessions_per_day, 3):02d}:00"
                elif "Evening" in preferred_time or session == 2:
                    start_time = "17:00"
                    end_time = f"{17 + min(daily_hours // sessions_per_day, 3):02d}:00"
                else:  # Night or additional sessions
                    start_time = "20:00"
                    end_time = f"{20 + min(daily_hours // sessions_per_day, 3):02d}:00"
                
                # Create different task descriptions for multiple sessions
                if sessions_per_day == 1:
                    description = f"Study {subject} - Day {day + 1}"
                else:
                    if session == 0:
                        description = f"Read and understand {subject} concepts"
                    elif session == 1:
                        description = f"Practice problems on {subject}"
                    elif session == 2:
                        description = f"Review and summarize {subject}"
                    else:
                        description = f"Additional practice on {subject}"
                
                tasks.append({
                    'id': task_id,
                    'subject': subject,
                    'description': description,
                    'date': current_date.strftime("%Y-%m-%d"),
                    'start_time': start_time,
                    'end_time': end_time,
                    'type': 'study',
                    'priority': priority
                })
                task_id += 1
                current_task_count += 1
            
            # Add review session
            if day > 0 and day % 2 == 0:
                review_date = current_date
                
                tasks.append({
                    'id': task_id,
                    'subject': subject,
                    'description': f"Review {subject} - Quick recap",
                    'date': review_date.strftime("%Y-%m-%d"),
                    'start_time': "21:00",
                    'end_time': "22:00",
                    'type': 'review',
                    'priority': priority
                })
                task_id += 1
                current_task_count += 1
    
    # If we still don't have enough tasks, add some general study sessions
    if current_task_count < min_tasks:
        additional_tasks_needed = min_tasks - current_task_count
        
        # Add general review sessions
        for i in range(additional_tasks_needed):
            day_index = i % max(1, days_until_exam)
            current_date = today + timedelta(days=day_index)
            
            # Alternate between different types of tasks
            if i % 3 == 0:
                description = "Final review of all subjects"
                task_type = "review"
            elif i % 3 == 1:
                description = "Practice mock exam questions"
                task_type = "study"
            else:
                description = "Summarize key concepts"
                task_type = "study"
            
            tasks.append({
                'id': task_id,
                'subject': "All Subjects",
                'description': description,
                'date': current_date.strftime("%Y-%m-%d"),
                'start_time': "19:00",
                'end_time': "20:00",
                'type': task_type,
                'priority': "High"
            })
            task_id += 1
    
    # Generate study techniques based on learning style
    study_techniques = generate_study_technique(learning_style)
    
    # Generate resource recommendations
    resources = generate_resource_recommendations(subjects, learning_style)
    
    # Create the plan
    plan = {
        'id': plan_id,
        'type': 'Exam Time',
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'exam_date': exam_date.strftime("%Y-%m-%d"),
        'tasks': tasks,
        'study_techniques': study_techniques,
        'resources': resources
    }
    
    return plan

def generate_submissions_plan(assignments, due_date_dict, daily_hours, 
                            complexity_dict, preferred_time, special_events, 
                            work_style, priority_settings):
    # In a real app, this would use AI to generate a personalized plan
    # For this example, we'll create a simulated plan
    
    plan_id = f"plan_{datetime.now().timestamp()}"
    
    # Parse priorities
    priorities = {}
    if priority_settings:
        for line in priority_settings.split('\n'):
            if ':' in line:
                item, priority = line.split(':', 1)
                priorities[item.strip()] = priority.strip()
    
    # Create tasks
    tasks = []
    task_id = 0
    
    today = datetime.now().date()
    
    # Sort assignments by due date
    sorted_assignments = sorted(
        [(a, due_date_dict.get(a, today + timedelta(days=7))) for a in assignments],
        key=lambda x: x[1]
    )
    
    # Ensure we have at least 7-8 tasks
    min_tasks = 8
    current_task_count = 0
    
    for assignment, due_date in sorted_assignments:
        # Determine priority
        priority = priorities.get(assignment, "Medium")
        
        # Determine complexity
        complexity = complexity_dict.get(assignment, 3)
        
        # Calculate days available
        days_available = max(1, (due_date - today).days)
        
        # Calculate days needed based on complexity and work style
        if work_style == "Focused Sessions":
            days_needed = max(1, complexity // 2)
        elif work_style == "Spread Out":
            days_needed = complexity
        else:  # Deadline Driven
            days_needed = max(1, complexity // 3)
        
        # Adjust days needed if not enough days available
        days_needed = min(days_needed, days_available)
        
        # For short time gaps, ensure we create enough tasks by adding multiple sessions per day
        sessions_per_day = 1
        if days_available < 4 and len(assignments) < 4:
            sessions_per_day = max(2, 8 // (len(assignments) * days_available))
        
        # Create a list of task descriptions based on the assignment type
        task_descriptions = []
        
        # Generate different task descriptions based on the assignment
        if sessions_per_day == 1:
            if days_needed == 1:
                task_descriptions = [f"Complete {assignment}"]
            else:
                task_descriptions = [
                    f"Start {assignment} - Research and planning",
                    f"Continue {assignment} - Draft initial content",
                    f"Continue {assignment} - Develop main sections",
                    f"Finalize {assignment} - Review and polish",
                    f"Submit {assignment}"
                ]
                # Trim or repeat descriptions to match days_needed
                if len(task_descriptions) > days_needed:
                    task_descriptions = task_descriptions[:days_needed]
                while len(task_descriptions) < days_needed:
                    task_descriptions.append(f"Continue working on {assignment}")
        else:
            # More detailed tasks for multiple sessions per day
            task_descriptions = [
                f"Research for {assignment}",
                f"Create outline for {assignment}",
                f"Draft introduction for {assignment}",
                f"Develop main content for {assignment}",
                f"Create supporting materials for {assignment}",
                f"Review and edit {assignment}",
                f"Finalize and format {assignment}",
                f"Submit {assignment}"
            ]
        
        # Distribute work across days
        day_index = 0
        for task_desc in task_descriptions:
            if day_index >= days_needed and sessions_per_day == 1:
                break
                
            work_date = today + timedelta(days=day_index)
            
            # For multiple sessions per day, create multiple tasks on the same day
            if sessions_per_day > 1:
                session_index = task_descriptions.index(task_desc) % sessions_per_day
                day_index = task_descriptions.index(task_desc) // sessions_per_day
                if day_index >= days_needed:
                    break
                work_date = today + timedelta(days=day_index)
            else:
                session_index = 0
            
            # Determine work time based on preferences and session number
            if "Morning" in preferred_time and session_index == 0:
                start_time = "08:00"
                end_time = f"{8 + min(daily_hours // sessions_per_day, 3):02d}:00"
            elif "Afternoon" in preferred_time or session_index == 1:
                start_time = "13:00"
                end_time = f"{13 + min(daily_hours // sessions_per_day, 3):02d}:00"
            elif "Evening" in preferred_time or session_index == 2:
                start_time = "17:00"
                end_time = f"{17 + min(daily_hours // sessions_per_day, 3):02d}:00"
            else:  # Night or additional sessions
                start_time = "20:00"
                end_time = f"{20 + min(daily_hours // sessions_per_day, 3):02d}:00"
            
            tasks.append({
                'id': task_id,
                'subject': assignment,
                'description': task_desc,
                'date': work_date.strftime("%Y-%m-%d"),
                'start_time': start_time,
                'end_time': end_time,
                'type': 'study',
                'priority': priority
            })
            task_id += 1
            current_task_count += 1
            
            if sessions_per_day == 1:
                day_index += 1
    
    # If we still don't have enough tasks, add some general tasks
    if current_task_count < min_tasks:
        additional_tasks_needed = min_tasks - current_task_count
        
        general_tasks = [
            "Review all assignments for consistency",
            "Check formatting and citations",
            "Prepare submission documents",
            "Create backup copies of all work",
            "Verify submission requirements",
            "Proofread all assignments",
            "Organize supporting materials",
            "Final review before submission"
        ]
        
        for i in range(additional_tasks_needed):
            day_index = i % max(1, days_available)
            current_date = today + timedelta(days=day_index)
            
            task_desc = general_tasks[i % len(general_tasks)]
            
            tasks.append({
                'id': task_id,
                'subject': "All Assignments",
                'description': task_desc,
                'date': current_date.strftime("%Y-%m-%d"),
                'start_time': "19:00",
                'end_time': "20:00",
                'type': 'study',
                'priority': "Medium"
            })
            task_id += 1
    
    # Generate study techniques based on work style
    if work_style == "Focused Sessions":
        technique_style = "Visual"
    elif work_style == "Spread Out":
        technique_style = "Mixed"
    else:  # Deadline Driven
        technique_style = "Reading"
    
    study_techniques = generate_study_technique(technique_style)
    
    # Generate resource recommendations
    resources = generate_resource_recommendations(assignments, technique_style)
    
    # Create the plan
    plan = {
        'id': plan_id,
        'type': 'Submissions',
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'tasks': tasks,
        'study_techniques': study_techniques,
        'resources': resources
    }
    
    return plan

# Run the app
if __name__ == "__main__":
    main()
