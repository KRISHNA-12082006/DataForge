from cs50 import SQL
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_session import Session
from helpers import login_required, get_nm_pswd, red_err, red_scs, quote_identifier
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "AJdnn1#Lu39vo@Kcfo23eok'/B>lt"

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///dataforge.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    # Default page of webapp
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()                                     # Forget any user_id

    if request.method == "POST":                        # User reached route via POST

        try:
            username, password = get_nm_pswd()          # Retrieve form
            if not username:
                return red_err("login", "No Username Provided")
            elif not password:
                return red_err("login", "Password Required")

            try:
                rows = db.execute(                      # Query database for user
                    "SELECT * FROM users WHERE username = ?", username
                )
            except:
                red_err("login", "User Not Found")

            if len(rows) == 0:                          # Ensure user exists
                return red_err("login", "You Are Not Registered")

            if not check_password_hash(                 # Verify Password
                rows[0]["hash"], password
            ):
                return red_err("login", "Wrong Password")

            else:
                session["user_id"] = rows[0]["id"]      # Remember which user has logged in
                return red_scs("home", "Logged in successfully!")

        except Exception as e:
            return red_err("errored", None, f"Something Went Wrong:{str()}")

    # User reached route via GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()                                     # Forget any user_id
    return redirect("/")                                # Redirect user to default page


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()                                     # Forget any existing user

    if request.method == "POST":                        # User reached route via POST

        username, password = get_nm_pswd()              # Retrieve form
        if not username:
            return red_err("register", "No Username Provided")
        elif not password:
            return red_err("register", "Password Required")

        rows = db.execute(                              # Query database for username
            "SELECT username FROM users WHERE username = ?", username
        )

        """Verify Confirmation"""
        if len(rows) != 0:
            return red_err("register", "Username Alreday Taken")

        elif not request.form.get("confirmation"):
            return red_err("register", "Confirm Password")

        elif password != request.form.get("confirmation"):
            return red_err("register", "Passwords Don't Match")

        # Add User into the Database
        db.execute("BEGIN TRANSACTION")
        roll = True
        try:
            db.execute(                                 # Insert user into the database
                "INSERT INTO users (username, hash, status) VALUES (?, ?, 1)",
                username, generate_password_hash(password)
            )

            user = db.execute(                          # Query database for user
                "SELECT id FROM users WHERE username = ?", username
            )

            # Create tables for storing tables of the user
            user_id = user[0]["id"]
            user_tables = f"tables_{user_id}"

            # Construct the SQL query to create recoed of tables
            create_tables_sql = f"CREATE TABLE {user_tables} (tables TEXT)"
            db.execute(create_tables_sql)
            db.execute("COMMIT")
            roll = False

        except ValueError:
            try:
                if roll:
                    db.execute("ROLLBACK")              # Roll back transaction if error occurs
            except:
                pass
            return red_err("errored", "Either Username or Password or both not valid")

        return red_scs("login", "Registered Successfully ~ Log In")

    else:
        return render_template("register.html")


@app.route("/home")
@login_required
def home():
    try:
        # Load information about user for actions to be performed
        user_id = session["user_id"]
        user_tables = f"tables_{user_id}"
        list_table_sql = f"SELECT * FROM {user_tables}"
        tables = db.execute(list_table_sql)

        # List tables created by user to show from 'tables' dict
        show_tables = []
        for table in tables:
            show_tables.append(table["tables"])

        return render_template("home.html", show_tables=show_tables)
    except Exception as e:
        return red_err("errored", None, f"Something Went Wrong: {str(e)}")


