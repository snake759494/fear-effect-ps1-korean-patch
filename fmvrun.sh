# 디스크별 FMV 자막 적용: sh fmvrun.sh <disc> <path:tag> ...
export MSYS_NO_PATHCONV=1
d=$1; shift
for a in "$@"; do python -X utf8 tools/fmvapply.py $d ${a%%:*} ${a##*:}; done
echo DONE$d
