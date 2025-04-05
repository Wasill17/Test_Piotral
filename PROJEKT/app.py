from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import CheckConstraint

app = Flask(__name__)

# Baza danych - test
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #nazwa naszej bazy danych to database.db
db = SQLAlchemy(app)

class Oceny(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    Ocena = db.Column("Ocena", db.Integer, nullable = False) #NOT NULL)
    datadodania = db.Column("data_dodania", db.DateTime, default=datetime.utcnow) #tu trzeba bedzie dac jakas inną funkcje bo datetime.utcnow ma byc usunieta niedlugo
    __table_args__ = (CheckConstraint('Ocena >= 2 AND Ocena <= 5', name='Limit_Ocen'),)# oceny od 2 do 5

    #def __init__(self):


    def __repr__(self):
        return '<Task %r' % self.id

@app.route('/', methods=['POST','GET']) # POST daje nam mozliwosc wysylania danych do bazy danych
def index():
    if request.method == 'POST': # jezeli klikniemy np. przycisk ktory jest w <form action="/" method="POST"> to wykonuje sie to co pod spodem
        pole_oceny = int(request.form['ocena']) # ta zmienna zbiera wartość z pola obok przycisku w momencie kiedy go klikniemy
        nowa_ocena = Oceny(Ocena=pole_oceny)

        try:
            db.session.add(nowa_ocena)
            db.session.commit()
            return redirect('/')
        except:
            return "Wystapil blad przy dodawaniu oceny"

    else:
        return render_template('index.html')



if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # tworzy baze danych przy odpaleniu

    app.run(debug=True)