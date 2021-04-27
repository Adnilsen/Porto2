from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key ='\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
oauth = OAuth(app)

oauth.register(
    name='google',
    client_id='352148568912-aqc8n7jb36af5ca1m0pi77p9f1vdca21.apps.googleusercontent.com',
    client_secret='3ylG_r5BdCaiZHmBiuz0wSbD',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email'}

)

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
    user_email = db.Column(db.String(100))

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(20))
    product_description = db.Column(db.String(45))
    product_long_description = db.Column(db.String(45))
    image_connection = db.relationship('Img', backref='order_image', lazy=True)
    product_price = db.Column(db.Integer)
    order_connections = db.relationship('Order', secondary=products, backref='product_order', lazy=True)



class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    user_connection = db.Column(db.String(100), db.ForeignKey('user.user_email'))
    order_price = db.Column(db.Integer)
    order_status = db.Column(db.Boolean, unique=False, default=True)
    order_date = db.Column(db.Date)

class Img(db.Model):
    img_id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    main_image = db.Column(db.Boolean, unique=False, default=True)
    product_connection = db.Column(db.Integer, db.ForeignKey('product.product_id'))

@app.route('/')
def home_page():

    email = dict(session).get('email', None)
    print(email)
    return render_template('index.html', content=email)

#Google oAuth2 login
@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()

    #Control that the user is not already registered!
    registered = False
    for user in User.query.all():
        if user.user_email == user_info['email']:
            registered = True
            break
    if not registered:
        user_input = User(first_name=user_info['given_name'], last_name=user_info['family_name'], user_type=False, user_email=user_info['email'])
        db.session.add(user_input)
        db.session.commit()
    # do something with the token and profile
    session['email'] = user_info['email']
    session['first_name'] = user_info['given_name']
    session['last_name'] = user_info['family_name']
    session['picture'] = user_info['picture']
    session['logged_in'] = True

    user_email = user_info['email']
    get_user = User.query.filter_by(user_email=user_email).first()
    session['user_id'] = get_user.user_id
    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


@app.route('/user')
def user_page():
    user1 = session.get('first_name')
    print(user1)
    return render_template("index.html", content=user1)


@app.route('/products')
def products_page():
    user = session.get('user')
    img = Img.query.first()
    productlist = Product.query.all()
    imagelist = Img.query.all()
    route = f"/static/{img.img}"
    return render_template("products.html", content=route, user=user, productlist=productlist, imagelist = imagelist)

@app.route('/profile')
def myprofile():
    if 'email' in session:
        email = session['email']
        orders = Order.query.filter_by(user_connection=email).all()
        return render_template("myprofile.html", orders=orders)
    else:
        return redirect('/login')

@app.route('/shoppingcart')
def shoppingcart():

    return render_template('shoppingcart.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_product():
    if request.method == "POST":
        name = request.form["product_name"]
        short = request.form["short_description"]
        long = request.form["long_description"]
        price = request.form["price"]
        new_product = Product(product_name=name, product_description=short, product_long_description=long, product_price=price)
        db.session.add(new_product)
        db.session.commit()
        if request.files:
            image = request.files["image"]
            image_name = image.filename
            image.save(os.path.join('static', 'images', image_name))
            new_image = Img(img=image_name, main_image=True)
            db.session.add(new_image)
            db.session.commit()
            new_product.image_connection.append(new_image)
            db.session.commit()
        return redirect(request.url)
    else:
        return render_template("newproduct.html")


#Create db with content
db.drop_all()
db.create_all()
user = User(first_name='Trym', last_name='Stenberg', user_type=True, user_email='ufhsaufhasf')
user2 = User(first_name='Andre', last_name='Knutsen', user_type=True, user_email='gdokaosfjoAPR')
user3 = User(first_name='Martin', last_name='Kvam', user_type=True, user_email='martin_kvam@hotmail.com')
db.session.add(user)
db.session.add(user2)
db.session.add(user3)
product = Product(product_name='Ball', product_description='Bra ball', product_long_description='Denne ballen er sykt bra', product_price=100)
product2 = Product(product_name='Strikk', product_description='Elastisk strikk', product_long_description='Denne strikken er sykt elastisk', product_price=400)
db.session.add(product)
db.session.add(product2)
order = Order(order_price=100, order_status=True, order_date=datetime.datetime.now().date())
order2 = Order(order_price=300, order_status=True, order_date=datetime.datetime.now().date(), user_connection="martin_kvam@hotmail.com")
db.session.add(order)
db.session.add(order2)
db.session.commit()

filename = secure_filename("ball1.png")
img = Img(img=filename, main_image=True)
db.session.add(img)
db.session.commit()
product.image_connection.append(img)
product.order_connections.append(order)
product2.order_connections.append(order)
user.order_connection.append(order)
db.session.commit()

app.run(host='0.0.0.0', debug=True)