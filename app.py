from flask import Flask, render_template, request
from utils import extract_text, analyze

app=Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    result=None
    if request.method=="POST":
        f=request.files["resume"]
        jd=request.form["job_description"]
        path="uploads/"+f.filename
        f.save(path)
        resume=extract_text(path)
        result=analyze(resume,jd)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
