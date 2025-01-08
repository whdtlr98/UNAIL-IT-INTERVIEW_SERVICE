from fastapi import APIRouter, File, UploadFile, HTTPException
from google.cloud import speech
from google.oauth2 import service_account  
import subprocess
from util.get_parameter import get_parameter
import json

router = APIRouter()

def convert_webm_to_flac(webm_content):
    process = subprocess.Popen(['ffmpeg', '-i', 'pipe:0', '-f', 'flac', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    flac_content, stderr = process.communicate(input=webm_content)
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode()}")
    return flac_content


@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    try:
        # GCP 서비스 계정 키 가져오기
        account_key = get_parameter("/gcp/service-account-key")

        # JSON 문자열을 Python dict로 변환
        service_account_info = json.loads(account_key)

        # Google Cloud Speech-to-Text 클라이언트 생성
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        client = speech.SpeechClient(credentials=credentials)

        # 오디오 파일 읽기
        webm_content = await audio.read()
        
        # 오디오 포맷 변환
        try:
            flac_content = convert_webm_to_flac(webm_content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Audio conversion error: {str(e)}")

        # 음성 인식 요청 구성
        audio = speech.RecognitionAudio(content=flac_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=48000,
            language_code="ko-KR",
        )

        # 음성 인식 요청 보내기
        try:
            response = client.recognize(config=config, audio=audio)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Speech-to-Text API error: {str(e)}")

        # 응답에서 텍스트 추출
        try:
            transcript = "".join(result.alternatives[0].transcript for result in response.results)
        except IndexError:
            raise HTTPException(status_code=500, detail="No transcription results found.")

        return {"transcript": transcript}

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Service account key parsing error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
