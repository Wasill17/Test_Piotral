from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import CheckConstraint

app = Flask(__name__)
app.secret_key = 'tajny-klucz-zadymeczka'
# Baza danych
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # nazwa naszej bazy danych to database.db
db = SQLAlchemy(app)

# TABELE
class Grades(db.Model):
    id = db.Column("id", db.Integer, primary_key=True, autoincrement = True)
    Grade = db.Column("Grade", db.Integer, nullable = False) # NOT NULL)
    added_date = db.Column("added_date", db.DateTime, default=datetime.utcnow) # tu trzeba bedzie dac jakas inną funkcje bo datetime.utcnow ma byc usunieta niedlugo

    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False) #z jakiego powodu przy db.ForeignKey trzeba dac user_info.id zamiast UserInfo.id, bo tak generuje SQLalchemy
    user = db.relationship('UserInfo', backref='grades')
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    subject = db.relationship('Subjects', backref='grades')

    __table_args__ = (CheckConstraint('Grade >= 2 AND Grade <= 5', name='Limit_Ocen'),) # oceny od 2 do 5

    #def __init__(self):
    def __repr__(self):
        return '<Grade %r' % self.id

class UserInfo(db.Model):
    id = db.Column("id", db.Integer, primary_key=True, autoincrement = True)
    first_name = db.Column("first_name", db.String, nullable = False)
    last_name = db.Column("last_name", db.String, nullable = False)
    email = db.Column("email", db.String, nullable = False)
    password = db.Column("password", db.String, nullable = False)
    role = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<User %r' % self.id

class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Subject {self.subject_name}>'

class Tests(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_title = db.Column(db.String, nullable=False)
    test_description = db.Column(db.String, nullable=False)
    max_points = db.Column(db.Integer, nullable=False)

    teacher_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    teacher = db.relationship('UserInfo', backref='tests')
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    subject = db.relationship('Subjects', backref='tests')



    def __repr__(self):
        return f'<Test {self.test_title}>'

@app.route('/') #Strona glowna
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():


    if request.method == 'POST':
        # jeśli w formularzu jest pole 'first-name' znaczy ze to rejestracja
        if 'first-name' in request.form:
            role = request.form['role']
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
                password=password,
                role=role
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
                session['role'] = user1.role
                session['user_name'] = f"{user1.first_name} {user1.last_name}"
                if user1.role == 'nauczyciel':
                    return redirect(url_for('teacher'))
                else:
                    return redirect(url_for('student'))
            else:
                return render_template('auth.html', tab='login', error="Nieprawidłowy email lub hasło")

    # GET (lub żadne POST‐owe klucze), wtedy po prostu pokaż template
    tab = request.args.get('tab', 'register')
    return render_template('auth.html', tab=tab)

# USER BYL UZYWANY WCZESNIEJ - NA RAZIE TEGO NIE USUWAM, ALE RACZEJ SIE TO NIE PRZYDA BO CHCEMY MIEC PODZIAL NA NAUCZYCIELA I UCZNIA
'''
@app.route('/user') #ekran do ktorego przechodzimy po zalogowaniu - na razie pusty
def user():
    if 'user_id' in session:
        name = session.get('user_name')
        return render_template('student.html', name=name)
    else:
        return redirect(url_for('register', tab='login'))
'''

@app.route('/student')
def student():
    if session.get('role') != 'student':
        return redirect(url_for('register', tab='login'))
    elif 'user_id' in session:
        name = session.get('user_name')
        role = session.get('role')
        return render_template('student.html', name=name, role=role)


@app.route('/teacher')
def teacher():
    if session.get('role') != 'nauczyciel':
        return redirect(url_for('register', tab='login'))
    elif 'user_id' in session:
        name = session.get('user_name')
        role = session.get('role')
        return render_template('teacher.html', name=name, role=role)

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
        db.create_all()

        # Dodaj przedmioty, jeśli tabela jest pusta
        if Subjects.query.count() == 0:
            default_subjects = [
                Subjects(subject_name='Matematyka'), #losowe przedmioty dla testu, w kazdym momencie mozna je zmienic
                Subjects(subject_name='Fizyka'),
                Subjects(subject_name='Biologia'),
                Subjects(subject_name='Informatyka'),
                Subjects(subject_name='Chemia')
            ]
            db.session.bulk_save_objects(default_subjects)
            db.session.commit()
            print("✔️ Dodano domyślne przedmioty do bazy danych.")



    app.run(debug=True)