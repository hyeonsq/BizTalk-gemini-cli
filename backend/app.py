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
    Groq AI API를 사용하여 실제 변환 로직을 구현합니다.
    """
    data = request.json
    original_text = data.get('text')
    audience = data.get('audience')

    if not original_text or not audience:
        return jsonify({"error": "텍스트와 변환 대상은 필수입니다."}), 400

    if groq_client is None:
        return jsonify({"error": "AI 서비스가 초기화되지 않았습니다. API 키를 확인해주세요."}), 500

    # 대상별 프롬프트 정의
    prompts = {
        "상사": f"다음 텍스트를 상사에게 보고하기에 적합한, 정중하고 명확하며 격식 있는 비즈니스 말투로 변환해 주세요. 결론부터 제시하고 신뢰성을 강조해 주세요. 원문: '{original_text}'",
        "타팀 동료": f"다음 텍스트를 타팀 동료에게 협조를 요청하거나 정보를 공유하기에 적합한, 친절하고 상호 존중하는 비즈니스 말투로 변환해 주세요. 요청 사항과 마감 기한을 명확히 전달해 주세요. 원문: '{original_text}'",
        "고객": f"다음 텍스트를 고객에게 안내하거나 응대하기에 적합한, 극존칭을 사용하며 전문성과 서비스 마인드를 강조하는 비즈니스 말투로 변환해 주세요. 원문: '{original_text}'"
    }

    system_message = prompts.get(audience)

    if not system_message:
        return jsonify({"error": "유효하지 않은 변환 대상입니다."}), 400

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": original_text,
                }
            ],
            model="moonshotai/kimi-k2-instruct-0905",
            temperature=0.7, # 텍스트 변환의 창의성을 조절
            max_tokens=1024, # 생성될 최대 토큰 수
        )
        converted_text = chat_completion.choices[0].message.content
        
        response_data = {
            "original_text": original_text,
            "converted_text": converted_text,
            "audience": audience
        }
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Error during Groq API call: {e}")
        return jsonify({"error": f"텍스트 변환 중 오류가 발생했습니다: {str(e)}. 잠시 후 다시 시도해주세요."}), 500

if __name__ == '__main__':
    # Vercel 환경에서는 gunicorn이 이 파일을 직접 실행하지 않으므로,
    # 이 부분은 로컬 개발 시에만 사용됩니다.
    app.run(debug=True, port=5000)