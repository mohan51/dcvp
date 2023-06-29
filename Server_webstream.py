#server streaming to web browser
import cv2
import imagezmq
from flask import Flask, Response
from datetime import datetime
import time
import os 

output_folder = "./received_images"
os.makedirs(output_folder, exist_ok=True)
app = Flask(__name__)

@app.route('/')
def stream_images():
    def generate():
        receiver = imagezmq.ImageHub(open_port='tcp://10.42.0.89:5555',REQ_REP=False)
        start_time = time.time()
        while True:
            _, frame = receiver.recv_image()
            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            # # Generate a unique filename based on the current timestamp
            # timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
            # image_filename = os.path.join(output_folder, f"image_{timestamp}.jpg")

            # # Save the received frame as an image
            # cv2.imwrite(image_filename,frame)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
