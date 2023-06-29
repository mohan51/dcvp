import imagezmq
import cv2
import os
from datetime import datetime
import threading
import time

# Create a threading.Event object
stop_event = threading.Event()

output_folder = os.path.join("received_images")  # Specify the folder where the images will be saved
os.makedirs(output_folder, exist_ok=True)

# # face detection model
# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Variables for calculating average frame rate
frame_count = 0
start_time = time.time()
frame_rates = []

def receive_frames(pi_name,ip_address):
    global frame_count

    #receiver = imagezmq.ImageHub('tcp://'+ip_address+':5555',REQ_REP=False)
    receiver = imagezmq.ImageHub(open_port='tcp://*:5555')

    try:
        while not stop_event.is_set():
            _, frame = receiver.recv_image()

            # Increment the frame count
            frame_count += 1

            # Process the received frame and get the frame rate
            frame, frame_rate = process_frame(pi_name, frame)

            # Append the frame and frame rate to the list
            frames[pi_name] = (frame, frame_rate)

            # Send a reply to the sender
            receiver.send_reply(b'OK')
    except KeyboardInterrupt:
        # Set the stop_event when a keyboard interrupt occurs
        stop_event.set()
         
    receiver.close()

def process_frame(pi_name, frame):
    global frame_count

    height, width, _ = frame.shape
    print(f"Resolution: {width}x{height}")

    # Save the received frame as an image
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    image_filename = os.path.join(output_folder, f'{pi_name}_image_{timestamp}.jpg')

    cv2.imwrite(image_filename, frame)

    # # Perform face detection on the frame
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # # Draw rectangles around the detected faces
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Calculate and return the frame rate
    current_time = time.time()
    elapsed_time = current_time - start_time
    frame_rate = frame_count / elapsed_time

    # Return the processed frame and frame rate
    return frame, frame_rate


# Create a list of Raspberry Pi names and their corresponding IP addresses
pis = {
    'pi1': '10.11.10.57',
    #'pi2': '10.11.6.141'
    # 'pi3': '192.126.138.102'
}

frames ={}

# Create windows for each Raspberry Pi
while True:
    for pi_name in pis.keys():
        # Check if the frame exists in the dictionary
        if pi_name in frames:
            frame, frame_rate = frames[pi_name]

            # Check if a window for the current Raspberry Pi exists
            if not cv2.getWindowProperty(pi_name, cv2.WND_PROP_VISIBLE):
                # Create a window for the Raspberry Pi if it doesn't exist
                cv2.namedWindow(pi_name)

            # Display the frame in the corresponding window
            cv2.imshow(pi_name, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# Create threads for each Raspberry Pi
threads = []
for pi_name, ip_address in pis.items():
    thread = threading.Thread(target=receive_frames, args=(pi_name,ip_address), daemon=True)
    threads.append(thread)
    thread.start()

# Wait for all threads to complete or terminate on keyboard interrupt
try:
    for thread in threads:
        thread.join()
except KeyboardInterrupt:
    # Set the stop_event when a keyboard interrupt occurs
    stop_event.set()

# Calculate and display the overall average frame rate
    current_time = time.time()
    elapsed_time = current_time - start_time
    overall_frame_rate = frame_count / elapsed_time
    print(f"Overall Average Frame Rate: {overall_frame_rate:.2f} fps")

# Clean up any remaining resources
cv2.destroyAllWindows()