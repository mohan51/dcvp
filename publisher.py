import imagezmq
import cv2

sender = image.ImageSender(connect_to='tcp://*:5555',REQ_REP=False)
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
try:
  while True:
      ret,frame = camera.read()
      sender.send_image('pi1',frame)
      cv2.imshow("sender",frame)
      if cv2.waitKey(1) == ord('q'):
          break
except KeyboardInterrupt:
    pass
finally:
    camera.release()
    cv2.destroyAllWindows
