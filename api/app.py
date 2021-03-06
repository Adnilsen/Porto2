from flask import Flask, request, jsonify, redirect, url_for, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
from prometheus_flask_exporter import PrometheusMetrics
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key ='\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
oauth = OAuth(app)
metrics = PrometheusMetrics(app, path='/metrics')

metrics.info("app_info", "Info about the app")

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
google_token = ""

#Sqlalchemy database

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
    order_connections = db.relationship('OrderProduct', backref='product_order', lazy=True)


class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    user_connection = db.Column(db.String(100), db.ForeignKey('user.user_email'))
    order_price = db.Column(db.Integer)
    order_status = db.Column(db.Boolean, unique=False, default=True)
    order_date = db.Column(db.Date)
    product_connections = db.relationship('OrderProduct', backref='order_product', lazy=True)

class Img(db.Model):
    img_id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    main_image = db.Column(db.Boolean, unique=False, default=True)
    product_connection = db.Column(db.Integer, db.ForeignKey('product.product_id'))

class OrderProduct(db.Model):
    connection_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    product_amount = db.Column(db.Integer)
#API

@app.before_request
def before_request():
    # If the request is secure it should already be https, so no need to redirect
    if not request.is_secure:
        currentUrl = request.url
        if currentUrl.startswith('http://'):
            redirectUrl = currentUrl.replace('http://', 'https://', 1)
        elif currentUrl.startswith('localhost'):
            redirectUrl = currentUrl.replace('localhost', 'https://localhost', 1)
        elif currentUrl.startswith('0.0.0.0'):
            redirectUrl = currentUrl.replace('0.0.0.0', 'https://0.0.0.0', 1)
        elif currentUrl.startswith('127.0.0.1'):
            redirectUrl = currentUrl.replace('127.0.0.1', 'https://127.0.0.1', 1)
        else:
            # I do not now when this may happen, just for safety
            redirectUrl = 'https://localhost:5000'
        code = 301
        return redirect(redirectUrl, code=code)

@app.route('/') #Redirect to main page
def products_page():
    user = session.get('user')
    img = Img.query.first()
    productlist = Product.query.all()
    imagelist = Img.query.all()
    route = f"/static/{img.img}"
    return render_template("products.html", content=route, user=user, productlist=productlist, imagelist=imagelist)

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
    print(user_info)

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
    session['profile'] = user_info
    session['email'] = user_info['email']
    session['first_name'] = user_info['given_name']
    session['last_name'] = user_info['family_name']
    picture_string = "{}".format(user_info['picture'])
    session['picture'] = picture_string.replace("96", "1000")
    session['logged_in'] = True

    user_email = user_info['email']
    get_user = User.query.filter_by(user_email=user_email).first()
    session['user_id'] = get_user.user_id
    session['user_type'] = get_user.user_type

    return redirect('/')


@app.route('/logout') #Log out as user
def logout():
    for key in list(session.keys()):
        session.pop(key)
    session.clear()
    return redirect('/')


@app.route('/loggedInn') #The frontend needs to know if a user is logged in
def loggedInn():
    try:
        session['logged_in']
        return 'true'
    except Exception as e:
        return 'false'


def updateOrderPrice(): #Updates the price of a order
    order_id = session['current_order']
    totalPrice = 0
    for order in OrderProduct.query.filter_by(order_id=order_id).all():
        product = Product.query.filter_by(product_id=order.product_id).first()
        totalPrice += (order.product_amount*product.product_price)
    order = Order.query.filter_by(order_id=order_id).first()
    order.order_price = totalPrice
    db.session.commit()

@app.route('/orders/<user_id>/')
def get_orders(user_id):
    user = User.query.filter_by(user_id=user_id)
    email = db.session.query(User.user_email).filter_by(user_id=user_id)
    orders = Order.query.filter_by(user_connection=email).all()
    return render_template('orders.html', orders=orders, user=user)

@app.route('/order') #Creates a new order
def create_order():
    newOrder = Order(order_price=0, order_status=False, order_date=datetime.datetime.now().date(), user_connection=session['email'])
    db.session.add(newOrder)
    db.session.commit()
    session['current_order'] = newOrder.order_id
    return 'true'

