from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import CheckConstraint

app = Flask(__name__)

# Baza danych - test
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #nazwa naszej bazy danych to database.db
db = SQLAlchemy(app)

class Grades(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    Grade = db.Column("Grade", db.Integer, nullable = False) #NOT NULL)
    added_date = db.Column("added_date", db.DateTime, default=datetime.utcnow) #tu trzeba bedzie dac jakas inną funkcje bo datetime.utcnow ma byc usunieta niedlugo
    __table_args__ = (CheckConstraint('Grade >= 2 AND Grade <= 5', name='Limit_Ocen'),)# oceny od 2 do 5

    #def __init__(self):


    def __repr__(self):
        return '<Task %r' % self.id

@app.route('/') #Strona glowna
def index():
    return render_template('index.html')

@app.route('/grades', methods=['POST','GET']) # POST daje nam mozliwosc wysylania danych do bazy danych

def grades(): #kod do grades.html
    if request.method == 'POST': # jezeli klikniemy np. przycisk ktory jest w <form action="/" method="POST"> to wykonuje sie to co pod spodem
        grade_content = int(request.form['grade']) # ta zmienna zbiera wartość z pola obok przycisku w momencie kiedy go klikniemy
        new_grade = Grades(Grade=grade_content)

        try:
            db.session.add(new_grade)
            db.session.commit()
            return redirect('/')
        except:
            return "Wystapil blad przy dodawaniu oceny"

    else:
        return render_template('grades.html')






if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # tworzy baze danych przy odpaleniu\dodaje do niej nowe tabele albo kolumny w istniejacych tabelach
                         # ale nie aktualizuje juz istniejacych kolumn, wiec trzeba bedzie tez przy tym przysiąść jakbysmy chcieli cos modyfikowac
                         # no ale to w przyszlosci o tym pomyslimy

    app.run(debug=True)