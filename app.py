from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.Text)
    Password = db.Column(db.Text)
    DisplayName = db.Column(db.Text)
    Role = db.Column(db.Text)
    stock_histories = db.relationship('StockHistory', backref='user')

class Products(db.Model):
    ProductID = db.Column(db.Integer, primary_key=True)
    ProductName = db.Column(db.Text)
    Category = db.Column(db.Text)
    Price = db.Column(db.Float)
    StockQuantity = db.Column(db.Integer)
    stock_histories = db.relationship('StockHistory', backref='product')

class StockHistory(db.Model):
    HistoryID = db.Column(db.Integer, primary_key=True)
    ProductID = db.Column(db.Integer, db.ForeignKey('products.ProductID'))
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'))
    Quantity = db.Column(db.Integer)
    StockDate = db.Column(db.DateTime, default=datetime.utcnow)
    Note = db.Column(db.Text)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        category = request.form['category']
        price = float(request.form['price'])
        stock_quantity = int(request.form['stock_quantity'])

        new_product = Products(ProductName=product_name, Category=category, Price=price, StockQuantity=stock_quantity)
        db.session.add(new_product)
        db.session.commit()
        
        return redirect(url_for('add_product'))

    return render_template('add_product.html')

if __name__ == '__main__':
    app.run(debug=True)
