from flask import Flask, render_template, url_for, request, redirect
from database import ConsultancyDatabase
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'business'
app.config['SESSION_COOKIE_NAME'] = 'business_cookie'
app.debug = True # remove this part during actual launch

DATABASE_FILENAME = 'consultancy.db'
db = ConsultancyDatabase(DATABASE_FILENAME, temporary_run=True)

login_manager = LoginManager(app)
login_manager.login_view = "login"

class Consultant(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password
        self.authenticated = False
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return super().is_anonymous
    
    def is_authenticated(self):
        return self.authenticated
    
    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id: int):
    user_details = db.search_login_using_id(user_id)
    if user_details is None:
        return None
    else:
        return Consultant(int(user_details[0]), user_details[1], user_details[2])

@app.route('/')
def index():
    return render_template('index.html', ip_address='localhost', ports=[3000, 8000])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name, email, password = request.form['name'], request.form['email'], request.form['password']
        db.add_business(name, email, password)
        return redirect(url_for('login'))
    return render_template('regis.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    elif request.method == 'POST':
        email = request.form['email']
        user = db.search_login_using_email(email)
        category = user[3]
        if user:
            user = load_user(int(user[0]))
            if category == 2 and request.form['email'] == user.email and request.form['password'] == user.password:
                login_user(user, remember=True)
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', failed=True)
        else:
            return render_template('login.html', failed=True)
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('bdash.html', projects = db.get_projects_for_business(current_user.get_id()), dash_active='menu-active', name=db.get_business_from_login_id(current_user.get_id()), posted_count=db.get_projects_count_by_bid(current_user.get_id()), application_count=db.get_applications_count_by_bid(current_user.get_id()))

@app.route('/new-project', methods=['GET', 'POST'])
@login_required
def addproj():
    if request.method == 'POST':
        names = ['name', 'tagline', 'desc', 'stipend', 'tech']
        db.add_project(*[request.form[name] for name in names], current_user.get_id())
        return redirect(url_for('dashboard'))
    return render_template('addproj.html', name=db.get_business_from_login_id(current_user.get_id()))

@app.route('/view-project')
@login_required
def pinfo():
    return render_template('pdash.html', name=db.get_business_from_login_id(current_user.get_id()))

app.run('0.0.0.0', 8000)