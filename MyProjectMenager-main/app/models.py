# models.py
from app import db
from sqlalchemy.orm import relationship

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

    # Define the many-to-many relationship with itself
    dependencies = db.relationship(
        'Task',
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.dependent_task_id,
        backref=db.backref('dependent_tasks', lazy='dynamic'),
        lazy='dynamic'
    )