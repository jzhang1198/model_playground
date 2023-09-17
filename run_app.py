#!/usr/bin/env python3

import os
import sys
import argparse
from flask import Flask
from model_playground.routes import template

app = Flask(__name__, static_url_path='/static', template_folder='./templates')
app.config['model_file'], app.config['model'], app.config['plot_data'] = None, None, {}

# register route handling functions
app.register_blueprint(template)

if __name__ == '__main__':

    # construct parser
    parser = argparse.ArgumentParser(description='Runs a modelPlayground local server.')
    parser.add_argument('--model-file', type=str, help='Path to model file.', required=True)

    # access arguments
    args = parser.parse_args()
    app.config['model_file'] = args.model_file

    # ensure model file exists
    if not app.config['model_file']: 
        print('ERROR: A model file is required to run the local server.')
        sys.exit()

    elif not os.path.exists(app.config['model_file']):
        print('ERROR: Model file not found.')
        sys.exit()

    app.run()