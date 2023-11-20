from flask import Flask,render_template,url_for,g

app=Flask(__name__)


@app.route('/')
def home():
    g.connected=False
    return render_template('home.html')

if __name__=='__main__':
    app.run(debug=True)