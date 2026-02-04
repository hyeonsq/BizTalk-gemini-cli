import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)
# CORS 설정: 모든 origin에서의 요청을 허용합니다.
CORS(app)

# Groq 클라이언트 초기화
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    groq_api_key_set = True
except Exception as e:
    groq_api_key_set = False

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태를 확인하는 헬스 체크 엔드포인트"""
    return jsonify({"status": "ok"}), 200

@app.route('/api/convert', methods=['POST'])
def convert_text():
    """텍스트 변환을 처리하는 메인 API 엔드포인트"""
    if not groq_api_key_set:
        return jsonify({"error": "Groq API 키가 설정되지 않았습니다."}), 500

    data = request.get_json()
    if not data or 'text' not in data or 'target' not in data:
        return jsonify({"error": "유효하지 않은 요청입니다. 'text'와 'target' 필드가 필요합니다."}), 400

    input_text = data.get('text')
    target = data.get('target')

    # Sprint 1: 간단한 API 연동 테스트 및 더미 응답
    # 실제 프롬프트 엔지니어링은 다음 스프린트에서 진행합니다.
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful assistant that converts text into a professional tone for a specific audience: {target}."
                },
                {
                    "role": "user",
                    "content": input_text,
                }
            ],
            model="llama3-8b-8192",
        )
        
        converted_text = chat_completion.choices[0].message.content
        return jsonify({"converted_text": converted_text})

    except Exception as e:
        # 실제 프로덕션 환경에서는 로깅을 추가해야 합니다.
        print(f"An error occurred: {e}")
        return jsonify({"error": "AI 모델 호출 중 오류가 발생했습니다."}), 500

if __name__ == '__main__':
    # Vercel 환경에서는 gunicorn이 이 파일을 직접 실행하지 않으므로,
    # 이 부분은 로컬 개발 시에만 사용됩니다.
    app.run(debug=True, port=5000)
