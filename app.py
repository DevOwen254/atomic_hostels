from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random

app = Flask(__name__)
app.secret_key = 'secret123'
app.config['SESSION_PERMANENT'] = False

# DATABASE

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT"))
)
cursor = db.cursor()

# AUTH DECORATORS

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return wrapper

def resident_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'resident' not in session:
            return redirect(url_for('resident_login_page'))
        return f(*args, **kwargs)
    return wrapper

# HOME

@app.route('/')
def home():
    return render_template('login.html')

# ADMIN LOGIN

@app.route('/login', methods=['POST'])
def login():
    role = request.form['role']
    identifier = request.form['identifier']
    password = request.form['password']

    # ADMIN LOGIN
    if role == 'admin':
        cursor.execute("SELECT * FROM admin WHERE username=%s", (identifier,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            session.clear()
            session['admin'] = user[0]
            return redirect('/dashboard')

    # RESIDENT LOGIN
    elif role == 'resident':
        cursor.execute("SELECT * FROM residents WHERE email=%s", (identifier,))
        user = cursor.fetchone()

        if user and check_password_hash(user[4], password):
            session.clear()
            session['resident'] = user[0]
            return redirect('/residents_dashboard')

    return "Invalid login"


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

#  DASHBOARD 

@app.route('/dashboard')
@admin_required
def dashboard():
    cursor.execute("SELECT COUNT(*) FROM residents")
    total_residents = cursor.fetchone()[0]

    
    cursor.execute("SELECT COUNT(*) FROM rooms WHERE occupied < capacity")
    available_rooms = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount_paid) FROM payments")
    total_payments = cursor.fetchone()[0] or 0

    return render_template('dashboard.html',
                        total_residents=total_residents,
                        available_rooms=available_rooms,
                        total_payments=total_payments)


#  RESIDENTS 

@app.route('/residents')
@admin_required
def residents():
    search = request.args.get('search')

    
    if search:
        query = """
        SELECT * FROM residents 
        WHERE name LIKE %s OR phone LIKE %s OR email LIKE %s
        """
        values = ('%' + search + '%', '%' + search + '%', '%' + search + '%')
        cursor.execute(query, values)
    else:
        cursor.execute("SELECT * FROM residents")

    residents = cursor.fetchall()

    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()

    return render_template('residents.html', residents=residents, rooms=rooms)


@app.route('/add_resident', methods=['POST'])
@admin_required
def add_resident():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    room_id = request.form['room_id']
    password = generate_password_hash(request.form['password'])

    
    cursor.execute("SELECT capacity, occupied FROM rooms WHERE id=%s", (room_id,))
    room = cursor.fetchone()

    if room[1] < room[0]:
        cursor.execute(
            "INSERT INTO residents (name, phone, email, password, room_id) VALUES (%s, %s, %s, %s, %s)",
            (name, phone, email, password, room_id)
        )

        cursor.execute(
            "UPDATE rooms SET occupied = occupied + 1 WHERE id=%s",
            (room_id,)
        )

        db.commit()
        return redirect('/residents')
    else:
        return "Room is full!"


@app.route('/delete_resident/[int:id](int:id)')
@admin_required
def delete_resident(id):
    cursor.execute("DELETE FROM residents WHERE id=%s", (id,))
    db.commit()
    return redirect('/residents')

#  ROOMS 

@app.route('/rooms')
@admin_required
def rooms():
    cursor.execute("SELECT * FROM rooms")
    data = cursor.fetchall()
    return render_template('rooms.html', rooms=data)

@app.route('/add_room', methods=['POST'])
@admin_required
def add_room():
    room_number = request.form['room_number']
    capacity = request.form['capacity']


    cursor.execute(
        "INSERT INTO rooms (room_number, capacity) VALUES (%s, %s,%s)",
        (room_number, capacity,0)
    )

    db.commit()
    return redirect('/rooms')


#  PAYMENTS 

@app.route('/payments')
@admin_required
def payments():
    cursor.execute("""
    SELECT payments.id, residents.name, amount_paid, balance, date_paid
    FROM payments
    JOIN residents ON payments.resident_id = residents.id
    """)
    data = cursor.fetchall()

    
    cursor.execute("SELECT * FROM residents")
    residents = cursor.fetchall()

    return render_template('payments.html', payments=data, residents=residents)


@app.route('/add_payment', methods=['POST'])
@admin_required
def add_payment():
    resident_id = request.form['resident_id']
    amount = float(request.form['amount'])

    
    RENT = 5000

    cursor.execute("SELECT SUM(amount_paid) FROM payments WHERE resident_id=%s", (resident_id,))
    total_paid = cursor.fetchone()[0] or 0

    new_total = total_paid + amount
    balance = RENT - new_total

    cursor.execute(
        "INSERT INTO payments (resident_id, amount_paid, balance) VALUES (%s, %s, %s)",
        (resident_id, amount, balance)
    )

    db.commit()
    return redirect('/payments')


#  RESIDENT LOGIN 

@app.route('/resident_login')
def resident_login_page():
    return render_template('login.html')

@app.route('/resident_login', methods=['POST'])
def resident_login():
    email = request.form['email']
    password = request.form['password']


    cursor.execute("SELECT * FROM residents WHERE email=%s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user[4], password):
        session['resident'] = user[0]
        return redirect('/resident_dashboard')
    else:
        return "Invalid login"


@app.route('/resident_logout')
def resident_logout():
    session.pop('resident', None)
    return redirect('/resident_login')

#  PASSWORD RESET 

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']

        cursor.execute("SELECT id FROM residents WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            return "Email not found"

        # generate code
        code = str(random.randint(100000, 999999))

        session['reset_code'] = code
        session['reset_email'] = email

        #  TEMPORARY "FAKE EMAIL"
        return render_template('verify_code.html', message=f"Your reset code is {code}")

    return render_template('reset_password.html')

# verification
@app.route('/verify_code', methods=['POST'])
def verify_code():
    code = request.form['code']
    new_password = request.form['new_password']

    if code != session.get('reset_code'):
        return "Invalid code"

    email = session.get('reset_email')
    hashed = generate_password_hash(new_password)

    cursor.execute(
        "UPDATE residents SET password=%s WHERE email=%s",
        (hashed, email)
    )
    db.commit()

    session.pop('reset_code', None)
    session.pop('reset_email', None)

    return redirect('/resident_login')
#  RESIDENT DASHBOARD 

@app.route('/residents_dashboard')
@resident_required
def residents_dashboard():
    resident_id = session['resident']

    
    cursor.execute("""
        SELECT residents.name, rooms.room_number
        FROM residents
        JOIN rooms ON residents.room_id = rooms.id
        WHERE residents.id=%s
    """, (resident_id,))
    info = cursor.fetchone()

    cursor.execute("""
        SELECT amount_paid, balance, date_paid
        FROM payments
        WHERE resident_id=%s
    """, (resident_id,))
    payments = cursor.fetchall()

    return render_template('residents_dashboard.html', info=info, payments=payments)

# complaints

@app.route('/complaints', methods=['GET', 'POST'])
@resident_required
def complaints():

    resident_id = session['resident']

    if request.method == 'POST':
        subject = request.form.get('subject')
        complaint = request.form.get('complaint')

        if not subject or not complaint:
            return "All fields are required"

        cursor.execute("""
        INSERT INTO complaints(resident_id, subject, complaint)
        VALUES(%s, %s, %s)
        """, (resident_id, subject, complaint))

        db.commit()
        return redirect('/complaints')

    cursor.execute("""
    SELECT subject, status, date_created
    FROM complaints
    WHERE resident_id=%s
    ORDER BY date_created DESC
    """, (resident_id,))

    data = cursor.fetchall()

    return render_template("complaints.html", complaints=data)



if __name__ == '__main__':
    app.run(debug=True)
