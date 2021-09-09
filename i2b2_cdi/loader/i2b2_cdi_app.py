#
# This Source Code Form is subject to the terms of the Mozilla Public License, v.
# 2.0 with a Healthcare Disclaimer.
# A copy of the Mozilla Public License, v. 2.0 with the Healthcare Disclaimer can
# be found under the top level directory, named LICENSE.
# If a copy of the MPL was not distributed with this file, You can obtain one at
# http://mozilla.org/MPL/2.0/.
# If a copy of the Healthcare Disclaimer was not distributed with this file, You
# can obtain one at the project website https://github.com/igia.
#
# Copyright (C) 2021-2022 Persistent Systems, Inc.
#
import os
from flask import Flask, flash, request, redirect, url_for, jsonify
from i2b2_cdi.loader import i2b2_cdi_loader as I2b2CdiLoader

UPLOAD_FOLDER = 'data/'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(24)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/cdi-api/concept', methods=['DELETE', 'POST'])
def perform_concept():
    if request.method == 'DELETE':
        I2b2CdiLoader.delete_concepts()
        return "Concepts deleted successfully"
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return "File not provided"
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return "File not selected"
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_list = [ UPLOAD_FOLDER + filename]
            I2b2CdiLoader.load_concepts(file_list)
            return "Concepts uploaded successfully"

# driver function
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')