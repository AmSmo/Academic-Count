from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify
import json
import os.path
from CountSciClass import AnalyzeDoc as CSA
from werkzeug.utils import secure_filename
import CountSciClass as CSA
import pandas as pd
import re
wordcount = r"\S+"

app = Flask(__name__)
app.secret_key = 'ladida'
trouble =""
def cswebreport(analyze_file):
    subtract = 0
    excluded = "Sections subtracted from your count:<br>"
    included = "Sections left in for total count:<br>"
    report = ""
    highlighted = analyze_file.edited
    if request.form.get("title"):
        excluded += f"Title Count = {analyze_file.title_count}<br>"
        subtract += analyze_file.title_count
        for text in analyze_file.title_text:
            if text in highlighted:
                analyze_file.no_doubles += text + " "
                highlighted = highlighted.replace(text, f"<span style='background-color:powderblue;'>{text}</span>")
                if re.findall(r'\w', text):
                    highlighted = highlighted.replace(text, f"<span style='background-color:powderblue;'>{text}</span>")
    else:
        included += "Title<br>"

    if request.form.get("near_miss"):
        report += f"<h2>Following not quantified as a citation</h2><br>"
        for text in analyze_file.false_negatives:
            report += text + "<br>"
        report += text + "<br>"

    if request.form.get("keywords"):
        excluded += f"Keywords Count = {analyze_file.keywords_count}<br>"
        subtract += analyze_file.keywords_count
        for text in analyze_file.keywords_text:
            analyze_file.no_doubles += text + " "
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<span style='background-color:chartreuse;'>{text}</span>")
    else:
        included += "Keywords<br>"

    if request.form.get("abstract"):
        excluded += f"Abstract Count = {analyze_file.abstract_count}<br>"
        subtract += analyze_file.abstract_count
        for text in analyze_file.abstract_text:
            analyze_file.no_doubles += text + " "
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<span style='background-color:coral;'>{text}</span>")
    else:
        included += "Abstract<br>"

    if request.form.get("notes"):
        excluded += f"Notes Count = {analyze_file.notes_count}<br>"
        subtract += analyze_file.notes_count
        for text in analyze_file.notes_text:
            analyze_file.no_doubles += text + " "
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Notes<br>"

    if request.form.get("table_caption"):
        excluded += f"Table Caption Count = {analyze_file.table_intro_count}<br>"
        subtract += analyze_file.table_intro_count
        for text in analyze_file.table_intro_text:
            analyze_file.no_doubles += text + " "
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Table captions<br>"

    if request.form.get("table_text"):
        excluded += f"In Table Count = {analyze_file.table_count}<br>"

        for text in analyze_file.table_text:
            analyze_file.no_doubles += text + " "
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        analyze_file.total+=analyze_file.table_count
        included += "Table captions<br>"

    if request.form.get("figure_caption"):
        excluded += f"Figure Caption Count = {analyze_file.figures_count}<br>"
        subtract += analyze_file.figures_count
        for text in analyze_file.figures_text:
            analyze_file.no_doubles += text + " "
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Figure captions<br>"

    if request.form.get("appendices"):
        excluded += f"Appendices Count = {analyze_file.appendices_count}<br>"
        subtract += analyze_file.appendices_count
        for text in analyze_file.appendices_text:
            analyze_file.no_doubles += text + " "
            if text in highlighted:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
    else:
        included += "Appendix<br>"

    if request.form.get("bibliography"):
        excluded += f"Bibliography Count = {analyze_file.bibliography_count}<br>"
        subtract += analyze_file.bibliography_count
        text = analyze_file.bibliography_text
        analyze_file.no_doubles += text + " "
        if text == " " or text == "":
            pass
        else:
            highlighted = highlighted.replace(text, f"<span id=\"bibliography\" style='background-color:lightsteelblue;'>{text}</span>")
    else:
        included += "Bibliography<br>"


    if request.form.get("excised_text"):
        report += f"<h2>Following were words counted but found in a citation</h2><br>"
        count = 0
        for text in analyze_file.citation_excise_text:
            split = text.split("FROM: ")
            if re.search(rf"{split[1]}", analyze_file.no_doubles):
                analyze_file.citations_count -= len(re.findall(wordcount, split[1]))
                pass
            elif count == 0:
                report += "<ol>"
                count += 1
            report += f"<li>{text}</li> With a word count of <strong>{len(re.findall(wordcount, split[0]))}</strong> included in your total text <br>"
        report += "</ol><br>"

    if request.form.get("citations"):
        for text in analyze_file.citations_text:
            if text in analyze_file.no_doubles:
                analyze_file.citations_count-= len(re.findall(wordcount, text))
                continue
            if text in highlighted and text not in analyze_file.bibliography_text and text not in analyze_file.no_doubles:
                highlighted = highlighted.replace(text, f"<mark>{text}</mark>")
        for text in analyze_file.citation_excise_text:
            split = text.split("FROM: ")
            if re.search(rf"\(?{split[1]};?", analyze_file.no_doubles):
                pass
            else:
                highlighted = highlighted.replace(split[1], f"<span style='background-color:lightpink;'>{split[1]}</span>")

        excluded += f"In text citations = {analyze_file.citations_count}<br>"
        subtract += analyze_file.citations_count
    else:
        included += "Citations<br>"
    highlighted = highlighted.replace("\n", "<br><br>\n")
    return excluded, included, subtract, highlighted, report

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

    if request.form.get("intable_text"):
        text += f"<h2><p>In Table text:</p><br></h2><p>"
        tables=[]
        for table in analyze_file.opened.tables:
            df = [['' for i in range(len(table.columns))] for j in range(len(table.rows))]
            for i, row in enumerate(table.rows):
                for j, cell in enumerate(row.cells):
                    if cell.text:
                        df[i][j] = cell.text
            tables.append(pd.DataFrame(df))
            tables[-1].columns= tables[-1].iloc[0]
            tables[-1]= tables[-1].set_index(tables[-1].columns[0])
            item = pd.DataFrame.to_html(tables[-1])
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
            if item in analyze_file.no_doubles:
                continue
            else:
                text += f"{item}<br>"
        text += "</p>"

    if request.form.get("bibliography_text"):
        text += f"<h2><p>Bibliography:</p></h2><p>"
        prettify = analyze_file.bibliography_text.split("\n")
        for item in prettify:
            text += f"{item}<br>"
        text += "</p>"

    if request.form.get("appendices_text"):
        text += f"<h2><p>Appendices Text:</p></h2><p>"
        for item in analyze_file.appendices_text:
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
        user_file.save('./static/user_files/' + local)
        if request.form['stop_word'] == "":
            endnote = None
        else:
            endnote = request.form['stop_word']

        analyze_file = CSA.AnalyzeDoc('./static/user_files/'+local, endnote)

        excluded, included, subtract, highlighted, report = cswebreport(analyze_file)
        analyzed_text = cswebtext(analyze_file)
        if request.form.get("full_report"):
            highlighted = "<h2><b><center>Full Text Highlighted</center></h2></b>" + highlighted
        else:
            highlighted = ""
        return f"""<Center><h1>These are your results<h2></center><br>
        <h3>{excluded}<br>
            {included}<br>
            Total Count before excluding selections = {analyze_file.total}<br>
            Total Exclusions = {subtract} <br>
            Word Count for your submission = {analyze_file.total-subtract}<br>
            {analyzed_text}<br>
            {highlighted}<br>
            {report}<br>
            {trouble}
            
            </h3>"""
         
    else:
        return redirect(url_for('home'))

@app.route('/api')
def session_api():
    return jsonify(list(session.keys()))
