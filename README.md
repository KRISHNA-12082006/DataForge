# DataForge

#### Video Demo: 
### Description:

## Overview

DataForge is a web application designed to empower users in creating, managing, and sharing custom data tables. It utilizes Flask and SQLite, offering a robust platform for both personal and collaborative data management. Whether organizing personal datasets or facilitating team projects, DataForge provides essential tools for handling structured data effectively.

## Features

### User Authentication

DataForge includes a secure user authentication system to ensure that only authorized users can access their data. This system integrates password hashing for security and session management to maintain user sessions securely.

### Custom Table Creation

Users can create custom tables tailored to their specific needs. The application allows defining table structures dynamically, enabling users to add fields and specify data types during table creation. This flexibility is crucial for diverse data management scenarios, from simple lists to complex relational datasets.

### Data Management

DataForge supports comprehensive data management operations:
- **Add**: Users can add new data entries to their custom tables, inputting values for each defined field.
- **View**: Provides functionalities to view all records within a selected table, with options for pagination and sorting based on columns.
- **Edit**: Allows users to modify existing data entries directly within the application, ensuring data accuracy and relevance.
- **Delete**: Enables the removal of unwanted data entries or entire tables, offering robust data cleanup capabilities.

### Responsive Design

The application features a responsive design powered by Bootstrap, ensuring seamless usability across various devices, including desktops, tablets, and smartphones. This responsiveness enhances accessibility, allowing users to manage their data effectively regardless of their device preference.

## File Structure

### Overview

DataForge's file structure is organized to maintain clarity and separation of concerns, adhering to best practices for Flask applications.

