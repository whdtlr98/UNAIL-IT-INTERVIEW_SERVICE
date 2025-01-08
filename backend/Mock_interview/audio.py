import os
import pyaudio
import time
import soundfile as sf
import numpy as np
from google.cloud import speech
from dotenv import load_dotenv
import queue

# .env 파일의 환경 변수 로드
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# 오디오 설정
STREAMING_LIMIT = 240000  # 4 minutes
SAMPLE_RATE = 16000  # 샘플링 속도 (Hz)
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms 동안 수집할 오디오 데이터 크기

# 면접 스트리밍을 위한 설정
SILENCE_THRESHOLD = 4 * 1000  # 4초 (밀리초 단위)
INITIAL_SILENCE_GRACE_PERIOD = 10 * 1000  # 최초 10초간 무음 허용 (밀리초 단위)
MAX_STREAMING_DURATION = 90 * 1000  # 각 스트리밍 최대 90초 (밀리초 단위)

# 파일명 생성 함수
def get_next_filename(prefix="recorded_audio", ext="flac"):
    """순차적으로 증가하는 파일명을 생성합니다."""
    i = 1
    while os.path.exists(f"{prefix}_{i}.{ext}"):
        i += 1
    return f"{prefix}_{i}.{ext}"

class ResumableMicrophoneStream:
    def __init__(self, rate, chunk_size):
        self._rate = rate
        self.chunk_size = chunk_size
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()
        self.audio_data_frames = []
        self.last_sound_time = get_current_time()  # 마지막으로 소리가 감지된 시간

        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._fill_buffer,
        )

    def __enter__(self):
        self.closed = False
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _fill_buffer(self, in_data, *args, **kwargs):
        self._buff.put(in_data)
        self.audio_data_frames.append(np.frombuffer(in_data, dtype=np.int16))  # 녹음 데이터 누적
        # 소리 감지 시점 갱신
        if np.max(np.abs(np.frombuffer(in_data, dtype=np.int16))) > 500:
            self.last_sound_time = get_current_time()
        return None, pyaudio.paContinue

    def generator(self):
        initial_silence_grace_period_end = self.start_time + INITIAL_SILENCE_GRACE_PERIOD
        max_streaming_duration_end = self.start_time + MAX_STREAMING_DURATION
        while not self.closed:
            # 무음 탐지 및 최대 스트리밍 시간 초과 여부 확인
            current_time = get_current_time()
            if current_time > initial_silence_grace_period_end and \
               current_time - self.last_sound_time > SILENCE_THRESHOLD:
                print("4초 동안 무음 상태입니다. 스트리밍을 종료합니다.")
                self.closed = True  # 무음 시 스트리밍 종료
                break
            elif current_time > max_streaming_duration_end:
                print("최대 스트리밍 시간(90초) 초과. 스트리밍을 종료합니다.")
                self.closed = True  # 최대 시간 초과 시 스트리밍 종료
                break

            data = [self._buff.get()]
            while True:
                try:
                    data.append(self._buff.get(block=False))
                except queue.Empty:
                    break
            yield b"".join(data)

    def close(self):
        self.closed = True
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self._audio_interface.terminate()

def get_current_time():
    return int(round(time.time() * 1000))

def listen_print_loop(responses, stream):
    """STT 결과를 실시간으로 처리하고 출력하며, 무음 상태로 스트리밍을 종료."""
    final_result = ""
    last_interim = ""

    for response in responses:
        for result in response.results:
            transcript = result.alternatives[0].transcript

            # 중간(interim) 결과가 업데이트될 때마다 확인
            if not result.is_final:
                if transcript != last_interim:  # 중복 방지
                    print("Transcript (interim):", transcript)
                    last_interim = transcript
            else:
                # 최종 텍스트 변환 결과가 발생한 시점에서 최종 답변 추가
                final_result += transcript + " "
                print("Final Transcript (confirmed):", final_result)

    # 최종 결과와 녹음 파일 저장
    output_filename = get_next_filename()
    sf.write(output_filename, np.concatenate(stream.audio_data_frames), SAMPLE_RATE, format='FLAC')
    print(f"Recording saved as {output_filename}")
    return final_result

def real_time_transcription():
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code="ko-KR",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    # 면접자의 답변을 반환
    with ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE) as stream:
        stream.start_time = get_current_time()
        stream.audio_data_frames = []  # 녹음 데이터 초기화

        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)
        final_result = listen_print_loop(responses, stream)

        # 스트리밍이 종료되면 결과를 리턴
        return final_result



