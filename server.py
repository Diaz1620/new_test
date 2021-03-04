from flask import Flask, render_template,request, redirect, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
app = Flask(__name__)
app.secret_key = "keychain"
bcrypt = Bcrypt(app)

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
name = re.compile(r'^[a-zA-Z]{2,50}$')
password = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,20}$')



@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    mysql2 = connectToMySQL('magazines')
    query2 = "SELECT email FROM users WHERE email = %(user)s;"

    is_valid = True
    if not name.match(request.form['first']):
        is_valid = False
        flash("First Name Not A Valid Entry!")
        print(request.form['first'])
    if not name.match(request.form['last']):
        is_valid = False
        flash("Last Name Not A Valid Entry!")
        print(request.form['last'])
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Email Not A Valid Entry!")
        print(request.form['email'])
    for email in query2:
        if email == request.form['email']:
            is_valid = False
            flash("Email Is Already In Use")
            print(email)
    if not password.match(request.form['pass']):
        is_valid = False
        flash("Password Not A Valid Entry!")
    if request.form['confirm'] != request.form['pass']:
        is_valid = False
        flash("Passwords Must Match!")
    data2 = {
        "user": request.form["email"]
    }
    result2 = mysql2.query_db(query2,data2)
    if len(result2) > 0:
        is_valid = False
        flash("Email already in use!")
    
    if not is_valid:
        return redirect('/')
    else:
        pw_hash = bcrypt.generate_password_hash(request.form['pass'])  
        print(pw_hash)
        confirm_hash = bcrypt.generate_password_hash(request.form['confirm'])
        mysql = connectToMySQL('magazines')
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pass_hash)s, Now(), Now());"
        data = {
            "fn": request.form['first'],
            "ln": request.form['last'],
            "em": request.form['email'],
            "pass_hash": pw_hash
        }
        user_id = mysql.query_db(query,data)
        # save the id in session
        session['user_id'] = user_id
        flash("Registered Successfully, Please Login To Continue")
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    mysql = connectToMySQL('magazines')
    query = "SELECT * FROM users where email = %(email)s;"
    data = {
        "email": request.form["loginemail"]
    }
    result = mysql.query_db(query,data)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['password'], request.form['loginpass']):
            session['userid'] = result[0]['id']
            flash("Login Successful")
            return redirect('/success')
        else:
            flash("Email/Username Combination Incorrect!")
            return redirect('/')


@app.route('/success')
def success():
    if "userid" not in session:
        flash('Must Be Logged In To Access Content')
        return redirect('/')
    print(session['userid'])
    # get the logged in user
    mysql = connectToMySQL('magazines')
    query = "SELECT * FROM users where id = %(id)s;"
    data = {
        "id": session['userid']
    }
    name = mysql.query_db(query,data)
    # get magazine info
    mysql = connectToMySQL('magazines')
    query = "SELECT * FROM magazines.users JOIN magazines ON users.id = user_id;"
    data = {
        "id": session['userid']
    }
    magazine_info = mysql.query_db(query,data)
    return render_template('dashboard.html', user_name = name, magazines = magazine_info)


@app.route('/show/<magazine_id>')
def view(magazine_id):
    if "userid" not in session:
        flash('Must Be Logged In To Access Content')
        return redirect('/')
    mysql = connectToMySQL('magazines')
    query = "SELECT * FROM magazines.users JOIN magazines ON users.id = user_id WHERE magazines.id = %(magazine_id)s;"
    data = {
        "magazine_id": magazine_id
    }
    magazine_info = mysql.query_db(query,data)

    mysql = connectToMySQL('magazines')
    query = "SELECT * FROM magazines.users JOIN subscribers ON users.id = user_id WHERE magazine_id = %(mag)s;"
    data = {
        "mag": magazine_id
    }
    subs = mysql.query_db(query,data)
    return render_template('show.html', magazine = magazine_info, subscribers = subs)

@app.route('/user_account/<user_id>')
def account(user_id):
    if "userid" not in session:
        flash('Must Be Logged In To Access Content')
        return redirect('/')
    mysql = connectToMySQL('magazines')
    query = "SELECT * FROM magazines.users JOIN magazines ON users.id = user_id WHERE users.id = %(user_id)s;"
    data = {
        "user_id": user_id
    }
    magazine_info = mysql.query_db(query,data)
    
    mysql = connectToMySQL('magazines')
    query = "SELECT id, magazine_id,count(user_id) as num_subs FROM magazines.subscribers group by magazine_id;"
    num_of_subs = mysql.query_db(query,data)
    return render_template('user_account.html', magazine = magazine_info, subscribers = num_of_subs)

@app.route('/add_new_magazine')
def add():
    return render_template("add_magazine.html")

@app.route('/add', methods=['POST'])
def create():
    if "userid" not in session:
        flash('Must Be Logged In To Access Content')
        return redirect('/')
    is_valid = True
    if len(request.form['title']) < 2:
        is_valid = False
        flash("Title Not A Valid Entry! Must be at least two characters.")
        print(request.form['title'])
    if len(request.form['desc']) < 10:
        is_valid = False
        flash("Desciption Not A Valid Entry! Must be at least 10 characters.")
        print(request.form['desc'])
    
    if not is_valid:
        flash("All fields are required")
        return redirect('/add_new_magazine')
    else:
        mysql = connectToMySQL('magazines')
        query = "INSERT INTO magazines.magazines (title, description, user_id) VALUES(%(title)s, %(desc)s, %(user_id)s);"
        data = {
            "title": request.form['title'],
            "desc": request.form['desc'],
            "user_id": session['userid']
        }
        mysql.query_db(query,data)
        return redirect('/success')

@app.route("/submit_edits", methods=['POST'])
def submit_edit():
    if "userid" not in session:
        flash('Must Be Logged In To Access Content')
    is_valid = True
    if len(request.form['first_name']) < 2:
        is_valid = False
        flash("First Name Not A Valid Entry!  Must be at least two characters.")
        print(request.form['first_name'])
    if len(request.form['last_name']) < 2:
        is_valid = False
        flash("Last Name Not A Valid Entry!  Must be at least two characters.")
        print(request.form['last_name'])
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Email Not A Valid Entry!")
        print(request.form['email'])
    if not is_valid:

        flash("All fields are required")
        return redirect(f"/user_account/{session['userid']}")
    else:
        mysql = connectToMySQL('recipes')
        query = "UPDATE magazines.users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s WHERE users.id = %(user_id)s;"
        data = {
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "email": request.form['email'],
            "user_id": session['userid']
        }
        mysql.query_db(query,data)
        return redirect('/success')

@app.route('/subscribe/<magazine_id>')
def sub(magazine_id):
    mysql = connectToMySQL('magazines')
    query = "INSERT INTO `magazines`.`subscribers` (`magazine_id`, `user_id`) VALUES(%(mag)s, %(user)s);"
    data = {
        "mag": magazine_id,
        "user": session['userid']
    }
    mysql.query_db(query,data)
    return redirect('/success')






@app.route('/delete/<magazine_id>')
def delete(magazine_id):
    if "userid" not in session:
        flash('Must Be Logged In To Access Content')
        return redirect('/')
    mysql = connectToMySQL('magazines')
    query = "DELETE FROM `magazines`.`magazines` WHERE id = %(mag_id)s;"
    data = {
        "mag_id": magazine_id
    }
    mysql.query_db(query,data)
    return redirect('/success')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
        
if __name__ == "__main__":
    app.run(debug=True)
