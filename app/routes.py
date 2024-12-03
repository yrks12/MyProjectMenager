from flask import Flask, render_template, request, redirect, url_for, Blueprint, flash, session
from app.models import Project, Task, task_dependencies
from app import db
from datetime import datetime
from functools import wraps
import os

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

# Use the decorator on routes that require login
@project_routes.route('/some_protected_route')
@login_required
def some_protected_route():
    return render_template('protected.html')