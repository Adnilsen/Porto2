from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

products = db.Table('products',
                    db.Column('product_id', db.Integer, db.ForeignKey('product.product_id')),
                    db.Column('order_id', db.Integer, db.ForeignKey('order.order_id'))
                 )

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    order_connection = db.relationship('Order', backref='user_order', lazy=True)
    user_type = db.Column(db.Boolean, unique=False, default=True)

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(20))
    product_description = db.Column(db.String(45))
    product_image = db.Column(db.String(100))
    order_connections = db.relationship('Order', secondary=products, backref='product_order', lazy=True)


class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    user_connection = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    order_price = db.Column(db.Integer)
    order_status = db.Column(db.Boolean, unique=False, default=True)
    order_date = db.Column(db.Date)



@app.route('/')
def home_page():

    return render_template("index.html")

@app.route('/products')
def products_page():
    print("yes")
    return render_template("products.html")


@app.route('/login')
def login_page():
    print("yes")
    return render_template("login.html")


@app.route('/profile')
def myprofile():
    orders = Order.query.all()
    return render_template("myprofile.html", orders=orders)



if __name__ == "__main__":
    db.create_all()
    user = User(first_name='Adrian', last_name='Nilsen', user_type=True)
    user2 = User(first_name='Andre', last_name='Knutsen', user_type=True)
    db.session.add(user)
    db.session.add(user2)
    order = Order(order_price=100, order_status=True, order_date=datetime.datetime.now().date())
    db.session.add(order)
    user.order_connection.append(order)
    db.session.commit()
    app.run(debug=True)
    """app.run(debug=True, host='0.0.0.0')"""
