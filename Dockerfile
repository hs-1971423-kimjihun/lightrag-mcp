# 1. 베이스 이미지 설정 (Python 3.11 사용)
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 정의 파일을 먼저 복사합니다.
#    (프로젝트에 pyproject.toml 파일이 있다고 가정)
COPY pyproject.toml ./

# 4. 의존성을 먼저 설치합니다.
#    이렇게 하면 소스 코드가 변경될 때마다 매번 의존성을 새로 설치하지 않고
#    Docker의 캐시를 활용하여 빌드 속도를 높일 수 있습니다.
RUN pip install .

# 5. 서버 소스 코드를 복사합니다.
COPY src/ ./src/

# 6. 서버가 사용할 포트 노출 (선택사항, 문서화 목적)
EXPOSE 8000

# 7. 컨테이너 실행 시 기본 명령어 설정 (이 경로는 올바릅니다)
CMD ["python", "src/lightrag_mcp/main.py"]
