from flask import Flask, request, session, redirect, url_for, render_template,flash,send_from_directory
import sqlite3
import os
import uuid
from flask import jsonify
import datetime
import hashlib
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static\data-files'
upload_folder = app.config['UPLOAD_FOLDER']

# Secret key for session management
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

conn = sqlite3.connect('main.db', check_same_thread=False)
cursor = conn.cursor()

def create_database_tables():
    conn = sqlite3.connect('main.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS assignments (id TEXT PRIMARY KEY, name TEXT, description TEXT, file TEXT, last_date TEXT, price REAL, email TEXT,uploaded_at DATE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS freelancers (email TEXT PRIMARY KEY,name TEXT,phone TEXT,password TEXT,skills TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bids (id TEXT PRIMARY KEY, freelancer_email TEXT,user_email TEXT,assignment_id TEXT,price REAL,status TEXT,
    FOREIGN KEY (freelancer_email) REFERENCES freelancers(email),
    FOREIGN KEY (user_email) REFERENCES users(email),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id))''')
    conn.commit()

create_database_tables()
# Connect to the database



# Home page
@app.route('/')
def home():
    return render_template("freelancer_home_page.html")

#Redirection to StudentLogin
@app.route("/hometostudent")
def hometostudent():
    return render_template('login_signup_student.html')

#Redirection to FreelancerLogin

@app.route("/hometofreelancer")
def hometofreelancer():
    return render_template('login_signup_freelancer.html')

#<---------------student_side_start----------------->

@app.route("/student_signup", methods=["POST"])
def signup():
    try:
        # Get the user's input from the form
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        secretcodestudent=request.form.get("secretcodestudent")
        print(secretcodestudent)

        if not name or not email or not phone or not password:
            return jsonify({"status": "error", "message": "All fields are required"})

        # Check if the email already exists in the database
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        print(user)
        if user:
            return jsonify({"status": "error", "message": "Email already exists"})

        # Hash the password before storing it in the database
        password = hashlib.sha256(password.encode()).hexdigest()

        # Insert the new user's data into the database
        cursor.execute("INSERT INTO users (name, email, phone, password,secret_code_user) VALUES (?,?,?,?,?)", (name, email, phone, password,secretcodestudent))
        conn.commit()

        return jsonify({"status": "success", "message": "Account created successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Email already exists"})
    except Exception as e:
        return jsonify({"status": "error", "message": "An unknown error occurred"})


@app.route("/student_login", methods=["POST"])
def login():
    try:
        # Get the user's input from the form
        email = request.form["email"]
        password = request.form["password"]

        print(email)
        print(password)
        # Connect to the database

        # Hash the password before checking it against the stored password
        password = hashlib.sha256(password.encode()).hexdigest()

        # Check if the email and password match a user in the database
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        print(user)
        if user:
            session['username'] = email
            return jsonify({"status": "success", "message": "Logged in successfully"})
        else:
            return jsonify({"status": "error", "message": "Invalid email or password"})
    except Exception as e:
        return jsonify({"status": "error", "message": "An unknown error occurred"})


@app.route('/user-dashboard')
def user_dashboard():
    email = session['username']
    return render_template('collectdata.html')

@app.route('/user-dashboard-data')
def user_dashboard_data():
    email = session['username']
    cursor.execute('''SELECT name FROM users WHERE email = ?''', (email,))
    name = cursor.fetchone()[0]
    cursor.execute('''SELECT a.*, b.status FROM assignments a LEFT JOIN bids b on a.assignment_id = b.assignment_id where a.email = ?''', (email, ))
    assignments1 = cursor.fetchall()
    # Convert the data to a list of dictionaries
    assignments = [
        {
            'assignment_id': row[0],
            'name': row[1],
            'description': row[2],
            'price': row[5],
            'status': row[7] if row[7] else 'Awaiting Status'
        }
        for row in assignments1
    ]
    return jsonify(assignments=assignments, name=name)


@app.route('/post_assignment', methods=['POST'])
def post_assignment():
    if request.method == 'POST':
        # get the data from the form
        print(request.form)

        assignment_name = request.form['assignment_name']
        description = request.form['description']
        file = request.files['file']
        last_date = request.form['last_date']
        price = request.form['price']
        email = session['username']
        id = str(uuid.uuid1())
        uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # save the file
        file.save(os.path.join(upload_folder, id))

        # insert the data into the database
        cursor.execute('''INSERT INTO assignments (assignment_id, assignment_name, description, file, last_date, price, email,uploaded_at) VALUES (?,?,?,?,?,?,?,?)''', (id, assignment_name, description, id, last_date, price, email,uploaded_at))
        conn.commit()

        # return success message
        return jsonify(status=200)


#<----------------------student_side_end------------------------------>




#<----------------------Freelancer_Side_Start-------------------------->
@app.route("/freelancer_signup", methods=["POST"])
def freelancersignup():
    try:
        # Get the user's input from the form
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        skills = request.form.get("skills")
        secret_code=request.form.get("secretcode")

        if not name or not email or not phone or not password:
            return jsonify({"status": "error", "message": "All fields are required"})

        # Check if the email already exists in the database
        cursor.execute("SELECT * FROM freelancers WHERE email=?", (email,))
        user = cursor.fetchone()
        print(user)
        if user:
            return jsonify({"status": "error", "message": "Email already exists"})

        # Hash the password before storing it in the database
        password = hashlib.sha256(password.encode()).hexdigest()

        # Insert the new user's data into the database
        cursor.execute("INSERT INTO freelancers (name, email, phone, password,skills,secret_code_user) VALUES (?,?,?,?,?,?)", (name, email, phone, password,skills,secret_code))
        conn.commit()

        return jsonify({"status": "success", "message": "Account created successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Email already exists"})
    except Exception as e:
        return jsonify({"status": "error", "message": "An unknown error occurred"})


@app.route("/freelancer_login", methods=["POST"])
def freelancerlogin():
    try:
        # Get the user's input from the form
        email = request.form["email"]
        password = request.form["password"]

        print(email)
        print(password)
        # Connect to the database

        # Hash the password before checking it against the stored password
        password = hashlib.sha256(password.encode()).hexdigest()

        # Check if the email and password match a user in the database
        cursor.execute("SELECT * FROM freelancers WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        print(user)
        if user:
            session['username'] = email
            return jsonify({"status": "success", "message": "Logged in successfully"})
        else:
            return jsonify({"status": "error", "message": "Invalid email or password"})
    except Exception as e:
        return jsonify({"status": "error", "message": "An unknown error occurred"})


@app.route('/freelancer_dashboard')
def freelancer_dashboard():
    # get the email from the session
    email = session['username']
    #connect to the database
    conn = sqlite3.connect('main.db')
    c = conn.cursor()
    #get freelancer name from the database
    c.execute('SELECT name FROM freelancers WHERE email = ?', (email,))
    freelancer = c.fetchone()
    conn.close()
    # render the template and pass the freelancer name as a variable
    return render_template('freelancer-dashboard.html', freelancer_name=freelancer[0])


@app.route('/load_assignments/<int:page>', methods=['GET'])
def load_assignments(page):
    conn = sqlite3.connect('main.db')
    c = conn.cursor()

    offset = page * 10
    c.execute(f"SELECT * FROM assignments ORDER BY datetime(uploaded_at) DESC LIMIT 10 OFFSET {offset}")
    assignments = c.fetchall()
    print("Bhar")
    assignments_list = []
    for assignment in assignments:
        assignments_list.append({
            'assignment_id': assignment[0],
            'description': assignment[3],
            'name': assignment[2],
            'last_date': assignment[5],
            'price': assignment[6]
        })

    return jsonify(assignments_list)


@app.route('/accept_assignment', methods=['POST'])
def accept_assignment():
    assignment_id = request.form['assignment_id']
    print(assignment_id)
    freelancer_email = session['username']
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute("SELECT email FROM assignments WHERE assignment_id=?", (assignment_id,))
    user_email = cur.fetchone()[0]
    timestamp = datetime.datetime.now()
    cur.execute("INSERT INTO bids(freelancer_email, assignment_id, user_email, status,timestamp) VALUES(?,?,?,'accepted',?)", (freelancer_email, assignment_id,user_email,timestamp))
    cur.execute("SELECT timestamp FROM bids WHERE assignment_id=? and freelancer_email=?", (assignment_id,freelancer_email))
    timestamp = cur.fetchone()
    print(timestamp)
    conn.commit()
    if conn.total_changes > 0:
        print('Data has been successfully inserted into the bids table.')
    else:
        print('Data insertion failed, please check your query and try again.')
    return jsonify({'success': True})


@app.route('/bid_assignment', methods=['POST'])
def bid_assignment():
    assignment_id = request.form['assignment_id']
    print(assignment_id)
    freelancer_email = session['username']
    bid_price = request.form['custom_price']
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()
    cur.execute("SELECT email FROM assignments WHERE assignment_id=?", (assignment_id,))
    user_email = cur.fetchone()[0]
    timestamp = datetime.datetime.now()
    cur.execute("INSERT INTO bids(freelancer_email, assignment_id, user_email, status, bid_price,timestamp) VALUES(?,?,?, 'bid',?,?)", (freelancer_email, assignment_id,user_email, bid_price,timestamp))
    conn.commit()
    if conn.total_changes > 0:
        print('Data has been successfully inserted into the bids table.')
    else:
        print('Data insertion failed, please check your query and try again.')
    return jsonify({'success': True})

@app.route('/assignment_download/<filename>')
def download_file(filename):
    print(filename)
    return send_from_directory(upload_folder, filename, as_attachment=True)

#<---------------------Freelancer_Side_End------------------------------->

#<---------------------Freelancer_Home_Page_Start------------------------------->

# @app.route('/get_data', methods=["GET"])
# def get_data():
#     page = request.args.get('page')
#     per_page = request.args.get('per_page')
#     offset = (int(page) - 1) * int(per_page)
#     query = f"SELECT * FROM assignments ORDER BY datetime(uploaded_at) DESC LIMIT {per_page} OFFSET {offset}"
#     cursor.execute(query)
#     data = cursor.fetchall()
#     print(data)
#     assignments = []
#     for row in data:
#         assignments.append({"sno": row[0], "assignment_name": row[1], "description": row[2], "price": row[5], "last_date": row[4]}
# )
#     return jsonify(assignments)
@app.route('/get_data', methods=["GET"])
def get_data():
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page',5))
    offset = (page - 1) * per_page

    # Get sorting parameters
    order_by = request.args.get('order_by', 'uploaded_at')
    order_dir = request.args.get('order_dir', 'desc')

    # Get filtering parameters
    name_filter = request.args.get('name_filter')
    price_filter = request.args.get('price_filter')
    domain_filter = request.args.get('domain_filter')

    # Build the query based on the parameters
    query = "SELECT * FROM ASSIGNMENTS"
    where_clauses = []
    if name_filter:
        where_clauses.append(f"assignment_name LIKE '%{name_filter}%'")
    if price_filter:
        where_clauses.append(f"price = {price_filter}")
    if domain_filter:
        where_clauses.append(f"assignment_domain = '{domain_filter}'")
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += f" ORDER BY {order_by} {order_dir}"
    query += f" LIMIT {per_page} OFFSET {offset}"

    # Execute the query and return the results as JSON
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    assignments = []
    for row in data:
        assignments.append({
            "id": row[0],
            "assignment_name": row[1],
            "description": row[2],
            "uploaded_at": row[3],
            "last_date": row[4],
            "price": row[5],
            "assignment_domain": row[6]
        })
    conn.close()
    return jsonify(assignments)

@app.route("/get_total_count_and_value")
def get_total_count_and_value():
    # Retrieve total count and value from the database
    cursor.execute("SELECT COUNT(*) FROM assignments")
    total_count = cursor.fetchone()[0]
    #print(total_count)
    cursor.execute("SELECT SUM(price) FROM assignments")
    total_value = cursor.fetchone()[0]
    #print(total_value)

    return jsonify({"total_count": total_count, "total_value": total_value})

#<---------------------Freelancer_Home_Page_End--------------------------------------->
#<--------------------------------LogOut Start ---------------------------------------->

@app.route('/logout',methods=["GET"])
def logout():
    # Clear the user's session
    session.pop('username', None)
    # Redirect the user back to the home page
    return redirect(url_for('home'))

#<--------------------------------LogOut End ---------------------------------------->

#<--------------------------------Student Password_Reset_Start------------------------>

@app.route('/reset_password_student', methods=['POST'])
def reset_password_student():
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    secret_code = request.form.get('secret_code')
    password = request.form.get('password')

    # Check if the provided email, mobile and secret code match with any records in the database
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE email=? AND mobile=? AND secret_code_user=?"
    cursor.execute(query, (email, mobile, secret_code))
    user = cursor.fetchone()

    if user:
        # Update the password for the user
        query = "UPDATE users SET password=? WHERE email=?"
        cursor.execute(query, (password, email))
        conn.commit()

        # Return success message
        return jsonify({'result': 'success'})
    else:
        # Return failure message
        return jsonify({'result': 'failure'})

#<--------------------------------Student Password_Reset_End------------------------>

#<--------------------------------Freelancer_Password_Reset_Start------------------->

@app.route('/reset_password_freelancer', methods=['POST'])
def reset_password_freelancer():
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    secret_code = request.form.get('secret_code')
    password = request.form.get('password')

    # Check if the provided email, mobile and secret code match with any records in the database
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE email=? AND mobile=? AND secret_code_user=?"
    cursor.execute(query, (email, mobile, secret_code))
    user = cursor.fetchone()

    if user:
        # Update the password for the user
        query = "UPDATE users SET password=? WHERE email=?"
        cursor.execute(query, (password, email))
        conn.commit()

        # Return success message
        return jsonify({'result': 'success'})
    else:
        # Return failure message
        return jsonify({'result': 'failure'})

#<--------------------------------Freelancer_Password_Reset_Start------------------->


#<-------------------------------------Route-To-StudentSide-Start-------------------------------->
@app.route('/Student_Password_Reset', methods=['GET'])
def reset_password_form_Student():
    return render_template('password_reset_student.html')
#<-------------------------------------Route-To-StudentSide-Start-------------------------------->


#<-------------------------------------Route-To-StudentSide-Start-------------------------------->
@app.route('/Freelancer_Password_Reset', methods=['GET'])
def reset_password_form_Freelancer():
    return render_template('password_reset_freelancer.html')
#<-------------------------------------Route-To-StudentSide-Start-------------------------------->

if __name__ == '__main__':
    app.run()
