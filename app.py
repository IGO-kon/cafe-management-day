import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# 商品情報をデータベースに保存する関数
def add_product_to_db(product_name, category, price, stock_quantity):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Products (ProductName, Category, Price, StockQuantity)
    VALUES (?, ?, ?, ?)
    """, (product_name, category, price, stock_quantity))

    conn.commit()
    conn.close()

# 商品情報をデータベースから取得する関数
def get_products_from_db():
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    cursor.execute("SELECT ProductName, Category, Price, StockQuantity FROM Products")
    products = cursor.fetchall()

    conn.close()
    return products

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        category = request.form.get('category')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        
        add_product_to_db(product_name, category, price, stock_quantity)
        
        return "商品情報をデータベースに保存しました！"

    return render_template('add_product.html')

@app.route('/products')
def products():
    products = get_products_from_db()
    return render_template('products.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
