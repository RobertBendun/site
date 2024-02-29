#!/usr/bin/env bash

. .env

if [ -z "$1" ]; then
	echo "usage: $(basename "$0") <imdb id>" 1>&2
	exit 1
fi

readonly ID="$1"

if [ -z "$OMDB_KEY" ]; then
	echo "$(basename "$0"): OMDB_KEY variable is empty" 1>&2
	exit 1
fi

BASE_URL="http://www.omdbapi.com/?apikey=$OMDB_KEY&i="

curl -s "$BASE_URL$ID" | jq -r .Poster

