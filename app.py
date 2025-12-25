import os
from flask import Flask
from config import SECRET_KEY
from blueprints.auth import auth_bp
from blueprints.product import product_bp
from blueprints.cart import cart_bp
from blueprints.order import order_bp
from blueprints.account import account_bp
app = Flask(__name__)
app.secret_key = SECRET_KEY

app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(order_bp)
app.register_blueprint(account_bp)



if __name__ == "__main__":
    app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    debug=False
)


