from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy import func
import os
import datetime
from datetime import timedelta
current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = "secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + \
    os.path.join(current_dir, "database.sqlite3")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Member(db.Model):
    __tablename__ = 'member'
    UserName = db.Column(db.String(20), primary_key=True,
                         nullable=False, unique=True)
    Password = db.Column(db.String(20), nullable=False)
    Type = db.Column(db.Integer, nullable=False)


class Categories(db.Model):
    __tablename__ = 'categories'
    CategoryName = db.Column(db.String(20), primary_key=True, nullable=False)
    Date = db.Column(db.String(12), nullable=False)



class Books(db.Model):
    __tablename__ = 'Books'
    BookName = db.Column(db.String(20), primary_key=True, nullable=False)
    Author = db.Column(db.String(20), nullable=False)
    Category = db.Column(db.String(20), nullable=False)
    Status = db.Column(db.String(20), nullable=False)
    Owner = db.Column(db.String(20), nullable=False)
    Link = db.Column(db.String(100), nullable=False)
    Expiry = db.Column(db.String(12), nullable=False)

class Cart(db.Model):
    __tablename__ = 'cart'
    S_No = db.Column(db.Integer, nullable=False, primary_key = True)
    UserName = db.Column(db.String(20), nullable=False)
    ProductName = db.Column(db.String(20), nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)

def check():
    q1 = Books.query.all()
    for i in q1:
        if i.Expiry < str(datetime.datetime.now().date()) and i.Expiry != '':
            Books.query.filter_by(BookName = i.BookName).update({'Status': 'Available', 'Owner': 'Library', 'Expiry':''})
            db.session.commit()
check()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/managerlogin', methods=['GET', 'POST'])
def managerlogin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form['password']
        check = Member.query.all()
        for i in check:
            if password == i.Password and username == i.UserName and i.Type == 0:
                return redirect(url_for("managerdash", user=username))
        else:
            return render_template('managerlogin.html')

    return render_template('managerlogin.html')


@app.route('/managerdash/<user>', methods=['GET', 'POST'])
def managerdash(user):
    q1 = Categories.query.all()
    q2 = Books.query.all()
    return render_template('managerdash.html', user=user, q1=q1, q2=q2)



@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form['password']
        check = Member.query.all()
        for i in check:
            if password == i.Password and username == i.UserName and i.Type == 1:

                return redirect(url_for("userdash", user=username))
        else:
            return render_template('userlogin.html')

    return render_template('userlogin.html')


@app.route('/userdash/<user>/books', methods=['GET', 'POST'])
def userdash(user):
    q1 = Categories.query.all()
    q2 = Books.query.all()
    print(q2)
    count = 0
    for i in q2:
        if i.Owner == user:
            count += 1
    return render_template('userdash.html', user=user, q1=q1, q2=q2, count = count)

@app.route('/userdash/<user>/mybooks', methods=['GET', 'POST'])
def mybooks(user):
    q1 = Categories.query.all()
    q2 = Books.query.all()
    date = datetime.datetime.now().date()
    return render_template('mybooks.html', user=user, q1=q1, q2=q2, date = date)

@app.route('/returnb', methods=['GET', 'POST'])
def returnb():
    if request.method == "POST":
        user = request.form["User"]
        bookname = request.form["BookName"]
        Books.query.filter_by(BookName = bookname).update({'Status': 'Available', 'Owner': 'Library'})
        db.session.commit()
        return redirect(url_for("userdash", user = user))
    
@app.route('/requestb', methods=['GET', 'POST'])
def requestb():
    if request.method == "POST":
        q1 = Books.query.all()
        user = request.form["User"]
        bookname = request.form["BookName"]
        Books.query.filter_by(BookName = bookname).update({'Status': 'Requested', 'Owner': user})
        db.session.commit()
        return redirect(url_for("userdash", user = user))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form['password']
        check = Member.query.all()
        for i in check:
            if username == i.UserName:
                flash('Already registered! Please Login', 'ERROR')
                return redirect(url_for('userlogin'))
        entry = Member(UserName=username, Password=password, Type=1)

        db.session.add(entry)
        db.session.commit()
        db.session.refresh(entry)
        flash('User registered! Please Login', 'Success')
        return (redirect(url_for("userlogin")))
    return render_template('userlogin.html')

@app.route('/managerdash/<user>/requests', methods=['GET', 'POST'])
def requests(user):
    q1 = Books.query.all()
    return render_template('requests.html', user=user, q1=q1)

@app.route('/allowb', methods=['GET', 'POST'])
def allowb():
     if request.method == "POST":
        user = request.form.get('User')
        bookname = request.form['BookName']
        Books.query.filter_by(BookName = bookname).update({'Status': 'Not Available', 'Expiry': (datetime.datetime.now().date()) + timedelta(7)})
        db.session.commit()
        return redirect(url_for("requests", user = user))
     
