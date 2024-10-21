#!/usr/bin/env -S awk -f
# Note that -S is a non POSIX extension,
# that works on GNU Coreutils and FreeBSD
# but is NOT supported on OpenBSD or in BusyBox

match($0, /<h3 +data-spooky=(0|1|2)>([^(]+)/, a) {
	matched++
	spook_factor += a[1]
	if (a[1] >= 1) spooky += 1

	print_next_title = 1
	m[0] = "not spooky"
	m[1] = "spooky"
	m[2] = "very spooky"

	print a[2] "is " m[a[1]]
}

END {
	print "---"
	print "You watched " spooky " spooky media (out of " matched "), with spook factor = " (spook_factor / matched)
}
