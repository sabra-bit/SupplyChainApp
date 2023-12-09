from flask import Flask,redirect, render_template,request, session ,flash ,jsonify,Response,url_for
from datetime import datetime ,date,timedelta
import  sqlite3 , json 


conn = sqlite3.connect("data.db")


app = Flask(__name__)
app.secret_key = 'anybetngan'
app.permanent_session_lifetime = timedelta(minutes=66731)
session_cookie_samesite=app.config["SESSION_COOKIE_SAMESITE"]
@app.route('/')
def welcome():
    return render_template("login.html")
@app.route('/auth', methods=['POST'])
def auth():

    user = request.form['username']
    password = request.form['password']
    ip_address = request.remote_addr
    time = datetime.now()
    # to add login info
    conn = sqlite3.connect("data.db")

    c = conn.cursor()
    Data = c.execute("""SELECT * FROM Users""").fetchall()
    
    flag = False
    for data in Data:
        
        if user ==data[1] and password==data[2]:
            session['username'] =user
            session['name'] =data[3]
            session['role'] =data[4]
            session['password'] = data[2]
            flag = True
            break;
    c.close()
    if flag and session.get('role') == "admin":
        return redirect('/admin')
    elif flag and session.get('role') == "user":

        return redirect('/user')
        
    else:
        
        flash('bad usename or password')
        return redirect("/")



@app.route('/admin')
def admin():
    if session.get('role') == "admin":
        return render_template("admin.html",name = session['name'])
    else:
        flash('requested page not found')
        return redirect('/')
    
    
@app.route('/usersData', methods=['POST' ,'GET'])
def usersData():
    if session.get('role') == "admin" and request.method == 'GET':
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        Data = c.execute("""SELECT * FROM Users""").fetchall()
        c.execute("""CREATE TABLE IF NOT EXISTS Pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        urlPage TEXT NOT NULL,
        pageName TEXT NOT NULL
        )""")
        Page = c.execute("SELECT * FROM Pages").fetchall()
        return render_template("usersData.html",name = session['name'] , Data=Data ,Page=Page)
    elif session.get('role') == "admin" and request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        Data = c.execute("""SELECT * FROM Users WHERE username = ?""", ([email])).fetchall()
        print(Data)
        if Data:
            flash('type another email ')
            return redirect('/usersData')
        else:
            c.execute("""INSERT INTO Users (username, password, name, roll) VALUES (?, ?,?,?)""", (email, password, name, role))
            conn.commit()
            flash('user added successfully ')
            return redirect('/usersData')
    else:
        flash('requested page not found')
        return redirect('/')


