from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('home.html')


@app.route("/checkuser", methods=['GET'])
def bacc():
    return render_template('checkuser.html')


@app.route("/checkuser", methods=['POST'])
def bacc_post():
    wiki = request.form['wiki'].strip()
    user = request.form['username'].strip()
    return render_template(
        'checkuser_done.html',
        wiki=wiki,
        user=user)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
