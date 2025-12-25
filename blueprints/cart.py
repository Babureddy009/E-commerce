from flask import Blueprint, render_template, redirect, session, flash, request, jsonify
from models.db import get_db

cart_bp = Blueprint("cart", __name__)

# ==================================================
# ADD PRODUCT TO CART (NORMAL)
# ==================================================
@cart_bp.route("/add/<int:pid>")
def add_to_cart(pid):
    if "user_id" not in session:
        flash("Please login first")
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT quantity FROM cart WHERE user_id=%s AND product_id=%s",
        (uid, pid)
    )
    item = cursor.fetchone()

    if item:
        cursor.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE user_id=%s AND product_id=%s",
            (uid, pid)
        )
    else:
        cursor.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s,%s,1)",
            (uid, pid)
        )

    db.commit()
    return redirect("/cart")


# ==================================================
# VIEW CART
# ==================================================
@cart_bp.route("/cart")
def view_cart():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            c.product_id,
            c.quantity,
            p.name,
            p.price,
            (p.price * c.quantity) AS total_price
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (uid,))

    items = cursor.fetchall()

    cart_total = sum(item["total_price"] for item in items)
    total_items = sum(item["quantity"] for item in items)

    # ✅ PLATFORM FEE LOGIC
    if total_items > 0:
        platform_fee = 7
    else:
        platform_fee = 0

    grand_total = cart_total + platform_fee

    return render_template(
        "cart/cart.html",
        items=items,
        cart_total=cart_total,
        total_items=total_items,
        platform_fee=platform_fee,
        grand_total=grand_total
    )


# ==================================================
# REMOVE ITEM (USED IN CART + CHECKOUT)
# ==================================================
@cart_bp.route("/remove/<int:pid>")
def remove_item(pid):
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM cart WHERE user_id=%s AND product_id=%s",
        (uid, pid)
    )
    db.commit()

    return redirect(request.referrer or "/cart")


# ==================================================
# CLEAR CART
# ==================================================
@cart_bp.route("/clear_cart")
def clear_cart():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM cart WHERE user_id=%s", (uid,))
    db.commit()

    return redirect("/cart")


# ==================================================
# AJAX CART APIs (PRODUCT LISTING)
# ==================================================
@cart_bp.route("/api/cart/add", methods=["POST"])
def api_add_to_cart():
    if "user_id" not in session:
        return jsonify({"error": "login_required"}), 401

    pid = request.json["product_id"]
    uid = session["user_id"]

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT quantity FROM cart WHERE user_id=%s AND product_id=%s",
        (uid, pid)
    )
    item = cursor.fetchone()

    if not item:
        cursor.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s,%s,1)",
            (uid, pid)
        )
        qty = 1
    else:
        qty = item["quantity"]

    db.commit()
    return jsonify({"quantity": qty})


@cart_bp.route("/api/cart/update", methods=["POST"])
def api_update_cart():
    if "user_id" not in session:
        return jsonify({"error": "login_required"}), 401

    pid = request.json["product_id"]
    action = request.json["action"]
    uid = session["user_id"]

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT quantity FROM cart WHERE user_id=%s AND product_id=%s",
        (uid, pid)
    )
    item = cursor.fetchone()

    if not item:
        return jsonify({"quantity": 0})

    qty = item["quantity"]

    if action == "plus":
        qty += 1
    elif action == "minus":
        qty -= 1

    if qty <= 0:
        cursor.execute(
            "DELETE FROM cart WHERE user_id=%s AND product_id=%s",
            (uid, pid)
        )
        db.commit()
        return jsonify({"quantity": 0})

    cursor.execute(
        "UPDATE cart SET quantity=%s WHERE user_id=%s AND product_id=%s",
        (qty, uid, pid)
    )
    db.commit()

    return jsonify({"quantity": qty})


# ==================================================
# BUY NOW → DIRECT CHECKOUT
# ==================================================
@cart_bp.route("/buy_now/<int:pid>")
def buy_now(pid):
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT quantity FROM cart WHERE user_id=%s AND product_id=%s",
        (uid, pid)
    )
    item = cursor.fetchone()

    if not item:
        cursor.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s,%s,1)",
            (uid, pid)
        )
        db.commit()

    return redirect("/checkout")


# ==================================================
# CHECKOUT PAGE QTY UPDATE (+ / -)
# ==================================================
@cart_bp.route("/cart/update/<int:pid>/<action>")
def update_cart_from_checkout(pid, action):
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT quantity FROM cart WHERE user_id=%s AND product_id=%s",
        (uid, pid)
    )
    item = cursor.fetchone()

    if not item:
        return redirect("/checkout")

    qty = item["quantity"]

    if action == "plus":
        qty += 1
    elif action == "minus":
        qty -= 1

    if qty <= 0:
        cursor.execute(
            "DELETE FROM cart WHERE user_id=%s AND product_id=%s",
            (uid, pid)
        )
    else:
        cursor.execute(
            "UPDATE cart SET quantity=%s WHERE user_id=%s AND product_id=%s",
            (qty, uid, pid)
        )

    db.commit()
    return redirect("/checkout")