@app.route('/editDeletePage', methods=['POST' ,'GET'])
def editDeletePage():
    if session.get('role') == "admin" and request.method == 'POST':
        data =json.loads(request.data)
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS userPages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userName TEXT NOT NULL,
        urlPage TEXT NOT NULL,
        pageName TEXT NOT NULL
        )""")
        
        
        if data['ActionType'] == 'delete':
            c.execute("DELETE FROM userPages WHERE [userName] = ? and [pageName] = ?",[(str(data['userName'])),(str(data['PageName']))])
            conn.commit()
            
            return 'page deleted'
        elif data['ActionType'] == 'add':
            print(data['PageName'])
            Data = c.execute(
            'SELECT * FROM userPages where userName = ? and pageName = ?',
            ((str(data['userName'])),(str(data['PageName'])))
            ).fetchall()
            if (str(data['PageName'])) == "":
                return"page not selected"
            if Data:
                return "page exist"
            else:
                
                c.execute(
                'insert into userPages (userName,pageName,urlPage) values(?,?,?);',
                (str(data['userName']),str(data['PageName']),str(data['URL']))
                )
                conn.commit()
            
                return 'page added'
        elif data['ActionType'] == 'view':
            time = datetime.now()
            data = c.execute(
            'SELECT [pageName] FROM userPages where userName = ?',
            ([str(data['userName'])])
            ).fetchall()
            conn.commit()
            print(data)
            return str(data).replace(']', '').replace('[', '').replace(',)', '').replace('(', '')
        else:
            flash('requested page not found')
            return redirect('/')
    else:
        flash('requested page not found')
        return redirect('/')
@app.route('/user', methods=['POST','GET'])
def UserApp():
    if session.get('role') == "user" and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Home')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        return render_template("userHome.html",name = session['name'] ,Pages =Pages)
    else:
        flash('requested page not found')
        return redirect('/')
    

@app.route('/addCar', methods=['POST','GET'])
def addCar():
    if session.get('role') == "user" and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Add Car')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        number TEXT NOT NULL,
        model TEXT NOT NULL,
        creater TEXT NOT NULL
        )""")
        
        Data = c.execute("""SELECT * FROM Cars """, ).fetchall()
        return render_template("addCar.html",name = session['name'] ,Pages =Pages,Data=Data)
    
    elif session.get('role') == "user" and request.method == 'POST':
        name = request.form['name']
        Number = request.form['Number']
        Model = request.form['Model']
        
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        number TEXT NOT NULL,
        model TEXT NOT NULL,
        creater TEXT NOT NULL
        )""")
        
        Data = c.execute("""SELECT * FROM Cars WHERE number = ?""", ([Number])).fetchall()
        
        if Data:
            flash('Car Number Exist')
            return redirect('/addCar')
        else:
            c.execute("""INSERT INTO Cars (name, number, model, creater) VALUES (?, ?,?,?)""", (name, Number, Model, session['username']))
            conn.commit()
            flash('Car added successfully ')
            return redirect('/addCar')
    else:
        flash('requested page not found')
        return redirect('/')

@app.route('/addDriver', methods=['POST','GET'])
def addDriver():
    if session.get('role') == "user" and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Add Driver')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        
        
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        NID TEXT NOT NULL,
        Phone TEXT NOT NULL,
        creater TEXT NOT NULL
        )""")
        
        Data = c.execute("""SELECT * FROM Drivers """, ).fetchall()
        return render_template("addDriver.html",name = session['name'] ,Pages =Pages,Data=Data)
    
    elif session.get('role') == "user" and request.method == 'POST':
        name = request.form['name']
        NID = request.form['NID']
        Phone = request.form['Phone']
        
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        NID TEXT NOT NULL,
        Phone TEXT NOT NULL,
        creater TEXT NOT NULL
        )""")
        
        Data = c.execute("""SELECT * FROM Drivers WHERE NID = ?""", ([NID])).fetchall()
        
        if Data:
            flash('Driver Exist')
            return redirect('/addDriver')
        else:
            c.execute("""INSERT INTO Drivers (name, NID, Phone, creater) VALUES (?, ?,?,?)""", (name, NID, Phone, session['username']))
            conn.commit()
            flash('Driver added successfully ')
            return redirect('/addDriver')
        
    else:
        flash('requested page not found')
        return redirect('/')
    
@app.route('/createTrip', methods=['POST','GET'])
def createTrip():
    if session.get('role') == "user" and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Create a Trip')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        carNumber TEXT NOT NULL,
        carName TEXT NOT NULL,
        carModel TEXT NOT NULL,
        driverName TEXT NOT NULL,
        driverID TEXT NOT NULL,
        startLocation TEXT NOT NULL,
        endLocation TEXT NOT NULL,
        loaded TEXT ,
        starDateTime TEXT ,
        endDateTime TEXT ,
        shipmentType TEXT NOT NULL,
        shipmentAmount TEXT NOT NULL ,
        discription TEXT NOT NULL,
        Notes TEXT ,
        createrDateTime TEXT NOT NULL,
        creater TEXT NOT NULL
        )""")
        # 16 column wooooo
        Data = c.execute("""SELECT * FROM Trips """, ).fetchall()
        Drivers = c.execute("""SELECT * FROM Drivers """, ).fetchall()
        Cars = c.execute("""SELECT * FROM Cars """, ).fetchall()
        return render_template("createTrip.html",name = session['name'] ,Pages =Pages,Data=Data,Drivers=Drivers,Cars=Cars)
    
    elif session.get('role') == "user" and request.method == 'POST':
        carNumber = request.form['carNumber']
        driverName = request.form['driverName']
        startLocation = request.form['startLocation']
        endLocation = request.form['endLocation']
        shipmentType = request.form['shipmentType']
        shipmentAmount = request.form['shipmentAmount']
        Discription = request.form['Discription']
        Notes = request.form['Notes']
        
        
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        carNumber TEXT NOT NULL,
        carName TEXT NOT NULL,
        carModel TEXT NOT NULL,
        driverName TEXT NOT NULL,
        driverID TEXT NOT NULL,
        startLocation TEXT NOT NULL,
        endLocation TEXT NOT NULL,
        loaded TEXT ,
        starDateTime TEXT ,
        endDateTime TEXT ,
        shipmentType TEXT NOT NULL,
        shipmentAmount TEXT NOT NULL ,
        discription TEXT NOT NULL,
        Notes TEXT ,
        createrDateTime TEXT NOT NULL,
        creater TEXT NOT NULL
        )""")
        driverID=c.execute("""SELECT * FROM Drivers WHERE  name = ?  """, ([driverName])).fetchall()[0]
        Car =c.execute("""SELECT * FROM Cars WHERE  number = ?  """, ([carNumber])).fetchall()[0]
        
        Data1  = c.execute("""SELECT * FROM Trips WHERE  driverID = ?  and  endDateTime is NULL """, ([driverID[2]])).fetchall()
        Data2  = c.execute("""SELECT * FROM Trips WHERE  carNumber = ?  and  endDateTime is NULL """, ([carNumber])).fetchall()
        
       
        if Data1 or Data2:
            flash('invalled trip data')
            return redirect('/createTrip')
        else:
            date = datetime.now()
            c.execute("""INSERT INTO Trips (carNumber, carName, carModel, driverName,driverID,startLocation,endLocation,shipmentType,shipmentAmount,discription,Notes,createrDateTime,creater) 
                      VALUES (?, ?, ?, ?,?,?,?,?,?,?,?,?,?)""", (carNumber, Car[1], Car[2], driverName, driverID[2] ,startLocation, endLocation,shipmentType,shipmentAmount,Discription,Notes,date ,session['username']))
            conn.commit()
            flash('trip created successfully ')
            return redirect('/createTrip')
        
        
    
    
    
    else:
        flash('requested page not found')
        return redirect('/')   

@app.route('/warehouse', methods=['POST','GET'])
def warehouse():
    if session.get('role') == "user" and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'WareHouse')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        return render_template("wareHouse.html",name = session['name'] ,Pages =Pages)
    else:
        flash('requested page not found')
        return redirect('/')  

@app.route('/tripTracker', methods=['POST','GET'])
def tripTracker():
    if session.get('role') == "user" and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Track a trip')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        
        
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Data = c.execute("""SELECT * FROM Trips """, ).fetchall()

        
        return render_template("trackTrip.html",name = session['name'] ,Pages =Pages,Data=Data)
    else:
        flash('requested page not found')
        return redirect('/') 

    
@app.route("/logOut")
def Logout():
    name = session['name']
    session.pop("username",None)
    session.pop("role",None)
    session.pop("name",None)
    # session.pop("Pages",None)
    flash(name + ' logout')
    return redirect('/')
if __name__ == '__main__':
    
    c = conn.cursor()
    Table = c.execute(f"""SELECT name FROM sqlite_master WHERE type='table' AND name='Users';""").fetchall()
    if Table:
        print(f"Table user exists")
    else:
        print(f"Table user does not exist")
        c.execute("""CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        roll TEXT NOT NULL
        )""")
        c.execute("""INSERT INTO Users (username, password, name, roll) VALUES (?, ?,?,?)""", ("armada@test.com", "123", "sabra", "admin"))
        conn.commit()
    c.close()
    app.run(debug = True , host="0.0.0.0")
