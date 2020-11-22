from flask import Flask, jsonify, render_template, request,url_for, redirect
from random import choice
from OMR import OMR_Evaluator
import os

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html') 

@app.route('/upload',methods = ['GET','POST'])
def upload():
    if request.method == 'POST':
        f = request.files['omr']
        img_name = f.filename
        f.save(img_name)
        
        key = []
        f = request.files['key']
        key_name = f.filename
        f.save(key_name)
        with open(key_name) as fs:
            option = fs.readlines()
            for o in option:
                key.append(tuple(str(o).split()))
        print(key)

        obj = OMR_Evaluator(img_name,key)
        os.remove(img_name)
        os.remove(key_name)
        return render_template('result.html', enroll = obj.enroll, score = obj.student_score)

if __name__ == "__main__":
    app.run(debug = True)