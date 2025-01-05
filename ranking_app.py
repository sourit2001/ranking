from flask import Flask, render_template, request, send_file, Response, stream_with_context
from flask_cors import CORS
import pandas as pd
import bar_chart_race as bcr
import os
import matplotlib.pyplot as plt
import json
import traceback  # 添加traceback模块
import sys
import matplotlib.font_manager as fm

app = Flask(__name__)
CORS(app)

# 配置上传文件夹
app.config['UPLOAD_FOLDER'] = 'uploads'

# 设置中文字体
plt.rcParams['font.family'] = ['Noto Sans CJK JP', 'Noto Sans CJK SC', 'Noto Sans CJK TC', 'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

# 确保字体缓存更新
fm.findfont('Noto Sans CJK SC')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return json.dumps({"error": "没有文件被上传"}), 400, {'Content-Type': 'application/json'}
    
    try:
        file = request.files['file']
        if file.filename == '':
            return json.dumps({"error": "没有选择文件"}), 400, {'Content-Type': 'application/json'}
        
        # 确保uploads目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx')
        file.save(excel_path)
        
        def generate():
            try:
                # 读取数据
                yield json.dumps({"progress": 10, "message": "读取数据中..."}) + '\n'
                print("开始读取数据...")  # 添加日志
                df = pd.read_excel(excel_path)
                print("数据读取完成")  # 添加日志
                
                # 数据处理
                yield json.dumps({"progress": 20, "message": "处理数据中..."}) + '\n'
                print("开始处理数据...")  # 添加日志
                df.set_index('车型', inplace=True)
                
                # 处理每个时间点
                total_cols = len(df.columns)
                for i, col in enumerate(df.columns):
                    print(f"处理列 {i+1}/{total_cols}")  # 添加日志
                    top_20 = df[col].nlargest(20)
                    df.loc[df.index.difference(top_20.index), col] = 0
                    progress = 20 + (i / total_cols * 30)
                    yield json.dumps({"progress": int(progress), "message": f"处理数据 {i+1}/{total_cols}"}) + '\n'
                
                # 转置数据
                print("转置数据...")  # 添加日志
                df = df.T
                df.index = [f"{int(float(x))}-{str(float(x)).split('.')[-1]}" for x in df.index]
                
                # 生成视频
                yield json.dumps({"progress": 60, "message": "生成视频中..."}) + '\n'
                print("开始生成视频...")  # 添加日志
                output_file = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mp4')
                
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
                        'size': 28
                    },
                    period_fmt='{x}',
                    period_summary_func=lambda v, r: {
                        'x': .95,
                        'y': .2,
                        's': f'总销量: {v.nlargest(20).sum():,.0f}',
                        'ha': 'right',
                        'size': 24
                    }
                )
                print("视频生成完成")  # 添加日志
                
                yield json.dumps({"progress": 100, "message": "完成！", "done": True}) + '\n'
                
            except Exception as e:
                print(f"错误: {str(e)}")  
            
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
        
    except Exception as e:
        return json.dumps({"error": str(e), "message": "处理文件时出错"}), 500, {'Content-Type': 'application/json'}

@app.route('/download')
def download():
    try:
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mp4')
        if not os.path.exists(output_file):
            return json.dumps({"error": "视频文件不存在"}), 404, {'Content-Type': 'application/json'}
            
        return send_file(
            output_file,
            mimetype='video/mp4',
            as_attachment=True,
            download_name='ranking_video.mp4'
        )
    except Exception as e:
        print(f"下载错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)