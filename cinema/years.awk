#!/usr/bin/env -S awk -f
# Note that -S is a non POSIX extension,
# that works on GNU Coreutils and FreeBSD
# but is NOT supported on OpenBSD or in BusyBox

match($0, /<h3[^>]*>[^(]+\(([0-9]+)-?([0-9]+)?\)<\/h3>/, a) {
	matched++

	if (a[2]) {
		for (i = a[1]; i <= a[2]; i++) {
			counts[i]++
		}
	} else {
		counts[a[1]]++
	}
}

END {
	min = 9999
	max = 0
	len = 0
	for (idx in counts) {
		if (idx > max) {
			max = idx
		}
		if (idx < min) {
			min = idx
		}
		if (counts[idx] > len) {
			len = counts[idx]
		}
	}

	missing = ""

	for (idx = min; idx <= max; idx++) {
		if (!counts[idx]) {
			missing = missing " " idx
			continue
		}

		printf "%d %2d ", idx, counts[idx]
		for (c = 0; c < counts[idx]; c++) {
			printf "█"
		}
		print
	}

	for (i = -8; i < len; i++) {
		printf "-"
	}
	print

	print "Total watched: ", matched
	print "      Missing:", missing
}
