
mkdir MagIC_Working_Directory
i=0

for d in "$1"*/ ; do
    python fix_linebreaks.py "$d"pmag_specimens.txt
    cat "$d"pmag_specimens.txt > MagIC_Working_Directory/"$i"b_.magic
    i=$((i+1))
done
