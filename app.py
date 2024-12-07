from os import pathconf_names
from flask import Flask, request, render_template, redirect, url_for, session
from database import engine
from sqlalchemy.sql import text
from database import add_product_to_db, add_orders_to_db, accept_order, update, cancel_order, delivered_order, add_user_to_db, remove_Product
from datetime import datetime
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = "your_secret_key"


def insert_message_into_db(sid, rid, pid, mesg):
    with engine.connect() as conn:
        try:
            query = text("""
                INSERT INTO chats(sender_id, reciver_id, pid, mesg, sentat)
                VALUES (:sid, :rid, :pid, :mesg, :time)
            """)

            conn.execute(
                query, {
                    "sid": sid,
                    "rid": rid,
                    "pid": pid,
                    "mesg": mesg,
                    "time": datetime.now()
                })
            conn.commit()

        except Exception as e:
            print(f"Error inserting message: {e}")


def remove_orders(oid):
    with engine.connect() as conn:
        result = conn.execute(text("DELETE FROM orders WHERE oid = :oid"),
                              {"oid": oid})
        conn.commit()

def accept_users(uid):
    with engine.connect() as conn:
        # Start an explicit transaction
        with conn.begin():
            conn.execute(
                text("UPDATE UserD SET status = 'Accepted' WHERE uid = :uid"),
                {"uid": uid}
            )
def reject_users(uid):
    with engine.connect() as conn:
        # Start an explicit transaction
        with conn.begin():
            conn.execute(
                text("UPDATE UserD SET status = 'Reject' WHERE uid = :uid"),
                {"uid": uid}
            )


def load_products_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products"))
        products = []
        for row in result:
            products.append(row._asdict())
        return products


def load_message_from_db(sid, rid, pid):
    with engine.connect() as conn:
        try:
            # Query to fetch chat messages
            query = text("""
                SELECT sender_id, reciver_id, mesg, sentat 
                FROM chats 
                WHERE pid = :pid AND ((sender_id = :sid AND reciver_id = :rid) OR (sender_id = :rid AND reciver_id = :sid))
            """)

            # Execute the query with parameters
            result = conn.execute(query, {"pid": pid, "sid": sid, "rid": rid})

            # Convert query result rows to dictionaries
            messages = [
                dict(zip(result.keys(), row)) for row in result.fetchall()
            ]

        except Exception as e:
            print(f"Error loading messages: {e}")
            messages = []

    return messages


def load_rating(pid):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT AVG(rating) FROM orders WHERE pid = :pid"),
            {"pid": pid})
        avg_rating = result.scalar()
        return int(avg_rating) if avg_rating is not None else 0


def load_fproducts_from_db(uid):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products WHERE fid=:uid"),
                              {"uid": uid})
        products = []
        for row in result:
            products.append(row._asdict())
        return products


def load_bproducts_from_db(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT Products.url as img,Products.pname as name,Orders.quantity as qt,Orders.price as pri FROM Orders,Products WHERE Orders.fid=Products.fid AND Orders.pid=Products.pid AND Orders.status='Ordered' AND Orders.bid=:uid"
            ), {"uid": uid})
        products = []
        for row in result:
            products.append(row._asdict())
        return products


def load_users_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM USR"))
        users = []
        for row in result:
            users.append(row._asdict())
        return users


def load_admins_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM AdminT"))
        users = []
        for row in result:
            users.append(row._asdict())
        return users


def load_UserD_from_db():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM UserD WHERE status='Accepted'"))
        users = []
        for row in result:
            users.append(row._asdict())
        return users


def load_UserA_from_db():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM UserD WHERE status='Pending'"))
        users = []
        for row in result:
            users.append(row._asdict())
        return users


def load_OrdersD_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM orders"))
        users = []
        for row in result:
            users.append(row._asdict())
        return users


def load_ProductsD_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM Products"))
        users = []
        for row in result:
            users.append(row._asdict())
        return users


