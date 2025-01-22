from flask import Flask
from flask import render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def user():
    return render_template("login.html")

@app.route("/login")
def loginpage():
    return render_template("loginpage.html", message="log")

@app.route("/register")
def registerpage():
    return render_template("loginpage.html", message="reg")