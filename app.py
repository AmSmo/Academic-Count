from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify
import json
import os.path
from CountSciClass import AnalyzeDoc as CSA
from werkzeug.utils import secure_filename
import CountSciClass as CSA



app = Flask(__name__)
app.secret_key = 'ladida'

def cswebreport(analyze_file):
    subtract = 0
    excluded = "Sections subtracted from your count:<br>"
    included = "Sections left in for total count:<br>"
    highlighted = analyze_file.edited
    if request.form.get("title"):
        excluded += f"Title Count = {analyze_file.title_count}<br>"
        subtract += analyze_file.title_count
        for text in analyze_file.title_text:
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Title<br>"

    if request.form.get("keywords"):
        excluded += f"Title Count = {analyze_file.keywords_count}<br>"
        subtract += analyze_file.keywords_count
        for text in analyze_file.keywords_text:
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Keywords<br>"

    if request.form.get("abstract"):
        excluded += f"Abstract Count = {analyze_file.title_count}<br>"
        subtract += analyze_file.abstract_count
        for text in analyze_file.abstract_text:
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Abstract<br>"

    if request.form.get("notes"):
        excluded += f"Notes Count = {analyze_file.notes_count}<br>"
        subtract += analyze_file.notes_count
        for text in analyze_file.notes_text:
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Notes<br>"

    if request.form.get("table_caption"):
        excluded += f"Table Caption Count = {analyze_file.table_intro_count}<br>"
        subtract += analyze_file.table_intro_count
        for text in analyze_file.table_intro_text:
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Table captions<br>"

    if request.form.get("figure_caption"):
        excluded += f"Figure Caption Count = {analyze_file.figures_count}<br>"
        subtract += analyze_file.figures_count
        for text in analyze_file.figures_text:
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Figure captions<br>"

    if request.form.get("citations"):
        excluded += f"In text citations = {analyze_file.citations_count}<br>"
        subtract += analyze_file.citations_count
        for text in analyze_file.citations_text:
            if text in highlighted and text not in analyze_file.bibliography_text:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Citations<br>"

    if request.form.get("bibliography"):
        excluded += f"Bibliography Count = {analyze_file.bibliography_count}<br>"
        subtract += analyze_file.bibliography_count
        text = analyze_file.bibliography_text
        highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Bibliography<br>"
    highlighted = highlighted.replace("\n", "<br><br>")
    return excluded, included, subtract, highlighted

def cswebtext(analyze_file):
    text = ""
    if request.form.get("title_text"):
        text += f"<h2><p>Title:</p></h2><p>"
        for item in analyze_file.title_text:
            text+= f"{item}<br>"
        text += "</p>"

    if request.form.get("keywords_text"):
        text += f"<h2><p>Keywords:</p></h2><p>"
        for item in analyze_file.keywords_text:
            text+= f"{item}<br>"
        text += "</p>"

    if request.form.get("abstract_text"):
        text += f"<h2><p>Abstract:</p></h2><p>"
        for item in analyze_file.abstract_text:
           text += f"{item}<br>"
        text += "</p>"

    if request.form.get("notes_text"):
        text += f"<h2><p>Notes:</p></h2><p>"
        for item in analyze_file.notes_text:
            text += f"{item}<br>"
        text += "</p>"

    if request.form.get("tcaption_text"):
        text += f"<h2><p>Table captions:</p></h2><p>"
        for item in analyze_file.table_intro_text:
            text += f"{item}<br>"
        text += "</p>"

    if request.form.get("figure_text"):
        text += f"<h2><p>Figure Caption Text:</p></h2><p>"
        for item in analyze_file.figures_text:
            text += f"{item}<br>"
        text += "</p>"

    if request.form.get("citations_text"):
        text += f"<h2><p>In Text Citation Text:</p></h2><p>"
        for item in analyze_file.citations_text:
            text += f"{item}<br>"
        text += "</p>"

    if request.form.get("bibliography_text"):
        text += f"<h2><p>Bibliography:</p></h2><p>"
        prettify = analyze_file.bibliography_text.split("\n")
        for item in prettify:
            text += f"{item}<br>"
        text += "</p>"

    return text

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

        excluded, included, subtract, highlighted = cswebreport(analyze_file)
        analyzed_text = cswebtext(analyze_file)
        return f"""<Center><h1>These are your results<h2></center><br>
        <h3>{excluded}<br>
            {included}<br>
            {analyzed_text}<br>
            {highlighted}
            
            
            
            
            In Table Text = {analyze_file.table_count}<br>
            Table Caption Text = {analyze_file.table_intro_count}<br>
            Figure Caption Text = {analyze_file.figures_count}<br>
            
            In text citations = {analyze_file.citations_count}<br>
            Total Count = {analyze_file.total+analyze_file.table_count}<br>
            {endnote}
            </h3>"""
         
    else:
        return redirect(url_for('home'))

@app.route('/api')
def session_api():
    return jsonify(list(session.keys()))