@app.route('/order/current/<product_id>') #Add a product to the order
def add_product_order(product_id):
    order_product = OrderProduct(product_amount=1)
    choosen_product = Product.query.filter_by(product_id=product_id).first()
    currentOrder = Order.query.filter_by(order_id=session['current_order']).first()
    choosen_product.order_connections.append(order_product)
    currentOrder.product_connections.append(order_product)
    db.session.commit()
    if controll_order(currentOrder, choosen_product) < 3:
        print(f'---A {choosen_product.product_name} was added to order with id {currentOrder.order_id} ---')
    updateOrderPrice()
    return 'true'

def controll_order(currentOrder, choosen_product): #Controls the products in the order, delete duplicates and sum up amount
    productOrder = OrderProduct.query.filter_by(order_id = currentOrder.order_id, product_id= choosen_product.product_id)
    counter = 1
    totalProducts = 0
    for order in productOrder:
        if counter > 1: #If there are two or more of the filtered order it will sum up the amounts and delete duplicates in db
            totalProducts += order.product_amount
            db.session.delete(order)
            db.session.commit()
            print(f"---Order {order.order_id} updated product count for product {order.product_id}({choosen_product.product_name}) to: {totalProducts}---")
        else:
            totalProducts += order.product_amount
        counter += 1
    productOrder = OrderProduct.query.filter_by(order_id=currentOrder.order_id, product_id=choosen_product.product_id).first()
    productOrder.product_amount = totalProducts
    db.session.commit()
    return counter

@app.route('/order/unfinished/<status_id>') #Gets last unfinished order
def start_unfinished_order(status_id):
    if(status_id == "0"):
        retrievedOrder = Order.query.filter_by(user_connection=session['email'], order_status=False).first()
        if retrievedOrder == None:
            return 'false'
        return 'true'
    else:
        retrievedOrder = Order.query.filter_by(user_connection=session['email'], order_status=False).first()
        session['current_order'] = retrievedOrder.order_id
        return 'true'


@app.route('/order/delete')  # Delete current order
def delete_current_order():
    retrievedOrder = Order.query.filter_by(user_connection=session['email'], order_status=False).first()
    for order in OrderProduct.query.filter_by(order_id=retrievedOrder.order_id).all():
        db.session.delete(order)
    db.session.delete(retrievedOrder)
    db.session.commit()
    return 'true'

@app.route('/order/current/<product_id>/<product_amount>') #Update a single product count
def update_order_product_count(product_id, product_amount):
    order_product_connection = OrderProduct.query.filter_by(order_id=session['current_order'], product_id=product_id).first()
    order_product_connection.product_amount = product_amount
    db.session.commit()
    updateOrderPrice()
    return 'true'

@app.route('/order/current/delete/<product_id>') #Delete product from order
def delete_product_from_order(product_id):

    OrderProduct.query.filter_by(order_id=session['current_order'], product_id=product_id).delete()
    db.session.commit()
    updateOrderPrice()
    return 'true'

@app.route('/order/count') #Get the amount of different products in the current order
def get_product_count():
    try:
        produts_counted = OrderProduct.query.filter_by(order_id=session['current_order']).count()
        return f'{produts_counted}'
    except Exception:
        return "0"

@app.route('/order/checkout') #Finish order
def finish_order():
    order = Order.query.filter_by(order_id=session['current_order']).first()
    order.order_status = True
    db.session.commit()
    session['current_order'] = ""
    return 'true'

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

@app.route('/order/products') #Get the products in the order
def getOrderProduct():
    output = []
    for order in OrderProduct.query.filter_by(order_id=session['current_order']).all():
        product = Product.query.filter_by(product_id=order.product_id).first()
        image = Img.query.filter_by(product_connection=order.product_id).first()
        if image:
            product_data = {'product_id': product.product_id, 'product_name': product.product_name, 'product_color': product.product_color, 'product_price': product.product_price, 'product_amount': order.product_amount, 'product_image': image.img}
        else:
            product_data = {'product_id': product.product_id, 'product_name': product.product_name,
                            'product_color': product.product_color, 'product_price': product.product_price,
                            'product_amount': order.product_amount, 'product_image': 'placeholder.png'}
        output.append(product_data)

    return {"products": output}


