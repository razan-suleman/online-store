from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import requests
import pyrebase

config = {
    "apiKey": "AIzaSyDqhsnIkMKahsodnt-vwS6a6V2WbraEP6k",
    "authDomain": "assignment-7ada3.firebaseapp.com",
    "projectId": "assignment-7ada3",
    "storageBucket": "assignment-7ada3.appspot.com",
    "messagingSenderId": "381640609494",
    "appId": "1:381640609494:web:d27dd0b8dbf418a3270377",
    "measurementId": "G-T8W39RYPMX",
    "databaseURL": "https://assignment-7ada3-default-rtdb.europe-west1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

products = [
    {"name": "Earth", "price": "$1", "image": "static/images/Earth.jpg", "description": ""},
    {"name": "Venus", "price": "$590,000,000", "image": "static/images/Venus.jpg", "description": ""},
    {"name": "Mars", "price": "$999,999,999", "image": "static/images/mars.png", "description": ""},
    {"name": "Jupiter", "price": "$80,000,000", "image": "static/images/Jupiter.jpg", "description": ""},
    {"name": "Saturn", "price": "$580,000,000 , 600,000,000 with the rings", "image": "static/images/Saturn.jpg", "description": ""},
    {"name": "Uranus", "price": "$300,000,000", "image": "static/images/Uranus.jpg", "description": ""},
    {"name": "Neptune", "price": "$34,500,000", "image": "static/images/Neptune.png", "description": ""},
    {"name": "Pluto", "price": "$76,000,000", "image": "static/images/Pluto.png", "description": ""},
    {"name": "Mercury", "price": "$98,000,000", "image": "static/images/Mercury.png", "description": ""},
]

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'ygy77t7gyvjfcxsz88yuiuiucet56dz,;,;zewzewwew88yvtyjzdyhuvdfxtxdtty7866rt6yuffy7'

apod_url = "https://api.nasa.gov/planetary/apod"
api_key = "a3QwiOa3IeYL4L144fISGGGCRjd1OFC7IZLqCpDp"

@app.route('/apod')
def apod():
    response = requests.get(apod_url, params={"api_key": api_key})
    if response.status_code == 200:
        data = response.json()
        image_url = data['url']
        title = data['title']
        explanation = data['explanation']
        return render_template('photo_of_day.html',  logged_in=is_user_logged_in(), image_url=image_url, title=title, explanation=explanation)
    else:
        return "Error fetching data from NASA APOD API"

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', logged_in=is_user_logged_in())

@app.route('/store', methods=['GET', 'POST'])
def store():
    if request.method == 'POST':
        if 'add' in request.form:
            product_index = int(request.form['add'])
            product = products[product_index]
            cart = db.child("Cart").child(login_session['user']['localId']).get().val()
            if cart is None:
                cart = []
            cart.append(product)
            db.child("Cart").child(login_session['user']['localId']).set(cart)

    return render_template("store.html", products=products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user' not in login_session:
        return redirect(url_for('signin'))

    selected_product = products[product_id]
    user_id = login_session['user']['localId']
    user_cart = db.child("Cart").child(user_id).get().val()

    if user_cart is None:
        user_cart = [selected_product]
    else:
        user_cart.append(selected_product)

    db.child("Cart").child(user_id).set(user_cart)

    return redirect(url_for('cart'))

def is_user_logged_in():
    return 'user' in login_session

@app.route('/logout')
def logout():
    if 'user' in login_session:
        del login_session['user']
    
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        
        try:
            user = auth.create_user_with_email_and_password(email, password)
            user_data = {"email": email, "fname": fname, "lname": lname}
            db.child("Users").child(user['localId']).set(user_data)
            return redirect(url_for('signin'))

        except Exception as e:
            error = str(e)
            print(error)
            return render_template("signup.html", error=error)
    else:
        return render_template("signup.html")

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('index'))
        except:
            error = "Authentication failed"
            return render_template('signin.html', error=error)
    else:
        return render_template("signin.html")

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart = db.child("Cart").child(login_session.get('user', {}).get('localId')).get().val()

    if cart is None or len(cart) == 0:
        return render_template("cart.html", empty_cart=True, logged_in=is_user_logged_in(), total=0)
    
    total = sum(float(product['price'].replace('$', '').replace(',', '')) for product in cart)
    return render_template("cart.html", total=total, empty_cart=True, logged_in=is_user_logged_in(), cart=cart)

if __name__ == '__main__':
    app.run(debug=True)
