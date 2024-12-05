# models.py
from app import db
from sqlalchemy.orm import relationship
from datetime import datetime

# Define the relationship between tasks
# Ensure that this table is defined only once and reused where needed
task_dependencies = db.Table(
    'task_dependencies',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('dependent_task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    extend_existing=True  # Allows redefinition of the table if it already exists
)

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default='Active')
    ai_notes = db.Column(db.Text)
    tags = db.Column(db.String(100))
    progress = db.Column(db.Integer, default=0)

    # Relationship to access tasks
    tasks = relationship('Task', backref='project', cascade='all, delete-orphan')

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default='Pending')
    priority = db.Column(db.String(20), default='Low')
    task_type = db.Column(db.String(50))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    time_spent = db.Column(db.Integer, default=0)  # Store time in seconds
    timer_start = db.Column(db.DateTime, nullable=True)  # Store timer start time
    time_entries = db.relationship('TimeEntry', backref='task', lazy='dynamic', cascade='all, delete-orphan')

    # Add the get_deadline_status method
    def get_deadline_status(self):
        if not self.deadline:
            return 'no-deadline'
        
        from datetime import datetime
        today = datetime.now().date()
        
        if self.deadline < today:
            return 'overdue'
        elif self.deadline == today:
            return 'due-today'
        elif (self.deadline - today).days <= 3:
            return 'due-soon'
        else:
            return 'upcoming'

    # Define the many-to-many relationship with itself
    dependencies = db.relationship(
        'Task',
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.dependent_task_id,
        backref=db.backref('dependent_tasks', lazy='dynamic'),
        lazy='dynamic'
    )

    def is_timer_running(self):
        """Check if the timer is currently running"""
        return self.timer_start is not None

    def get_formatted_time_spent(self):
        """Format the total time spent in a human-readable format"""
        if self.time_spent is None:
            return "0m"
            
        hours = self.time_spent // 3600
        minutes = (self.time_spent % 3600) // 60
        seconds = self.time_spent % 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{seconds}s"

    def get_current_timer_duration(self):
        """Get the duration of the current timer session if running"""
        if self.timer_start:
            now = datetime.utcnow()
            return int((now - self.timer_start).total_seconds())
        return 0

    def get_total_time_spent(self):
        """Get total time spent including current timer session"""
        total = self.time_spent or 0
        if self.timer_start:
            total += self.get_current_timer_duration()
        return total

    def start_timer(self):
        """Start the task timer"""
        if not self.timer_start:
            self.timer_start = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def stop_timer(self):
        """Stop the task timer and calculate elapsed time"""
        if self.timer_start:
            now = datetime.utcnow()
            elapsed = int((now - self.timer_start).total_seconds())
            self.time_spent = (self.time_spent or 0) + elapsed
            
            # Create a time entry record
            time_entry = TimeEntry(
                task_id=self.id,
                start_time=self.timer_start,
                end_time=now,
                duration=elapsed
            )
            db.session.add(time_entry)
            
            self.timer_start = None
            db.session.commit()
            return elapsed
        return 0

    def __repr__(self):
        return f'<Task {self.name}>'

class TimeEntry(db.Model):
    __tablename__ = 'time_entry'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer)  # Duration in seconds
    manual_entry = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)