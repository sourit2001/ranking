from flask import Flask, request, render_template, send_file, jsonify
import os
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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
            return jsonify({'error': f'视频生成失败: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/download')
def download():
    try:
        return send_file('uploads/output.mp4',
                        as_attachment=True,
                        download_name='ranking.mp4',
                        mimetype='video/mp4')
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=port)