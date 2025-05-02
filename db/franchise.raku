grammar Franchises {
	rule TOP {
		<metadata>
		<franchises>
	}

	rule metadata {
		<assigment>* %% "\n"+
	}

	rule franchises {
		<franchise>*
	}

	rule franchise {
		"[" <franchise_title> "]"
		<franchise_entry>* %% "\n"+
	}

	token franchise_title {
		<-[\]]>+
	}

	token franchise_entry {
		<watched> <title> "(" <year> ")"
	}

	token title {
		<-[\(]>+
	}

	token watched {
		"-" \s* ("[ ]"|"[x]"|"[X]") \s*
	}

	token year {
		(\d+) | (\d+) "-" (\d+)
	}

	token assigment {
		<name> \s* "=" \s* <value>
	}

	token name  { \S+ }
	token value { <-[\n]>+ }
}

class Entry {
	has Str $.title;
	has Range $.year;
	has Bool $.watched;
}

class FranchisesActions {
	method franchises($/) {
		make $/<franchise>>>.made.Hash;
	}

	method franchise($/) {
		my $title = $<franchise_title>.Str;
		my $entries = $<franchise_entry>>>.made;
		make $title => $entries;
	}

	method franchise_entry($/) {
		make Entry.new(
			watched => $/<watched>[0] ne "[ ]",
			title => $/<title>.Str,
			year => $/<year>.made,
		);
	}

	method year($/) {
		if $/.elems == 2 {
			make(+$/[0] .. +$/[1]);
		} else {
			make(+$/ .. +$/);
		}
	}
}

my $file = "./franchise.txt".IO.slurp;

# Remove comments
$file = $file.subst(/"#" <-[\n]>*/, "", :g);

if !Franchises.parse($file, actions => FranchisesActions.new) {
	say "Failed to parse";
	exit;
}
my %franchises =  $<franchises>.made;
my $f = %franchises.sort(-> $e {if +$e.value { 1 - $e.value>>.watched>>.Int.sum / +$e.value } else { -1 }});

for $f>>.kv -> ($k, $v) {
	my $completion = do if $v == 0 {
		"undefined";
	} else {
		my $watched = $v>>.watched>>.Int.sum;
		my $total = +$v;
		my $per = ($watched / $total * 100).floor ~ "%";
		"$per;$watched;$total";
	};
	say "$k;$completion\r";
}
