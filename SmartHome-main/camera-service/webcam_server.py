import cv2
from flask import Flask, Response
from flask_cors import CORS

app = Flask(__name__)
# Cho phép Frontend (React/Next.js) lấy dữ liệu mà không bị chặn lỗi CORS
CORS(app)

# Khởi tạo đọc webcam. Số 1 thường là USB Camera (Logitech) gắn ngoài khi laptop đã có sẵn Camera tự thân (số 0).
camera = cv2.VideoCapture(1)

# Cấu hình độ phân giải cho vừa với webcam (Logitech C270 hỗ trợ tốt 1280x720)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

def generate_frames():
    """
    Hàm này liên tục đọc khung hình (frame) từ Logitech cam và đóng gói thành chuỗi byte dạng JPEG.
    Cách hoạt động này tạo ra định dạng luồng 'MJPEG' (Motion JPEG) y hệt như Raspberry Pi.
    """
    while True:
        success, frame = camera.read()
        if not success:
            # Nếu không tìm thấy frame do camera bị kẹt, vòng lặp dừng lại.
            break
        else:
            # Mã hóa khung hình hiện tại thành ảnh .jpg
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # 'yield' gửi từng đoạn ảnh liên tục tới trình duyệt
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # Cấu hình Response Header để báo cho trình duyệt biết đây là một luồng (stream) các video ngắt quãng
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "Server Stream Camera đang chạy! Hãy truy cập route /video_feed để xem luồng."

if __name__ == "__main__":
    # Để host='0.0.0.0' để biến máy bạn thành một server mở trong mạng LAN.
    # Các điện thoại, máy tính khác quét IP máy bạn + Port 5050 là có thể xem được.
    app.run(host='0.0.0.0', port=5050, debug=False)
