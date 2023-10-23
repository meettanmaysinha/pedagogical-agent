import cv2
import sounddevice as sd
import numpy as np
import time
# Open the webcam (you may need to change the argument to the appropriate camera index)
cap = cv2.VideoCapture(0)
# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

videoWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
videoHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter('output.mp4', fourcc, 20.0,(videoWidth,videoHeight))
# Set the start time
start_time = time.time()

# Audio settings
sample_rate = 44100
duration = 5  # seconds

# while True:
#     # Capture frame-by-frame
#     ret, frame = cap.read()
    
#     # Write the frame to the output video file
#     out.write(frame)

#     # Display the resulting frame
#     cv2.imshow('Webcam Feed', frame)

#     # # Record audio
#     # audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype=np.int16)
#     # sd.wait()
    
#     # Check if 5 seconds have elapsed
#     if time.time() - start_time > 10:
#         # Save the video file every 4.5 seconds
#         out.release()
#         out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (videoWidth,videoHeight))  # Adjust resolution if needed
#         start_time = time.time()

#     # Break the loop if 'q' key is pressed
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break


def getVideoFeed():
    video_id = 0

    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        # Write the frame to the output video file
        out.write(frame)

        # Display the resulting frame
        cv2.imshow('Webcam Feed', frame)

        # # Record audio
        # audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype=np.int16)
        # sd.wait()
        
        # Check if 5 seconds have elapsed
        if time.time() - start_time > 5:
            # Save the video file every 5 seconds
            out.release()
            out = cv2.VideoWriter(f'output_{video_id}.mp4', fourcc, 20.0, (videoWidth,videoHeight))  # Adjust resolution if needed
            print(f"Run: {video_id}")
            start_time = time.time()
            video_id += 1

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # Release the webcam and close the window
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            break
            



# Release the webcam and close the window
cap.release()
out.release()
cv2.destroyAllWindows()
