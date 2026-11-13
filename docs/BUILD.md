# 재빌드

## 준비물

빌드 스크립트는 저장소 폴더를 작업 폴더로 쓰고, 원본 BIN/CUE는 **저장소의 상위 폴더**에서 찾습니다.

```
<상위 폴더>/
  Helix - Fear Effect (Japan) (Disc 1).bin / .cue   … Disc 4까지
  <이 저장소>/
    fonts/Galmuri11.ttf
    fonts/NanumSquareNeo-cBd.ttf  fonts/NanumSquareNeo-dEb.ttf
```

- Python 3.13, `Pillow`, `numpy`, `numba`, `opencv-python`, `scipy` (`capstone`은 디스어셈블 도구 `tools/mips.py`, `keystone-engine`은 실행 파일 패치에 필요)
- 글꼴 출처는 `docs/FONT_CREDITS.md`
- xdelta3 (배포 파일을 만들 때만)

## 빌드

저장소 폴더에서 실행합니다. 디스크 번호마다 반복합니다(아래는 1번).

```powershell
python tools/extract.py 1 "../Helix - Fear Effect (Japan) (Disc 1).bin"   # 디스크 파일 → orig/d1/
python tools/build.py 1                                                    # 글꼴·문자열·그림 글자 → [KR].bin/.cue
bash fmvrun.sh 1 /OPEN.SID:OPEN /BOOT.SID:BOOT /ABGA/ABGA.FLX:ABGA /ABGC/ABGC.FLX:ABGC   # 동영상 자막
```

동영상 스트림은 디스크마다 다릅니다.

| 디스크 | `fmvrun.sh` 인수 |
| --- | --- |
| 1 | `1 /OPEN.SID:OPEN /BOOT.SID:BOOT /ABGA/ABGA.FLX:ABGA /ABGC/ABGC.FLX:ABGC` |
| 2 | `2 /ABGB/ABGB.FLX:ABGB /ABGH/ABGH.FLX:ABGH` |
| 3 | `3 /ABGI/ABGI.FLX:ABGI /ABGE/ABGE.FLX:ABGE` |
| 4 | `4 /ABGD/ABGD.FLX:ABGD /ABGF/ABGF.FLX:ABGF` |

`build.py`는 원본 BIN을 `… (Disc N) [KR].bin`으로 복사한 뒤 바꾼 파일을 다시 쓰고 `.cue`를 만듭니다. `fmvapply.py`는 원본 BIN에서 프레임을 읽어 `[KR].bin`의 같은 섹터에 씁니다. 동영상 단계는 디스크 하나에 수십 분 걸립니다. 결과 BIN의 SHA-256을 `release_manifest.json`의 `output_bin_sha256`과 비교하세요.

## 배포 파일

```powershell
xdelta3 -e -0 -S none -A -s "Helix - Fear Effect (Japan) (Disc 1).bin" "Helix - Fear Effect (Japan) (Disc 1) [KR].bin" Fear_Effect_PS1_KO_v1.0_Disc1.xdelta
```

## 번역 수정

- 게임 문자열: `text/ui_ko.tsv`(아이템·무기·메시지), `text/sna_ko.tsv`(장면 이름)의 `키<TAB>번역`. 키는 원문의 SHA-1 앞 16자리입니다(`tools/ui.py` `hkey`). 원문을 보려면 `tools/collect.py`로 `orig/`에서 뽑습니다.
- 새 한글 글자는 266자 + 남는 슬롯까지 넣을 수 있습니다(`tools/ui.py` `slots`).
- 타이틀·옵션·디스크 교체 화면: `text/title_ko.tsv`의 `파일<TAB>오프셋<TAB>번역`. 원문 바이트 수를 넘을 수 없습니다.
- 메뉴 그림 글자: `tools/bkg.py`의 `KO`.
- 동영상 자막: `text/fmv/<TAG>_ko.tsv`의 `구간 번호<TAB>번역`. `/`는 세로 열 나눔, `<…>`는 노란 강조입니다. 구간 프레임·상자는 `text/fmv/<TAG>.json`.
- 새 구간 찾기: `tools/scan.py`로 스트림을 스캔한 뒤(`scan/run.sh`) `tools/segs.py`·`tools/sheet.py`로 구간과 확인용 시트를 만듭니다.
