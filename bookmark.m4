define(`bookmark', `<section>
				<h2><time datetime="esyscmd(`date -Isecond | perl -pe "chomp if eof"')">esyscmd(`date -Idate | perl -pe "chomp if eof"')</time> <a target="_blank" href="$1">$1</a></h2>
				<p></p>
			</section>')dnl
