from flask import Flask, render_template, request, send_file, redirect, url_for
import threading
import os
from generateYearBook import YearBook

progress_thread = None

app = Flask(__name__)

class ProgressThread(threading.Thread):
    def __init__(self, email, password, **kwargs):
        self.progress = 0
        self.email = email
        self.password = password
        self.kwargs = kwargs
        super().__init__()

    def run(self):
        self.yb = YearBook(self.email, self.password, **self.kwargs)
        self.maxProg = len(self.yb.messagesForYou) + len(self.yb.messagesByYou)
        def update_progress(current):
            self.progress = int((current / self.maxProg) * 100)
        self.yb.set_progress_callback(update_progress)
        self.yb.generate_pdf("yearbook.pdf")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/process', methods=['POST', 'GET'])
def process():
    if request.method == 'POST':
        global progress_thread
        email = request.form['email']
        password = request.form['password']
        include_friends = 'friends' in request.form
        dark_mode = 'dark_mode' in request.form
        progress_thread = ProgressThread(
            email=email,
            password=password,
            include_friends=include_friends,
            dark_mode=dark_mode
        )
        progress_thread.start()
        return render_template("progress.html")
    else:
        return redirect(url_for('home'))

@app.route('/download', methods=['GET'])
def download():
    if os.path.exists("yearbook.pdf"):
        return send_file(
            'yearbook.pdf',
            as_attachment=True,
            download_name="yearbook.pdf",
            mimetype='application/pdf'
        ), 200
    else:
        return "Yearbook is not generated yet", 404

@app.route('/progress', methods=['GET'])
def progress():
    global progress_thread
    if progress_thread is not None:
        return str(int(progress_thread.progress)), 200
    else:
        return "Yearbook generation not started", 404

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)