from flask import Flask, render_template, url_for, request, flash, redirect
from jinja2.exceptions import TemplateNotFound
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@127.0.0.1:8889/BD_FARMERS"
app.config['SECRET_KEY'] = "This is super Duper Key of master, walk!"
db = SQLAlchemy(app)



################################################################################################
################################################################################################

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'





################################################################################################
################################################################################################
################################          DB          ##########################################
################################################################################################
################################################################################################

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    User_ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.Enum('Farmer', 'Customer'), nullable=False)
    Created_At = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def id(self):
        return self.User_ID

    # Relationships
    posts = db.relationship('Posts', backref='author', lazy=True)
    comments = db.relationship('Comments', backref='user', lazy=True)
    orders = db.relationship('Orders', backref='customer', lazy=True)

class Posts(db.Model):
    __tablename__ = 'posts'
    Post_ID = db.Column(db.Integer, primary_key=True)
    User_ID = db.Column(db.Integer, db.ForeignKey('users.User_ID'), nullable=False)
    Title = db.Column(db.String(200), nullable=False)
    Description = db.Column(db.Text)
    Price = db.Column(db.Numeric(10,2))
    Quantity = db.Column(db.Integer)
    Image_URL = db.Column(db.String(255))
    Created_At = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    comments = db.relationship('Comments', backref='post', lazy=True)
    orders = db.relationship('Orders', backref='post', lazy=True)

class Comments(db.Model):
    __tablename__ = 'comments'
    Comment_ID = db.Column(db.Integer, primary_key=True)
    Post_ID = db.Column(db.Integer, db.ForeignKey('posts.Post_ID'), nullable=False)
    User_ID = db.Column(db.Integer, db.ForeignKey('users.User_ID'), nullable=False)
    Comment_Text = db.Column(db.Text, nullable=False)
    Created_At = db.Column(db.DateTime, server_default=db.func.now())

class Orders(db.Model):
    __tablename__ = 'orders'
    Order_ID = db.Column(db.Integer, primary_key=True)
    Customer_ID = db.Column(db.Integer, db.ForeignKey('users.User_ID'), nullable=False)
    Post_ID = db.Column(db.Integer, db.ForeignKey('posts.Post_ID'), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    Total_Price = db.Column(db.Numeric(10,2))
    Order_Date = db.Column(db.DateTime, server_default=db.func.now())
    Status = db.Column(db.Enum('Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled'), default='Pending')

with app.app_context():
    db.create_all()



################################################################################################
################################################################################################
################################          APP         ##########################################
################################################################################################
################################################################################################



@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/')
def home():
    try:
        return render_template("home.html")
    except TemplateNotFound:
        return render_template("lufy.html")

    
@app.route('/product')
def product():
    try:
        return render_template('product.html')
    except TemplateNotFound:
        return render_template("lufy.html")
    
@app.route('/services')
def services():
    try:
        return render_template('services_page.html')
    except TemplateNotFound:
        return render_template("lufy.html")

@app.route('/contact')
def contact():
    try:
        return render_template('contact_page.html')
    except TemplateNotFound:
        return render_template("lufy.html")
    



    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Users.query.filter_by(Email=email).first()

        if user and check_password_hash(user.Password, password):
            login_user(user)
            return redirect(url_for('home'))  # or user dashboard
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for('login'))

    return render_template('login_page.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for('login'))

    


    
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # 'Farmer' or 'Customer'

        if len(password) < 8:
            flash("Password must be at least 8 characters long.")
            return redirect(url_for('signup'))

        # Proceed to hash and store the password
        hashed_password = generate_password_hash(password)
        new_user = Users(Name=name, Email=email, Password=hashed_password, Role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Signed Up successfully. Please log in")
        return redirect(url_for('login'))

    return render_template("signup_page.html")
    

if __name__ == '__main__':
    app.run(debug=True, port=5001)