from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

# MySQL Configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "transport_system",
    "autocommit": True
}

def db():
    return mysql.connector.connect(**DB_CONFIG)

# START → Redirect to Register
@app.route('/')
def start():
    return redirect('/register')

# USER REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        con = db()
        cur = con.cursor()
        cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name, email, password))
        con.commit()
        return redirect('/login')
    return render_template("register.html")

# USER LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        con = db()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        if user:
            session['user'] = user['id']
            return redirect('/home')
    return render_template("login.html")

# HOME PAGE - Show Routes
@app.route('/home', methods=['GET'])
def home():
    if 'user' not in session:
        return redirect('/login')

    from_city = request.args.get('from_city')
    to_city = request.args.get('to_city')
    departure_date = request.args.get('departure_date')

    con = db()
    cur = con.cursor(dictionary=True)

    query = "SELECT r.*, c.name AS company_name, c.website AS company_website FROM routes r LEFT JOIN bus_companies c ON r.company_id=c.id WHERE 1=1"
    params = []

    if from_city:
        query += " AND r.from_city LIKE %s"
        params.append(from_city)
    if to_city:
        query += " AND r.to_city LIKE %s"
        params.append(to_city)
    # Optional: Filter by departure date if you store date in routes
    # if departure_date:
    #     query += " AND r.departure_date = %s"
    #     params.append(departure_date)

    query += " ORDER BY r.departure_time"

    cur.execute(query, params)
    routes = cur.fetchall()

    return render_template("home.html", routes=routes)


# BOOK ROUTE
@app.route('/book/<int:route_id>', methods=['GET','POST'])
def book(route_id):
    if 'user' not in session:
        return redirect('/login')
    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM routes WHERE id=%s", (route_id,))
    route = cur.fetchone()
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        seats = request.form['seats']
        cur2 = con.cursor()
        cur2.execute("INSERT INTO bookings (route_id, user_name, user_email, seats) VALUES (%s,%s,%s,%s)", (route_id, name, email, seats))
        con.commit()
        return redirect('/success')
    return render_template("booking.html", route=route)

# BOOKING SUCCESS
@app.route('/success')
def success():
    if 'user' not in session:
        return redirect('/login')
    return render_template("success.html")

# ADMIN LOGIN
@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        con = db()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM admins WHERE email=%s AND password=%s", (email, password))
        admin = cur.fetchone()
        if admin:
            session['admin'] = admin['id']
            return redirect('/admin/dashboard')
    return render_template("admin_login.html")

# ADMIN DASHBOARD
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin')
    return render_template("admin_dashboard.html")

# ADD ROUTE
@app.route('/admin/add-route', methods=['GET','POST'])
def admin_add_route():
    if 'admin' not in session:
        return redirect('/admin')
    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM bus_companies")
    companies = cur.fetchall()
    if request.method == "POST":
        f = request.form
        cur.execute("""INSERT INTO routes 
            (from_city, to_city, departure_time, arrival_time, transport_type, company_id)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (f['from_city'], f['to_city'], f['departure_time'], f['arrival_time'], f['transport_type'], f['company_id']))
        con.commit()
        return redirect('/admin/dashboard')
    return render_template("admin_add_route.html", companies=companies)

# VIEW BOOKINGS
@app.route('/admin/bookings')
def admin_bookings():
    if 'admin' not in session:
        return redirect('/admin')
    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT b.user_name, b.user_email, b.seats, b.booking_time,
               r.from_city, r.to_city, c.name AS company_name
        FROM bookings b
        JOIN routes r ON b.route_id = r.id
        LEFT JOIN bus_companies c ON r.company_id = c.id
        ORDER BY b.booking_time DESC
    """)
    bookings = cur.fetchall()
    return render_template("admin_booking.html", bookings=bookings)

# USER PROFILE
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')
    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id=%s", (session['user'],))
    user = cur.fetchone()
    return render_template("profile.html", user=user)

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    return redirect('/login')

# RUN SERVER
if __name__ == "__main__":
    app.run(debug=True)
