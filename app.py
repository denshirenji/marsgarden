import os

from flask import Flask, flash, redirect, render_template, request, session
from datetime import datetime
import re
from flask.scaffold import Scaffold
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import time

from helpers import login_required, apology, weatherCheck

import sqlite3 

app = Flask(__name__)

#Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

gardenItems = [
    {"name": "Moon lilly", "image":"moonlilly", "price":10, "tempstrength":-60, "windstrength":5, "pressurestrength": 600},
    {"name": "Chrysalids", "image":"chrysalids", "price":50, "tempstrength":-90, "windstrength":3, "pressurestrength":580},
    {"name": "Saturn's Tulip Rings", "image":"saturnstuliprings", "price":20, "tempstrength":-63, "windstrength":10, "pressurestrength": 500},
    {"name": "Jupiter Drops", "image":"jupiterdrops", "price":60, "tempstrength":-5, "windstrength":40, "pressurestrength": 650},
    {"name": "Ice Dhalia", "image":"icedhalia", "price":100, "tempstrength":-100, "windstrength":0, "pressurestrength": 700},
    {"name": "Crater Crab Grass", "image":"cratercrabgrass", "price":2, "tempstrength":-62, "windstrength":8, "pressurestrength": 200},
    {"name": "Whipper Willow", "image":"whipperwillow", "price":10, "tempstrength":-70, "windstrength":7, "pressurestrength": 610}
]
gardenItems2 = {
    "Moon Lilly": {"image":"moonlilly", "price":10, "tempstrength":-60, "windstrength":5, "pressurestrength": 600},
    "Chrysalids": {"image":"chrysalids", "price":50, "tempstrength":-90, "windstrength":3, "pressurestrength":580},
    "Saturn's Tulip Rings": {"image":"saturnstuliprings", "price":20, "tempstrength":-63, "windstrength":10, "pressurestrength": 500},
    "Jupiter Drops": {"image":"jupiterdrops", "price":60, "tempstrength":-5, "windstrength":40, "pressurestrength": 650},
    "Ice Dhalia": {"image":"icedhalia", "price":100, "tempstrength":-100, "windstrength":0, "pressurestrength": 700},
    "Crater Crab Grass": {"image":"cratercrabgrass", "price":2, "tempstrength":-62, "windstrength":8, "pressurestrength": 200},
    "Whipper Willow": {"image":"whipperwillow", "price":10, "tempstrength":-70, "windstrength":7, "pressurestrength": 610},
}

#make sure it is https not http
@app.before_request
def enforceHttpsInHeroku():
  if request.headers.get('X-Forwarded-Proto') == 'http':
  url = request.url.replace('http://', 'https://', 1)
  code = 301
  return redirect(url, code=code)

# Ensure responses aren't cached

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
#app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def home():

