from flask import Blueprint, render_template, session, redirect, request
from models.db import get_db

order_bp = Blueprint("order", __name__)

# ==========================================
# CHECKOUT PAGE
# ==========================================

@order_bp.route("/checkout")
def checkout():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Cart items
    cursor.execute("""
        SELECT 
            p.id AS product_id,
            p.name,
            p.image,
            p.price,
            c.quantity,
            (p.price * c.quantity) AS total
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (uid,))
    items = cursor.fetchall()

    total_price = sum(i["total"] for i in items)
    total_items = sum(i["quantity"] for i in items)
    platform_fee = 7 if total_items > 0 else 0
    grand_total = total_price + platform_fee

    # 🔥 ALL ADDRESSES
    cursor.execute("""
        SELECT id, address, city, state, pincode
        FROM addresses
        WHERE user_id=%s
    """, (uid,))
    addresses = cursor.fetchall()

    # 🔥 SELECTED ADDRESS
    selected_address_id = session.get("selected_address_id")

    if selected_address_id:
        cursor.execute("""
            SELECT * FROM addresses
            WHERE id=%s AND user_id=%s
        """, (selected_address_id, uid))
        address = cursor.fetchone()
    else:
        address = addresses[0] if addresses else None
    # after fetching addresses
    

    return render_template(
        "order/checkout.html",
        items=items,
        total_items=total_items,
        total_price=total_price,
        platform_fee=platform_fee,
        grand_total=grand_total,
        address=address,
        addresses=addresses
        
    )

@order_bp.route("/checkout/select_address/<int:aid>")
def select_address(aid):
    if "user_id" not in session:
        return redirect("/login")

    session["selected_address_id"] = aid
    return redirect("/checkout")



# ==========================================
# PLACE ORDER
# ==========================================
@order_bp.route("/place_order", methods=["POST"])
def place_order():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    payment_method = request.form.get("payment_method")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 1️⃣ Get cart items
    cursor.execute("""
        SELECT 
            c.product_id,
            p.name,
            p.price,
            c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id=%s
    """, (uid,))
    cart_items = cursor.fetchall()

    if not cart_items:
        return redirect("/cart")

    # 2️⃣ Calculate total
    total_amount = sum(i["price"] * i["quantity"] for i in cart_items)

    address_id = session.get("selected_address_id")

    # 3️⃣ Insert order
    cursor.execute("""
        INSERT INTO orders (user_id, address_id, total, status)
        VALUES (%s, %s, %s, %s)
    """, (uid, address_id, total_amount, f"Placed ({payment_method})"))

    order_id = cursor.lastrowid  # 🔥 VERY IMPORTANT

    # 4️⃣ Insert order items
    for item in cart_items:
        cursor.execute("""
            INSERT INTO order_items 
            (order_id, product_id, product_name, price, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            order_id,
            item["product_id"],
            item["name"],
            item["price"],
            item["quantity"]
        ))

    # 5️⃣ Clear cart
    cursor.execute("DELETE FROM cart WHERE user_id=%s", (uid,))
    db.commit()

    session.pop("selected_address_id", None)

    return render_template("order/success.html", payment_method=payment_method)

# ==========================================
# PAYMENT PAGE
# ==========================================
@order_bp.route("/payment")
def payment():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get cart totals
    cursor.execute("""
        SELECT 
            SUM(p.price * c.quantity) AS total_price,
            SUM(c.quantity) AS total_items
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id=%s
    """, (uid,))

    result = cursor.fetchone()

    total_price = result["total_price"] or 0
    total_items = result["total_items"] or 0

    # ✅ Apply platform fee ONLY if items exist
    if total_items > 0:
        platform_fee = 7
    else:
        platform_fee = 0

    grand_total = total_price + platform_fee

    return render_template(
        "order/payment.html",
        total_price=total_price,
        platform_fee=platform_fee,
        grand_total=grand_total
    )


