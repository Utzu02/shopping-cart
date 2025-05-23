
import json, os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
BASE_DIR = os.path.dirname(__file__)
DB_PATH  = os.path.join(BASE_DIR, "database", "shop.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "images")
ALLOWED_EXT = {"jpg", "jpeg", "png", "gif", "webp"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)

class Product(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(80))
    description = db.Column(db.Text)
    price       = db.Column(db.Float)
    category    = db.Column(db.String(40))
    image       = db.Column(db.String(120))
    author      = db.Column(db.String(60))
    sales       = db.Column(db.Integer, default=0)


class Order(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    full_name      = db.Column(db.String(80))
    email          = db.Column(db.String(120))
    phone          = db.Column(db.String(30))
    address        = db.Column(db.Text)
    payment_method = db.Column(db.String(20))
    total_price    = db.Column(db.Float)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    items          = db.relationship("OrderItem", backref="order", cascade="all, delete")


class OrderItem(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey("order.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity   = db.Column(db.Integer)
    price      = db.Column(db.Float)

with app.app_context():
    db.create_all()
    if not Product.query.first():
        try:
            with open(os.path.join(BASE_DIR, "products.json")) as f:
                for p in json.load(f):
                    db.session.add(Product(**p))
            db.session.commit()
            print("Products loaded into DB.")
        except Exception as e:
            print("Error loading products.json →", e)

@app.context_processor
def inject_cart_count():
    return {"cart_count": sum(session.get("cart", {}).values())}

def db_products_by_id():
    return {p.id: p for p in Product.query.all()}

@app.route("/")
def index():
    category = request.args.get("category")
    q = (request.args.get("q") or "").lower().strip()

    query = Product.query
    if category: query = query.filter_by(category=category)
    if q:        query = query.filter(
                    db.or_(Product.name.ilike(f"%{q}%"),
                           Product.description.ilike(f"%{q}%")))
    products = query.all()
    categories = sorted({p.category for p in Product.query.all()})
    return render_template("index.html", products=products,
                           categories=categories, selected_category=category,
                           q=q, active_page="home")

@app.route("/product/<int:prod_id>")
def product_page(prod_id):
    prod = Product.query.get_or_404(prod_id)
    return render_template("product.html", product=prod, active_page=None)

@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    prods = db_products_by_id()
    items, total = [], 0.0
    for pid, qty in cart.items():
        p = prods.get(int(pid))
        if p:
            sub = p.price * qty
            total += sub
            items.append({"id": p.id, "name": p.name, "price": p.price,
                          "quantity": qty, "subtotal": sub})
    return render_template("cart.html", cart_items=items,
                           total_price=total, active_page="cart")

@app.route("/cart/add-item")
def add_to_cart():
    pid = request.args.get("id", type=int)
    if not Product.query.get(pid):
        return redirect(url_for("index"))
    cart = session.setdefault("cart", {})
    cart[str(pid)] = cart.get(str(pid), 0) + 1
    session.modified = True
    return redirect(request.headers.get("Referer", url_for("view_cart")))
app.add_url_rule("/cart/add-item", "add_item", add_to_cart)

@app.route("/cart/remove-item")
def remove_from_cart():
    pid = request.args.get("id")
    session.get("cart", {}).pop(pid, None)
    session.modified = True
    return redirect(url_for("view_cart"))

@app.route("/cart/update-qty")
def update_qty():
    """
    ?id=<prod_id>&action=inc | dec
    sau   ?id=<prod_id>&qty=<nou_numar_int>
    """
    pid = request.args.get("id")
    if not pid or "cart" not in session:
        return redirect(url_for("view_cart"))

    cart = session["cart"]
    if pid not in cart:
        return redirect(url_for("view_cart"))

    action = request.args.get("action")
    qty    = request.args.get("qty", type=int)

    if action == "inc":
        cart[pid] += 1
    elif action == "dec":
        cart[pid] = max(1, cart[pid] - 1)
    elif qty is not None and qty > 0:
        cart[pid] = qty

    session.modified = True
    return redirect(url_for("view_cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = session.get("cart", {})
    if not cart and request.method == "GET":
        return redirect(url_for("view_cart"))

    def cart_summary():
        prods = db_products_by_id()
        items, ttl = [], 0.0
        for pid, qty in cart.items():
            p = prods.get(int(pid))
            if p:
                sub = p.price * qty
                ttl += sub
                items.append({"id": p.id, "name": p.name, "price": p.price,
                              "quantity": qty, "subtotal": sub})
        return items, ttl

    if request.method == "GET":
        items, ttl = cart_summary()
        return render_template("checkout.html", cart_items=items,
                               total_price=ttl, active_page="checkout")

    data = {k: request.form.get(k) for k in
            ("full_name", "email", "phone", "address", "payment_method")}
    if not all([data["full_name"], data["email"], data["address"], data["payment_method"]]):
        items, ttl = cart_summary()
        return render_template("checkout.html", cart_items=items,
                               total_price=ttl, error="Please complete all fields.",
                               active_page="checkout")

    items, ttl = cart_summary()
    order = Order(**data, total_price=ttl)
    db.session.add(order); db.session.flush() 
    for it in items:
        db.session.add(OrderItem(order_id=order.id, product_id=it["id"],
                                 quantity=it["quantity"], price=it["price"]))
        Product.query.get(it["id"]).sales += it["quantity"]
    db.session.commit()
    debug_order = {
        "full_name":      data["full_name"],
        "email":          data["email"],
        "phone":          data["phone"],
        "address":        data["address"],
        "payment_method": data["payment_method"],
        "items":          items,
        "total_price":    ttl,
        "timestamp":      datetime.utcnow().isoformat(timespec="seconds")
    }
    print("=== ORDER DEBUG ===")
    print(json.dumps(debug_order, indent=2))
    print("===================")
    print("New order stored in DB:", order.id)
    session["cart"] = {}; session.modified = True
    return render_template("order_confirm.html", order=order,
                           order_items=items, active_page=None)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = {k: request.form.get(k) for k in ("name", "email", "subject", "message")}
        print("=== CONTACT FORM ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("====================")
        return render_template("contact.html", success=True, active_page="contact")

    return render_template("contact.html", success=False, active_page="contact")


@app.route("/admin/products")
def admin_products():
    return render_template("admin_products.html", products=Product.query.all())

@app.route("/admin/products/new", methods=["POST"])
@app.route("/admin/products/new", methods=["POST"])
def add_product():
    file = request.files.get("image_file")
    if not file or file.filename == "" or not allowed(file.filename):
        return "Invalid image", 400
    fname = secure_filename(file.filename)
    ts    = datetime.now().strftime("%Y%m%d%H%M%S")
    fname = f"{ts}_{fname}"
    file.save(os.path.join(UPLOAD_DIR, fname))

    p = Product(
        name=request.form["name"],
        description=request.form["description"],
        category=request.form["category"],
        price=float(request.form["price"]),
        image=fname,
        author="Admin"
    )
    db.session.add(p); db.session.commit()
    return redirect(url_for("admin_products"))


@app.route("/admin/products/delete")
def delete_product():
    pid = request.args.get("pid", type=int)
    if pid:
        db.session.delete(db.session.get(Product, pid))
        db.session.commit()
    return redirect(url_for("admin_products"))

@app.route("/admin/orders")
def admin_orders():
    """
    Afișează toate comenzile salvate în DB, fiecare cu lista de produse.
    """
    orders = (Order.query
                    .order_by(Order.created_at.desc())
                    .all())
    return render_template("admin_orders.html", orders=orders, active_page=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

