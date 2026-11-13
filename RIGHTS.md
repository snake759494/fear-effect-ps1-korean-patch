# 권리 및 외부 자료

이 저장소는 비공식 한국어 패치의 제작 소스·번역·검증 자료를 공개하기 위한 것입니다. 『Fear Effect』(일본판 『Helix フィアー エフェクト』)와 그 텍스트·이미지·영상·음성·실행 코드의 권리는 원 권리자에게 있습니다.

배포하지 않는 것은 원본 게임, 패치를 적용한 게임, 게임에서 추출한 실행 파일·그래픽·영상·음성, 일본어 원문입니다. 릴리즈에는 원본 디스크 이미지가 있어야만 쓸 수 있는 차분 파일(xdelta)만 첨부합니다. 게임 문자열 번역(`text/ui_ko.tsv`, `text/sna_ko.tsv`)은 원문 대신 원문의 해시 키로, 화면 문자열(`text/title_ko.tsv`)은 파일과 오프셋으로, 동영상 자막(`text/fmv/*_ko.tsv`)은 구간 번호로만 연결됩니다. 원문은 빌드할 때 사용자의 원본 디스크에서 읽어 대조합니다. 문자 코드표(`tools/jtab.py`, `tools/ttab.py`)에는 게임 글꼴의 글자 배열만 들어 있습니다.

저장소를 공개했다고 해서 모든 파일에 같은 오픈소스 라이선스를 부여한다는 뜻은 아닙니다. 자체 제작 코드와 번역 전체에 대한 포괄 라이선스는 따로 지정하지 않았습니다.

게임 안 한글은 갈무리(Galmuri11, © Lee Minseo, SIL Open Font License 1.1, 전문 `LICENSES/Galmuri-OFL-1.1.md`)와 나눔스퀘어네오(© NAVER Corp., 네이버 나눔글꼴 라이선스)로 그렸습니다. 글꼴 파일 자체는 저장소에 넣지 않았습니다(`docs/FONT_CREDITS.md` 참고).

xdelta, DuckStation, Python 라이브러리(Pillow, NumPy, numba, OpenCV, SciPy, Capstone, Keystone) 등 외부 도구는 각 프로젝트의 라이선스를 따르며, 바이너리는 재배포하지 않습니다. 게임 코드를 디스어셈블한 결과물은 넣지 않았고, 해석한 내용만 `docs/TECHNICAL.md`에 정리했습니다.
