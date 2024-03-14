from flask import Flask,session,render_template,request,send_file
from pandas.core.series import Series
import pymysql
import os, datetime
import pandas as pd
from werkzeug.utils import redirect
db = pymysql.connect(host="localhost",user="root",password="admin",database="foodwaste")
cur = db.cursor()
app = Flask(__name__)
app.secret_key = os.urandom(16)
l = []
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        q = "select * from admin where username = '{}' and password = '{}'".format(username,password)
        cur.execute(q)
        res = cur.fetchall()
        if len(res) >= 1:
            session['user'] = username
            return "<html><body><script>alert(\"Logged In Succesfully\");window.location.href=\"admin\";</script></body></html>"
        q = "select * from charity where email = '{}' and password = '{}'".format(username,password)
        print(q)
        cur.execute(q)
        res = cur.fetchall()
        if len(res) >= 1:
            session['user'] = username

            return "<html><body><script>alert(\"Logged In Succesfully\");window.location.href=\"customer\";</script></body></html>"
        else:
            return "<html><body><script>alert(\"Invalid Credentials\");window.location.href=\"login\";</script></body></html>"
            

    return render_template('login.html')

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        email = request.form.get('emailid')
        username = request.form.get('username')
        password = request.form.get('password')
        phone = request.form.get('phno')
        address = request.form.get('address')
        q = "insert into charity(name,email,address,phone,password) values('{}','{}','{}','{}','{}')".format(username,email,address,phone,password)
        cur.execute(q)
        db.commit()
        return "<html><body><script>alert(\"Data registered Succesfully\");window.location.href=\"signup\";</script></body></html>"
    return render_template('signup.html')

@app.route('/logout')
def logout():
    l.clear()
    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('adminhome.html')

@app.route('/customer')
def customer():
    return render_template('customerhome.html')

@app.route('/addFood',methods=['POST','GET'])
def addMedicine():
    if request.method == 'POST':
        medName = request.form.get('medName')
        quantity = request.form.get('quantity')
        q = "select *  from food where foodname = '{}'".format(medName)
        cur.execute(q)
        res = cur.fetchall()
        if len(res) >= 1:
            q = "update food set capacity = capacity + {} where foodname = '{}'".format(quantity,medName)
            cur.execute(q)
            db.commit()
            return "<html><body><script>alert(\"Food Updated Succesfully\");window.location.href=\"addFood\";</script></body></html>"
        else:
            q = "insert into food(foodname,capacity) values('{}',{})".format(medName,quantity)
            print(q)
            cur.execute(q)
            db.commit()
            return "<html><body><script>alert(\"Food Added Succesfully\");window.location.href=\"addFood\";</script></body></html>"
    return render_template("addMedicine.html")


@app.route('/delete',methods=['POST','GET'])
def delete():
    q= "select foodname from food"
    cur.execute(q)
    names =  cur.fetchall()
    if request.method == 'POST':
        medicine = request.form.get('medicine')
        q = "select * from food where foodname = '{}'".format(medicine)
        cur.execute(q)
        res = cur.fetchall()
        return render_template('delete.html',names=names,res=res,post=True)
    return render_template('delete.html',names=names)

@app.route('/deleteMedicine',methods=['POST','GET'])
def deleteMedicine():
    if request.method == 'POST':
        medName = request.form.getlist('medName')
        print(medName)
        q = "delete from food where foodname = '{}'".format(medName[0])
        print(q)
        cur.execute(q)
        db.commit()
        return "<html><body><script>alert(\"FoodData Updated Succesfully\");window.location.href=\"delete\";</script></body></html>"


@app.route('/request',methods=['POST','GET'])
def Shop():
    # print(session['user'])
    q= "select foodname from food"
    cur.execute(q)
    names =  cur.fetchall()
    if request.method == 'POST':
        name = request.form.get('medicine')
        quantity = int(request.form.get('quantity'))
        q = "select capacity from food where foodname = '{}'".format(name)
        cur.execute(q)
        quan = cur.fetchall()
        if quantity > int(quan[0][0]):
            return "<html><body><script>alert(\"Selected Quantity is not Available. Only {} units are available\");window.location.href=\"request\";</script></body></html>".format(quan[0][0])

        q = "select capacity from food where foodname = '{}'".format(name)
        cur.execute(q)
        p = cur.fetchall()
        price = p[0][0]
        tpl = name,quantity
        l.append(tpl)
        return render_template('shop.html',names=names,res=l,post=True)
    return render_template('shop.html',names=names)

@app.route('/CustTrans')
def CustTrans():
    q = "select * from transactions where charity = '{}'".format(session['user'])
    print(q)
    cur.execute(q)
    res = cur.fetchall()
    return render_template('CustTrans.html',res=res)
    
@app.route('/buy',methods=['POST','GET'])
def buy():
    if request.method == 'POST':
        medName = request.form.getlist('medName')
        quantity = request.form.getlist('quantity')
        print(medName,quantity)

        for i in range(len(medName)):
            q = "select capacity from food where foodname = '{}'".format(medName[i])
            cur.execute(q)
            quan = cur.fetchall()
            quan = int(quan[0][0]) - int(quantity[i])
            q = "update food set capacity = '{}' where foodname = '{}'".format(quan,medName[i])
            cur.execute(q)
            db.commit()

            q = "insert into transactions(charity,food,quantity) values('{}','{}','{}')".format(session['user'],medName[i],quantity[i])
            cur.execute(q)
            db.commit()
            
        return "<html><body><script>alert(\"Purchased Successfully\");window.location.href=\"request\";</script></body></html>"


@app.route('/display')
def display():
    q = "select * from food"
    cur.execute(q)
    res = cur.fetchall()
    if len(res) == 0:
        return "<html><body><script>alert(\"No FoodItems Found\");window.location.href=\"admin\";</script></body></html>"
    return render_template('display.html',res=res)

@app.route('/trans',methods=['GET','POST'])
def trans():
    q = "select * from transactions"
    cur.execute(q)
    res = cur.fetchall()
    if len(res) == 0:
        return "<html><body><script>alert(\"No FoodItems Transactions Found\");window.location.href=\"admin\";</script></body></html>"
    return render_template('transaction.html',res=res)
  

if __name__ == "__main__":
    app.run(debug=True)
    