# import os
# import pyaudio
# import time
# import soundfile as sf
# import numpy as np
# from google.cloud import speech
# from dotenv import load_dotenv

# # .env 파일의 환경 변수 로드
# load_dotenv()
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# # 오디오 설정
# STREAMING_LIMIT = 240000  # 4 minutes
# SAMPLE_RATE = 16000  # 샘플링 속도 (Hz)
# CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms 동안 수집할 오디오 데이터 크기
# SILENCE_THRESHOLD = 4 * 1000  # 4초 (밀리초 단위)
# INITIAL_SILENCE_GRACE_PERIOD = 10 * 1000  # 최초 10초간 무음 허용 (밀리초 단위)

# def get_next_filename(prefix="recorded_audio", ext="flac"):
#     """순차적으로 증가하는 파일명을 생성합니다."""
#     i = 1
#     while os.path.exists(f"{prefix}_{i}.{ext}"):
#         i += 1
#     return f"{prefix}_{i}.{ext}"

# def real_time_transcription():
#     # Google Speech-to-Text API 클라이언트 생성
#     client = speech.SpeechClient()

#     # 오디오 스트림 설정
#     audio_interface = pyaudio.PyAudio()
#     stream = audio_interface.open(format=pyaudio.paInt16,
#                                   channels=1,
#                                   rate=SAMPLE_RATE,
#                                   input=True,
#                                   frames_per_buffer=CHUNK_SIZE)

#     # 녹음 데이터를 저장할 배열
#     audio_data_frames = []

#     # 초기화
#     start_time = time.time() * 1000  # 스트리밍 시작 시간 기록
#     last_sound_time = start_time  # 마지막 소리가 감지된 시간
#     final_result = ""  # 최종 결과를 저장할 변수
#     last_interim = ""  # 중간 결과를 저장할 변수 (중복 방지)

#     # 스트리밍 요청 생성 함수
#     def request_stream():
#         nonlocal last_sound_time
#         while True:
#             data = stream.read(CHUNK_SIZE)
#             audio_data = np.frombuffer(data, dtype=np.int16)
#             audio_data_frames.append(audio_data)  # 녹음 데이터 누적

#             # 소리가 감지되는지 확인 (무음 기준)
#             if np.max(np.abs(audio_data)) > 500:  # 임계값 이상인 경우 소리 감지
#                 last_sound_time = time.time() * 1000
            
#             # 스트리밍 시작 후 10초가 지난 경우에만 무음 상태를 체크
#             if (time.time() * 1000) - start_time > INITIAL_SILENCE_GRACE_PERIOD:
#                 # 4초 이상 무음일 경우 스트리밍 종료
#                 if (time.time() * 1000) - last_sound_time > SILENCE_THRESHOLD:
#                     print("4초 동안 무음 상태입니다. 스트리밍을 종료합니다.")
#                     break
            
#             yield speech.StreamingRecognizeRequest(audio_content=data)

#     # Google STT 스트리밍 설정
#     streaming_config = speech.StreamingRecognitionConfig(
#         config=speech.RecognitionConfig(
#             encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#             sample_rate_hertz=SAMPLE_RATE,
#             language_code="ko-KR",
#         ),
#         interim_results=True
#     )

#     # STT 결과를 순회하며 최종 텍스트 반환
#     responses = client.streaming_recognize(streaming_config, request_stream())
#     for response in responses:
#         for result in response.results:
#             transcript = result.alternatives[0].transcript

#             # 중간(interim) 결과가 업데이트될 때마다 확인
#             if not result.is_final:
#                 if transcript != last_interim:  # 중복 방지
#                     print("Transcript (interim):", transcript)
#                     last_interim = transcript  # 마지막 중간 결과 업데이트
#             else:
#                 # 최종 텍스트 변환 결과가 발생한 시점에서 스트리밍 종료
#                 final_result = transcript
#                 print("Final Transcript (confirmed):", final_result)  # 각 최종 결과 확인

#                 # 스트림 종료
#                 stream.stop_stream()
#                 stream.close()
#                 audio_interface.terminate()

#                 # FLAC 파일로 녹음 데이터 저장
#                 output_filename = get_next_filename()
#                 sf.write(output_filename, np.concatenate(audio_data_frames), SAMPLE_RATE, format='FLAC')
#                 print(f"Recording saved as {output_filename}")
                
#                 return final_result  # 최종 결과 반환

#     # 스트림 종료 시 예외 대비
#     stream.stop_stream()
#     stream.close()
#     audio_interface.terminate()


