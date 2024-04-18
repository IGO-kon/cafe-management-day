from flask import Flask, render_template

app = Flask(__name__)

@app.route('/add_product', methods=['GET'])
def add_product():
    return render_template('add_product.html')

if __name__ == '__main__':
    app.run(debug=True)
