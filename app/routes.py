from flask import Flask, render_template, request, redirect, url_for, Blueprint, flash, session, jsonify
from app.models import Project, Task, task_dependencies, TimeEntry
from app import db
from datetime import datetime, timedelta
from functools import wraps
import os
import logging
from app import app

project_routes = Blueprint('project_routes', __name__)

def priority_order(priority):
    return {
        'High': 3,
        'Medium': 2,
        'Low': 1
    }.get(priority, 0)

def status_order(status):
    return {
        'Completed': 3,
        'In Progress': 2,
        'Pending': 1
    }.get(status, 0)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to log in first!', 'warning')
            return redirect(url_for('project_routes.login'))
        return f(*args, **kwargs)
    return decorated_function

@project_routes.route('/')
@login_required
def index():
    projects = Project.query.all()
    for project in projects:
        total_tasks = len(project.tasks)
        completed_tasks = sum(1 for task in project.tasks if task.status == 'Completed')
        project.progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Sort tasks by custom status and priority order, then by deadline
        project.top_tasks = sorted(
            project.tasks,
            key=lambda t: (
                status_order(t.status),
                priority_order(t.priority),
                t.deadline if isinstance(t.deadline, datetime) else (
                    datetime.strptime(t.deadline, '%Y-%m-%d') if isinstance(t.deadline, str) and t.deadline else datetime.max
                )
            )
        )[:4]  # Get top 4 tasks sorted by status, priority, and deadline
    return render_template('index.html', projects=projects)

@project_routes.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        deadline_str = request.form['deadline']
        status = request.form['status']
        ai_notes = request.form['ai_notes']
        tags = request.form['tags']
        
        # Validate input
        if not name:
            flash('Project name is required!', 'error')
            return redirect(url_for('project_routes.create_project'))

        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
        
        project = Project(name=name, description=description, deadline=deadline, status=status, ai_notes=ai_notes, tags=tags)
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('project_routes.index'))
    return render_template('create_project.html')

@project_routes.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        project.name = request.form['name']
        project.description = request.form['description']
        
        # Convert the deadline string to a date object
        deadline_str = request.form['deadline']
        project.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
        
        project.status = request.form['status']
        project.ai_notes = request.form['ai_notes']
        project.tags = request.form['tags']
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('project_routes.index'))
    return render_template('edit_project.html', project=project)


@project_routes.route('/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)  # Ensure the project exists
        # Delete associated tasks
        for task in project.tasks:
            db.session.delete(task)  # Delete each task
        db.session.delete(project)  # Delete the project
        db.session.commit()  # Commit changes to the database
        flash('Project deleted successfully!', 'success')  # Confirmation message
    except Exception as e:
        db.session.rollback()  # Rollback in case of any errors
        flash(f'Error deleting project: {str(e)}', 'danger')  # Error message
    return redirect(url_for('project_routes.index'))  # Redirect to the index page

@project_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials
        if username == os.getenv('username') and password == os.getenv('password'):
            session['username'] = username  # Store username in session
            flash('Login successful!', 'success')
            return redirect(url_for('project_routes.index'))  # Redirect to index after login
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')  # Render login template

@project_routes.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    flash('You have been logged out successfully!', 'success')  # Flash message for logout
    return redirect(url_for('project_routes.login'))  # Redirect to login page

task_routes = Blueprint('task_routes', __name__)

@task_routes.route('/tasks/<int:project_id>', methods=['GET'])
@login_required
def tasks(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project_id).all()
    return render_template('tasks.html', project=project, tasks=tasks)

@task_routes.route('/create_task/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_task(project_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        deadline_str = request.form['deadline']
        status = request.form['status']
        priority = request.form['priority']
        task_type = request.form['task_type']
        
        # Validate input
        if not name:
            flash('Task name is required!', 'error')
            return redirect(url_for('task_routes.create_task', project_id=project_id))

        # Validate and parse deadline
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
        except ValueError:
            flash('Invalid deadline format! Use YYYY-MM-DD.', 'error')
            return redirect(url_for('task_routes.create_task', project_id=project_id))
        
        task = Task(name=name, description=description, deadline=deadline, status=status, priority=priority, task_type=task_type, project_id=project_id)
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('task_routes.tasks', project_id=project_id))
    return render_template('create_task.html', project_id=project_id)

    
@task_routes.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        task.name = request.form['name']
        task.description = request.form['description']

        # Validate and parse deadline
        deadline_str = request.form['deadline']
        try:
            task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else None
        except ValueError:
            flash('Invalid deadline format! Use YYYY-MM-DD.', 'error')
            return redirect(url_for('task_routes.edit_task', task_id=task_id))

        task.status = request.form['status']
        task.priority = request.form['priority']
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('task_routes.tasks', project_id=task.project_id))
    return render_template('edit_task.html', task=task)