@app.route('/rejectb', methods=['GET', 'POST'])
def rejectb():
    if request.method == "POST":
        user = request.form.get('User')
        bookname = request.form['BookName']
        Books.query.filter_by(BookName = bookname).update({'Status': 'Available', 'Owner': 'Library'})
        db.session.commit()
        return redirect(url_for("requests", user = user))
     
@app.route('/revokeb', methods=['GET', 'POST'])
def revokeb():
    if request.method == "POST":
        user = request.form.get('User')
        bookname = request.form['BookName']
        Books.query.filter_by(BookName = bookname).update({'Status': 'Available', 'Owner': 'Library'})
        db.session.commit()
        return redirect(url_for("requests", user = user))

@app.route('/newproduct', methods=['GET', 'POST'])
def newProduct():
    if request.method == "POST":
        cat = request.form["CatName"]
        user = request.form["user"]
        return render_template("newProduct.html", cat=cat, user=user)

    return render_template('newproduct.html')

@app.route('/addinv', methods=['GET', 'POST'])
def addinv():
    if request.method == "POST":
        username = request.form["user"]
        entry = Books(BookName=request.form["bname"], Author=request.form["aname"], Category=request.form["category"], Link = request.form["content"], Owner = 'Library', Status = 'Available')
        db.session.add(entry)
        db.session.commit()
        db.session.refresh(entry)
        return redirect(url_for("managerdash", user=username))

@app.route('/addcat', methods=['GET', 'POST'])
def addcat():
    if request.method == "POST":
        username = request.form["user"]
    return render_template('addcat.html', user=username, date= datetime.datetime.now().date())

@app.route('/createcat', methods=['GET', 'POST'])
def createcat():
    if request.method == 'POST':
        username = request.form["user"]
        entry = Categories(CategoryName = request.form["cname"], Date = datetime.datetime.now().date())
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for("managerdash", user = username))
    
@app.route('/editcat', methods=['GET', 'POST'])
def editcat():
    if request.method == "POST":
        cname = request.form["CatName"]
        username = request.form["user"]
        return render_template('editcat.html', cname = cname, user = username)
    
    
    
@app.route('/editcategory', methods=['GET', 'POST'])
def editcategory():    
    if request.method == 'POST':
        OldName = request.form["cname"]
        username = request.form["user"]
        Categories.query.filter_by(CategoryName = OldName).update({'CategoryName':request.form["newcname"]})
        Books.query.filter_by(Category = OldName).update({'Category':request.form["newcname"]})
        db.session.commit()
        return redirect(url_for("managerdash", user = username))
    
@app.route('/delcat', methods=['GET', 'POST'])
def deletecat():
    if request.method == "POST":
        cname = request.form["CatName"]
        username = request.form["user"]
        Categories.query.filter_by(CategoryName = cname).delete()
        Books.query.filter_by(Category = cname).delete()
        db.session.commit()
        return redirect(url_for('managerdash', user = username))
    
@app.route('/delprod', methods=['GET', 'POST'])
def deleteprod():
    if request.method == "POST":
        pname = request.form["ProdName"]
        username = request.form["user"]
        Books.query.filter_by(ProductName = pname).delete()
        db.session.commit()
        return redirect(url_for('managerdash', user = username))
    
@app.route('/editprod', methods = ['GET', 'POST'])
def editprod():
    if request.method == "POST":
        prodname = request.form['ProdName']
        username = request.form['user']
        return render_template('editprod.html', pname = prodname, user = username)
    
@app.route('/editproduct', methods=['GET', 'POST'])
def editproduct():
    if request.method == 'POST':
        oldprodname = request.form['pname']
        username = request.form['user']
        Books.query.filter_by(ProductName = oldprodname).update({'ProductName': request.form['newpname'], 'Price': request.form['rate'], 'Quantity': request.form['quantity'], 'Unit': request.form['unit']})
        db.session.commit()
        return redirect(url_for('managerdash', user = username))           
    
@app.route('/search', methods=['GET','POST'])
def search():
     if request.method == 'POST':
        username = request.form['User']
        q1 = Categories.query.all()
        q2 = Books.query.all()
        count = 0
        for i in q2:
            if i.Owner == username:
                count += 1
        term = request.form.get('term', '')
        print('Term:', term)
        #Search for the book with all the lowercase and upercase letters
        search_results = Books.query.filter(db.or_(Books.BookName.ilike(f"%{term}%"), Books.Author.ilike(f"%{term}%"))).all()
        #Fetch all the accepted requests
        return(render_template('userdash.html',user = username, books=search_results, q2=q2, q1=q1, count=count))
     
if __name__ == '__main__':
    app.run()