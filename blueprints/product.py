from flask import Blueprint, render_template, request
from models.db import get_db
from flask import Blueprint, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
import os
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from models.db import get_db
from flask import request
product_bp = Blueprint("product", __name__)



@product_bp.route("/")
def index():
    search_query = request.args.get("search", "")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if search_query:
        cursor.execute("""
            SELECT p.*, c.name AS category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.name LIKE %s
               OR p.description LIKE %s
               OR c.name LIKE %s
            ORDER BY c.id
        """, (
            f"%{search_query}%",
            f"%{search_query}%",
            f"%{search_query}%"
        ))
    else:
        cursor.execute("""
            SELECT p.*, c.name AS category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            ORDER BY c.id
        """)

    products = cursor.fetchall()

    # Group by category
    categorized_products = {}
    for p in products:
        categorized_products.setdefault(p["category_name"], []).append(p)

    return render_template(
        "products/index.html",
        categorized_products=categorized_products,
        search_query=search_query
    )


@product_bp.route("/product/<int:id>")
def detail(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id=%s",(id,))
    product = cursor.fetchone()
    return render_template("products/detail.html", product=product)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@product_bp.route("/admin/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        desc = request.form["description"]
        category_id = request.form["category_id"]
        image = request.files["image"]

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))

            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO products (name, price, description, category_id, image)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, price, desc, category_id, filename))

            db.commit()
            flash("Product added successfully")
            return redirect("/")

        flash("Invalid image file")


    return render_template("admin/add_product.html")
