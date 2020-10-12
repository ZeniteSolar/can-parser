#!/bin/sh
for FILENAME in *.log; do
    cat $FILENAME | \grep -I '([0-9]*.[0-9]*) can0 021#F' > filtered/$FILENAME.filtered
done
