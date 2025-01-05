from flask import Flask, render_template, request, send_file
from flask_cors import CORS
import pandas as pd
import bar_chart_race as bcr
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

app = Flask(__name__)
CORS(app)

# 配置上传文件夹
app.config['UPLOAD_FOLDER'] = 'uploads'

# 设置中文字体
plt.rcParams['font.family'] = ['PingFang HK', 'Heiti TC', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # 获取上传的文件
        file = request.files['file']
        
        # 保存Excel文件
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx')
        file.save(excel_path)
        
        print("开始读取数据...")
        # 读取数据
        df = pd.read_excel(excel_path)
        
        print("处理数据中...")
        # 数据处理
        df.set_index('车型', inplace=True)
        
        # 对每个时间点进行排序，只保留前20名
        for col in tqdm(df.columns, desc="处理数据"):
            top_20 = df[col].nlargest(20)
            df.loc[df.index.difference(top_20.index), col] = 0
        
        # 转置数据
        df = df.T
        
        # 处理时间格式
        df.index = [f"{int(float(x))}-{str(float(x)).split('.')[-1]}" for x in df.index]
        
        print("生成视频中...")
        # 生成视频文件路径
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mp4')
        
        # 生成动态排名视频
        bcr.bar_chart_race(
            df=df,
            filename=output_file,
            orientation='h',
            sort='desc',
            n_bars=20,
            figsize=(16, 12),
            dpi=144,
            title='车型销量动态排名',
            bar_size=0.8,
            period_length=800,
            bar_label_size=14,
            tick_label_size=16,
            period_label={
                'x': .95,
                'y': .5,
                'ha': 'right',
                'va': 'center',
                'size': 28,
                'family': 'PingFang HK'
            },
            period_fmt='{x}',
            period_summary_func=lambda v, r: {
                'x': .95,
                'y': .2,
                's': f'总销量: {v.nlargest(20).sum():,.0f}',
                'ha': 'right',
                'size': 24,
                'family': 'PingFang HK'
            }
        )
        
        print("视频生成完成！")
        # 返回生成的视频文件
        return send_file(output_file, as_attachment=True)
    except Exception as e:
        return f'处理文件时出错: {str(e)}', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)