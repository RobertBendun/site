#!/usr/bin/env bash

mkdir -p backups

for fname in *.jpg; do
	if [ ! -f backups/$fname ]; then
		echo "Resizing $fname"
		mv {,backups/}$fname
		convert backups/$fname -resize x150 $fname
	fi
done