@task_routes.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('task_routes.tasks', project_id=task.project_id))

@project_routes.route('/start_timer/<int:task_id>', methods=['POST'])
@login_required
def start_timer(task_id):
    task = Task.query.get_or_404(task_id)
    if task.start_timer():
        return jsonify({
            'status': 'success',
            'message': 'Timer started',
            'timer_running': True,
            'start_time': task.timer_start.isoformat()
        })
    return jsonify({'status': 'error', 'message': 'Timer already running'}), 400

@project_routes.route('/stop_timer/<int:task_id>', methods=['POST'])
@login_required
def stop_timer(task_id):
    task = Task.query.get_or_404(task_id)
    elapsed = task.stop_timer()
    if elapsed:
        return jsonify({
            'status': 'success',
            'message': 'Timer stopped',
            'timer_running': False,
            'elapsed_time': elapsed,
            'formatted_time': task.get_formatted_time_spent()
        })
    return jsonify({'status': 'error', 'message': 'Timer not running'}), 400

@task_routes.route('/add_manual_time/<int:task_id>', methods=['POST'])
@login_required
def add_manual_time(task_id):
    """Add manual time entry to a task"""
    task = Task.query.get_or_404(task_id)
    hours = int(request.form.get('hours', 0))
    minutes = int(request.form.get('minutes', 0))
    notes = request.form.get('notes', '')
    
    duration = (hours * 3600) + (minutes * 60)
    if duration > 0:
        time_entry = TimeEntry(
            task_id=task_id,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration=duration,
            manual_entry=True,
            notes=notes
        )
        task.time_spent += duration
        db.session.add(time_entry)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Time added successfully',
            'formattedTimeSpent': task.get_formatted_time_spent()
        })
    return jsonify({'status': 'error', 'message': 'Invalid time entry'}), 400

# Use the decorator on routes that require login
@project_routes.route('/some_protected_route')
@login_required
def some_protected_route():
    return render_template('protected.html')

@project_routes.route('/dashboard')
@login_required
def dashboard():
    # Get all tasks across all projects
    tasks = Task.query.join(Project).all()
    
    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == 'Completed')
    total_hours = sum((task.time_spent or 0) for task in tasks) // 3600
    
    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'total_hours': total_hours
    }
    
    # Group tasks by priority
    tasks_by_priority = {
        'High': [t for t in tasks if t.priority == 'High'][:5],
        'Medium': [t for t in tasks if t.priority == 'Medium'][:5],
        'Low': [t for t in tasks if t.priority == 'Low'][:5]
    }
    
    # Pass the current date to the template (already a date object)
    current_date = datetime.now().date()
    
    return render_template('dashboard.html', stats=stats, tasks_by_priority=tasks_by_priority, now=current_date)

@project_routes.route('/api/task/<int:task_id>/timer', methods=['POST'])
@login_required
def toggle_timer(task_id):
    """API endpoint to start/stop task timer"""
    task = Task.query.get_or_404(task_id)
    action = request.json.get('action')
    
    try:
        if action == 'start':
            if task.start_timer():
                return jsonify({
                    'status': 'success',
                    'message': 'Timer started',
                    'isRunning': True,
                    'startTime': task.timer_start.isoformat(),
                    'formattedTimeSpent': task.get_formatted_time_spent()
                })
            return jsonify({'status': 'error', 'message': 'Timer already running'}), 400
            
        elif action == 'stop':
            elapsed = task.stop_timer()
            if elapsed:
                return jsonify({
                    'status': 'success',
                    'message': 'Timer stopped',
                    'isRunning': False,
                    'formattedTimeSpent': task.get_formatted_time_spent(),
                    'elapsedTime': elapsed
                })
            return jsonify({'status': 'error', 'message': 'Timer not running'}), 400
            
        else:
            return jsonify({'status': 'error', 'message': 'Invalid action'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error processing timer: {str(e)}'
        }), 500