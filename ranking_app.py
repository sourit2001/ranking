from flask import Flask, request, render_template, send_file, jsonify
import os
import pandas as pd
import bar_chart_race as bcr

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

# ... 其他路由和函数 ...

# 确保创建app实例在全局范围
port = int(os.environ.get('PORT', 10000))
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)