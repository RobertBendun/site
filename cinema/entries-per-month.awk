#!/usr/bin/env -S awk -f
# Note that -S is a non POSIX extension,
# that works on GNU Coreutils and FreeBSD
# but is NOT supported on OpenBSD or in BusyBox

/nav.*month-toc/ {
	count_mode = 1
}

match($0, /aside.*id="([^"]+)"/, a)  {
	if (count_mode == 1) {
		date = a[1]
		count = 0
	}
}

/<li>/ {
	if (count_mode) {
		count++
		total++
	}
}

/<\/nav>/ {
	if (count > 0) {
		printf date ": %2d ", count
		for (c = 0; c < count; c++) {
			printf "█"
		}
		printf "\n"
		count_mode = 0
		entries[months++] = count
	}
}

END {
	print "  Total: " total
	print "Average: " (total / months)
	print " Median: " (months % 2 == 0 ? ((entries[int(months/2)-1] + entries[int(months/2)]) / 2) : entries[int(months/2)])
}
