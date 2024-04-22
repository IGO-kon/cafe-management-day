# 必要なライブラリをインポート
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

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

    cursor.execute("SELECT ProductID, ProductName, Category, Price, StockQuantity FROM Products")
    products = cursor.fetchall()

    conn.close()
    return products

# 在庫の数量を更新する関数
def update_stock_quantity(product_id, quantity):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE Products
    SET StockQuantity = StockQuantity + ?
    WHERE ProductID = ?
    """, (quantity, product_id))

    conn.commit()
    conn.close()

# 在庫履歴をデータベースに保存する関数
def add_stock_history_to_db(product_id, user_id, quantity, note):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO StockHistory (ProductID, UserID, Quantity, StockDate, Note)
    VALUES (?, ?, ?, datetime('now', 'localtime'), ?)
    """, (product_id, user_id, quantity, note))

    conn.commit()
    conn.close()

# 在庫履歴をデータベースから取得する関数
def get_stock_history_from_db():
    try:
        conn = sqlite3.connect('cafe_management.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM StockHistory")
        stock_history = cursor.fetchall()

        conn.close()
        return stock_history
    except sqlite3.Error as e:
        print("データベースエラー:", e)
        return []

# 商品情報を更新する関数
def update_product_in_db(product_id, product_name, category, price, stock_quantity):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE Products
    SET ProductName = ?, Category = ?, Price = ?, StockQuantity = ?
    WHERE ProductID = ?
    """, (product_name, category, price, stock_quantity, product_id))

    conn.commit()
    conn.close()

# 商品を削除する関数
def delete_product_from_db(product_id):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))

    conn.commit()
    conn.close()

# 入出庫を登録する関数
def register_stock_change(product_id, user_id, quantity, note):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    # 在庫の更新
    update_stock_quantity(product_id, quantity)

    # 在庫履歴の追加
    add_stock_history_to_db(product_id, user_id, quantity, note)

    conn.close()

# 入出庫履歴を削除する関数
def delete_stock_history_from_db(history_id):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM StockHistory WHERE HistoryID = ?", (history_id,))

    conn.commit()
    conn.close()

# 入出庫履歴を更新する関数
def update_stock_history_in_db(history_id, product_id, user_id, quantity, note):
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE StockHistory
    SET ProductID = ?, UserID = ?, Quantity = ?, Note = ?
    WHERE HistoryID = ?
    """, (product_id, user_id, quantity, note, history_id))

    conn.commit()
    conn.close()

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        category = request.form.get('category')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        
        add_product_to_db(product_name, category, price, stock_quantity)
        
        return redirect(url_for('products'))

    return render_template('add_product.html')

@app.route('/products')
def products():
    products = get_products_from_db()
    return render_template('products.html', products=products)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        category = request.form.get('category')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        
        update_product_in_db(product_id, product_name, category, price, stock_quantity)
        
        return redirect(url_for('products'))

    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ProductID, ProductName, Category, Price, StockQuantity FROM Products WHERE ProductID = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    delete_product_from_db(product_id)
    return redirect(url_for('products'))

@app.route('/stock_history', methods=['GET', 'POST'])
def stock_history():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        user_id = request.form.get('user_id')  # 今回はユーザーIDは固定で1とします
        quantity = int(request.form.get('quantity'))  # 数量を取得
        note = request.form.get('note')

        # 入出庫を登録
        register_stock_change(product_id, user_id, quantity, note)

        return redirect(url_for('stock_history_list'))

    products = get_products_from_db()
    return render_template('stock_history.html', products=products)

# 入出庫履歴一覧表示のルート関数
@app.route('/stock_history_list')
def stock_history_list():
    stock_history = get_stock_history_from_db()
    return render_template('stock_history_list.html', stock_history=stock_history)

# 入出庫履歴の削除
@app.route('/delete_stock_history/<int:history_id>', methods=['POST'])
def delete_stock_history(history_id):
    delete_stock_history_from_db(history_id)
    return redirect(url_for('stock_history_list'))

# 入出庫履歴の編集
@app.route('/edit_stock_history/<int:history_id>', methods=['GET', 'POST'])
def edit_stock_history(history_id):
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        user_id = request.form.get('user_id')  # 今回はユーザーIDは固定で1とします
        quantity = int(request.form.get('quantity'))
        note = request.form.get('note')

        # 入出庫履歴を更新
        update_stock_history_in_db(history_id, product_id, user_id, quantity, note)

        return redirect(url_for('stock_history_list'))

    # GETリクエストの場合は履歴の情報を取得してフォームに表示
    conn = sqlite3.connect('cafe_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM StockHistory WHERE HistoryID = ?", (history_id,))
    stock_history = cursor.fetchone()
    conn.close()

    return render_template('edit_stock_history.html', stock_history=stock_history)

if __name__ == '__main__':
    app.run(debug=True)