@app.route("/verify", methods=["GET", "POST"])
@login_required
def verify():

    try:
        if bool(session["verified"]):                   # If Already Verified
            return red_err("update")
    except:
        pass

    if request.method == "POST":

        username, password = get_nm_pswd()              # Retrieve form
        if not username:
            return red_err("verify", "No Username Provided")
        if not password:
            return red_err("verify", "Password Required")

        # Start verification
        rows = db.execute(
            "SELECT username, hash FROM users WHERE id = ?", session["user_id"]
        )

        if (rows[0]["username"] != username):
            return red_err("verify", "Wrong Username")

        elif not check_password_hash(rows[0]["hash"], password):
            return red_err("verify", "Wrong Password")

        session["verified"] = True                      # Verified Successfully
        return red_scs("update", "User Verification Successful")

    else:
        return render_template("verify.html")


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Update Details"""
    if request.method == "POST" and bool(session["verified"]):

        # Retrieve form
        user_id = session["user_id"]
        name = request.form.get("username")
        password = request.form.get("password")

        # Check for updates
        if not name and not password:
            flash("No Changes Made", "info")
            return redirect(url_for("home"))

        db.execute("BEGIN TRANSACTION")
        roll = True
        try:
            if name:                                    # If username changed
                db.execute(
                    "UPDATE users SET username = ? WHERE id = ?", name, user_id
                )
            if password:                                # If password changed
                db.execute(
                    "UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(
                        password), user_id
                )

            db.execute("COMMIT")
            roll = False
            return red_scs("home", "Profile Updated Successfully!")

        except Exception as e:
            try:
                if roll:
                    print("roll")
                    db.execute("ROLLBACK")
            except:
                pass
            return red_err("errored", "Profile update failed", f"Error updating profile: {str(e)}")

    else:
        try:
            bool(session["verified"])                   # Check if user has completed verification
        except:
            return redirect("/verify")

        username = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )
        username = username[0]["username"]

        return render_template("update.html", username=username)


@app.route("/add_table", methods=["GET", "POST"])
@login_required
def add_table():
    if request.method == "POST":
        try:
            # Retrieve form
            table_name = request.form.get('table_name')
            columns = request.form.getlist('columns[]')
            if not table_name or not columns:
                flash("No New Table Created", "info")
                return rederict(url_for("home"))

            """Check for characters that can cause syntax error in sql queries"""
            if ' ' in table_name or '.' in table_name or '\"' in table_name:
                return red_err("add_table", f'No spaces or dots( . ) or quotes( \', \" ) allowed ~ use _ or * instead')
            if "\'" in table_name:
                return red_err("add_table", f'No spaces or dots( . ) or quotes( \', \" ) allowed ~ use _ or * instead')

            for column in columns:
                if ' ' in column or '.' in column or '\"' in column:
                    return red_err("add_table", f'No spaces or dots( . ) or quotes( \', \" ) allowed ~ use _ or * instead')
                if "\'" in column:
                    return red_err("add_table", f'No spaces or dots( . ) or quotes( \', \" ) allowed ~ use _ or * instead')

            # Information for actions
            user_id = session["user_id"]
            user_tables = f"tables_{user_id}"
            table_name = str(f"{table_name}_{user_id}")

            # Quote the table_name if necessary
            table_name = quote_identifier(table_name)

            # Quote each column name if necessary
            quoted_columns = [quote_identifier(column) for column in columns]

            # Str to be passed in sql query
            columns_str = ', '.join([f'{column} TEXT' for column in quoted_columns])

            # Sql queries
            create_table_sql = f"CREATE TABLE {table_name} ({columns_str})"
            add_table_sql = f"INSERT INTO {user_tables} (tables) VALUES ('{table_name}')"

            db.execute("BEGIN TRANSACTION")
            roll = True
            try:
                db.execute(create_table_sql)
                db.execute(add_table_sql)
                db.execute("COMMIT")
                roll = False
                return red_scs("user_tables", f"Table '{table_name}' created successfully with columns: {columns_str}")

            except Exception as e:
                try:
                    if roll:
                        print("roll")
                        db.execute("ROLLBACK")
                except:
                    pass
                return red_err("add_table", f"Error creating table: {str(e)}")

        except Exception as e:
            return red_err("errored", None, f"Something Went Wrong: {str(e)}")

    else:
        return render_template("add_table.html")


@app.route("/user_tables", methods=["GET", "POST"])
@login_required
def user_tables():
    try:
        """Show Tables"""
        user_id = session["user_id"]
        user_tables = f"tables_{user_id}"
        list_table_sql = f"SELECT * FROM {user_tables}"
        tables = db.execute(list_table_sql)

        # Construct list of tables from 'tables' dict
        show_tables = []
        for table in tables:
            show_tables.append(table["tables"])
        return render_template("user_tables.html", show_tables=show_tables)

    except Exception as e:
        return red_err("errored", None, f"Something Went Wrong: {str(e)}")


@app.route("/show_table/<table_name>", methods=["GET", "POST"])
def show_table(table_name):

    # Check if user has access to the requested table
    try:
        user_id = session["user_id"]
        user_tables = f"tables_{user_id}"
        list_table_sql = f"SELECT * FROM {user_tables}"
        tables = db.execute(list_table_sql)

        # Construct list of tables from 'tables' dict
        show_tables = []
        for table in tables:
            show_tables.append(table["tables"])

        if table_name not in show_tables:
            return red_err("user_tables", "Access denied")
    except:
        return red_err("user_tables", "Access denied")

    if request.method == "POST":
        try:
            # Load column names
            columns_sql = f"SELECT * FROM pragma_table_info('{table_name}')"
            columns = db.execute(columns_sql)
            # Load the rows
            rows_sql = f"SELECT * FROM {table_name}"
            rows = db.execute(rows_sql)

            """Add row functionality"""
            values = {}
            for column in columns:
                column_name = column['name']  # Access column name from dictionary
                values[column_name] = request.form.get(column_name)

            # Construct SQL INSERT query    ###ChatGPT
            columns_str = ', '.join(values.keys())
            for key in values.keys():
                if not values[key]:
                    flash(f"No value provided for {key}", "danger")
                    return redirect(url_for("edit_table", table_name=table_name))
            values_str = ', '.join(f":{key}" for key in values.keys())
            edit_table_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"

            db.execute(edit_table_sql, **values)

            flash("Row added successfully", "success")
            page = f"/show_table/{table_name}"
            return redirect(page)

        except Exception as e:
            return red_err("errored", None, f"Something Went Wrong: {str(e)}")
    else:
        try:
            # Load column names
            columns_sql = f"SELECT * FROM pragma_table_info('{table_name}')"
            columns = db.execute(columns_sql)
            # Load the rows
            rows_sql = f"SELECT * FROM {table_name}"
            rows = db.execute(rows_sql)

            return render_template("show_table.html", table_name=table_name, columns=columns, rows=rows)

        except Exception as e:
            return red_err("errored", None, f"Something Went Wrong: {str(e)}")


@app.route("/delete_table/<table_name>", methods=["GET", "POST"])
@login_required
def delete_table(table_name):

    # Check if user has access to the requested table
    try:
        user_id = session["user_id"]
        user_tables = f"tables_{user_id}"
        list_table_sql = f"SELECT * FROM {user_tables}"
        tables = db.execute(list_table_sql)

        # Construct list of tables from 'tables' dict
        show_tables = []
        for table in tables:
            show_tables.append(table["tables"])

        if table_name not in show_tables:
            return red_err("user_tables", "Access denied")
    except:
        return red_err("user_tables", "Access denied")

    try:
        user_id = session["user_id"]
        user_tables = f"tables_{user_id}"

        delete_table_sql = f"DROP TABLE {table_name}"
        remove_table_sql = f"DELETE FROM {user_tables} WHERE tables = '{table_name}'"

        db.execute(delete_table_sql)
        db.execute(remove_table_sql)

        flash("Table deleted successfully", "info")
        return redirect(url_for("user_tables"))

    except Exception as e:
        return red_err("errored", None, f"Something Went Wrong: {str(e)}")


@app.route("/edit_table/<table_name>", methods=["GET", "POST"])
@login_required
def edit_table(table_name):

    # Check if user has access to the requested table
    try:
        user_id = session["user_id"]
        user_tables = f"tables_{user_id}"
        list_table_sql = f"SELECT * FROM {user_tables}"
        tables = db.execute(list_table_sql)

        # Construct list of tables from 'tables' dict
        show_tables = []
        for table in tables:
            show_tables.append(table["tables"])

        if table_name not in show_tables:
            return red_err("user_tables", "Access denied")
    except:
        return red_err("user_tables", "Access denied")

    if request.method == "POST":

        try:
            """Add row functionality"""
            columns_sql = f"SELECT * FROM pragma_table_info('{table_name}')"
            columns = db.execute(columns_sql)

            values = {}
            for column in columns:
                column_name = column['name']  # Access column name from dictionary
                values[column_name] = request.form.get(column_name)

            # Construct SQL INSERT query    ###ChatGPT
            columns_str = ', '.join(values.keys())
            for key in values.keys():
                if not values[key]:
                    flash(f"No value provided for {key}", "danger")
                    return redirect(url_for("edit_table", table_name=table_name))
            values_str = ', '.join(f":{key}" for key in values.keys())
            edit_table_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
            db.execute(edit_table_sql, **values)

            flash("Row added successfully", "success")
            return redirect(url_for('edit_table', table_name=table_name))

        except Exception as e:
            return red_err("errored", None, f"Something Went Wrong: {str(e)}")

    else:
        try:
            # Load column names
            columns_sql = f"SELECT * FROM pragma_table_info('{table_name}')"
            columns = db.execute(columns_sql)
            # Load the rows
            rows_sql = f"SELECT * FROM {table_name}"
            rows = db.execute(rows_sql)
            return render_template("edit_table.html", table_name=table_name, columns=columns, rows=rows)

        except Exception as e:
            return red_err("errored", None, f"Something Went Wrong: {str(e)}")


@app.route('/delete_row/<string:table_name>/<string:key>/<key_value>', methods=['GET'])
@login_required
def delete_row(table_name, key, key_value):

    # Check if user has access to the requested table
    try:
        user_id = session["user_id"]
        user_tables = f"tables_{user_id}"
        list_table_sql = f"SELECT * FROM {user_tables}"
        tables = db.execute(list_table_sql)

        # Construct list of tables from 'tables' dict
        show_tables = []
        for table in tables:
            show_tables.append(table["tables"])

        if table_name not in show_tables:
            return red_err("user_tables", "Access denied")
    except:
        return red_err("user_tables", "Access denied")

    # ChatGPT
    delete_row_sql = f"DELETE FROM {table_name} WHERE {key} = :key_value"
    db.execute(delete_row_sql, key_value=key_value)
    flash("Row deleted successfully", "info")
    return redirect(url_for('edit_table', table_name=table_name))


@app.route('/edit_row/<string:table_name>/<string:key>/<key_value>', methods=['GET', 'POST'])
@login_required
def edit_row(table_name, key, key_value):

    # Check if user has access to the requested table
    try:
        user_id = session["user_id"]
        user_tables = f"tables_{user_id}"
        list_table_sql = f"SELECT * FROM {user_tables}"
        tables = db.execute(list_table_sql)

        # Construct list of tables from 'tables' dict
        show_tables = []
        for table in tables:
            show_tables.append(table["tables"])

        if table_name not in show_tables:
            return red_err("user_tables", "Access denied")
    except:
        return red_err("user_tables", "Access denied")

    if request.method == "POST":
        try:
            # Fetch all columns in the table
            columns_sql = f"SELECT * FROM pragma_table_info('{table_name}')"
            columns = db.execute(columns_sql)

            # Prepare a dictionary to hold the new values
            values = {}
            for column in columns:
                column_name = column['name']
                values[column_name] = request.form.get(column_name)

            # Build the UPDATE query    ###ChatGPT
            set_columns = []
            # Include the key and key_value in update_values
            update_values = {key: key_value}
            for column, value in values.items():
                set_columns.append(f"{column} = '{value}'")
                update_values[column] = value

            set_columns_str = ', '.join(set_columns)
            edit_row_sql = f"UPDATE {table_name} SET {set_columns_str} WHERE {key} = '{key_value}'"
            try:
                db.execute(edit_row_sql)
                flash("Row edited successfully", "success")
                return redirect(url_for('edit_table', table_name=table_name))
            except Exception as e:
                flash(edit_row_sql)
                return redirect("/user_tables")

        except Exception as e:
            return red_err("errored", None, f"Something Went Wrong: {str(e)}")

    else:

        try:
            # Fetch columns information
            columns_sql = f"SELECT * FROM pragma_table_info('{table_name}')"
            columns = db.execute(columns_sql)
            # Fetch the row to be edited
            row_sql = f"SELECT * FROM {table_name} WHERE {key} = :key_value"
            row = db.execute(row_sql, key_value=key_value)

            return render_template("edit_row.html", columns=columns, row=row)

        except Exception as e:
            return red_err("errored", None, f"Something Went Wrong: {str(e)}")


if __name__ == '__main__':
    app.run()
