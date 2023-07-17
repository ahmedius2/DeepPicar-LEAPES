import cv2
import csv
import numpy as np
import math

def text(frame, angle, groundtruth, current_frame):
    angle = angle / math.pi * 180.0
    text = f"Angle: {angle} Direction: {groundtruth} Frame: {current_frame}"
    # Calculate the font scale to fit within a width of 320 pixels
    width_threshold = 320
    font_scale = min(1.0, width_threshold / cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)[0][0])
    font_thickness = 1
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
    # Calculate the position to center the text horizontally
    text_x = int((frame.shape[1] - text_size[0]) / 2)

    # Create a white background image for the text
    text_bg = np.ones((text_size[1] + 10, frame.shape[1], 3), dtype=np.uint8) * 255

    # Add the text to the white background image
    cv2.putText(text_bg, text, (text_x, text_size[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255),
                font_thickness)

    # Combine the text background image with the original frame
    combined_frame = np.vstack([frame, text_bg])

    cv2.imshow('Video', combined_frame)


def display_video(video_path, csv_file_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    paused = False
    frames = []

    with open(csv_file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        angles = np.array([float(row[2]) for row in reader])

    keep_frame_arr = np.ones_like(angles, dtype=bool)
    current_frame = 0
    while current_frame < frame_count:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        angle = angles[current_frame]

        if angle > 0.0:
            t = "Right"
        elif angle < 0.0:
            t = "Left"
        else:
            t = "Center"

        text(frame, angle, t, current_frame)

        key = cv2.waitKey(50) & 0xFF
        if key == ord('d'):  # Delete frame
            for f in range(current_frame, current_frame+10):
                if f < len(keep_frame_arr):
                    keep_frame_arr[f] = False
                    print(f"Deleted frame {f}")
        elif key == ord('q') or key == 27:  # Quit if 'q' or ESC is pressed
            break


        current_frame += 1

    cap.release()
    cv2.destroyAllWindows()

    # Save edited video
    edited_video_path = "./edited_video.avi"  # Replace with your desired output path
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    edited_video = cv2.VideoWriter(edited_video_path, fourcc, fps, (width, height), True)
    for i, frame in enumerate(frames):
        if keep_frame_arr[i]:
            edited_video.write(frame)
    edited_video.release()


    edited_csv_file_path = "./edited_key.csv"  # Replace with your desired output path
    with open(edited_csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['frame', 'wheel'])
        new_angles = angles[keep_frame_arr]
        for i, angle in enumerate(new_angles):
            writer.writerow([i+1, angle])

    print(f"Edited video saved as {edited_video_path}")
    print(f"Frame information saved as {csv_file_path}")
    print(f"Edited angles saved as {edited_csv_file_path}")


# Example usage
video_file = "/Users/mahgoubhusien/Documents/out-video.avi"  # Replace with the path to your video file
csv_file = "/Users/mahgoubhusien/Documents/out-key.csv"  # Replace with the path to your CSV file
display_video(video_file, csv_file)
