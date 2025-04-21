
my %url_from_name;

my $bag = gather {
	for "abyss.html".IO.lines {
		when /"img" \s+ "src=\"" ( <-[\"]>+ ) \" \s+ "alt=\"" ( <-[\"]>+ )/ {
			my $name = "$1".subst("_", " ");
			%url_from_name{$name} = "$0";
			take "$name";
		}
	}
}.Bag;

for $bag.keys.sort({$bag{$_}}).reverse -> $name {
	my $p = ($bag{$name} - $bag.values.min) / ($bag.values.max - $bag.values.min);
	my $h = (1 - $p) * 100 + 20;
	my $a = $p * 100 * 0.7 + 10;

	my $clr = "hsla($h, 100%, 50%, $a%)";
	my $usage = ($bag{$name} / ($bag.total / 4) * 100).floor;
	my $times = do if $bag{$name} == 1 { "time" } else { "times" };
	say "<div title=\"$bag{$name} $times\" style=\"background-color: $clr\"><img alt=\"$name\" src=\"%url_from_name{$name}\"><div>$usage%", "</div></div>";
}


