# Libraries required to run the script
import cv2
import os

# Directory containing the video files
video_directory = r"C:\Users\benth\Desktop\capstone\smile_test"

# Get a list of all .avi files in the directory
video_files = [f for f in os.listdir(video_directory) if f.endswith('.avi')]

# Load the trained classifiers for face and smile detection
trained_smile_data = cv2.CascadeClassifier(r"C:\Users\benth\Desktop\capstone\smile_test\cascade_files\Smile.xml")
trained_face_data = cv2.CascadeClassifier(
    r"C:\Users\benth\Desktop\capstone\smile_test\cascade_files\haarcascade_frontalface_default.xml")

for video_file in video_files:
    print(f"Processing {video_file}...")

    # Change the path to the video file
    smilevideo = cv2.VideoCapture(os.path.join(video_directory, video_file))
    # Set the resolution to 640 x 480
    smilevideo.set(3, 640)
    smilevideo.set(4, 480)

    total_frames = 0
    smiling_frames = 0

    while True:
        read_successful, frame = smilevideo.read()

        if read_successful:
            total_frames += 1  # Increment total frame count

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            face_coords = trained_face_data.detectMultiScale(gray_frame)

            any_smiling = False  # Flag to check if at least one face is smiling

            for cell in face_coords:
                x, y, width, height = cell
                cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255), 2)
                font = cv2.FONT_HERSHEY_SIMPLEX
                FaceText = cv2.putText(frame, 'Face', (x, y - 10), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)

                # Crop the detected face region
                cropped_face = frame[y:y + height, x:x + width]
                grayscaled_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)

                # Detect smiles within the detected face
                smile_coords = trained_smile_data.detectMultiScale(grayscaled_face, scaleFactor=1.65, minNeighbors=17)

                if len(smile_coords) > 0:  # If any smiles are detected
                    any_smiling = True  # Set flag to True

                # Draw smile rectangles for visual feedback
                for cell in smile_coords:
                    a, b, c, d = cell
                    cv2.rectangle(cropped_face, (a, b), (a + c, b + d), (0, 255, 0), 2)
                    SmileText = cv2.putText(cropped_face, 'Smile', (a, b - 10), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)

            # Increment smiling frame count if at least one face is smiling
            if any_smiling:
                smiling_frames += 1

            # Optionally display the frame with detections
            new_frame = cv2.resize(frame, (720, 480))
            cv2.imshow("Video Smile Detection", new_frame)

            # Break the loop on 'q' or 'Q' key press
            key = cv2.waitKey(1)
            if key == 81 or key == 113:
                break
        else:
            break

    smilevideo.release()
    cv2.destroyAllWindows()

    # Calculate and print the smile percentage
    if total_frames > 0:
        smile_percentage = (smiling_frames / total_frames) * 100
        print(f"File: {video_file}, Total Frames: {total_frames}, Smiling Frames: {smiling_frames}, Smile Percentage: {smile_percentage:.2f}%")
    else:
        print(f"File: {video_file}, No frames processed.")

