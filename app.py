import os
from datetime import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = 'sqlite:///{}'.format(os.path.join(project_dir, 'bojm.db'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Ledger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(255))
    creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.creation_date = datetime.now()

    def __repr__(self):
        return '{0: <5} {1:.2f} {2}'.format(self.name, self.amount, self.note)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.form:
        entry = Ledger(name=request.form.get('name'),
                       amount=float(request.form.get('amount')) *
                       float(request.form.get('trans_type')),
                       note=request.form.get('note'))
        db.session.add(entry)
        db.session.commit()

    entries = Ledger.query.order_by(Ledger.creation_date.desc()).limit(5).all()
    balances = db.session.query(Ledger.name, func.sum(Ledger.amount)
                                .label('balance')).group_by(Ledger.name).all()
    return render_template('home.html', entries=entries, balances=balances)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