#to have the same info regardless of the login state
    weatherJSON = weatherCheck()
    print(weatherJSON)
    
    if len(weatherJSON["sol_keys"]) > 0:
        key = weatherJSON["sol_keys"][0]
        temperature = weatherJSON[key]["AT"]["av"]
        temperatureNotAverage = weatherJSON[key]["AT"]
        pressure = weatherJSON[key]["PRE"]["av"]
        windSpeed = weatherJSON[key]["HWS"]["av"]
        print(temperature, "degrees celsius")
        print(temperatureNotAverage)
        print(pressure, "Pascals")
        print(windSpeed, "Meters per second")
    
    else:
        key = 1098
        temperature = -60.566
        pressure = 619.839
        windSpeed = 5.169
        
        
    return render_template(
        "index.html", temperature = temperature, pressure = pressure, windSpeed = windSpeed, key = key
        )

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        #CS50: rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        try:
            con = sqlite3.connect('users.db')
            print ("connected successfully")
    
        except Exception as e:
            print ("connection error")
        
        cur = con.cursor()
        username = request.form.get("username")
        print(username)
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = cur.fetchall()
        #print(rows)
        #print(rows[0])
        #print(rows[0][2])

        # Ensure username exists and password is correct
        if len(rows) != 1: 
            #print(rows)
            print(request.form.get("username"))
            print(request.form.get("password"))
            #print(check_password_hash(rows[0][2], request.form.get("password")))
            return apology("invalid username and/or password", 403)
        
        if not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        
        cur.close()
        con.close()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    if request.method == "POST":
        
        newPassword = request.form.get("password")
        
        letterCount = 0
        numberCount = 0
        symbolCount = 0
        numbers = ['1','2','3','4','5','6','7','8','9','0']
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        symbols = ['`','~','!','@','#','$','%','^','&','*','(',')','_','-','+','=','{','[','}','}','|',':',';','"',"'",'<',',','>','.','?','/']
        
        print(len(newPassword))
        
        for element in range(0, len(newPassword)):
            if newPassword[element] in numbers:
                numberCount += 1
            if newPassword[element] in letters:
                letterCount += 1
            if newPassword[element] in symbols:
                symbolCount += 1
        
        #ensure this username doesn't exist already
        #rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        try:
            con = sqlite3.connect('users.db')
            print ("connected successfully")
    
        except Exception as e:
            print ("connection error")
        
        cur = con.cursor()
        username = request.form.get("username")
        print(username)
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = cur.fetchall()
        #print(rows)
        #print(rows[0])
        #print(rows[0][2])
        
        cur.close()
        con.close() 
        
        
        # Ensure username was submitted
        if not request.form.get("username"):
          return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
            
        #ensure new password = confirm password
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords are not equal", 400)
            
        # Ensure username exists and password is correct
        elif len(rows) > 0:
            return apology("Username already exists", 400)
        
        #ensure password hits all of the password requirements
        elif letterCount == 0:
            return apology ("Password must include at least 1 letter", 403)
            
        elif numberCount == 0:
            return apology ("Password must include at least 1 number", 403)
            
        elif symbolCount == 0:
            return apology ("password must include at least 1 symbol", 403)
            
        elif len(newPassword) < 10:
            return apology ("password must be at least 10 characters long", 403)
        
        else:
            try:
                con = sqlite3.connect('users.db')
                print ("connected successfully")
    
            except Exception as e:
                print ("connection error")
            
            cur = con.cursor()
            username = request.form.get("username")
            hashedPass = generate_password_hash(request.form.get("password"))
            print (hashedPass)
            
            cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashedPass))
            
            con.commit()
            
            cur.close()
            con.close()
            
            return redirect("/login")
            
    else:
        return render_template("register.html") 
    
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    
    if request.method == "POST":
        
        currentPassword = request.form.get("currentPassword")
        newPassword = request.form.get("newPassword")
        confirmPassword = request.form.get("confirmPassword")
        user_id = session["user_id"]
        
        #CS50 version:
        #username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]
        #rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        
        try:
            con = sqlite3.connect('users.db')
            print ("connected successfully")
    
        except Exception as e:
            print ("connection error")
        
        cur = con.cursor()
        username = request.form.get("username")
        print(username)
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        rows = cur.fetchall()
        cur.close()
        con.close() 
        
        print(rows)
        
        check = check_password_hash(rows[0][2], currentPassword)
        print(check)
        
        if not check:
            return apology("The current password wasn't correct!", 403)
            
        elif newPassword != confirmPassword:
            return apology("The confirmation password didn't match original!", 403)
            
        letterCount = 0
        numberCount = 0
        symbolCount = 0
        numbers = ['1','2','3','4','5','6','7','8','9','0']
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        symbols = ['`','~','!','@','#','$','%','^','&','*','(',')','_','-','+','=','{','[','}','}','|',':',';','"',"'",'<',',','>','.','?','/']
        
        for element in range(0, len(newPassword)):
            if newPassword[element] in numbers:
                numberCount += 1
            if newPassword[element] in letters:
                letterCount += 1
            if newPassword[element] in symbols:
                symbolCount += 1
        
        if letterCount == 0:
            return apology ("Password must include at least 1 letter", 403)
        elif numberCount == 0:
            return apology ("Password must include at least 1 number", 403)
        elif symbolCount == 0:
            return apology ("password must include at least 1 symbol", 403)
        elif len(newPassword) < 10:
            return apology ("password must be at least 10 characters long", 403)
        
        else:
            hashpass = generate_password_hash(newPassword)
            #CS50 version:
            #db.execute("UPDATE users SET hash = ? WHERE id = ?", 
            #hashpass,
            #user_id)
            
            try:
                con = sqlite3.connect('users.db')
                print ("connected successfully")
    
            except Exception as e:
                print ("connection error")
        
            cur = con.cursor()
            cur.execute("UPDATE users SET hash = ? WHERE id = ?", (hashpass, user_id))
            con.commit()
            cur.close()
            con.close() 
            
        
            return render_template("updated.html", username = username) 
        
    else:
        
        user_id = session["user_id"]
        print(user_id)
        #CS50 version:
        #username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]
        
        try:
            con = sqlite3.connect('users.db')
            print ("connected successfully")
    
        except Exception as e:
            print ("connection error")
        
        print(user_id)
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchall()
        username = row[0][1]
        cur.close()
        
        cur = con.cursor()
        cur.execute("SELECT points FROM users WHERE id = ?", (user_id,))
        row = cur.fetchall()
        points = row[0][0]
        cur.close()
        con.close()
        
        
        return render_template("account.html", username = username, points = points)
       

