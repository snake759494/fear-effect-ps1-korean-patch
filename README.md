# 피어 이펙트 PS1 한글패치

PS1 일본판 **Helix フィアー エフェクト (SLPS-03340~03343, 4장)**용 비공식 한국어 패치입니다. 아이템·무기·메시지, 장면 이름, 타이틀·옵션·디스크 교체 화면을 한국어로 바꿨습니다. **4장 디스크의 동영상에 박힌 일본어 세로 자막 1,285구간**은 영상에서 지운 뒤 한글 자막을 새로 그렸고, 메뉴 그림 글자도 한글로 다시 그렸습니다. 현재 배포판은 **v1.0 (2026-11-13)**입니다.

[패치 다운로드](https://github.com/snake759494/fear-effect-ps1-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈 첨부 파일은 디스크별 한글패치 **Fear_Effect_PS1_KO_v1.0_Disc1.xdelta ~ Disc4.xdelta** 4개뿐입니다. 저장소에는 제작 소스와 한국어 번역만 공개합니다. 원본·완성 디스크 이미지, 추출한 게임 파일, 일본어 원문, 글꼴 파일, 외부 실행 파일은 포함하지 않습니다. GitHub가 자동으로 만드는 Source code ZIP/TAR는 저장소 소스를 압축한 것이며 게임 파일이 아닙니다.

## 게임 소개 및 대상 버전

『Fear Effect』는 Kronos Digital Entertainment가 개발하고 에이도스가 2000년에 낸 PS1 액션 어드벤처입니다. 일본판은 『Helix フィアー エフェクト』라는 이름으로 나왔습니다. 용병 세 사람이 홍콩 삼합회 보스의 딸을 쫓다가 지옥의 문턱까지 휘말려 들어가는 이야기로, 셀 셰이딩 캐릭터와 미리 렌더링된 동영상 배경, 공포 게이지(Fear Meter)가 특징입니다. 대사는 대부분 음성과 동영상 자막으로 진행됩니다.

이 패치는 **PS1 일본판 4장 디스크의 BIN/CUE 이미지(디스크마다 데이터 1트랙)**에 적용합니다. 파일 이름보다 아래 표의 크기와 해시가 일치하는지가 중요합니다.

## 적용할 원본

| 디스크 | 게임 ID | 원본 BIN 크기 (바이트) | **원본 BIN MD5** | xdelta 크기 (바이트) |
| --- | --- | --- | --- | --- |
| 1 | SLPS-03340 | 724,688,832 | `c474444af100c827f91daa4bc9ac0765` | 74,101,126 |
| 2 | SLPS-03341 | 729,658,608 | `e34d9ba40a03555410871d3ce18a5b93` | 104,164,230 |
| 3 | SLPS-03342 | 674,483,040 | `7d3a4b25502bd6650075a91c034111c5` | 79,403,532 |
| 4 | SLPS-03343 | 749,523,600 | `3fd8dec53c2f6c0c47be76ec0c97e621` | 62,187,369 |

| 디스크 | 원본 BIN SHA-256 | 적용 결과 BIN SHA-256 (크기는 원본과 같음) |
| --- | --- | --- |
| 1 | `4190633c7eadcb4422f59c5a33ede97b7c0d64efae2c1bb85413f61ed536065a` | `f541d13d1781e8113036215b4606f3644479ac9be3d4e20436a9ff15d09fda1d` |
| 2 | `bd3cf66d4879f7a851921f5f62022999fafd75678fe02dec35db203607d02e06` | `3da2ee973c1f327620983945600801218f45232c8ff3036fce33e5fa321b063c` |
| 3 | `ee0e41d379e2776e57c08d7bd749fc174adcef00847e77d3e08ee984a8c06182` | `95b36a78ac6faa060e95ac774b344a750a374ec7b96b997b1de8c79c59f63ca9` |
| 4 | `5c20077da5fc612352c6568ef884bd1fa39d01b7df302f6ff27f3d3052753440` | `f1efb694a5500080f2ca9816afc7a239bb527bc1a01410cb40995c654e69b9eb` |

SHA-1과 xdelta 파일의 SHA-256은 [release_manifest.json](release_manifest.json)에 있습니다. 원본 게임 파일은 사용자가 직접 준비해야 합니다.

## 패치 적용 방법

디스크 4장 모두에 각각 적용합니다. 아래는 1번 디스크 예시입니다.

### Windows에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Helix - Fear Effect (Japan) (Disc 1).bin'
```

위 표와 다르면 적용을 중단하세요. CHD, PBP, ECM, 압축 이미지에는 적용할 수 없습니다.

### xdelta UI 사용

1. 릴리즈에서 `Fear_Effect_PS1_KO_v1.0_Disc1.xdelta` ~ `Disc4.xdelta`를 받습니다.
2. xdelta3 패치를 지원하는 도구에서 **Apply Patch** 기능을 엽니다.
3. **Patch**에는 xdelta 파일을, **Source File**에는 해시가 일치하는 같은 번호의 원본 `.bin`을 선택합니다.
4. **Output File**에는 새 파일 이름을 지정합니다(예: `Fear Effect (Korean) (Disc 1).bin`).
5. 원본 `.cue`를 복사해 이름을 바꾸고, `FILE "..."` 줄을 결과 BIN 파일 이름으로 고칩니다.

```
FILE "Fear Effect (Korean) (Disc 1).bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
```

xdelta는 호환성을 위해 압축·2차 압축·파일 경로 헤더 없이 만들었습니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s '.\Helix - Fear Effect (Japan) (Disc 1).bin' '.\Fear_Effect_PS1_KO_v1.0_Disc1.xdelta' '.\Fear Effect (Korean) (Disc 1).bin'
```

해시를 자동으로 검사하고 CUE까지 만들어 주는 도구도 있습니다. Python 3과 xdelta3가 필요하며, 같은 이름의 출력 파일이 이미 있으면 덮어쓰지 않습니다.

```powershell
python tools/apply_release.py --disc 1 --xdelta '.\xdelta3.exe' --source '.\Helix - Fear Effect (Japan) (Disc 1).bin' --patch '.\Fear_Effect_PS1_KO_v1.0_Disc1.xdelta' --output '.\Fear Effect (Korean) (Disc 1).bin'
```

### 실행

에뮬레이터에서 결과 `.cue`를 여세요. 디스크 교체 화면이 나오면 다음 번호의 **한글패치 디스크**로 바꾸세요(패치한 디스크와 원본 디스크를 섞지 마세요). 여러 장을 한 번에 다루려면 `.m3u` 목록을 써도 됩니다. 원본판의 세이브 스테이트는 불러오지 마세요. 메모리 카드 세이브 형식은 바꾸지 않았습니다. 게임 자체 글꼴에 한글을 넣었으므로 BIOS 종류와 관계없이 한글이 나옵니다.

## 작업 내용과 범위

| 구분 | 작업량 및 내용 |
| --- | --- |
| 게임 문자열 | 아이템·무기·메시지 문자열 174개(`ENV/?E.DB`, 각 환경 WAD 안 DB) |
| 장면 이름 | 장소 이름 50개(`SNAMEE.SNA`, 세이브·레벨 선택 화면 등) |
| 게임 글꼴 | 한글 **266자**(갈무리11, 12px). 일본어 글리프 자리와 새 확장 코드 칸에 그리고, 실행 파일 렌더러를 고쳐 확장 칸을 읽게 함 |
| 화면 문자열 | 타이틀·옵션·메모리 카드·디스크 교체 화면 문자열 13개(`GSHELL.OVR`, `SWAP.OVR`), 화면 글꼴 한글 62자 |
| 그림 글자 | 메뉴 그림 30종: 세이브 비컨, 조작 설정 항목(공격/퀵 드로, 액션/무기 선택, 웅크리기, 달리기, 피하기, 퀵 턴, 아이템 전환 등), 진동·스테레오/모노럴, 볼륨, 난이도, START 버튼 안내, 타이틀 메뉴 등 |
| 동영상 자막 | 동영상 12개(디스크 1: 오프닝·부팅·ABGA·ABGC, 2: ABGB·ABGH, 3: ABGI·ABGE, 4: ABGD·ABGF)에 박힌 일본어 세로 자막 **1,285구간**을 지우고 한글 세로 자막을 그림. 강조(노란 글자)도 유지 |

동영상 자막은 영상 프레임을 디코드해 자막을 지우고 한글을 그린 다음, 바뀐 매크로블록만 다시 인코딩해 원래 섹터 크기 안에 넣었습니다. 자세한 내용은 [docs/TECHNICAL.md](docs/TECHNICAL.md)를 참고하세요.

### 번역 원칙

- 기계 번역 없이 문맥을 보고 직접 번역했습니다.
- 인명은 한 가지 표기로 통일했습니다(데크, 레인, 메이위안 등). 팔선(八仙)의 이름은 중국어 발음으로 적었습니다(리톄과이, 허셴구, 장궈라오 등).
- 동영상 자막은 원래 자막이 있던 화면 오른쪽 세로쓰기 자리와 한 화면 줄 수 안에 들어가게 나눴습니다.

### 번역하지 않은 것

- 음성(일본어 더빙)
- 원래 영문인 HUD·메뉴 일부
- 동영상 자막을 다시 인코딩하다 크기 안에 넣지 못한 프레임 29개(디스크 1: 5, 2: 11, 3: 8, 4: 5)는 원본 그대로입니다. 대부분 구간 끝의 한 프레임이라 잠깐 일본어가 비칠 수 있습니다.

## 알려진 한계

- 모든 장면을 게임으로 직접 플레이하며 확인하지는 못했습니다. 게임 화면 일부와 4장 디스크의 동영상 자막을 에뮬레이터에서 표본으로 확인했고, 동영상 자막 구간은 디코드한 프레임 덤프로도 확인했습니다.
- 동영상 자막 부분은 원본보다 화질이 조금 떨어질 수 있습니다(바뀐 매크로블록만 다시 압축).
- 인게임 확인은 DuckStation으로 했습니다. 실기에서의 동작은 확인하지 못했습니다. 문제가 있으면 이슈로 알려 주세요.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `tools/build.py` | 게임 파일 빌드(글꼴 생성, 실행 파일 패치, 문자열 표·장면 이름·화면 문자열·그림 글자 교체, 디스크에 다시 씀) |
| `tools/fmvapply.py`, `fmvrun.sh` | 동영상 자막 적용 |
| `tools/` | 빌드·검증 도구(Python). `extract.py` 디스크 파일 추출, `iso.py`·`disc.py`·`cdsec.py` 디스크 읽기/쓰기(EDC/ECC), `wad.py` 묶음 파일, `ui.py`·`jtab.py` 게임 글꼴·문자 코드, `db.py`·`dbw.py` 문자열 표, `sna.py` 장면 이름, `title.py`·`ttab.py` 화면 글꼴, `bkg.py` 메뉴 그림, `fmv.py`·`mdec.py`·`str.py` 동영상 디코드/인코드, `scan.py`·`segs.py`·`jseg.py`·`sheet.py` 자막 구간 검출, `sub.py` 자막 지우기·그리기, `emu.py` 에뮬레이터 조작, `apply_release.py` 해시 검사 후 적용 |
| `text/` | 번역. `ui_ko.tsv`·`sna_ko.tsv`(키 = 원문 해시), `title_ko.tsv`(파일·오프셋), `fmv/<TAG>.json` 자막 구간, `fmv/<TAG>_ko.tsv` 자막 번역 |
| `scan/` | 동영상 스캔 스크립트 |
| `docs/` | 기술 설명, 재빌드 방법, 글꼴 출처 |

권리 관련 내용은 [RIGHTS.md](RIGHTS.md)를 참고하세요.
