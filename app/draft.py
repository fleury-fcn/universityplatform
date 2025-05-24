from flask import Flask,render_template,url_for



app = Flask(__name__,
        static_folder= 'static',
        template_folder= 'templates')

@app.route('/')
def HomePage():
    return render_template('HomePage.html')

@app.route('/PageConnexion')
def PageConnexion():
    return render_template('PageConnexion.html')

@app.route('/PageInscription')
def PageInscription():
    return render_template('PageInscription.html')




if __name__ == "__main__":
        app.run(debug= True)
   