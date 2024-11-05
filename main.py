from flask import Flask, request, jsonify, redirect, url_for, render_template, make_response, session, flash
from flask import make_response
from flask_bcrypt import Bcrypt
from loguru import logger
from datetime import datetime
import mysql.connector
import csv
import io

# from db folder
from backend.db.db import dbconfig

# from py folder
from backend.py.checkMissingData import check_missing_data
from backend.py.generateExamSched import titleForExam


app = Flask(__name__)
app.secret_key = 'oes'
bcrypt = Bcrypt(app)

db_config = dbconfig()
mysql = mysql.connector.connect(**db_config)

def log_event(UserID, action, description):
    # Log event
    event_time = datetime.now()
    cursor = mysql.cursor()
    cursor.execute("INSERT INTO user_logs (UserID, Action, Description, Timestamp) VALUES (%s, %s, %s, %s)", (UserID, action, description, event_time))
    mysql.commit()
    
    # Log event using loguru logger
    logger.info(f"UserID '{UserID}' {action} {description} at {event_time}")

#Home route
@app.route('/')
def home():
    
    if 'username' in session:
        session.clear()
        return redirect(url_for('logout'))
    return redirect(url_for('login'))

# login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    # If the user is already logged in, redirect them to their dashboard
    if 'username' in session:
        if session['role'] == 1:
            return redirect(url_for('superadmin2'))
        elif session['role'] == 2:
            return redirect(url_for('admin'))
        elif session['role'] == 3:
            return redirect(url_for('faculty'))
        else:
            return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.cursor(dictionary=True)
        cursor.execute('SELECT * FROM User WHERE Username = %s', (username,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user['PasswordHash'], password):
            session['username'] = user['Username']
            session['UserID'] = user['UserID']  # Add UserID to session
            session['role'] = user['RoleID']
            
             # Log successful login
            log_event(user['UserID'], 'logged in', 'welcome back')
            logger.info(f"User '{username}' logged in successfully.")


            if user['RoleID'] == 1:
                return redirect(url_for('superadmin'))
            elif user['RoleID'] == 2:
                return redirect(url_for('admin'))
            elif user['RoleID'] == 3:
                return redirect(url_for('faculty'))
            else:
                return redirect(url_for('home'))
        else:
            error = "Invalid credentials, please try again."

    return render_template('login.html', error=error)

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None

    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        role = request.form['role']

        # Validate form data
        if not username or not password or not confirm_password or not email or not firstName or not lastName or not role:
            error = "All fields are required."
        elif len(password) < 8:  # Password length validation
            error = "Password must be at least 8 characters long."
        elif password != confirm_password:  # Password match validation
            error = "Passwords do not match."

        # Check if username or email already exists
        cursor = mysql.cursor()
        try:
            cursor.execute("SELECT * FROM user WHERE Username = %s OR Email = %s", (username, email))
            user = cursor.fetchone()
            if user:
                error = "Username or email already exists."
        except mysql.connector.Error as err:
            error = f"Database error: {err}"
        finally:
            cursor.close()

        if not error:
            # Hash password
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Insert user into database
            cursor = mysql.cursor()
            try:
                cursor.execute('INSERT INTO user (Username, PasswordHash, Email, firstName, lastName, RoleID, CreatedAt, UpdatedAt) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)',
                               (username, hashed_password, email, firstName, lastName, role))
                mysql.commit()
                
                # Log successful registration
                log_event(session['UserID'], 'registered', 'Welcome User')
                logger.info(f"User '{username}' registered successfully.")
            
                flash("Register inserted successfully.")
                return redirect(url_for('superadmin'))
            except mysql.connector.Error as err:
                error = f"Database error: {err}"
            finally:
                cursor.close()

    # return render_template('supe.html', error=error, session=session)
    return redirect(url_for('superadmin', error=error, session=session))



# Route to view all announcements
@app.route('/announcements')
def announcements():
    if 'username' in session and session['role'] == 1:
        username = session['username']
    else:
        return redirect(url_for('login'))

    cursor = mysql.cursor(dictionary=True)
    cursor.execute('SELECT * FROM announcements ORDER BY created_at DESC')
    announcements = cursor.fetchall()
    cursor.close()
    return render_template('announcementss.html', announcements=announcements)


# Route to create a new announcement
@app.route('/create_announcement', methods=['GET', 'POST'])
def create_announcement():
    if 'username' not in session or session.get('role') not in [1, 2]:  # Only superadmin and admin can create announcements
        return redirect(url_for('login'))

    username = session['username']

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        cursor = mysql.cursor()
        try:
            cursor.execute('INSERT INTO announcements (title, content) VALUES (%s, %s)', (title, content))
            mysql.commit()

            # Log event
            log_event(session['UserID'], 'created announcement', f'title: {title}')
            logger.info(f"Announcement '{title}' created successfully.")
            
            flash('Announcement created successfully.', 'success')
            return redirect(url_for('announcements'))
        except mysql.connector.error as err:
            flash(f'Database error: {err}', 'danger')
        finally:
            cursor.close()

    return render_template('create_announcement.html', username=username)



# CRUD: View all users
@app.route('/users')
def list_users():
    if 'username' in session and session['role'] == 1:
        username = session['username']
    else:
        return redirect(url_for('login'))
    
    cursor = mysql.cursor(dictionary=True)
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    cursor.close()

    return render_template('users.html', users=users, username=username, session=session)

@app.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if 'username' in session and session['role'] == 1:
        username = session['username']
    else:
        return redirect(url_for('login'))
    
    # Extract form data
    new_username = request.form['username']
    new_email = request.form['email']
    new_first_name = request.form['firstName']
    new_last_name = request.form['lastName']
    new_role = request.form['role']

    try:
        cursor = mysql.cursor(dictionary=True)
        # Update user information in the database
        cursor.execute("""
            UPDATE users 
            SET Username = %s, Email = %s, firstName = %s, lastName = %s, RoleID = %s 
            WHERE UserID = %s
        """, (new_username, new_email, new_first_name, new_last_name, new_role, user_id))
        mysql.commit()
        cursor.close()
        flash('User updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating user: {str(e)}', 'danger')
    
    return redirect(url_for('users_management'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' in session and session['role'] == 1:
        username = session['username']
    else:
        return redirect(url_for('login'))

    try:
        cursor = mysql.cursor(dictionary=True)
        # Delete user from the database
        cursor.execute("DELETE FROM users WHERE UserID = %s", (user_id,))
        mysql.commit()
        cursor.close()
        flash('User deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'danger')

    return redirect(url_for('users_management'))


# # CRUD: Edit user
# @app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
# def edit_user(user_id):
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     cursor = mysql.cursor(dictionary=True)
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         firstName = request.form['firstName']
#         lastName = request.form['lastName']
#         role = request.form['role']

#         cursor.execute('UPDATE user SET Username = %s, Email = %s, firstName = %s, lastName = %s, RoleID = %s, UpdatedAt = CURRENT_TIMESTAMP WHERE UserID = %s',
#                        (username, email, firstName, lastName, role, user_id))
#         mysql.commit()

#         # Log successful edited the userlist
#         log_event(session['UserID'], 'updated', f"user with ID {user_id}")
#         logger.info(f"User '{username}'  successfully.")


#         cursor.close()
#         return redirect(url_for('list_users'))

#     cursor.execute('SELECT * FROM user WHERE UserID = %s', (user_id,))
#     user = cursor.fetchone()
#     cursor.close()

#     return render_template('edit_user.html', user=user, session=session)

# # CRUD: Delete user
# @app.route('/delete_user/<int:user_id>', methods=['POST'])
# def delete_user(user_id):
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     cursor = mysql.cursor(dictionary=True)
#     cursor.execute('SELECT Username FROM user WHERE UserID = %s', (user_id,))
#     user = cursor.fetchone()

#     # Log successful deletion
#     log_event(session['UserID'], 'Deleted', f"user with ID {user_id}")
#     logger.info(f"User '{'Username'}' successfully deleted.")

#     cursor.execute('DELETE FROM user WHERE UserID = %s', (user_id,))
#     mysql.commit()
#     cursor.close()
    
#     return redirect(url_for('list_users'))


# CRUD: Delete users log
@app.route('/delete_user_logs/<int:user_id>', methods=['POST'])
def delete_user_logs(user_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cursor = mysql.cursor(dictionary=True)
    cursor.execute('SELECT * FROM user_logs WHERE LogID = %s', (user_id,))
    user = cursor.fetchone()

    # Log successful deletion
    log_event(session['UserID'], 'Deleted', f"user with ID {user_id}")
    logger.info(f"User '{'Username'}' successfully deleted.")

    cursor.execute('DELETE * FROM user_logs WHERE LogID = %s', (user_id,))
    mysql.commit()
    cursor.close()
    
    return redirect(url_for('list_logs'))

#filter user logs
@app.route('/filter_logs', methods=['POST'])
def filter_logs():
    if 'username' in session and session['role'] == 1:
        username = session['username']
    else:
        return redirect(url_for('login'))

    try:
        cursor = mysql.cursor(dictionary=True)

        # Fetch all logs
        cursor.execute("SELECT * FROM filtered_logs")
        all_logs = cursor.fetchall()

        # Fetch filtered logs based on selected actions
        selected_actions = request.form.getlist('action')
        if "All" in selected_actions:
            users = all_logs  # Display all logs if "All" is selected
        elif selected_actions:
            placeholders = ', '.join(['%s'] * len(selected_actions))
            query = f"SELECT * FROM filtered_logs WHERE Action IN ({placeholders})"
            cursor.execute(query, selected_actions)
            users = cursor.fetchall()
        else:
            users = all_logs  # Display all logs if no actions are selected
                
    except mysql.connector.Error as e:
        print("Error:", e)
        users = []
    finally:
        cursor.close()

    return render_template('supadminlogs.html', users=users, username=username)


# logs list
@app.route('/fecth_logs')
def fecth_logs():
    if 'username' in session and session['role'] == 1:
        username = session['username']
    else:
        return redirect(url_for('login'))
    
    cursor = mysql.cursor(dictionary=True)
    cursor.execute('SELECT * FROM filtered_logs')
    users = cursor.fetchall()
    cursor.close()

    return render_template('supadminlogs.html', users=users, username=username, session=session)

@app.route('/process_csv', methods=['POST'])
def process_csv():
    if 'csvFile' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['csvFile']
    
    # Check if the file is a CSV
    if file.filename.endswith('.csv'):
        # Save the file temporarily
        file_path = 'temp.csv'
        file.save(file_path)
        
        # Process the CSV file to check for missing data
        total_errors, missing_data_html = check_missing_data(file_path)
        
        # Store the processed HTML in the session
        return jsonify({'total_errors': total_errors, 'missing_data_html': missing_data_html})
     
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/result')
def show_result():
    missing_data_html = request.args.get('data', '')
    return render_template('result.html', missing_data_html=missing_data_html)

@app.route('/history')
def show_history():
    exam_title = titleForExam()
    return render_template('history.html', exam_title=exam_title)

@app.route('/get-csv')
def get_csv():
    csv_path = './Final Exam2ndSemS.Y2023-2024.csv'
    output = io.StringIO()
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(output)
        
        # Combine the first row into one column and add empty columns to fill up to 7 columns
        first_row = next(reader)
        combined_row = ' '.join(first_row)
        writer.writerow([combined_row] + [''] * 5)
        
        # Write the next rows with a maximum of 7 columns
        for row in reader:
            writer.writerow(row[:6])
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    response.headers["Content-type"] = "text/csv"

    # Log generated exam schedule
    if 'UserID' in session:
        log_event(session['UserID'], 'exam generated', 'study hard!')
        logger.info(f"UserID '{session['UserID']}' exam generated successfully.")
    else:
        logger.warning("Attempt to generate exam schedule without login.")

    return response

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '')
    csv_path = './Final Exam2ndSemS.Y2023-2024.csv'
    results = []

    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)  # Read the headers
        results.append(headers)  # Add headers to results

        for row in reader:
            if query.lower() in ','.join(row).lower():
                results.append(row)
    
    return jsonify({'results': results})

# generate exam
@app.route('/index')
def index():
    if 'username' in session and session['role'] == 1:
        username = session['username']
        return render_template('index.html', username=username)
    else:
        return redirect(url_for('login'))

# superadmin
# @app.route('/superadmin')
# def superadmin():
#     if 'username' in session and session['role'] == 1:
#         username = session['username']
#         return render_template('superadmin.html', username=username)
#     else:
#         return redirect(url_for('login'))
    
# superadmin
@app.route('/superadmin')
def superadmin():
    if 'username' in session and session['role'] == 1:
        username = session['username']
        
        cursor = mysql.cursor(dictionary=True)
        
        # Fetch the email of the logged-in user
        cursor.execute('SELECT email FROM user WHERE username = %s', (username,))
        user = cursor.fetchone()
        email = user['email'] if user else 'No email found'
        
        # Fetch users
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()
        
        # Fetch logs
        cursor.execute('SELECT * FROM filtered_logs')
        logs = cursor.fetchall()
        
        cursor.close()
        
        return render_template('superadmin2.html', users=users, logs=logs, username=username, email=email)
    else:
        return redirect(url_for('login'))

    
#for superadmin register
@app.route('/supadregister')
def supadregister():
    if 'username' in session and session['role'] == 1:
        username = session['username']
        return render_template('supadregister.html', username=username)
    else:
        return redirect(url_for('login'))

#superadmin logs
@app.route('/supad_logs')
def supad_logs():
    if 'username' in session and session['role'] == 1:
        username = session['username']
        return render_template('supadminlogs.html', username=username)
    else:
        return redirect(url_for('login'))

#users route
@app.route('/users')
def users():
    if 'username' in session and session['role'] == 1:
        username = session['username']
        return render_template('users.html', username=username)
    else:
        return redirect(url_for('login'))

# admin
@app.route('/admin')
def admin():
    if 'username' in session and session['role'] == 2:
        username = session['username']
        
        cursor = mysql.cursor(dictionary=True)
        
        # Fetch the email of the logged-in user
        cursor.execute('SELECT email FROM user WHERE username = %s', (username,))
        user = cursor.fetchone()
        email = user['email'] if user else 'No email found'
        
        # Fetch users
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()
        
        # Fetch announcements
        cursor.execute('SELECT * FROM announcements ORDER BY created_at DESC')
        announcements = cursor.fetchall()
        
        cursor.close()
        
        return render_template('admin.html', users=users, username=username, email=email, session=session, announcements=announcements)
    else:
        return redirect(url_for('login'))

# faculty
@app.route('/faculty')
def faculty():
    if 'username' in session and session['role'] == 3:
        username = session['username']

        cursor = mysql.cursor(dictionary=True)
        
        # Fetch the email of the logged-in user
        cursor.execute('SELECT email FROM user WHERE username = %s', (username,))
        user = cursor.fetchone()
        email = user['email'] if user else 'No email found'
        
        # Fetch specific user details (for demo, filtering on a specific UserId)
        cursor.execute('SELECT UserID, Username, Email, firstName, lastName FROM user WHERE UserId = 68')  
        users = cursor.fetchall()
        
        # Fetch announcements
        cursor.execute('SELECT * FROM announcements ORDER BY created_at DESC')
        announcements = cursor.fetchall()
        
        cursor.close()

        return render_template('faculty.html', users=users, username=username, email=email, session=session, announcements=announcements)
    else:
        return redirect(url_for('login'))


# Logout route
@app.route('/logout')
def logout():
    if 'UserID' in session:
        # Log logout event
        log_event(session['UserID'], 'logged out', 'Thank you!')
        logger.info(f"UserID '{session['UserID']}' logged out.")
    session.clear()
    return redirect(url_for('home'))

# create schedule
@app.route('/createSchedule')
def createSchedule():
    return render_template('createSchedule.html')

if __name__ == '__main__':
    app.run(debug=True)