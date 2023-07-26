import tkinter as tk
import cv2
import time
import datetime
from PIL import ImageTk, Image

class VideoSurveillanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCULUS")

        # Label to display video feed
        self.video_frame = tk.Label(root)
        self.video_frame.pack()

        # Button to start recording
        self.start_button = tk.Button(root, text="Rec", command=self.start_recording, fg="red")
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Button to stop recording
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Open video capture from the default camera (index 0)
        self.cap = cv2.VideoCapture(0)

        # Load Haar cascades for face and full-body detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")

        # Variables to manage recording
        self.detection = False
        self.timer_started = False
        self.detection_stopped_time = None
        self.SECS_TO_REC_AFTER_DETECTION = 5

        # Get the size of the video frame and define the video writer
        self.frame_size = (int(self.cap.get(3)), int(self.cap.get(4)))
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.out = None

        # Call the method to continuously update the video feed
        self.update_video()

    def start_recording(self):
        # Reset detection and timer flags
        self.detection = False
        self.timer_started = False

        # Get the current time to use it as the filename for the recorded video
        current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        # Create a new video writer
        self.out = cv2.VideoWriter(f"{current_time}.mp4", self.fourcc, 20, self.frame_size)

        # Disable the start button and enable the stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_recording(self):
        # Reset detection and timer flags
        self.detection = False
        self.timer_started = False
        # Release the video writer to stop recording
        self.out.release()

        # Enable the start button and disable the stop button
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_video(self):
        # Read a frame from the video capture
        ret, frame = self.cap.read()

        if ret:
            # Convert the frame to grayscale for face and body detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect faces and bodies in the frame
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            bodies = self.body_cascade.detectMultiScale(gray, 1.3, 5)

            # Check if any faces or bodies are detected
            if len(faces) + len(bodies) > 0:
                if self.detection:
                    # If already detecting, reset the timer
                    self.timer_started = False
                else:
                    # If not detecting, start detecting and recording
                    self.detection = True
                    current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
                    self.out = cv2.VideoWriter(f"{current_time}.mp4", self.fourcc, 20, self.frame_size)
                    print("Started Recording")

            # If no faces or bodies are detected, check for recording duration
            elif self.detection:
                if self.timer_started:
                    # If recording duration has exceeded SECS_TO_REC_AFTER_DETECTION, stop recording
                    if time.time() - self.detection_stopped_time >= self.SECS_TO_REC_AFTER_DETECTION:
                        self.detection = False
                        self.timer_started = False
                        self.out.release()
                        print("Stop Recording!")
                else:
                    # If not already started, start the timer
                    self.timer_started = True
                    self.detection_stopped_time = time.time()

            # If detection is active, write the frame to the video writer
            if self.detection:
                self.out.write(frame)

            # Convert the frame to RGB for displaying with tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = ImageTk.PhotoImage(img)
            self.video_frame.configure(image=img)
            self.video_frame.image = img

        # Call the update_video method after 10 milliseconds for continuous video update
        self.root.after(10, self.update_video)

# Create a tkinter window
root = tk.Tk()
# Initialize the VideoSurveillanceApp with the tkinter window
app = VideoSurveillanceApp(root)
# Run the tkinter main loop
root.mainloop()
