import os
import pathlib
import filetype
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import cv2
import numpy as np



# 取得目前檔案所在的資料夾
SRC_PATH = pathlib.Path(__file__).parent.absolute()
UPLOAD_FOLDER = os.path.join(SRC_PATH, 'static', 'uploads')

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'     # 請自行修改密鑰
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_file():
    if 'filename' not in request.files:
        flash('沒有上傳檔案')
        return redirect(url_for('index'))

    file = request.files['filename']

    if file.filename == '':
        flash('請選擇要上傳的影像')
        return redirect(url_for('index'))
    if file:
        file_type = filetype.guess_extension(file)

        if file_type in ALLOWED_EXTENSIONS:
            file.stream.seek(0)
            filename = secure_filename(file.filename)
#######################

            img = cv2.imread(filename)
            qrcode = cv2.QRCodeDetector()
            data, bbox, rectified = qrcode.detectAndDecode(img)

            # 取得座標的函式
            def boxSize(arr):
                global data
                box_roll = np.rollaxis(arr,1,0)   # 轉置矩陣，把 x 放在同一欄，y 放在同一欄
                xmax = int(np.amax(box_roll[0]))  # 取出 x 最大值
                xmin = int(np.amin(box_roll[0]))  # 取出 x 最小值
                ymax = int(np.amax(box_roll[1]))  # 取出 y 最大值
                ymin = int(np.amin(box_roll[1]))  # 取出 y 最小值
                return (xmin,ymin,xmax,ymax)

            # 如果 bbox 是 None 表示圖片中沒有 QRCode
            if bbox is not None:
                print(data)
                # print(bbox)
                # print(rectified)
                box = boxSize(bbox[0])
                cv2.rectangle(img,(box[0],box[1]),(box[2],box[3]),(0,0,255),5)  # 畫矩形
#######################

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # flash('影像上傳完畢！')
            flash(data)
            return render_template('index.html', filename=filename)
        else:
            flash('僅允許上傳png, jpg, jpeg和gif影像檔')
            return redirect(url_for('index'))  # 令瀏覽器跳回首頁


@app.route('/img/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)





