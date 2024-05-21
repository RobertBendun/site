import re
from datetime import datetime
import collections


def main():
    print(HTML.format(
        statistics='\n'.join(statistics()),
        entries='\n'.join(entries())
    ))

def entries():
    for post in POSTS:
        date = post.date.strftime('%Y-%m-%d')
        yield f'<li id="{date}"><time>{date}</time> &ndash; <a href="{post.path}">{post.name}</a></li>'


def statistics():
    dates = [post.date for post in POSTS]
    min_year = min((date.year for date in dates))
    max_year = max((date.year for date in dates))

    for year in range(min_year, max_year+1):
        yield '<div class="year" style="display: grid; grid-template-columns: min-content auto; align-items: center">'
        yield f'<div style="padding: 5px">{year}</div>'
        yield '<div style="padding-left: 5px; border-left: 1px solid var(--text);">'

        first = datetime(year, 1, 1).strftime('%W')
        last = datetime(year, 12, 31, 23, 59).strftime('%W')

        dates_in_year = [date for date in dates if date.year == year]
        weeks_for_dates = [int(date.strftime('%W')) for date in dates_in_year]
        weeks = collections.Counter(weeks_for_dates)
        max_entries_in_week = max(weeks.values())

        for week in range(int(first), int(last)+1):
            alpha = weeks[week] / max_entries_in_week
            try:
                href = dates_in_year[weeks_for_dates.index(week)].strftime('%Y-%m-%d')
                href = f"href=\"#{href}\""
            except ValueError:
                href = ""
            yield f'<a {href} style="background-color: rgba(69, 133, 136, {alpha})"></a>'
        yield '</div>'
        yield '</div>'

class Post:
    def __init__(self, name: str, path: str, date: str):
        self.name = name
        self.path = path
        self.date = datetime.strptime(date, '%Y-%m-%d')


    def __lt__(self, other: 'Post'):
        return self.name < other.name if self.date == other.date else self.date > other.date


    def __str__(self) -> str:
        return f"Post(name={self.name}, path={self.path}, date={self.date})"


HTML = """<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<title>The Archive | Diana's Lab</title>

		<script src="/scramble.js"></script>
		<script src="/glass-light.js"></script>
		<script src="/prompt.js"></script>
		<link rel="stylesheet" href="/common.css" />
		<link rel="stylesheet" href="/tiers.css" />
        <style>
        .year a {{
            display: inline-block;
            width: 1ch;
            aspect-ratio: 1;
            border: 1px solid #fbf1c744;
        }}
        </style>
	</head>
	<body>
		<header>
			<a href="/" class="hover-scramble" data-text="Diana's Chaotic Lab">Diana's Chaotic Lab</a>
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
					<li><a href="/archive/">archive</a></li>
				</ul>
				<div contenteditable></div>
			</nav>
		</header>
		<main id="page" class="glass">
			<h1>The Archive</h1>
            <section class="stats">
                <p>Here how my posting looks across the weeks:</p>
                {statistics}
            </section>
            <p>And here all of my posts:</p>
			<ul>
                {entries}
			</ul>
            <p>Generated using <a href="index.py">index.py</a></p>
		</main>
	</body>
</html>
"""

POSTS = sorted([
    Post(date="2024-05-21", path="python-turtles.html", name="Python turtles"),
    Post(date="2024-05-18", path="wayland-keyboard.html", name="How to disable builtin keyboard in Wayland"),
    Post(date="2024-05-06", path="odd-versioning-systems.html", name="Odd versioning systems"),
    Post(date="2024-04-17", path="arlecchino-backstory-thoughts.html", name="Arlecchino backstory thoughts"),
    Post(date="2024-04-17", path="i-want-to-just-spend-time-with-them.html", name="I just want to spend time with them"),
    Post(date="2024-04-14", path="16-by-19-is-an-antipattern.html", name="16:9 is an antipattern"),
    Post(date="2024-03-24", path="fun-with-imdb-using-duckdb.html", name="Fun with IMDb using DuckDB"),
    Post(date="2024-03-09", path="gym-lockers.html", name="Finding locker at the gym in O(1)"),
    Post(date="2024-03-03", path="css-position-relative-grid.html", name="Nested elements onto grid using relative position"),
    Post(date="2024-02-26", path="new-version-announcement-post.html", name="Website Update!"),
    Post(date="2024-02-25", path="exploration-lore-abyss-and-lantern-rite.html", name="Exploration, Lore, Spiral Abyss and Lantern Rite"),
])

if __name__ == "__main__":
    main()
