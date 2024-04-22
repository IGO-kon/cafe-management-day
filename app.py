# 必要なライブラリをインポート
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションの暗号化に使用するキー

# データベース接続関数
def connect_db():
    conn = sqlite3.connect('cafe_management.db')
    conn.row_factory = sqlite3.Row  # 行データをディクショナリ形式で取得
    return conn

# ログイン関数
def authenticate(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT UserID, DisplayName FROM Users WHERE Username = ? AND Password = ?", (username, password))
    user = cursor.fetchone()

    conn.close()
    return user

# 商品情報をデータベースに保存する関数
def add_product_to_db(product_name, category, price, stock_quantity):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Products (ProductName, Category, Price, StockQuantity)
    VALUES (?, ?, ?, ?)
    """, (product_name, category, price, stock_quantity))

    conn.commit()
    conn.close()

# 商品情報をデータベースから取得する関数
def get_products_from_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT ProductID, ProductName, Category, Price, StockQuantity FROM Products")
    products = cursor.fetchall()

    conn.close()
    return products

# 在庫の数量を更新する関数
def update_stock_quantity(product_id, quantity):
    conn = connect_db()
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
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO StockHistory (ProductID, UserID, Quantity, StockDate, Note)
    VALUES (?, ?, ?, datetime('now', 'localtime'), ?)
    """, (product_id, user_id, quantity, note))

    conn.commit()
    conn.close()

# 在庫履歴をデータベースから取得する関数
def get_stock_history_from_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM StockHistory")
    stock_history = cursor.fetchall()

    conn.close()
    return stock_history

# 商品情報を更新する関数
def update_product_in_db(product_id, product_name, category, price, stock_quantity):
    conn = connect_db()
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
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))

    conn.commit()
    conn.close()

# 入出庫を登録する関数
def register_stock_change(product_id, user_id, quantity, note):
    conn = connect_db()
    cursor = conn.cursor()

    # 在庫の更新
    update_stock_quantity(product_id, quantity)

    # 在庫履歴の追加
    add_stock_history_to_db(product_id, user_id, quantity, note)

    conn.close()

# 入出庫履歴を削除する関数
def delete_stock_history_from_db(history_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM StockHistory WHERE HistoryID = ?", (history_id,))

    conn.commit()
    conn.close()

# 入出庫履歴を更新する関数
def update_stock_history_in_db(history_id, product_id, user_id, quantity, note):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE StockHistory
    SET ProductID = ?, UserID = ?, Quantity = ?, Note = ?
    WHERE HistoryID = ?
    """, (product_id, user_id, quantity, note, history_id))

    conn.commit()
    conn.close()

# ユーザー登録関数
def register_user(username, password, display_name):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Users (Username, Password, DisplayName) VALUES (?, ?, ?)", (username, password, display_name))
    conn.commit()

    user_id = cursor.lastrowid

    conn.close()
    return user_id

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        return redirect(url_for('login'))

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

    conn = connect_db()
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
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        user_id = session['user_id']  # セッションからユーザーIDを取得
        quantity = int(request.form.get('quantity'))  # 数量を取得
        note = request.form.get('note')

        # 入出庫を登録
        register_stock_change(product_id, user_id, quantity, note)

        return redirect(url_for('stock_history_list'))

    products = get_products_from_db()
    return render_template('stock_history.html', products=products)

@app.route('/stock_history_list')
def stock_history_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    stock_history = get_stock_history_from_db()
    return render_template('stock_history_list.html', stock_history=stock_history)

@app.route('/delete_stock_history/<int:history_id>', methods=['POST'])
def delete_stock_history(history_id):
    delete_stock_history_from_db(history_id)
    return redirect(url_for('stock_history_list'))

@app.route('/edit_stock_history/<int:history_id>', methods=['GET', 'POST'])
def edit_stock_history(history_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        user_id = session['user_id']  # セッションからユーザーIDを取得
        quantity = int(request.form.get('quantity'))
        note = request.form.get('note')

        # 入出庫履歴を更新
        update_stock_history_in_db(history_id, product_id, user_id, quantity, note)

        return redirect(url_for('stock_history_list'))

    # GETリクエストの場合は履歴の情報を取得してフォームに表示
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM StockHistory WHERE HistoryID = ?", (history_id,))
    stock_history = cursor.fetchone()
    conn.close()

    return render_template('edit_stock_history.html', stock_history=stock_history)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = authenticate(username, password)
        if user:
            # ユーザーが存在する場合、セッションにユーザー情報を保存し、ホームページにリダイレクト
            session['user_id'] = user['UserID']
            session['display_name'] = user['DisplayName']
            return redirect(url_for('products'))
        else:
            # ユーザーが存在しない場合、再度ログインを促す
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    # セッションからユーザー情報を削除
    session.pop('user_id', None)
    session.pop('display_name', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        display_name = request.form.get('display_name')

        # ユーザーが既に存在するかチェック
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            return render_template('register.html', error="Username already exists")

        # 新しいユーザーをデータベースに追加
        user_id = register_user(username, password, display_name)

        # ユーザーをログイン状態にするため、セッションにユーザー情報を保存
        session['user_id'] = user_id
        session['display_name'] = display_name

        return redirect(url_for('products'))

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
