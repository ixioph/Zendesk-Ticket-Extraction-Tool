from frontend import Frontend
from flask import Flask, render_template, request, redirect, flash
from werkzeug import secure_filename
import configparser
import pandas as pd
import sys
import ast

app = Flask(__name__)
VALID_EXTENSIONS = set(['json', 'csv'])
body_prepend = '{% extends "base.html" %}\n\n{% block content %}\n'
body_postpend = '\n{% endblock %}'
config_filename = 'config.ini'

config = configparser.ConfigParser()
config.read(config_filename)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/extract')
def extractor(table='',omit=ast.literal_eval(config['COLUMNS']['Omit']), msg=''):
    return render_template('extract.html', table=table, omit=omit, msg=msg)

@app.route('/parse')
def parser(table='',omit=ast.literal_eval(config['COLUMNS']['Omit']), msg=''):
    print(omit)
    return render_template('parse.html', table=table, omit=omit, msg=msg)

@app.route('/search')
def searcher(table='',omit=ast.literal_eval(config['COLUMNS']['Omit']), msg=''):
    return render_template('search.html', table=table, omit=omit, msg=msg)

@app.route('/zextractor', methods=['GET', 'POST'])
def zextractor():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename == '':
            flash('No File Selected.') # This does not work properly
            return redirect(request.url)
        if valid_file(f.filename):
            f.save(secure_filename(f.filename))
            try:
                if request.form['filters'] == 'tags':
                    results, outFile = init_backend(['--pull', '--tags', f.filename])
                elif request.form['filters'] == 'users':
                    results, outFile = init_backend(['--pull', '--user', f.filename])
                elif request.form['filters'] == 'emails':
                    results, outFile = init_backend(['--pull', '--email', f.filename])
                elif request.form['filters'] == 'comments':
                    results, outFile = init_backend(['--pull', '--comt', f.filename])
                else:
                    init_backend(['--help'])
            except Exception as e:
                print(e)
                return 'Script Run Failure!'
            # return file name
            data = pd.DataFrame.from_dict(results)
            return extractor(data.to_html(classes=['table', 'table-bordered', 'table-striped', 'table-sm'], index=False, index_names=False), msg=f'Records successfully saved to {outFile}!')
        return redirect(request.url)
    return 'Wut?' # This happens if the wrong filetype is chosen

@app.route('/zparser', methods=['GET', 'POST'])
def zparser():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename == '':
            flash('No File Selected.') # This does not work properly
            return redirect(request.url)
        if valid_file(f.filename):
            f.save(secure_filename(f.filename))
            try:
                results, outFile = init_backend(['--simple', '--trim', f.filename, 'out.csv'])

            except Exception as e:
                print(e)
                return 'Script Run Failure!'
            data = pd.DataFrame.from_dict(results)
            return parser(data.to_html(classes=['table', 'table-bordered', 'table-striped', 'table-sm'], index=False, index_names=False), msg=f'Records successfully saved to {outFile}!')
        return redirect(request.url)
    return 'Wut U Do?' # This happens if the wrong filetype is chosen

def format_arguments(form):
    args = form['search-args'].split(' ')
    args = '[' + ','.join(args) + ']'
    return args

@app.route('/zsearcher', methods=['GET', 'POST'])
def zsearcher():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename == '':
            flash('No File Selected.') # This does not work properly
            return redirect(request.url)
        if valid_file(f.filename):
            f.save(secure_filename(f.filename))
            try:
                results = {}
                outFile = ''
                args = format_arguments(request.form)
                if request.form['categ'] == 'tags':
                    results, outFile = init_backend(['--element', '--tags', f.filename, args])
                elif request.form['categ'] == 'score':
                    results, outFile = init_backend(['--element', '--score', f.filename, args])
                elif request.form['categ'] == 'date':
                    results, outFile = init_backend(['--element', '--range', f.filename, args])
                elif request.form['categ'] == 'form':
                    results, outFile = init_backend(['--element', '--form', f.filename, args])
                elif request.form['categ'] == 'brand':
                    results, outFile = init_backend(['--element', '--brand', f.filename, args])
                else:
                    init_backend(['--help'])
            except Exception as e:
                print(e)
                return 'Script Run Failure!'
            data = pd.DataFrame.from_dict(results)
            print('Outfile: ' + outFile)
            return searcher(data.to_html(classes=['table', 'table-bordered', 'table-striped', 'table-sm'], index=False, index_names=False), msg=f'Records successfully saved to {outFile}!')
        return redirect(request.url)
    return 'Wut U Do?' # This happens if the wrong filetype is chosen

def valid_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in VALID_EXTENSIONS

def init_backend(cmds):
    program = Frontend()
    return program.start(cmds)


def main():

    app.run(port=1337, debug=True)
    #init_backend(['--simple', '--trim', 'test00.json', 'out.csv'])
    #print(sys.argv)
    #sys.argv.pop(0)
    #print(sys.argv)
    #program = Frontend()
    #program.start(sys.argv)


if __name__ == "__main__":
    main()
