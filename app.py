from flask import Flask, render_template, request, send_file, send_from_directory
import os
import tempfile
import re
import psutil

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 7 * 1024 * 1024  # 5MB

import subprocess
import os

def increment_runs():
    # Open the file in read mode to read the current number
    with open('runs.txt', 'r') as file:
        current_number = int(file.read().strip())

    # Increment the number by 1
    new_number = current_number + 1

    # Open the file in write mode to overwrite with the new number
    with open('runs.txt', 'w') as file:
        file.write(str(new_number))



def process_file(file_path):
    # Get the absolute path to the worker.sh script
    script_path = os.path.abspath('./worker6.sh')

    # Get the directory containing the worker.sh script
    script_dir = os.path.dirname(script_path)

    try:
        # Change to the script's directory and execute the worker.sh script with the file_path argument
        r = subprocess.run([script_path, file_path], check=True, cwd=script_dir)
        print(r)
    except subprocess.CalledProcessError as e:
        print(f"Error executing worker script: {e}")

def format_time(hours):
    # Calculate the hours and minutes
    hours = float(hours.strip())
    hours_int = int(hours)
    minutes = int((hours - hours_int) * 60)

    # Format the time as "(XXh YYm)"
    formatted_time = f"{hours_int}h {minutes}m"
    
    return formatted_time

def sanitize_filename(filename):
    # Replace all non-alphanumeric, non-hyphen, non-underscore, and non-period characters with an underscore
    sanitized_filename = re.sub(r'[^\w\-.]', '_', filename)
    return sanitized_filename


# Define a route to render the upload form
@app.route('/')
def upload_form():

    with open("runs.txt","r", encoding="UTF-8") as file:
        runs=file.readline()
    return render_template('upload.html',runs=runs,cpu=psutil.cpu_percent(0.3))

# Define a route to handle file upload and processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    if file:
        # Save the uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        print(temp_dir)
        file.filename.replace(" ","_")
       	file.filename = sanitize_filename(file.filename)
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        print(file_path)

        # Run your Python script to process the file
        # Replace this with your actual processing logic
        process_file(file_path)

        # Serve the generated files for download
        data_file = os.path.join("downloads/", file.filename+'.zip')
        time = "1.5"
        with open(os.path.join(temp_dir, "time.txt"),"r", encoding="UTF-8") as time_file:
            time=time_file.readline()

        increment_runs()
        return render_template('download.html', data_file=data_file, ETA=format_time(time))

# Define a route to download the generated files
@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory('downloads', filename, as_attachment=True)

@app.errorhandler(413)
def request_entity_too_large(error):
        return "File is too large. Maximum file size is 5MB.", 413


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0",port=63080)

