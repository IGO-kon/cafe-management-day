import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# 商品情報をデータベースに保存する関数
def add_product_to_db(product_name, category, price, stock_quantity):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    # Productsテーブルに新しい商品を追加
    cursor.execute("""
    INSERT INTO Products (ProductName, Category, Price, StockQuantity)
    VALUES (?, ?, ?, ?)
    """, (product_name, category, price, stock_quantity))

    conn.commit()
    conn.close()

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        category = request.form.get('category')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        
        # 商品情報をデータベースに保存
        add_product_to_db(product_name, category, price, stock_quantity)
        
        return "商品情報をデータベースに保存しました！"

    return render_template('add_product.html')

if __name__ == '__main__':
    app.run(debug=True)
