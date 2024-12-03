```# MyProjectManager

MyProjectManager is a web-based project management application built with Flask. It allows users to create, edit, and manage projects and tasks efficiently.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features
- User authentication (login/logout)
- Create, edit, and delete projects
- Create, edit, and delete tasks within projects
- View project progress and task details
- Flash messages for user feedback

## Technologies Used
- Flask: A lightweight WSGI web application framework.
- Flask-SQLAlchemy: An ORM for managing database interactions.
- Flask-Migrate: A tool for handling SQLAlchemy database migrations.
- Jinja2: A templating engine for rendering HTML.
- HTML/CSS: For front-end design.
- JavaScript: For client-side interactivity.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yrks12/MyProjectManager.git
   cd MyProjectManager
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   SQLALCHEMY_DATABASE_URI=sqlite:///app.db
   username=your_username
   password=your_password
   SECRET_KEY=your_secret_key
   ```

## Usage
1. Run the application using Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```
   Here, `-w 4` specifies the number of worker processes, and `-b 0.0.0.0:8000` binds the server to all interfaces on port 8000.

2. Open your web browser and go to `http://127.0.0.1:8000`.

3. You can log in with the credentials specified in the `.env` file.

4. Start managing your projects and tasks!

## Deployment
To deploy the application, you can use a platform like Heroku or any other cloud service that supports Flask applications. Here’s a brief guide for deploying on Heroku:

1. Install the Heroku CLI and log in:
   ```bash
   heroku login
   ```

2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```

3. Set the environment variables on Heroku:
   ```bash
   heroku config:set SQLALCHEMY_DATABASE_URI=your_database_uri
   heroku config:set username=your_username
   heroku config:set password=your_password
   heroku config:set SECRET_KEY=your_secret_key
   ```

4. Push your code to Heroku:
   ```bash
   git push heroku main
   ```

5. Open your app in the browser:
   ```bash
   heroku open
   ```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.