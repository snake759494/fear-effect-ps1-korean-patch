export MSYS_NO_PATHCONV=1
B="../Helix - Fear Effect (Japan) (Disc"
job(){ python tools/scan.py "$B $1).bin" "$2" "scan/d$1_$3.npz"; }
job 1 /BOOT.SID BOOT & job 1 /ABGA/ABGA.FLX ABGA & job 1 /ABGC/ABGC.FLX ABGC & job 2 /ABGB/ABGB.FLX ABGB & wait
job 2 /ABGH/ABGH.FLX ABGH & job 3 /ABGE/ABGE.FLX ABGE & job 3 /ABGI/ABGI.FLX ABGI & job 4 /ABGD/ABGD.FLX ABGD & wait
job 4 /ABGF/ABGF.FLX ABGF & job 1 /LOGO.SID LOGO & wait
echo ALLDONE