@app.route("/mygarden", methods=["GET", "POST"])
@login_required
def mygarden():
    
    if request.method == "POST":
        pass
        
        #QUERY SOLS, WEATHER, and TIME, THEN UPDATE LEVELS ACCORDINGLY
        
        #for some plants, if min temp is below temp resistance, kill plant (level 0)
        
        #for some plants, if average temp is below temp resistence, kill plant (level 0)
        
        #for some plants if average wind is above wind strength, kill plant (level 0)
        
        #for some plants if average pressure is too high or too low, kill plant (level 0)
    
    else:
        weatherJSON = weatherCheck()
        
        if len(weatherJSON["sol_keys"]) > 0:
            key = weatherJSON["sol_keys"][0]
            temperature = weatherJSON[key]["AT"]["av"]
            pressure = weatherJSON[key]["PRE"]["av"]
            windSpeed = weatherJSON[key]["HWS"]["av"]
            print(temperature, "degrees celsius")
            print(pressure, "Pascals")
            print(windSpeed, "Meters per second")
       
        else:
            key = 1098
            temperature = -60.566
            pressure = 619.839
            windSpeed = 5.169
        
        user_id = session["user_id"]
        print(weatherJSON)
        print(user_id)
        print(key)
        
        try:
            con = sqlite3.connect('users.db')
            print ("connected successfully")
    
        except Exception as e:
            print ("connection error")
        
        #up one level if sol increases by 1   
        cur = con.cursor()
        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
        rows = cur.fetchall()
        cur.close()
        
        #update and remove levels according to temperature/pressure/wind strength
        
        i = 0
        
        while i < len(rows):
            if int(key) > int(rows[i][5]):
                if rows[i][3] == "Moon Lilly":
                    if temperature < gardenItems2["Moon Lilly"]["tempstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    if pressure > gardenItems2["Moon Lilly"]["pressurestrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    if windSpeed > gardenItems2["Moon Lilly"]["windstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        print(rowsForLevel[6])
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    
                elif rows[i][3] == "Chrysalids":
                    if temperature < gardenItems2["Chrysalids"]["tempstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                        
                    if pressure > gardenItems2["Chrysalids"]["pressurestrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    
                    if windSpeed > gardenItems2["Chrysalids"]["windstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    
                elif rows[i][3] == "Crater Crab Grass":
                    if temperature < gardenItems2["Crater Crab Grass"]["tempstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                        
                    if pressure > gardenItems2["Crater Crab Grass"]["pressurestrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    
                    if windSpeed > gardenItems2["Crater Crab Grass"]["windstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                
                elif rows[i][3] == "Jupiter Drops":
                    if temperature < gardenItems2["Jupiter Drops"]["tempstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                        
                    if pressure > gardenItems2["Jupiter Drops"]["pressurestrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    
                    if windSpeed > gardenItems2["Jupiter Drops"]["windstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                
                elif rows[i][3] == "Whipper Willow":
                    if temperature < gardenItems2["Whipper Willow"]["tempstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                        
                    if pressure > gardenItems2["Whipper Willow"]["pressurestrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    
                    if windSpeed > gardenItems2["Whipper Willow"]["windstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    
                elif rows[i][3] == "Saturn's Tulip Rings":
                    if temperature < gardenItems2["Saturn's Tulip Rings"]["tempstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                        
                    if pressure > gardenItems2["Saturn's Tulip Rings"]["pressurestrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    
                    if windSpeed > gardenItems2["Saturn's Tulip Rings"]["windstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                
                elif rows[i][3] == "Ice Dhalia":
                    if temperature < gardenItems2["Ice Dhalia"]["tempstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                        
                    if pressure > gardenItems2["Ice Dhalia"]["pressurestrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
                    
                    if windSpeed > gardenItems2["Ice Dhalia"]["windstrength"]:
                        cur = con.cursor()
                        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                        rowsForLevel = cur.fetchall()[i]
                        cur.close()
                        newLevel = int(rowsForLevel[6]) - 2
                        cur = con.cursor()
                        cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[i][2], user_id))
                        con.commit()
                        cur.close()
            i += 1
        
        m = 0
        while m < len(rows):
            if int(key) > int(rows[m][5]):
                cur = con.cursor()
                cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
                rowsForDateCalc = cur.fetchall()[m]
                cur.close()
                newLevel = rowsForDateCalc[6] + 1
                print (newLevel)
                cur = con.cursor()
                cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, rows[m][2], user_id))
                con.commit()
                cur.close()
                cur = con.cursor()
                cur.execute("UPDATE garden SET sol = ? WHERE petname = ? AND user_id =?", (key, rows[m][2], user_id))
                con.commit()
                cur.close()
            m += 1

        #if timestamp is greater than 1 day beyond the timestamp in the garden collection, then level up those garden items
        timeNow = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        for row in rows:
            ts = row[4]
            f = '%Y-%m-%d %H:%M:%S'
            plantTime = datetime.strptime(ts, f)
            timeNowDatetimeFormat = datetime.strptime(timeNow, f)
            deltaTime = timeNowDatetimeFormat - plantTime
            deltaTimeDays = deltaTime.days
            
            if deltaTimeDays > 0:
                newLevel = row[6] + 1
                print(newLevel)
                cur = con.cursor()
                cur.execute("UPDATE garden SET level = ? WHERE petname = ? AND user_id = ?", (newLevel, row[2], user_id))
                con.commit()
                cur.close()
                cur = con.cursor()
                cur.execute("UPDATE garden SET time = ? WHERE petname = ? AND user_id =?", (timeNowDatetimeFormat, row[2], user_id))
                con.commit()
                cur.close()
        
        #find out total points
        cur = con.cursor()
        cur.execute("SELECT points FROM users WHERE id = ?", (user_id,))
        row = cur.fetchall()
        points = row[0][0]
        cur.close()
        
        #find out how many garden items
        cur = con.cursor()
        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
        rows = cur.fetchall()
        gardenQuantity = len(rows)
        cur.close()
        
        #find out how many living garden items
        cur = con.cursor()
        cur.execute("SELECT * FROM garden WHERE user_id = ? AND level > 0", (user_id,))
        rows = cur.fetchall ()
        gardenQuantityLiving = len(rows)
        cur.close()
        
        #get specific info on the garden items for the display in the garden table
        cur = con.cursor()
        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,) )
        rows = cur.fetchall()
        print(rows)
        cur.close()
        
        myGardenSpecificInfos = []
        
        
        for row in rows:
            sellingPrice = int(gardenItems2[row[3]]["price"] * (row[6]/10))
            imageName = gardenItems2[row[3]]["image"]
            myGardenSpecificInfos.append((row[2], row[6], sellingPrice, imageName))
        
        # Getting the oldest plant:
        originalMarker = 0;
        for row in rows:
            ts = row[7]
            f = '%Y-%m-%d %H:%M:%S'
            plantOriginalTime = datetime.strptime(ts, f)
            timeNowDatetimeFormat = datetime.strptime(timeNow, f)
            deltaOriginalTime = timeNowDatetimeFormat - plantOriginalTime
            deltaOriginalTimeDays = deltaOriginalTime.days
            
            if deltaOriginalTimeDays > originalMarker:
                    originalMarker = deltaOriginalTimeDays

        
        con.close()
        
        return render_template("mygarden.html", temperature = temperature, pressure = pressure, windSpeed = windSpeed, key = key, points=points, gardenQuantity = gardenQuantity, gardenQuantityLiving = gardenQuantityLiving, myGardenSpecificInfos = myGardenSpecificInfos, originalMarker = originalMarker)
    
@app.route("/browse", methods=["GET", "POST"])
@login_required
def browse():
    print(gardenItems)
    
    if request.method == "POST":
        pass
    
    else:
        return render_template("browse.html", gardenItems = gardenItems)
    
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    
    if request.method == "POST":
        
        name = request.form.get("name") 
        petname = request.form.get("petname")
        user_id = session["user_id"]
        
        try:
            con = sqlite3.connect('users.db')
            print ("connected successfully")
    
        except Exception as e:
            print ("connection error")
        
        #correcting the name variable because request.form.get only passes the first word
        if name == "Moon":
            name = "Moon Lilly"
        elif name == "Saturn's":
            name = "Saturn's Tulip Rings"
        elif name == "Jupiter":
            name = "Jupiter Drops"    
        elif name == "Ice":
            name = "Ice Dhalia"
        elif name == "Crater":
            name = "Crater Crab Grass"
        elif name == "Whipper":
            name = "Whipper Willow"
        elif not name:
            return apology("There is no plant name!", 404)
        
        print(name)
        print(petname)
        print(user_id)
        
        cur = con.cursor()
        cur.execute("SELECT points FROM users WHERE id = ?", (user_id,))
        row = cur.fetchall()
        points = row[0][0]
        cur.close()
        
        price = gardenItems2[name]["price"]
        
        if points < price:
            return apology("Not enough Mars Coin")
        
        weatherJSON = weatherCheck()
        
        if len(weatherJSON["sol_keys"]) > 0:
            key = weatherJSON["sol_keys"][0]
            temperature = weatherJSON[key]["AT"]["av"]
            pressure = weatherJSON[key]["PRE"]["av"]
            windSpeed = weatherJSON[key]["HWS"]["av"]
            print(temperature, "degrees celsius")
            print(pressure, "Pascals")
            print(windSpeed, "Meters per second")
            sol = weatherJSON["sol_keys"][0]
            
       
        else:
            key = 1098
            temperature = -60.566
            pressure = 619.839
            windSpeed = 5.169
            sol = 1098
        
        cur = con.cursor()
        cur.execute("INSERT INTO garden (user_id, petname, name, sol, level) VALUES (?, ?, ?, ?, 10 )", (user_id, petname, name, sol))
        con.commit()
        cur.close()
        
        remainingPoints = points - price
        
        cur = con.cursor()
        cur.execute("UPDATE users SET points = ? WHERE id = ?", (remainingPoints, user_id)) 
        con.commit()
        cur.close()
        con.close()
        
        return redirect ("/mygarden")
    
    else:
        
        return render_template("buy.html", gardenItems = gardenItems)
    
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    
    if request.method == "POST":
        
        petname = request.form.get("petname")
        
        user_id = session["user_id"]
        
        try:
            con = sqlite3.connect('users.db')
            print ("connected successfully")
    
        except Exception as e:
            print ("connection error")
        
        #get selling value
        cur = con.cursor()
        cur.execute("SELECT level FROM garden WHERE user_id = ? and petname = ?", (user_id, petname))
        level = cur.fetchall()[0][0]
        cur.close()
        
        print(level)
        
        #get price of that plant via their petname
        cur = con.cursor()
        cur.execute("SELECT name FROM garden WHERE petname = ?", (petname,))
        name = cur.fetchall()[0][0]
        cur.close()
        
        price = gardenItems2[name]["price"]
        
        #calculate the selling value by multiplying a prorated level by the price in the dict
        sellingValue = level/10 * price
        
        #get points
        cur = con.cursor()
        cur.execute("SELECT points FROM users WHERE id = ? ", (user_id,))
        points = cur.fetchall()[0][0]
        cur.close() 
        
        newTotalPoints = int(sellingValue + points)
        print(newTotalPoints)
        
        #update the points with more money
        cur = con.cursor()
        cur.execute("UPDATE users SET points = ? WHERE id = ?", (newTotalPoints, user_id))
        
        con.commit()
        cur.close()
        
        #drop that petname from the garden
        cur = con.cursor()
        cur.execute("DELETE FROM garden WHERE petname = ? and user_id = ?", (petname, user_id))
        con.commit()
        cur.close()
        con.close()
        
        return redirect ("/mygarden")
    
    else:
        user_id = session["user_id"]
        print(user_id)
        
        try:
            con = sqlite3.connect('users.db')
            print ("connected successfully")
    
        except Exception as e:
            print ("connection error")
        
        petnames=[]
        
        cur = con.cursor()
        cur.execute("SELECT * FROM garden WHERE user_id = ?", (user_id,))
        rows = cur.fetchall()
        print(rows)
        for row in rows:
            petnames.append(row[2])
        print(petnames)
        cur.close()
        con.close()
        
        return render_template("sell.html", petnames = petnames)