def load_full_order_details(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 
                    Orders.fid,
                    Orders.bid,
                    Orders.pid,
                    Orders.oid,
                    Orders.quantity,
                    Orders.price,
                    Orders.updates,
                    Products.pname,
                    Products.url,
                    Products.rating,
                   
                    Users.uname AS buyer_name,
                    Users.mobilno AS mobilno,
                    Users.email AS email,
                    Users.nationality as nationality,
                    Users.stat as stat,
                    Users.dist as dist,
                    Users.town as town,
                    Users.hno as hno
                FROM 
                    Orders
                JOIN 
                    Products ON Orders.pid = Products.pid
                JOIN 
                    UserD AS Users ON Orders.bid = Users.uid
                WHERE Orders.fid= :uid AND Orders.status= 'Ordered'
                """), {"uid": uid})
        orders = []
        for row in result:
            orders.append(row._asdict())
        return orders


def load_buyer_order_details(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 
                    
                    Orders.oid,
                    Orders.fid,
                    Orders.bid,
                    Orders.pid,
                    Orders.quantity,
                    Orders.price,
                    Orders.updates,
                    Products.pname,
                    Products.url,
                    Products.rating,
                    Users.uname AS buyer_name,
                    Users.mobilno AS mobilno,
                    Users.email AS email,
                    Users.nationality as nationality,
                    Users.stat as stat,
                    Users.dist as dist,
                    Users.town as town,
                    Users.hno as hno
                FROM 
                    Orders
                JOIN 
                    Products ON Orders.pid = Products.pid
                JOIN 
                    UserD AS Users ON Orders.bid = Users.uid
                WHERE Orders.bid= :uid AND Orders.status= 'Ordered'
                """), {"uid": uid})
        orders = []
        for row in result:
            orders.append(row._asdict())
        return orders


def load_full_accepted_details(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 
                    Orders.oid,
                    Orders.fid,
                    Orders.bid,
                    Orders.pid,
                    Orders.quantity,
                    Orders.price,
                    Orders.updates,
                    Products.pname,
                    Products.url,
                    Products.rating,
                    Users.uname AS buyer_name,
                    Users.mobilno AS mobilno,
                    Users.email AS email,
                    Users.nationality as nationality,
                    Users.stat as stat,
                    Users.dist as dist,
                    Users.town as town,
                    Users.hno as hno
                FROM 
                    Orders
                JOIN 
                    Products ON Orders.pid = Products.pid
                JOIN 
                    UserD AS Users ON Orders.bid = Users.uid
                WHERE Orders.fid= :uid AND Orders.status= 'Accepted'
                """), {"uid": uid})
        orders = []
        for row in result:
            orders.append(row._asdict())
        return orders


def load_buyer_accepted_details(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 
                    Orders.oid,
                    Orders.fid,
                    Orders.bid,
                    Orders.pid,
                    Orders.quantity,
                    Orders.price,
                    Orders.updates,
                    Products.pname,
                    Products.url,
                    Products.rating,
                    Users.uname AS buyer_name,
                    Users.mobilno AS mobilno,
                    Users.email AS email,
                    Users.nationality as nationality,
                    Users.stat as stat,
                    Users.dist as dist,
                    Users.town as town,
                    Users.hno as hno
                FROM 
                    Orders
                JOIN 
                    Products ON Orders.pid = Products.pid
                JOIN 
                    UserD AS Users ON Orders.bid = Users.uid
                WHERE Orders.bid= :uid AND Orders.status= 'Accepted'
                """), {"uid": uid})
        orders = []
        for row in result:
            orders.append(row._asdict())
        return orders


def load_full_delivered_details(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 
                    Orders.oid,
                    Orders.fid,
                    Orders.bid,
                    Orders.pid,
                    Orders.quantity,
                    Orders.price,
                    Orders.updates,
                    Orders.rating,
                    Products.pname,
                    Products.url,
                    Products.pid,
                    Products.rating,
                    Users.uname AS buyer_name,
                    Users.mobilno AS mobilno,
                    Users.email AS email,
                    Users.nationality as nationality,
                    Users.stat as stat,
                    Users.dist as dist,
                    Users.town as town,
                    Users.hno as hno
                FROM 
                    Orders
                JOIN 
                    Products ON Orders.pid = Products.pid
                JOIN 
                    UserD AS Users ON Orders.bid = Users.uid
                WHERE Orders.fid= :uid AND Orders.status= 'Delivered'
                """), {"uid": uid})
        orders = []
        for row in result:
            orders.append(row._asdict())
        return orders


def load_buyer_delivered_details(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 
                    Orders.oid,
                    Orders.fid,
                    Orders.bid,
                    Orders.pid,
                    Orders.quantity,
                    Orders.price,
                    Orders.updates,
                    Orders.rating,
                    Products.pname,
                    Products.url,
                    Products.rating,
                    Users.uname AS buyer_name,
                    Users.mobilno AS mobilno,
                    Users.email AS email,
                    Users.nationality as nationality,
                    Users.stat as stat,
                    Users.dist as dist,
                    Users.town as town,
                    Users.hno as hno
                FROM 
                    Orders
                JOIN 
                    Products ON Orders.pid = Products.pid
                JOIN 
                    UserD AS Users ON Orders.bid = Users.uid
                WHERE Orders.bid= :uid AND Orders.status= 'Delivered'
                """), {"uid": uid})
        orders = []
        for row in result:
            orders.append(row._asdict())
        return orders


