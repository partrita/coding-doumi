import os
import re
import time
import subprocess

from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin

application = Flask(__name__)
application.debug = True

def save_file(file_name, source_code):
    source_file = open(file_name, 'w', encoding='utf-8')
    source_file.write(source_code)
    source_file.close()

def run_code(command, file_name, compile_check=False):
    start_time = time.time() * 1000
    compile_status = False

    try:
        data = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True, timeout=5, encoding='utf8')
        if compile_check:
            compile_status = True
    except subprocess.CalledProcessError as e:
        data = str(e.output)
        data = data.replace(file_name.split('.')[0], 'source')
    except subprocess.TimeoutExpired:
        data = 'Timeout'
    except:
        data = 'Something wrong!'
    
    try:
        os.remove(file_name)
    except :
        pass
    
    result = {
        'result': data,
        'time': str( round( (time.time() * 1000 - start_time), 4) ) + 'ms'
    }
    if compile_check:
        result.update({'compile_status': compile_status})

    return result

@application.route('/')
def ide():
    return render_template('ide.html')

@application.route("/run/<type>", methods=['GET','POST'])
def run(type):
    if request.method =='GET':
        return str(type)
    
    if request.method =='POST':
        code = request.form['source']
        intt = request.args.get('intt')
        file_name = request.args.get('intt')

        if type == 'c':
            code = code.replace('#include', '')
            code = code.replace('<stdio.h>', '')
            code = "#include <stdio.h>\n" + code
            file_name += '.c'
        if type == 'cpp':
            code = code.replace('#include', '')
            code = code.replace('<iostream>', '')
            code = "#include <iostream>\n" + code
            file_name += '.cpp'
        if type == 'rs':
            code = code.replace('std::', '')
            file_name += '.rs'
        if type == 'py3':
            code = code.replace('open', '')
            code = code.replace('import', '')
            file_name += '.py'
        if type == 'js':
            code = code.replace('require', '')
            file_name += '.js'
        
        save_file(file_name, code)
        
        if type == 'c':
            result = run_code(['gcc', file_name, '-o', intt], file_name, compile_check=True)
            if result['compile_status'] == False:
                return result
            else:
                return run_code(['./' + intt], intt)
        if type == 'cpp':
            result = run_code(['g++', file_name, '-o', intt], file_name, compile_check=True)
            if result['compile_status'] == False:
                return result
            return run_code(['./' + intt], intt)
        if type == 'rs':
            result = run_code(['rustc', file_name], file_name, compile_check=True)
            if result['compile_status'] == False:
                return result
            return run_code(['./' + intt], intt)
        if type == 'py3':
            return run_code(['python', file_name], file_name)
        if type == 'js':
            return run_code(['node', file_name], file_name)
    
if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000)