@app.route('/order/<order_id>/products') #Get the products in the order
def getOrderProducts(order_id):
    output = []

    for order in OrderProduct.query.filter_by(order_id=order_id).all():
        product = Product.query.filter_by(product_id=order.product_id).first()
        image = Img.query.filter_by(product_connection=order.product_id).first()
        if image:
            product_data = {'product_id': product.product_id, 'product_name': product.product_name, 'product_color': product.product_color, 'product_price': product.product_price, 'product_amount': order.product_amount, 'product_image': image.img}
        else:
            product_data = {'product_id': product.product_id, 'product_name': product.product_name,
                            'product_color': product.product_color, 'product_price': product.product_price,
                            'product_amount': order.product_amount, 'product_image': 'placeholder.png'}
        output.append(product_data)

    return render_template("vieworder.html", products=output, order=order_id)


@app.route('/admin')
def admin():
    if 'user_type' in session and session['user_type'] is True:
        users = User.query.order_by(User.last_name)
        return render_template('admin.html', users=users)
    else:
        return redirect(url_for('products_page'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_type' in session and session['user_type'] is True :  # Only admins that are logged in will reach this page
        if request.method == "POST":
            name = request.form["product_name"]  # Get the info from the form
            short = request.form["short_description"]
            long = request.form["long_description"]
            price = request.form["price"]
            color = request.form['color']
            if name != '' and short != '' and long != '' and price != '':  # If all required fields are filled a new product is added to database
                if color != '':
                    new_product = Product(product_name=name, product_description=short, product_long_description=long, product_price=price, product_color=color)
                else:
                    new_product = Product(product_name=name, product_description=short, product_long_description=long, product_price=price)
                db.session.add(new_product)
                db.session.commit()
                files = request.files.getlist('image')  # Gets all files uploaded in the form
                if files[0].filename == '':  # No file attached
                    flash("The product was uploaded without a picture", category='info')
                    return render_template("newproduct.html")
                else:  # If there where files uploaded
                    images = []  # List of images that will be added to product
                    for file in files:  # Loops through all files to see if they are correct format
                        if filecheck(file.filename):
                            images.append(file)
                        else:  # If a file is incorrect, a message is displayed
                            flash("Accepted file types are: jpg, jpeg and png. One or more of your pictures were rejected", category='warning')
                    if len(images) > 0: # One or more pictures of correct types are added
                        first = images[0]
                        main_image = secure_filename(first.filename) # The first image is set as main image
                        first.save(os.path.join('static', 'images', main_image))  # First image saved to filesystem
                        new_image = Img(img=main_image, main_image=True)  # Reference to the image is saved in database
                        db.session.add(new_image)
                        db.session.commit()
                        new_product.image_connection.append(new_image)
                        db.session.commit()
                        for image in images[1:]: # All other images are added to the database, but not as main image
                            image_name = secure_filename(image.filename)
                            image.save(os.path.join('static', 'images', image_name))
                            new_image = Img(img=image_name, main_image=False)
                            db.session.add(new_image)
                            db.session.commit()
                            new_product.image_connection.append(new_image)
                            db.session.commit()
                    flash('The product was succesfully uploaded', category='info')
                    return render_template('newproduct.html')
            else:  # If some of the fields are not filled
                flash("All required fields are not filled", category='danger')
                return render_template("newproduct.html")
        else:  # If the request is a get request
            return render_template("newproduct.html")
    else:  # If the user is not logged in, or does not have admin rights they are redirected to homepage
        return redirect(url_for('home_page'))


def filecheck(file):  # Method that checks if files are of correct types
    allowed_types = {'jpg', 'jpeg', 'png'}
    type = file.split('.')[-1].lower()  # This splits the filename on . to find the extension
    if type in allowed_types:
        return True
    else:
        return False


'''#Create db with content
db.drop_all()
db.create_all()
user = User(first_name='Ola', last_name='Nordmann', user_type=True, user_email='onordenmann@gmail.com')
db.session.add(user)
db.session.commit()


product10 = Product(product_name='Football', product_description='Football', product_long_description='Nice and cheap football for play and practice', product_price=40, product_color="Black/white")
db.session.add(product10)

img101 = Img(img=secure_filename("football1.jpg"), main_image=True)
db.session.add(img101)
img102 = Img(img=secure_filename("football2.jpg"), main_image=False)
db.session.add(img102)

product10.image_connection.append(img101)
product10.image_connection.append(img102)

product20 = Product(product_name='Boxing gloves', product_description='Starter boxing gloves', product_long_description='Sporty lightweight boxing gloves for beginners, perfect for junior and up', product_price=100, product_color="Blue")
db.session.add(product20)

img201 = Img(img=secure_filename("boxing1.jpg"), main_image=True)
db.session.add(img201)
img202 = Img(img=secure_filename("boxing2.jpg"), main_image=False)
db.session.add(img202)
img203 = Img(img=secure_filename("boxing3.jpg"), main_image=False)
db.session.add(img203)
img204 = Img(img=secure_filename("boxing4.jpg"), main_image=False)
db.session.add(img204)

product20.image_connection.append(img201)
product20.image_connection.append(img202)
product20.image_connection.append(img203)
product20.image_connection.append(img204)

product30 = Product(product_name='Yoga mat', product_description='Colorful yoga mat', product_long_description='Lightweight, non slip mat for yoga. Can also be used for exercise', product_price=40, product_color="Multi")
db.session.add(product30)

img301 = Img(img=secure_filename("yogamat1.jpg"), main_image=True)
db.session.add(img301)
img302 = Img(img=secure_filename("yogamat2.jpg"), main_image=False)
db.session.add(img302)
img303 = Img(img=secure_filename("yogamat3.jpg"), main_image=False)
db.session.add(img303)

product30.image_connection.append(img301)
product30.image_connection.append(img302)
product30.image_connection.append(img303)

product40 = Product(product_name='Kettlebell', product_description='12 kg kettlebell', product_long_description='12 kg kettlebell for exercise. Perfect for strength workout, can be used for multiple exercices', product_price=100, product_color="Orange")
db.session.add(product40)

img401 = Img(img=secure_filename("kettlebell1.jpg"), main_image=True)
db.session.add(img401)
img402 = Img(img=secure_filename("kettlebell2.jpg"), main_image=False)
db.session.add(img402)
img403 = Img(img=secure_filename("kettlebell3.jpg"), main_image=False)
db.session.add(img403)

product40.image_connection.append(img401)
product40.image_connection.append(img402)
product40.image_connection.append(img403)

product50 = Product(product_name='Sunglasses', product_description='Stylish sunglasses', product_long_description='Stylish sunglasses with full UV protection', product_price=200, product_color="Orange")
db.session.add(product50)

img501 = Img(img=secure_filename("sunglass1.jpg"), main_image=True)
db.session.add(img501)
img502 = Img(img=secure_filename("sunglass2.jpg"), main_image=False)
db.session.add(img502)

product50.image_connection.append(img501)
product50.image_connection.append(img502)

product60 = Product(product_name='World Cup football', product_description='Original World Cup ball', product_long_description='Original professional world cup football. Perfect for matches, games and training.', product_price=150, product_color="Multi")
db.session.add(product60)

img601 = Img(img=secure_filename("wcball1.jpg"), main_image=True)
db.session.add(img601)
img602 = Img(img=secure_filename("wcball2.jpg"), main_image=False)
db.session.add(img602)
img603 = Img(img=secure_filename("wcball3.jpg"), main_image=False)
db.session.add(img603)

product60.image_connection.append(img601)
product60.image_connection.append(img602)
product60.image_connection.append(img603)

product70 = Product(product_name='Tennis racket', product_description='Strong and durable tennis racket', product_long_description='High quality tennis racket for both play and exercise. Good grip to get the most out of every strike.', product_price=100, product_color='Multi')
db.session.add(product70)

img701 = Img(img=secure_filename("tennis1.jpg"), main_image=True)
db.session.add(img701)
img702 = Img(img=secure_filename("tennis2.jpg"), main_image=False)
db.session.add(img702)
img703 = Img(img=secure_filename("tennis3.jpg"), main_image=False)
db.session.add(img703)

product70.image_connection.append(img701)
product70.image_connection.append(img702)
product70.image_connection.append(img703)


newOrder = Order(order_price=100, order_status=True, order_date=datetime.datetime.now().date(), user_connection="onordenmann@gmail.com")
db.session.add(newOrder)
order_product = OrderProduct(product_amount=1)
db.session.add(order_product)
chosen_product = Product.query.filter_by(product_id=2).first()
chosen_product.order_connections.append(order_product)
newOrder.product_connections.append(order_product)
product80 = Product(product_name='Baseball cap', product_description='Adjustable and stylish cap', product_long_description='Adjustable, stylish baseball cap. Perfect for both sports and everyday use.', product_price=15, product_color='Black')
db.session.add(product80)

db.session.commit()
'''

app.run(host='0.0.0.0', debug=False, ssl_context=('cert.pem', 'key.pem'))