def load_delivered_from_db(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT * FROM Orders WHERE status='Delivered' AND (fid=:uid OR bid=:uid)"
            ), {"uid": uid})
        delivered = []
        for row in result:
            delivered.append(row._asdict())
        return delivered


@app.route("/removeP", methods=["POST"])
def removeP():
    pid = request.form.get('pid')
    remove_Product(pid)
    return redirect(url_for('ManageP'))


@app.route("/removeO", methods=["POST"])
def removeO():
    oid = request.form.get('oid')
    remove_orders(oid)
    return redirect(url_for('ManageO'))
    
@app.route("/acceptUser", methods=["POST"])
def accept_user():
    uid = request.form.get('uid')  # Retrieve the uid from the form
    if not uid:
        return "User ID not provided", 400

    try:
        accept_users(uid)  # Call the function to update the user status
        return render_template('manageA.html', message="User accepted successfully!")
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route("/rejectUser", methods=["POST"])
def reject_user():
    uid = request.form.get('uid')  # Retrieve the uid from the form
    if not uid:
        return "User ID not provided", 400

    try:
        reject_users(uid)  # Call the function to update the user status
        return render_template('manageA.html', message="User accepted successfully!")
    except Exception as e:
        return f"An error occurred: {e}", 500


@app.route("/ManageO")
def ManageO():
    logged_in = "username" in session
    orders = load_OrdersD_from_db()
    return render_template('manageO.html', orders=orders, logged_in=logged_in)


@app.route("/ManageP")
def ManageP():
    logged_in = "username" in session
    products = load_ProductsD_from_db()
    return render_template('manageP.html',
                           Products=products,
                           logged_in=logged_in)


@app.route("/ManageU")
def ManageU():
    logged_in = "username" in session
    users = load_UserD_from_db()
    return render_template('manageU.html', users=users, logged_in=logged_in)


@app.route("/ManageA")
def ManageA():
    logged_in = "username" in session
    users = load_UserA_from_db()
    return render_template('manageA.html', users=users, logged_in=logged_in)


@app.route("/admin")
def admin():
    uc = len(load_UserD_from_db())
    oc = len(load_OrdersD_from_db())
    pc = len(load_ProductsD_from_db())

    return render_template('admin.html', uc=uc, pc=pc, oc=oc)


@app.route("/")
def home():
    logged_in = "username" in session
    return render_template('home.html', logged_in=logged_in)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/login")
def login():
    return render_template('login.html')




@app.route("/search")
def search():
    query = request.args.get('query')
    logged_in = "username" in session
    all_products = load_products_from_db()
    products = [p for p in all_products if query in p['pname']]
    return render_template('search.html',
                           products=products,
                           logged_in=logged_in,
                           query=query)


@app.route("/about")
def about():
    logged_in = "username" in session
    return render_template('about.html', logged_in=logged_in)


@app.route("/SingUp")
def SingUp():
    return render_template('SingUp.html')


@app.route("/log")
def log():
    utype = request.args.get('utype')
    return render_template('log.html', utype=utype)


@app.route("/service")
def service():
    logged_in = "username" in session
    return render_template('service.html', logged_in=logged_in)


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    utype = session["utype"]
    uid = session["uid"]
    users = load_UserD_from_db()
    user = next((u for u in users if u["uid"] == uid), None)
    logged_in = "username" in session
    if (utype == "Farmer"):
        ordered = len(load_full_order_details(uid))
        accepted = len(load_full_accepted_details(uid))
        delivered = len(load_full_delivered_details(uid))

    else:
        ordered = len(load_buyer_order_details(uid))
        accepted = len(load_buyer_accepted_details(uid))
        delivered = len(load_buyer_delivered_details(uid))

    return render_template('profile.html',
                           user=user,
                           ordered=ordered,
                           accepted=accepted,
                           delivered=delivered,
                           logged_in=logged_in)


