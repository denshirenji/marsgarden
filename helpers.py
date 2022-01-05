import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def weatherCheck():
    # Contact API
    try:
        url = f"https://api.nasa.gov/insight_weather/?api_key=Ga5zBJKMIXwOGFFTVK14z3Hpm7nNUcFc6Lk8XhLr&feedtype=json&ver=1.0"
        #"https://api.nasa.gov/planetary/apod?api_key=Ga5zBJKMIXwOGFFTVK14z3Hpm7nNUcFc6Lk8XhLr"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    
    try:
        quote = response.json()
        #return {
        #    "name": quote["companyName"],
        #    "price": float(quote["latestPrice"]),
        #    "symbol": quote["symbol"]
        #}
    except (KeyError, TypeError, ValueError):
        return None
    
    return quote;