1. **static/**: Contains static assets such as images (`abstract_background.jpg`), icons (`dataforge.ico`), and stylesheets (`style.css`) used for customizing the application's appearance and user interface.

2. **templates/**: This directory houses HTML templates that employ Flask's Jinja templating engine. Each template corresponds to different functionalities within the application, ensuring modular and maintainable frontend development.

3. **dataforge.db**: SQLite database file that serves as the backend storage for user authentication details and all custom tables created by users. SQLite was chosen for its lightweight nature and suitability for small to medium-scale web applications without requiring a separate database server.

4. **helpers.py**: This file contains utility functions essential for various tasks within the application. Functions like `login_required`, `get_nm_pswd`, `red_err`, `red_scs`, and `quote_identifier` assist in user authentication, error handling, and database operations.

5. **app.py**: The core of DataForge's backend functionality. This file initializes the Flask application (`app`) and configures essential components such as session management (`Session(app)`) and database connectivity (`db = SQL("sqlite:///dataforge.db")`). It defines numerous route decorators (`@app.route`) that handle HTTP requests and implement the application's logic for user authentication, table management, and data operations.

### Detailed Description of app.py

#### Initialization and Configuration

The `app.py` file starts by importing necessary modules and libraries:
```python
from cs50 import SQL
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_session import Session
from helpers import login_required, get_nm_pswd, red_err, red_scs, quote_identifier
from werkzeug.security import check_password_hash, generate_password_hash
```

#### Flask Application Setup

```python
app = Flask(__name__)
app.secret_key = "AJdnn1#Lu39vo@Kcfo23eok'/B>lt"
```
- `app`: The Flask application instance is created, and a secret key is set for session management and security purposes.

#### Session Configuration

```python
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
```
- Session management is configured to use filesystem storage (`"filesystem"`) and ensures sessions are not permanent.

#### Database Initialization

```python
db = SQL("sqlite:///dataforge.db")
```
- The SQLite database (`dataforge.db`) is initialized using the `cs50` library's `SQL` class for database operations throughout the application.

#### Route Definitions

The `app.py` file defines numerous routes using the `@app.route` decorator, each handling specific functionalities within DataForge:

- **`@app.after_request`**: Ensures responses are not cached to prevent data inconsistencies.
- **`@app.route("/")`**: Renders the default page of the web application.
- **`@app.route("/login", methods=["GET", "POST"])`**: Manages user login functionality, verifying credentials and managing user sessions securely.
- **`@app.route("/logout")`**: Logs out the current user by clearing session data.
- **`@app.route("/register", methods=["GET", "POST"])`**: Handles user registration, ensuring unique usernames and securely storing hashed passwords.
- **`@app.route("/home")`**: Displays the user's homepage, listing all custom tables created by the user and providing options for managing data within these tables.
- **`@app.route("/verify", methods=["GET", "POST"])`**: Verifies user credentials for sensitive operations like profile updates.
- **`@app.route("/update", methods=["GET", "POST"])`**: Allows users to update their profile information, including username and password.
- **`@app.route("/add_table", methods=["GET", "POST"])`**: Enables users to create new custom tables with specified column names.
- **`@app.route("/user_tables", methods=["GET", "POST"])`**: Lists all tables created by the logged-in user.
- **`@app.route("/show_table/<table_name>", methods=["GET", "POST"])`**: Displays the content of a specific table, allowing users to view, add, edit, and delete rows.
- **`@app.route("/delete_table/<table_name>", methods=["GET", "POST"])`**: Deletes a specified table and its associated data.
- **`@app.route("/edit_table/<table_name>", methods=["GET", "POST"])`**: Allows users to edit the structure of a specified table, including adding new rows or modifying existing ones.
- **`@app.route("/delete_row/<string:table_name>/<string:key>/<key_value>", methods=["GET"])`**: Deletes a specific row from a table based on the provided key and key value.
- **`@app.route("/edit_row/<string:table_name>/<string:key>/<key_value>", methods=["GET", "POST"])`**: Enables users to edit a specific row in a table based on the provided key and key value.

#### Error Handling and Helper Functions

The `app.py` file also utilizes various helper functions imported from `helpers.py`, such as `login_required`, `get_nm_pswd`, `red_err`, `red_scs`, and `quote_identifier`. These functions aid in handling user authentication, error messages, and database operations throughout the application.

#### Main Execution

```python
if __name__ == '__main__':
    app.run()
```
- Starts the Flask application if executed directly.

## Secure Table Management and User Access

This Flask web application implements secure table management with user access controls. Users can create tables with specified columns, ensuring data is organized and retrievable. To prevent unauthorized access, the application checks a user's session against a database of registered users. This ensures only authorized users can view, edit, or delete their own tables. Additionally, the application restricts the use of special characters in table and column names, safeguarding against SQL injection attacks where malicious code could be inserted through user input.

## Robust Error Handling and Unauthorized Access Attempts

The application incorporates robust error handling to provide informative messages to users in case of issues. Error messages pinpoint problems like providing an incorrect password during login or trying to edit a table that doesn't belong to the user. This helps users identify and rectify mistakes. Furthermore, attempts to access unauthorized data are blocked. If a user tries to view or edit a table they don't have permission for, the application throws an error message and denies access. This enforces data security and prevents unauthorized modifications.

## Additional Features for Enhanced Functionality

The application leverages Jinja2 templating for a clean separation of concerns between code and presentation. This allows for easier development and maintenance. Additionally, the `login_required` decorator restricts access to specific routes for logged-in users only, ensuring certain functionalities are used appropriately. Helper functions streamline common tasks such as retrieving user credentials, generating secure password hashes, and displaying flash messages to the user. These features contribute to a more user-friendly and secure web application experience.

## Technologies Used

DataForge leverages the following technologies and frameworks:
- **Python 3.x**: Core programming language for backend logic.
- **Flask**: Lightweight web framework for building web applications.
- **SQLite**: Serverless SQL database engine for local data storage.
- **HTML/CSS**: Standard web technologies for frontend structure and styling.
- **Jinja 2**: Templating engine integrated with Flask for dynamic content generation.
- **JavaScript**: Enhances frontend interactivity.
- **Bootstrap**: CSS framework for responsive design and UI components.

## Design Choices

### Flask and SQLite

Flask was chosen for its simplicity and flexibility in web application development, allowing rapid prototyping and easy integration with other Python libraries. SQLite was selected as the database engine due to its lightweight nature, file-based storage, and seamless integration with Python applications without requiring a separate server setup.

### Responsive Design with Bootstrap

Bootstrap was utilized to ensure a responsive and mobile-friendly user interface, providing a consistent user experience across various devices and screen sizes. This design choice enhances accessibility and usability, catering to a broader audience of users accessing DataForge from different devices.

### Jinja Templating

Jinja templating was instrumental in separating application logic from presentation, promoting code maintainability and reusability by modularizing HTML templates. Templating allowed dynamic content generation based on user interactions and backend data, enhancing the application's flexibility and scalability.

