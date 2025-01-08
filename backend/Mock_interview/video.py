# video_recorder.py

import cv2
import threading
import datetime

cap = None
out = None

def generate_filename(prefix="recording", extension="avi"):
    """현재 날짜와 시간을 기반으로 고유한 파일명을 생성합니다."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{extension}"
    return filename

def start_video_recording():
    """
    Args:
        output_path (str): 저장할 비디오 파일의 경로 
        width (int): 녹화 해상도의 가로 크기 기본값은 640
        height (int): 녹화 해상도의 세로 크기 기본값은 480
        fps (float): 녹화 프레임 속도 기본값은 20.0
    """
    global cap, out
    output_path = generate_filename()  # 자동 파일명 생성
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))

    def record():
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                out.write(frame)  # 파일에 프레임 저장
            else:
                break

    threading.Thread(target=record, daemon=True).start()
    print(f"Recording started. Saving to {output_path}")

def stop_video_recording():
    """녹화를 중지하고 자원을 해제합니다."""
    global cap, out
    if cap is not None and out is not None:
        cap.release()
        out.release()
        print("Recording stopped and file saved.")
