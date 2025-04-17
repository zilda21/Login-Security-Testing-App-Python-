from flask import Flask, request, jsonify, render_template, redirect, url_for
import jwt
import datetime
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
from flask import Flask, request, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)


csrf._disable_on_test = True



users = {
    "admin": bcrypt.generate_password_hash("password123").decode('utf-8')
}


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username in users and bcrypt.check_password_hash(users[username], password):
            token = jwt.encode({
                'user': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }, app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({'message': 'Login successful', 'token': token})

        return jsonify({'message': 'Invalid credentials'}), 401

    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Missing token'}), 403

    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return f"Welcome {decoded['user']} to your dashboard!"
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 403

if __name__ == '__main__':
    app.run(debug=True)
    

    app = Flask(__name__)
comments = [] 

@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        user_comment = request.form['comment']
        comments.append(user_comment)
    
    return render_template_string('''
        <h1>Leave a Comment</h1>
        <form method="POST">
            <textarea name="comment" rows="4" cols="50" required></textarea><br>
            <button type="submit">Submit</button>
        </form>
        <h2>All Comments:</h2>
        <ul>
            {% for c in comments %}
                <li>{{ c|safe }}</li>
            {% endfor %}
        </ul>
    ''', comments=comments)
if __name__ == '__main__':
    app.run(debug=True)

    
