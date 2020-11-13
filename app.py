import calendar
from datetime import date, datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, request, jsonify, abort
import os

app = Flask(__name__)
# Firestore db connection
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, { 'projectId': 'bday-294317' })
db = firestore.client()
collection = 'hello'

@app.route('/hello/<name>',methods = ['POST', 'GET'])
def hello_name(name):
    if not name.isalpha():
        return jsonify(error='name must contain only letters!'), 400
    print(request.method)
    if request.method == 'POST':
        content = request.json
        try:
            past = datetime.strptime(content["dateOfBirth"], "%Y-%m-%d")
        except ValueError as e:
             return jsonify(error="Date should should be in format YYYY-MM-DD, " + e), 400
        present = datetime.now()
        if not past.date() < present.date():
            return jsonify(error='dateOfBirth must be before current date!'), 400
        db.collection(collection).document(name).set(content)
        return '', 204
    else:
        now = datetime.now()
        doc = db.collection(collection).document(name).get()
        if doc.exists:
            content = doc.to_dict()['dateOfBirth']
            bday = datetime.strptime(content, "%Y-%m-%d")
        else:
            return jsonify(error='No such name!'), 400
        number_to_bday = calculate_dates(bday, now)
        if now.month == bday.month and now.day == bday.day:
            return '{ "message": "Hello, %s! Happy birthday!" }' % name, 200
        else:
            return '{ "message": "Hello, %s! Your birthday is in %s day(s)" }' % ( name, number_to_bday ), 200
 
def calculate_dates(bday, now):
    """
    Calculate number of days between two dates
    """
    n = 1
    delta1 = datetime(now.year, bday.month, bday.day).date()
    # Taking care of those lucky ones born on February 29th
    if bday.month == 2 and bday.day == 29:
        while not calendar.isleap(now.year+n):
            n = n + 1            
    delta2 = datetime(now.year+n, bday.month, bday.day).date()
    return ((delta1 if delta1 > now.date() else delta2) - now.date()).days

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
   app.run(threaded=True, host='0.0.0.0', port=port)
 