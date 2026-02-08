from flask import Flask, render_template, request, redirect, session, flash
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret-key"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# =====================
# DATABASE
# =====================
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# =====================
# LOGIN ADMIN
# =====================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user:
            session["admin"] = True
            flash("Login efetuado com sucesso!")
            return redirect("/admin")
        else:
            flash("Usuário ou senha incorretos.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Você saiu da conta.")
    return redirect("/login")

# =====================
# HOME
# =====================
@app.route("/")
def home():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("home.html", products=products)

# =====================
# ADMIN
# =====================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "admin" not in session:
        flash("Faça login para acessar o admin.", "error")
        return redirect("/login")
    
    db = get_db()
    
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        stock = request.form["stock"]
        image = request.files["image"]

        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        db.execute(
            "INSERT INTO products (name, price, image, stock) VALUES (?, ?, ?, ?)",
            (name, price, filename, stock)
        )
        db.commit()
        flash(f"Produto '{name}' cadastrado com sucesso!")

    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("admin.html", products=products)

# =====================
# ADD TO CART
# =====================
@app.route("/add-to-cart/<int:id>")
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = {}

    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()

    if product and product["stock"] > 0:
        pid = str(id)
        if pid in session["cart"]:
            session["cart"][pid]["qty"] += 1
        else:
            session["cart"][pid] = {
                "name": product["name"],
                "price": float(product["price"]),
                "image": product["image"],
                "qty": 1
            }
        session.modified = True
        flash(f"{product['name']} adicionado ao carrinho!")
    else:
        flash("Produto sem estoque.", "error")

    return redirect("/")

# =====================
# CART
# =====================
@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    total = sum(item["price"] * item["qty"] for item in cart.values())
    return render_template("cart.html", cart=cart, total=total)

# =====================
# REMOVE ITEM
# =====================
@app.route("/remove/<id>")
def remove(id):
    cart = session.get("cart", {})
    cart.pop(id, None)
    session["cart"] = cart
    flash("Item removido do carrinho.")
    return redirect("/cart")

if __name__ == "__main__":
    app.run(debug=True)
