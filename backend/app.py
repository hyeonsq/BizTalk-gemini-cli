import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
# 프론트엔드からの 모든 출처에서의 요청을 허용 (개발 목적으로만, 프로덕션에서는 특정 출처로 제한 권장)
CORS(app) 

# Groq 클라이언트 초기화
# API 키는 환경 변수 'GROQ_API_KEY'에서 자동으로 로드됩니다.
try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    print("Groq client initialized successfully.")
except Exception as e:
    groq_client = None
    print(f"Error initializing Groq client: {e}")

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/convert', methods=['POST'])
def convert_text():
    """
    텍스트 변환을 위한 API 엔드포인트.
    Sprint 1에서는 실제 변환 로직 대신 더미 데이터를 반환합니다.
    """
    data = request.json
    original_text = data.get('text')
    target = data.get('audience') # Changed from 'target' to 'audience' to match frontend

    if not original_text or not target:
        return jsonify({"error": "텍스트와 변환 대상은 필수입니다."}), 400

    # Sprint 1: 실제 Groq API 호출 대신 더미 응답 반환
    dummy_response = f"'{original_text}'를 '{target}'에게 보내는 말투로 변환한 결과입니다. (이것은 더미 응답입니다.)"
    
    response_data = {
        "original_text": original_text,
        "converted_text": dummy_response,
        "target": target
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    # Vercel 환경에서는 gunicorn이 이 파일을 직접 실행하지 않으므로,
    # 이 부분은 로컬 개발 시에만 사용됩니다.
    app.run(debug=True, port=5000)