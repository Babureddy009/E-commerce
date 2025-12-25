from flask import Blueprint, render_template, session, redirect, request
from models.db import get_db

account_bp = Blueprint("account", __name__)

@account_bp.route("/account")
def account_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # ---------------- USER ----------------
    cursor.execute(
        "SELECT name, email FROM users WHERE id=%s",
        (uid,)
    )
    user = cursor.fetchone()

    # ---------------- ORDERS ----------------
    cursor.execute("""
        SELECT id, total, status, created_at
        FROM orders
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (uid,))
    orders = cursor.fetchall()

    # 🔥 FETCH PRODUCTS FOR EACH ORDER
    order_items_map = {}

    for o in orders:
        cursor.execute("""
            SELECT 
                product_name,
                price,
                quantity
            FROM order_items
            WHERE order_id=%s
        """, (o["id"],))

        order_items_map[o["id"]] = cursor.fetchall()

    # ---------------- ADDRESSES ----------------
    cursor.execute("""
        SELECT id, address, city, state, pincode
        FROM addresses
        WHERE user_id=%s
    """, (uid,))
    addresses = cursor.fetchall()

    return render_template(
        "account/dash.html",
        user=user,
        orders=orders,
        order_items_map=order_items_map,  # ✅ NEW
        addresses=addresses
    )


# ================= ADD ADDRESS =================
@account_bp.route("/account/add_address", methods=["POST"])
def add_address():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    address = request.form["address"]
    city = request.form["city"]
    state = request.form["state"]
    pincode = request.form["pincode"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO addresses (user_id, address, city, state, pincode)
        VALUES (%s,%s,%s,%s,%s)
    """, (uid, address, city, state, pincode))
    db.commit()

    return redirect("/account#addresses")


# ================= EDIT ADDRESS =================
@account_bp.route("/account/edit_address/<int:aid>")
def edit_address(aid):
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM addresses
        WHERE id=%s AND user_id=%s
    """, (aid, uid))
    address = cursor.fetchone()

    if not address:
        return redirect("/account")

    return render_template(
        "account/edit_address.html",
        address=address
    )


# ================= UPDATE ADDRESS =================
@account_bp.route("/account/update_address/<int:aid>", methods=["POST"])
def update_address(aid):
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    address = request.form["address"]
    city = request.form["city"]
    state = request.form["state"]
    pincode = request.form["pincode"]

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE addresses
        SET address=%s, city=%s, state=%s, pincode=%s
        WHERE id=%s AND user_id=%s
    """, (address, city, state, pincode, aid, uid))

    db.commit()
    return redirect("/account#addresses")


# ================= DELETE ADDRESS =================
@account_bp.route("/account/delete_address/<int:aid>")
def delete_address(aid):
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM addresses WHERE id=%s AND user_id=%s",
        (aid, uid)
    )
    db.commit()

    return redirect("/account#addresses")
