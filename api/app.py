from flask import Flask, request, jsonify, redirect, url_for, render_template, session, flash
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

#Sqlalchemy database
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
    product_color = db.Column(db.String(45))
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

#API
@app.route('/')
def products_page():
    user = session.get('user')
    img = Img.query.first()
    productlist = Product.query.all()
    imagelist = Img.query.all()
    route = f"/static/{img.img}"
    return render_template("products.html", content=route, user=user, productlist=productlist, imagelist = imagelist)

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
    session['user_type'] = get_user.user_type
    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


@app.route('/users')
def user_page():
    users = User.query.all()
    output = []

    for user in users:
        user_data = {'user_id': user.user_id, 'first_name': user.first_name}
        output.append(user_data)

    return {"users": output}


@app.route('/orders/<user_id>/pending')
def get_orders(user_id):

    orders = Order.query.filter_by(order_status=True).all()
    output = []

    for order in orders:
        order_data = {'order_id': order.order_id, 'user_connection': order.user_connection, 'order_price': order.order_price,
                      'order_status':order.order_status, 'order_date':order.order_date}
        output.append(order_data)

    return {"orders": output}


@app.route('/profile')
def myprofile():
    if 'email' in session:
        if 'user_type' in session and session['user_type'] is True:
            return redirect(url_for('admin'))
        else:
            email = session['email']
            orders = Order.query.filter_by(user_connection=email).all()
            return render_template("myprofile.html", orders=orders)
    else:
        return redirect('/login')


@app.route('/shoppingcart') #Show shopping cart page
def shoppingcart():
    return render_template('shoppingcart.html')

@app.route('/order/<order_id>') #Get the order
def getOrder(order_id):
    order1 = Order.query.first()
    return order1

@app.route('/order/<order_id>/products') #Get the products in the order
def getOrderProducts(order_id):
    order1 = Order.query.first()
    orderID = order1.order_id
    output = []

    for product in order1.product_order:
        product_data = {'product_id': product.product_id, 'product_name': product.product_name, 'product_color': product.product_color, 'product_price': product.product_price}
        output.append(product_data)

    return {"products": output}

@app.route('/admin')
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_type' in session and session['user_type'] is True :
        if request.method == "POST":
            name = request.form["product_name"]
            short = request.form["short_description"]
            long = request.form["long_description"]
            price = request.form["price"]
            if name != '' and short != '' and long != '' and price != '':
                new_product = Product(product_name=name, product_description=short, product_long_description=long, product_price=price)
                db.session.add(new_product)
                db.session.commit()
                files = request.files.getlist('image')
                images = []
                for file in files:
                    if filecheck(file.filename):
                        images.append(file)
                    else:
                        flash("Accepted file types are: jpg, jpeg and png. One or more of your files were rejected")
                if len(images) == 0:
                    return render_template("newproduct.html")
                first = images[0]
                if first.filename != '':  # If there is one or more images attached
                    if filecheck(first.filename):
                        main_image = secure_filename(first.filename)
                        first.save(os.path.join('static', 'images', main_image))
                        new_image = Img(img=main_image, main_image=True)
                        db.session.add(new_image)
                        db.session.commit()
                        new_product.image_connection.append(new_image)
                        db.session.commit()
                    for image in images[1:]: # All other images are added to the database, but not as main image
                        if filecheck(image.filename):
                            image_name = secure_filename(image.filename)
                            image.save(os.path.join('static', 'images', image_name))
                            new_image = Img(img=image_name, main_image=False)
                            db.session.add(new_image)
                            db.session.commit()
                            new_product.image_connection.append(new_image)
                            db.session.commit()
                return redirect(request.url)
            else:
                flash("All fields must be filled")
                return render_template("newproduct.html")
        else:
            return render_template("newproduct.html")
    else:
        return redirect(url_for('home_page'))


def filecheck(file):
    allowed_types = {'jpg', 'jpeg', 'png'}
    type = file.split('.')[-1].lower()
    if type in allowed_types:
        return True
    else:
        return False


#Create db with content
db.drop_all()
db.create_all()
user = User(first_name='Trym', last_name='Stenberg', user_type=True, user_email='ufhsaufhasf')
user2 = User(first_name='Andre', last_name='Knutsen', user_type=True, user_email='gdokaosfjoAPR')
user3 = User(first_name='Martin', last_name='Kvam', user_type=True, user_email='martin_kvam@hotmail.com')
user4 = User(first_name='Adrian', last_name='Nilsen', user_type=True, user_email='adrian1995nils1@gmail.com')
db.session.add(user)
db.session.add(user2)
db.session.add(user3)
db.session.add(user4)
product = Product(product_name='Ball', product_description='Bra ball', product_color = 'Black/white', product_long_description='Denne ballen er sykt bra', product_price=100)
product2 = Product(product_name='Strikk', product_description='Elastisk strikk', product_long_description='Denne strikken er sykt elastisk', product_price=400)
product3 = Product(product_name='Sko', product_description='Løpesko', product_long_description='God allround løpesko til hardt underlag', product_price=700)
product4 = Product(product_name='Jakke', product_description='Allværsjakke vanntett', product_long_description='Vanntett skalljakke. Perfekt til turer i skog og mark. Vantett med vannsøyle på 15.000 med god pusteevne', product_price=1200)
db.session.add(product)
db.session.add(product2)
db.session.add(product3)
db.session.add(product3)
order = Order(order_price=100, order_status=True, order_date=datetime.datetime.now().date())
order2 = Order(order_price=300, order_status=True, order_date=datetime.datetime.now().date(), user_connection="martin_kvam@hotmail.com")
db.session.add(order)
db.session.add(order2)
db.session.commit()

filename = secure_filename("ball1.png")
img = Img(img=filename, main_image=True)
db.session.add(img)
filename2 = secure_filename("strikk.jpg")
img2 = Img(img=filename2, main_image=True)
db.session.add(img2)
filename3 = secure_filename("sko.jpg")
img3 = Img(img=filename3, main_image=True)
db.session.add(img3)
filename4 = secure_filename("jakke.jpg")
img4 = Img(img=filename4, main_image=True)
db.session.add(img4)
db.session.commit()
product.image_connection.append(img)
product2.image_connection.append(img2)
product3.image_connection.append(img3)
product4.image_connection.append(img4)
product.order_connections.append(order)
product.order_connections.append(order2)
product2.order_connections.append(order)
user.order_connection.append(order)
db.session.commit()

app.run(host='0.0.0.0', debug=True)