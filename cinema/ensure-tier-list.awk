#!/usr/bin/env -S awk -f
# Note that -S is a non POSIX extension,
# that works on GNU Coreutils and FreeBSD
# but is NOT supported on OpenBSD or in BusyBox

/<details.+id="tier-list"/ {
	in_tier_list = 1
}

match($0, /<a[^>]+href="#([^"]+)"/, a) {
	if (in_tier_list) {
		tier_list[a[1]] = 1
	}
}

match($0, /<a[^>]+href="#([^"]+)"[^>]*>.*2024)\s*<\/a>/, a) {
	in2024[a[1]] = 1
}

/<\/details>/ {
	in_tier_list = 0
}

END {
	print "Present in tier list, not present on page:"
	for (key in tier_list) {
		if (!(key in in2024)) {
			print "  ", key
		}
	}

	print "Present on page, not present in tier list:"
	for (key in in2024) {
		if (!(key in tier_list)) {
			print "  ", key
		}
	}
}
