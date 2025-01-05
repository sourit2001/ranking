from flask import Flask, request, render_template, send_file, jsonify
import os
import pandas as pd
import bar_chart_race as bcr

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        # 保存文件
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # 生成视频
        try:
            generate_video(filename)
            return jsonify({'message': '视频生成成功'})
        except Exception as e:
            app.logger.error(f'视频生成错误: {str(e)}')
            return jsonify({'error': f'视频生成失败: {str(e)}'}), 500

    except Exception as e:
        app.logger.error(f'上传错误: {str(e)}')
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/download')
def download():
    try:
        return send_file('uploads/output.mp4',
                        as_attachment=True,
                        download_name='ranking.mp4',
                        mimetype='video/mp4')
    except Exception as e:
        app.logger.error(f'下载错误: {str(e)}')
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

def generate_video(input_file):
    # 读取Excel文件
    df = pd.read_excel(input_file)
    
    # 设置输出文件路径
    output_file = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mp4')
    
    # 生成视频
    bcr.bar_chart_race(
        df=df,
        filename=output_file,
        orientation='h',
        sort='desc',
        n_bars=20,
        figsize=(12, 8),
        dpi=72,
        title='车型销量动态排名',
        bar_size=0.8,
        period_length=200,
        steps_per_period=5,
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

# 确保创建app实例在全局范围
port = int(os.environ.get('PORT', 10000))
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)