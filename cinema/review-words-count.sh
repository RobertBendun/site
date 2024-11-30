#!/usr/bin/env bash

# This is the point when not using Python is just wrong

awk '
match($0, /<h3[^>]*>([^)]+\))/, a)  { capture_words = 1; print a[1] }
/<\/section>/ { capture_words = 0; print "" }
!/<h3/ { if (capture_words) { printf "%s ", $0 } }
' <"$(dirname "$0")/index.html" | while read -r title; do
	read -r review
	printf "%s\t%s\n" "$(echo "$review" | wc -w)" "$title"
done | sort -rn | awk '
{ print; total += $0; words[count++] = int($0); if (max_len < length) max_len = length }
END {
	for (i = 0; i < max_len+8; i++) { printf "-" } print ""
	print " Total: " total " words"
	print " Count: " count " reviews"
	print "   Avg: " int(total / count) " words"
	print "Median: " (count % 2 == 0 ? words[count/2-1] + words[count/2] : words[count/2]) " words"
}
'
