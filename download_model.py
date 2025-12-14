import os
from huggingface_hub import snapshot_download

# ==========================================
# ⚙️ 설정 (본인의 환경에 맞게 수정 가능)
# ==========================================
# 다운로드할 모델 ID (Meta Llama 3.1 8B Instruct)
MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct"

# 모델이 저장될 로컬 경로 (app/services/hf_llm.py에서 바라보는 경로와 일치해야 함)
# 현재 위치 기준: ./app/llama/Llama-3.1-8B-Instruct
LOCAL_DIR = os.path.join("app", "llama", "Llama-3.1-8B-Instruct")

def download_llama():
    print(f"🚀 [Start] 모델 다운로드를 시작합니다: {MODEL_ID}")
    print(f"📂 [Path] 저장 경로: {os.path.abspath(LOCAL_DIR)}")
    print("⚠️ 주의: 약 15GB의 용량이 필요합니다. Wi-Fi 환경을 권장합니다.")
    print("🔑 HuggingFace Access Token이 필요합니다 (권한 승인 필수).")
    
    # 토큰 입력 받기
    token = input("👉 HuggingFace Token을 입력하세요 (입력 후 엔터): ").strip()
    
    if not token:
        print("❌ 토큰이 입력되지 않았습니다. 다운로드를 중단합니다.")
        return

    try:
        # 다운로드 실행 (resume_download=True: 끊겨도 이어받기 가능)
        snapshot_download(
            repo_id=MODEL_ID,
            local_dir=LOCAL_DIR,
            token=token,
            resume_download=True,
            ignore_patterns=["*.msgpack", "*.h5", "*.ot"] # 불필요한 파일 제외
        )
        print("\n🎉 [Success] 모델 다운로드가 완료되었습니다!")
        print(f"✅ 이제 서버를 실행할 수 있습니다.")
        
    except Exception as e:
        print(f"\n❌ [Error] 다운로드 실패: {e}")
        print("�� 팁: Meta-Llama-3.1 페이지에서 사용 승인(Agree)을 받았는지 확인하세요.")

if __name__ == "__main__":
    download_llama()
