# MP3 Organizer

Python 기반 MP3 자동 분류 프로그램입니다. GUI를 통해 폴더를 선택하고 MP3 파일을 장르/가수 기준으로 분류할 수 있습니다.

## 요구 조건

- Python 3.10 이상
- `mutagen` 설치

## 설치

```bash
pip install -r requirements.txt
```

## 실행

```bash
python main.py
```

## 기능

- 폴더 재귀 검색으로 `.mp3` 파일 발견
- ID3 태그(artist, album, genre) 읽기
- 장르/가수 기반 자동 폴더 생성
- 이동 또는 복사 실행
- 태그 누락 파일은 지정된 fallback 폴더로 분류
- 중복 파일 처리: rename / skip / overwrite
- dry-run 모드로 실제 파일 작업 없이 시뮬레이션

## 참고

- GUI는 `src/gui.py`에서 구현되어 있습니다.
- 실제 분류 로직은 `src/runner.py`에 있습니다.
