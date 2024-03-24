#!/bin/sh

if [ -z "$1" ]; then
	2>&1 echo "$(basename "$0"): error: expected path argument"
	exit 2
fi


word_count=$(awk '/<main .*>/,/<\/main>/' $1 | sed "s/<[^>]*>//g" | wc -w)

echo "Word count: $word_count"
echo "In minutes: $(python -c "print($word_count / 200.0)" )"
