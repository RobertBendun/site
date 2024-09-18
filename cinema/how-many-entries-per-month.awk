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
		count += 1
		total += 1
	}
}

/<\/nav>/ {
	if (count > 0) {
		print date ": " count
		count_mode = 0
	}
}

END {
	print "  Total: " total
}