@app.route('/update-order', methods=['POST'])
def update_order():
    order_update = request.form.get('order_update')
    oid = request.form.get('oid')
    update(oid, order_update)
    return redirect(url_for('dashboard'))


@app.route("/view2", methods=["POST"])
def view2():
    uid = session.get('uid')
    utype = session["utype"]
    if not uid:
        return "User not logged in", 403

    oid = request.form.get('oid')
    temp = request.form.get('temp')
    pid = request.form.get('pid')
    rating = load_rating(pid)

    if not oid or not oid.isdigit():
        return "Invalid or missing order ID", 400

    oid = int(oid)

    # Mapping 'temp' values to their respective functions

    if utype == "Farmer":
        order_functions = {
            "1": load_full_order_details,
            "2": load_full_accepted_details,
            "3": load_full_delivered_details
        }
    else:
        order_functions = {
            "1": load_buyer_order_details,
            "2": load_buyer_accepted_details,
            "3": load_buyer_delivered_details
        }

    if temp not in order_functions:
        return "Invalid category", 400

    orders = order_functions[temp](uid)
    order = next((order for order in orders if order["oid"] == oid), None)

    if order:
        return render_template('view2.html',
                               order=order,
                               utype=utype,
                               temp=temp,
                               rating=rating)
    else:
        return "Order not found", 404


@app.route("/view")
def view():
    uid = session.get('uid')
    temp = request.args.get('temp')
    logged_in = "username" in session
    utype = session["utype"]
    # Mapping temp values to their respective functions
    if utype == "Farmer":
        order_functions = {
            "1": load_full_order_details,
            "2": load_full_accepted_details,
            "3": load_full_delivered_details
        }
    else:
        order_functions = {
            "1": load_buyer_order_details,
            "2": load_buyer_accepted_details,
            "3": load_buyer_delivered_details
        }
    if temp in order_functions:
        orders = order_functions[temp](uid)
        return render_template('view.html',
                               orders=orders,
                               logged_in=logged_in,
                               temp=int(temp),
                               utype=utype)

    return redirect(url_for('dashboard'))


@app.route("/products")
def products():
    logged_in = "username" in session
    products = load_products_from_db()
    return render_template('products.html',
                           products=products,
                           logged_in=logged_in)


@app.route("/add")
def add():
    return render_template('add.html')


@app.route("/Add", methods=["POST"])
def Add():
    data = request.form
    username = session["username"]
    uid = session["uid"]
    add_product_to_db(data, username, uid)
    return redirect(url_for('dashboard'))


@app.route("/accept", methods=["POST"])
def accept():
    oid = request.form.get('oid')
    pid = request.form.get('pid')
    quantity = request.form.get('quantity')
    accept_order(oid, pid, quantity)
    return redirect(url_for('dashboard'))


@app.route("/cancel", methods=["POST"])
def cancel():
    oid = request.form.get('oid')
    cancel_order(oid)
    return redirect(url_for('dashboard'))


@app.route('/delivered', methods=['POST'])
def delivered():
    rating = request.form.get('rating')
    oid = request.form.get('oid')
    pid = request.form.get('pid')
    delivered_order(oid, pid, rating)
    return redirect(url_for('dashboard'))


@app.route("/product")
def product():
    logged_in = "username" in session
    pid = request.args.get('pid')
    fid = request.args.get('fid')
    uid = session["uid"]
    if not pid:
        return "Product ID not provided", 400
    products = load_products_from_db()
    try:
        pid = int(pid)
        fid = int(fid)
    except ValueError:
        return "Invalid Product ID", 400
    users = load_UserD_from_db()
    user = next((u for u in users if u["uid"] == fid), None)
    pd = next((u for u in products if u["pid"] == pid), None)
    if pd is None:
        return "Product not found", 404
    return render_template('product.html',
                           pd=pd,
                           user=user,
                           logged_in=logged_in,
                           uid=uid)


