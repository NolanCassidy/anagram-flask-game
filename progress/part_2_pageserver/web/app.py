import os.path

from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def blank():
    return fileforbidden_403(403)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def findPath(path):
    if("~" in  path or "//" in  path or ".." in  path):
        return fileforbidden_403(403)
    if os.path.isfile("templates/"+path):
        return render_template(path), 200
    return filenotfound_404(404)

@app.errorhandler(404)
def filenotfound_404(error):
    return render_template("404.html"), 404

@app.errorhandler(403)
def fileforbidden_403(error):
    return render_template("403.html"), 403


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
