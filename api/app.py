from flask import Flask, request, jsonify, redirect, url_for, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
#from prometheus_flask_exporter import PrometheusMetrics
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key ='\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
oauth = OAuth(app)
#metrics = PrometheusMetrics(app, path='/metrics')

#metrics.info("app_info", "Info about the app")

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
    user_google_token = db.Column(db.String(200))

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
'''@app.before_request
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
        '''

@app.route('/') #Main page
def products_page():
    user = session.get('user')
    img = Img.query.first()
    productlist = Product.query.all()
    imagelist = Img.query.all()
    route = f"/static/{img.img}"
    return render_template("products.html", content=route, user=user, productlist=productlist, imagelist = imagelist)

#Google oAuth2 login
def verify_login():
    try:
        user = dict(session).get('profile', None)
        if user:
            return True,user
        else:
            return False,{}
    except Exception as e:
        return False,{}

@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    print("her")
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
        user_input = User(first_name=user_info['given_name'], last_name=user_info['family_name'], user_type=False, user_email=user_info['email'], user_google_token=token)
        db.session.add(user_input)
        db.session.commit()
    # do something with the token and profile
    session['profile'] = user_info
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
    session.clear()
    return redirect('/')


@app.route('/users')
def user_page():
    users = User.query.all()
    output = []

    for user in users:
        user_data = {'user_id': user.user_id, 'first_name': user.first_name}
        output.append(user_data)

    return {"users": output}


@app.route('/orders/<user_id>/')
def get_orders(user_id):
    user = User.query.filter_by(user_id=user_id)
    email = db.session.query(User.user_email).filter_by(user_id=user_id)
    orders = Order.query.filter_by(order_status=True, user_connection=email).all()
    return render_template('orders.html', orders=orders, user=user)

@app.route('/order')
def create_order():
    newOrder = Order(order_price=0, order_status=True, order_date=datetime.datetime.now().date(), user_connection=session['email'])
    db.session.add(newOrder)
    db.session.commit()
    session['current_order'] = newOrder.order_id
    return 'true'

@app.route('/order/current/<product_id>')
def add_product_order(product_id):
    order_product = OrderProduct(product_amount=1)
    choosen_product = Product.query.filter_by(product_id=product_id).first()
    currentOrder = Order.query.filter_by(order_id=session['current_order']).first()
    choosen_product.order_connections.append(order_product)
    currentOrder.product_connections.append(order_product)
    db.session.commit()
    if controll_order(currentOrder, choosen_product) < 3:
        print(f'---A {choosen_product.product_name} was added to order with id {currentOrder.order_id} ---')
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

@app.route('/order/current/<product_id>/<product_amount>')
def update_order_product_count(product_id, product_amount):
    order_product_connection = OrderProduct.query.filter_by(order_id=session['current_order'], product_id=product_id).first()
    order_product_connection.product_amount = product_amount
    db.session.commit()
    return 'true'

@app.route('/order/current/delete/<product_id>') #Delete product from order
def delete_product_from_order(product_id):
    print(session['current_order'])
    print(product_id)
    OrderProduct.query.filter_by(order_id=session['current_order'], product_id=product_id).delete()
    db.session.commit()
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

        product_data = {'product_id': product.product_id, 'product_name': product.product_name, 'product_color': product.product_color, 'product_price': product.product_price, 'product_amount': order.product_amount, 'product_image': image.img}
        output.append(product_data)

    return {"products": output}


@app.route('/order/<order_id>/products') #Get the products in the order
def getOrderProducts(order_id):
    output = []

    for order in OrderProduct.query.filter_by(order_id=order_id).all():
        product = Product.query.filter_by(product_id=order.product_id).first()
        image = Img.query.filter_by(product_connection=order.product_id).first()

        product_data = {'product_id': product.product_id, 'product_name': product.product_name, 'product_color': product.product_color, 'product_price': product.product_price, 'product_amount': order.product_amount, 'product_image': image.img}
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
            if name != '' and short != '' and long != '' and price != '':  # If all required fields are filled a new product is added to database
                new_product = Product(product_name=name, product_description=short, product_long_description=long, product_price=price)
                db.session.add(new_product)
                db.session.commit()
                files = request.files.getlist('image')  # Gets all files uploaded in the form
                if files[0].filename == '':  # No file attached
                    flash("The product was uploaded without a picture")
                    return render_template("newproduct.html")
                else:  # If there where files uploaded
                    images = []  # List of images that will be added to product
                    for file in files:  # Loops through all files to see if they are correct format
                        if filecheck(file.filename):
                            images.append(file)
                        else:  # If a file is incorrect, a message is displayed
                            flash("Accepted file types are: jpg, jpeg and png. One or more of your pictures were rejected")
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
                    return redirect(request.url)
            else:  # If some of the fields are not filled
                flash("All fields must be filled")
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


#Create db with content
db.drop_all()
db.create_all()
user = User(first_name='Trym', last_name='Stenberg', user_type=True, user_email='ufhsaufhasf')
user2 = User(first_name='Andre', last_name='Knutsen', user_type=True, user_email='gdokaosfjoAPR')
user3 = User(first_name='Martin', last_name='Kvam', user_type=True, user_email='martin_kvam@hotmail.com')
user4 = User(first_name='Adrian', last_name='Nilsen', user_type=True, user_email='adrian1995nils1@gmail.com', user_google_token='qwert')
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

order_product = OrderProduct(product_amount=9)
product.order_connections.append(order_product)
order.product_connections.append(order_product)
db.session.add(order_product)
order_product2 = OrderProduct(product_amount=2)
product2.order_connections.append(order_product2)
order.product_connections.append(order_product2)

product10 = Product(product_name='Football', product_description='Football', product_long_description='Nice and cheap football for play and practice', product_price=100)
db.session.add(product10)

img101 = Img(img=secure_filename("football1.jpg"), main_image=True)
db.session.add(img101)
img102 = Img(img=secure_filename("football2.jpg"), main_image=False)
db.session.add(img102)

product10.image_connection.append(img101)
product10.image_connection.append(img102)

product20 = Product(product_name='Boxing gloves', product_description='Starter boxing gloves', product_long_description='Sporty lightweight boxing gloves for beginners, perfect for junior and up', product_price=250)
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

product30 = Product(product_name='Yoga mat', product_description='Colorful yoga mat', product_long_description='Lightweight, non slip mat for yoga. Can also be used for exercise', product_price=120)
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

product40 = Product(product_name='Kettlebell', product_description='12 kg kettlebell', product_long_description='12 kg kettlebell for exercise. Perfect for strength workout, can be used for multiple exercices', product_price=200)
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

product50 = Product(product_name='Sunglasses', product_description='Stylish sunglasses', product_long_description='Stylish sunglasses with full UV protection', product_price=100)
db.session.add(product50)

img501 = Img(img=secure_filename("sunglass1.jpg"), main_image=True)
db.session.add(img501)
img502 = Img(img=secure_filename("sunglass2.jpg"), main_image=False)
db.session.add(img502)

product50.image_connection.append(img501)
product50.image_connection.append(img502)

product60 = Product(product_name='World Cup football', product_description='Original World Cup ball', product_long_description='Original professional world cup football. Perfect for matches, games and training.', product_price=1000)
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

db.session.commit()

app.run(host='0.0.0.0', debug=True)
