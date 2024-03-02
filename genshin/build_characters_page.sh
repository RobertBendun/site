#!/usr/bin/env bash

# Ensure that we are in the same directory as the script
cd "$(dirname "$(realpath $0)")"

>characters.html cat <<END
<!DOCTYPE html>
<html>
<head>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<title>My Genshin Characters | Diana's Lab</title>
		<script src="/scramble.js"></script>
		<script src="/glass-light.js"></script>
		<link rel="stylesheet" href="/common.css" />
</head>
<body>
		<header>
			<a href="/" class="hover-scramble" data-text="Diana Chaotic Lab">Diana Chaotic Lab</a>
			<p>created by hand with love</p>
			<nav class="roots">
				<ul>
					<li><a href="/archive">Archive</a></li>
					<li><a href="/cinema">Cinema</a></li>
					<!-- <li><a href="/workshop">Workshop</a></li> -->
					<li><a href="https://github.com/RobertBendun">Github</a></li>
				</ul>
			</nav>
			<nav class="prompt glass">
				<ul>
					<li>/</li>
					<li><a href="/genshin/">genshin</a></li>
					<li>/</li>
					<li><a href="/genshin/characters.html">characters</a></li>
				</ul>
				<div contenteditable></div>
			</nav>
		</header>
		<main id="page" class="glass">
		<h1>All my characters!</h1>
		<p>
			This are all of my characters listed by the time that I got them.
			You can find more information about some of the builds on my <a href="https://akasha.cv/profile/739467452">akasha profile</a>.
		</p>
		<p>
			This page was generated from the <a href="characters.csv">CSV file</a> containing all my characters
			using <a href="build_characters_page.sh">this shell script</a>.
		</p>
	<table style="width: 100%">
END

function avatar() {
	case "$1" in
		'Shikanoin Heizou'|\
		'Sangonomiya Kokomi'|\
		'Kaedehara Kazuha'|\
		'Kujou Sara'|\
		'Kamisato Ayato'|\
		'Kamisato Ayaka'|\
		'Arataki Itto')
			name="${1##* }"
			;;
		'Raiden Shogun')
			name="${1%% *}"
			;;
		*)
			name="$1"
			;;
	esac
	echo "https://rerollcdn.com/GENSHIN/Characters/1/$name.png"
}

while IFS="," read -r name date
do
	>>characters.html cat <<END
		<tr>
			<td><img width=70 height=70 src="$(avatar "$name")" alt="Avatar of $name"></td>
			<th>$name</th>
			<td>$date</td>
		</tr>
END
done < <(sort -k2 -t',' characters.csv -r)

>>characters.html cat <<END
	</main>
	</table>
</body>
</html>
END
