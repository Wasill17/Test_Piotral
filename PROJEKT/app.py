from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import CheckConstraint

app = Flask(__name__)
app.secret_key = 'tajny-klucz-zadymeczka'
# Baza danych
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #nazwa naszej bazy danych to database.db
db = SQLAlchemy(app)

# TABELE
class Grades(db.Model):
    id = db.Column("id", db.Integer, primary_key=True, autoincrement = True)
    Grade = db.Column("Grade", db.Integer, nullable = False) #NOT NULL)
    added_date = db.Column("added_date", db.DateTime, default=datetime.utcnow) #tu trzeba bedzie dac jakas inną funkcje bo datetime.utcnow ma byc usunieta niedlugo
    __table_args__ = (CheckConstraint('Grade >= 2 AND Grade <= 5', name='Limit_Ocen'),)# oceny od 2 do 5

    #def __init__(self):
    def __repr__(self):
        return '<Grade %r' % self.id

class UserInfo(db.Model):
    id = db.Column("id", db.Integer, primary_key=True, autoincrement = True)
    first_name = db.Column("first_name", db.String, nullable = False)
    last_name = db.Column("last_name", db.String, nullable = False)
    email = db.Column("email", db.String, nullable = False)
    password = db.Column("password", db.String, nullable = False)

    def __repr__(self):
        return '<User %r' % self.id



@app.route('/') #Strona glowna
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():


    if request.method == 'POST':
        # jeśli w formularzu jest pole 'first-name' znaczy ze to rejestracja
        if 'first-name' in request.form:
            first_name = request.form['first-name']
            last_name = request.form['last-name']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm-password']

            if password != confirm_password:
                return render_template('auth.html', tab='register', error="Hasła się nie zgadzają")

            new_user = UserInfo(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('register', tab='login'))

        # jeśli jest pole 'login-email' znaczy ze to logowanie
        elif 'login-email' in request.form:
            email = request.form['login-email']
            password = request.form['login-password']

            user1 = UserInfo.query.filter_by(email=email, password=password).first()
            if user1:
                session.permanent = True
                session['user_id'] = user1.id
                session['user_name'] = f"{user1.first_name} {user1.last_name}"
                return redirect(url_for('user'))
            else:
                return render_template('auth.html', tab='login', error="Nieprawidłowy email lub hasło")

    # GET (lub żadne POST‐owe klucze), wtedy po prostu pokaż template
    tab = request.args.get('tab', 'register')
    return render_template('auth.html', tab=tab)

@app.route('/user') #ekran do ktorego przechodzimy po zalogowaniu - na razie pusty
def user():
    if 'user_id' in session:
        name = session.get('user_name')
        return render_template('user.html', name=name)
    else:
        return redirect(url_for('register', tab='login'))

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