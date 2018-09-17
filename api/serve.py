#!/usr/bin/env python

'''
Serves the HTTP interface to FormulaEngine via a REST API.
TODO(aditya): Define HTTP interface to FormulaEngine via a REST API.
'''

__author__ = 'Aditya Viswanathan'
__email__ = 'aditya@adityaviswanathan.com'

from flask import Flask, flash, jsonify, redirect, render_template, request
import os
import sys
from werkzeug.utils import secure_filename
from app import app
# Append parent dir to $PYTHONPATH to import ReportTraverser, whose public
# methods have bindings into Function.
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(my_path, os.pardir)))
from report_utils import AxisDecision, ReportTraverser, to_csv
from formula_engine import ParseTree, Function
from entities import Db, ActionExecutor

ALLOWED_EXTENSIONS = set(['xlsx', 'csv', 'txt'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Entity API (supports GET/POST/PUT semantics).
@app.route('/<entity_name>', methods=['GET'])
def get_entity(entity_name):
    data = []
    try:
        print 'Querying %s...' % entity_name
        executor = ActionExecutor(entity_name)
        data = executor.query_all()
        print 'Found %d records' % len(data)
    except Exception as e:
        print(e)
    return render_template('entity_table.html', entityName=entity_name, entities=data)

@app.route('/<entity_name>', methods=['POST'])
def add_entity(entity_name):
    entry = {}
    payload = request.get_json()
    try:
        print 'Creating %s...' % entity_name
        executor = ActionExecutor(entity_name)
        entry = executor.create(payload)
    except Exception as e:
        print(e)
    return jsonify(entry)

@app.route('/<entity_name>', methods=['PUT'])
def update_entity(entity_name):
    entry = {}
    payload = request.get_json()
    try:
        print 'Updating %s with id %s' % (entity_name, payload['id'])
        executor = ActionExecutor(entity_name)
        entry = executor.update(payload)
    except Exception as e:
        print(e)
    return jsonify(entry)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        f = request.files['file']
        if f.filename == '':
            print 'No selected file.'
            return redirect(request.url)
        if not allowed_file(f.filename):
            print 'Extension of file "' + f.filename + '" not allowed.'
        if f:
            filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)
            print 'Processed file "' + filename + '".'
            print 'Making axis decision...'
            print filepath.endswith('.csv')
            data_file = to_csv(filepath, app.config['UPLOAD_FOLDER']) if \
                not filepath.endswith('.csv') else filepath
            axis_decision = AxisDecision(data_file)
            axis_decision.decide()
            print 'Decided that ' + str(axis_decision.date_axis) + \
                ' is the date axis and ' + str(axis_decision.title_axis) + \
                ' is the title axis.'
            print 'Decided that ' + str(axis_decision.date_index) + \
                ' is the date axis start index and ' + \
                str(axis_decision.title_index) + ' is the title axis start index.'
            traverser = ReportTraverser(data_file,
                                        axis_decision.date_axis,
                                        axis_decision.date_index,
                                        axis_decision.title_axis,
                                        axis_decision.title_index)
            print 'Constructed ReportTraverser.'
            dates_ptree = ParseTree('get_dates(0)', [traverser])
            titles_ptree = ParseTree('get_titles(0)', [traverser])
            print 'Constructed ParseTree.'
            d = [date.val for date in dates_ptree.evaluate_tree(is_list=True)]
            t = [title.val for title in titles_ptree.evaluate_tree(is_list=True)]
            print 'Fetched headers.'
            r = []
            for title in t:
                if not title.strip():
                    r.append([''] * len(d[1:]))
                    continue
                title_ptree = ParseTree('get_cells_by_title(0, ' + title  + ')', [traverser])
                r.append([date.val for date in title_ptree.evaluate_tree(is_list=True)])
            print 'Fetched base report data.'
            funcs = Function.NAMES
            return render_template('home.html', dates=d, titles=t, rows=r, funcs=funcs, filename=data_file)
    # GET request default case.
    return render_template('home.html')

@app.route('/execute', methods=['POST'])
def execute_formula():
    payload = request.get_json()
    # TODO(aditya): Check that 'filename' and 'formulaString' are in payload.
    axis_decision = AxisDecision(payload['filename'])
    axis_decision.decide()
    print 'Decided that ' + str(axis_decision.date_axis) + \
        ' is the date axis and ' + str(axis_decision.title_axis) + \
        ' is the title axis.'
    print 'Decided that ' + str(axis_decision.date_index) + \
        ' is the date axis start index and ' + \
        str(axis_decision.title_index) + ' is the title axis start index.'
    traverser = ReportTraverser(payload['filename'],
                                axis_decision.date_axis,
                                axis_decision.date_index,
                                axis_decision.title_axis,
                                axis_decision.title_index)
    print 'Constructed ReportTraverser.'
    ptree = ParseTree(payload['formulaString'], [traverser])
    if 'isList' in payload.keys() and payload['isList']:
        list_parse_output = ptree.evaluate_tree(is_list=True)
        print list_parse_output
        list_data = {
            'data' : [i.val for i in list_parse_output],
            'titles' : [i.title.val if i.title is not None else i.title for i in list_parse_output],
            'dates' : [i.date.val if i.date is not None else i.date for i in list_parse_output]
        }
        print 'Sending the following list data response to client: ' +  \
            str(list_data)
        return jsonify(list_data)
    parse_output = ptree.evaluate_tree()
    singleton_data = {
        'data' : parse_output.val,
        'titles' : parse_output.title.val,
        'dates' : parse_output.date.val
    }
    print 'Sending the following singleton data response to client: ' +  \
        str(singleton_data)
    return jsonify(singleton_data)

if __name__ == '__main__':
    Db.init_app(app)
    app.run(debug=True)