@app.route('/placeorder', methods=['POST', 'GET', 'PUT'])
def placeorder():
    # Get values from request
    fid = request.form.get('fid')
    pid = request.form.get('pid')
    bid = session.get('uid')
    quantity = request.form.get('orderQuantity')
    price = request.form.get('Price')
    total_price = float(quantity) * float(price)

    add_orders_to_db(fid, pid, bid, quantity, total_price)

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    utype = session["utype"]
    uid = session["uid"]
    users = load_UserD_from_db()
    logged_in = "username" in session
    if (utype == "Farmer"):
        ordered = len(load_full_order_details(uid))
        accepted = len(load_full_accepted_details(uid))
        delivered = len(load_full_delivered_details(uid))
        products = load_fproducts_from_db(uid)
    else:
        ordered = len(load_buyer_order_details(uid))
        accepted = len(load_buyer_accepted_details(uid))
        delivered = len(load_buyer_delivered_details(uid))
        products = load_buyer_accepted_details(uid)

    user = next((u for u in users if u["uname"] == username), None)

    if user:
        if utype == "Farmer" or "Buyer":

            return render_template("dashboard.html",
                                   user=user,
                                   products=products,
                                   ordered=ordered,
                                   accepted=accepted,
                                   delivered=delivered,
                                   utype=utype,
                                   logged_in=logged_in)

        elif utype == "Admin":
            return redirect(url_for("home"))

    return redirect(url_for("login"))


@app.route("/check_user", methods=["POST"])
def check_user():
    username = request.form.get("uid")
    password = request.form.get("pwd")
    utype = request.form.get("utype")
    users = load_users_from_db()
    admins = load_admins_from_db()
    if utype == '3':
        user = next((u for u in admins if u["uname"] == username), None)
        if user:
            if user["pwd"] == password:
                session["username"] = username
                session["uid"] = user['uid']
                return redirect(url_for("admin"))
            else:
                error = "Incorrect password!"
        else:
            error = "User does not exist!"
    else:
        user = next((u for u in users if u["uname"] == username), None)
        if user:
            if user["pwd"] == password:
                session["username"] = username
                session["utype"] = user["utype"]
                session["uid"] = user['uid']
                return redirect(url_for("home"))
            else:
                error = "Incorrect password!"
        else:
            error = "User does not exist!"

    return render_template("log.html", error=error)


@app.route('/chat', methods=['GET'])
def chat():
    pid = int(request.args.get('pid'))
    fid = int(request.args.get('fid'))
    bid = int(request.args.get('bid'))
    uid = session.get("uid")
    if uid == fid:
        sid = fid
        rid = bid
        messages = load_message_from_db(sid, rid, pid)
        return render_template("chat.html",
                               sid=sid,
                               pid=pid,
                               rid=rid,
                               messages=messages)
    else:
        sid = bid
        rid = fid
        messages = load_message_from_db(sid, rid, pid)
        return render_template("chat.html",
                               sid=sid,
                               pid=pid,
                               rid=rid,
                               messages=messages)


@app.route('/register', methods=['POST'])
def register():
    try:
        # Fetch form data
        utype = request.form.get('utype')
        full_name = request.form.get('Full Name')
        dob = request.form.get('Date of Birth')
        email = request.form.get('Email')
        mobile_number = request.form.get('Mobile Number')
        gender = request.form.get('Gender')
        occupation = request.form.get('Occupation')
        id_type = request.form.get('ID Type')
        id_number = request.form.get('ID Number')
        issued_authority = request.form.get('Issued Authority')
        address_type = request.form.get('Address Type')
        nationality = request.form.get('Nationality')
        state = request.form.get('State')
        district = request.form.get('District')
        town_village = request.form.get('Town/Village')
        house_number = request.form.get('House Number')
        username = request.form.get('Username')
        password = request.form.get('Enter Password')
        confirm_password = request.form.get('Confirm Password')

        # Validate passwords match
        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400

        # Insert data into the database using a transactional scope
        with engine.begin(
        ) as conn:  # `begin` starts a transaction automatically
            conn.execute(
                text("""
                    INSERT INTO UserD (
                        utype, uname, dob, email, mobilno, gender, ocup,
                        idtype, idnumber, auth, adtype, nationality,
                        stat, dist, town, hno,status
                    ) VALUES (
                        :utype, :full_name, :dob, :email, :mobile_number, :gender, :occupation,
                        :id_type, :id_number, :issued_authority, :address_type, :nationality,
                        :state, :district, :town_village, :house_number,:status
                    )
                """), {
                    "utype": utype,
                    "full_name": full_name,
                    "dob": dob,
                    "email": email,
                    "mobile_number": mobile_number,
                    "gender": gender,
                    "occupation": occupation,
                    "id_type": id_type,
                    "id_number": id_number,
                    "issued_authority": issued_authority,
                    "address_type": address_type,
                    "nationality": nationality,
                    "state": state,
                    "district": district,
                    "town_village": town_village,
                    "house_number": house_number,
                    "status": 'Pending'
                })

        return jsonify({"message": "Registration successful"}), 201

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
