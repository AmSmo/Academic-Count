from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify
import json
import os.path
from CountSciClass import AnalyzeDoc as CSA
from werkzeug.utils import secure_filename
import CountSciClass as CSA

app = Flask(__name__)
app.secret_key = 'ladida'
tocount=[]

@app.route('/')
def home():
    return render_template('home.html', nomdefiles=session.keys())


@app.route('/your-analysis', methods = ["GET", "POST"])
def your_analysis():
    if request.method == "POST":
        files = {}
        if os.path.exists('urls.json'):
            with open('urls.json') as urls_file:
                urls = json.load(urls_file)

        user_file = request.files['file']

        local = secure_filename(user_file.filename)
        user_file.save('/Users/adamsmolenski/documents/github/countsci2/static/user_files/' + local)
        if request.form['stop_word'] == "":
            endnote = None
        else:
            endnote = request.form['stop_word']

        analyze_file = CSA.AnalyzeDoc('./static/user_files/'+local, endnote)


        return f"""<Center><h1>These are your results<h2></center><br>
        <h3>Title Count = {analyze_file.title_count}<br>
            Abstract Count = {analyze_file.abstract_count}<br>
            Keywords Count = {analyze_file.keywords_count}<br>
            Notes = {analyze_file.notes_count}<br>
            In Table Text = {analyze_file.table_count}<br>
            Table Caption Text = {analyze_file.table_intro_count}<br>
            Figure Caption Text = {analyze_file.figures_count}<br>
            Bibliography = {analyze_file.bibliography_count}<br>
            In text citations = {analyze_file.citations_count}<br>
            Total Count = {analyze_file.total+analyze_file.table_count}<br>
            {endnote}
            </h3>"""
         
    else:
        return redirect(url_for('home'))

@app.route('/api')
def session_api():
    return jsonify(list(session.keys()))

print(*tocount)