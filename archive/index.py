import re
from datetime import datetime
import collections
import dataclasses
import textwrap
import functools

def main():
    print(HTML.format(
        statistics='\n'.join(statistics()),
        entries='\n'.join(entries())
    ))

def entries():
    for post in POSTS:
        date = post.date.strftime('%Y-%m-%d')
        yield textwrap.dedent(f"""<li id="{date}">
                <a href="{post.path}">
                    <div>{post.name}</div>
                    <time datetime="{post.date.isoformat()}">{date}</time></a>
            </li>""")


def statistics():
    dates = [post.date for post in POSTS]
    min_year = min((date.year for date in dates))
    max_year = max((date.year for date in dates))

    for year in range(min_year, max_year+1):
        yield '<div class="year" style="display: grid; grid-template-columns: min-content auto; align-items: center" aria-hidden="true">'
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
            yield f'<a {href} tabindex="-1" style="background-color: rgba(69, 133, 136, {alpha})"></a>'

        yield f'<span style="opacity: 0.4">({len(dates_in_year)} total)</span>'
        yield '</div>'
        yield '</div>'

@dataclasses.dataclass
class Tag:
    name: str
    description: str

class Post:
    def __init__(self, name: str, path: str, tag: Tag|None = None):
        self.name = name
        self.path = path
        self.tag = tag

    @property
    @functools.cache
    def date(self) -> datetime:
        with open(self.path, 'r') as file:
            html = file.read()
        return datetime.fromisoformat(re.search(r'<time datetime="([0-9:T+-]+)">[0-9-]+<\/time>', html).group(1))



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
		<link rel="stylesheet" href="/common.css" />
		<link rel="stylesheet" href="/tiers.css" />
        <style>
        .year a {{
            display: inline-block;
            width: 1ch;
            aspect-ratio: 1;
            border: 1px solid #fbf1c744;
        }}
        main li > a {{
            display: grid;
            grid-template-columns: auto 12ex;
            text-wrap: balance;
            align-items: center;
            gap: 1ex;
        }}
        main li:target a {{
            background-color: #00000040;
        }}
        main li a:hover {{
            background-color: #00000080;
        }}
        main li a div {{
            display: block;
            width: 100%;
            letter-spacing: 0.1ex;
        }}
        main li time {{
            opacity: 0.8;
            color: var(--text);
            text-decoration: none !important;
            text-align: right;
        }}

        main ul {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        main ul,
        main li {{
            list-style-type: none;
            margin: 0;
            padding: 0;
        }}
        </style>
	</head>
	<body>
		<header>
			<a href="/" class="hover-scramble">bendun.cc</a>
			<nav class="roots">
				<ul>
					<li><a href="/archive">Archive</a></li>
					<li><a href="/cinema">Cinema</a></li>
					<!-- <li><a href="/workshop">Workshop</a></li> -->
					<li><a href="https://github.com/RobertBendun">Github</a></li>
				</ul>
			</nav>
		</header>
		<main id="page" class="glass">
			<h1>The Archive</h1>
            <section class="stats" style="margin-bottom: 1rem">
                {statistics}
            </section>
			<ul>
                {entries}
			</ul>
            <p>Generated using <a href="index.py">index.py</a></p>
		</main>
	</body>
</html>
"""

class Tags:
    Linux = Tag(name="linux", description="Things that come up with administration of my Linux laptops")
    WebsiteUpdate = Tag(name="site", description="Changelog for my website")
    CSS = Tag(name="css", description="Articles about CSS")


POSTS = sorted([
    Post(path="defaults.html", name="Defaults"),
    Post(path="javascript-window.html", name="self is a cross-platform way to name a window"),
    Post(path="spooktober.html", name="Spooktober 🎃"),
    Post(path="github-archive.html", name="My Github Repositories"),
    Post(path="nestable-strings.html", name="Nestable strings"),
    Post(path="offlfirsoch-2024.html", name="OFFLFIRSOCH 2024: offline docs"),
    Post(path="interests.html", name="/interests"),
    Post(path="string-new-date-nan.html", name="String(new Date(NaN))"),
    Post(path="oxford-comma.html", name="Oxford Comma"),
    Post(path="datetime.html", name="Proper Timestamps"),
    Post(path="make-parallelism.html", name="Parallelism with Makefiles"),
    Post(path="years-ago.html", name="Trouble with Dates"),
    Post(path="phoneless.html", name="Phoneless"),
    Post(path="horror.html", name="Horror"),
    Post(path="output.html", name="On Output"),
    Post(path="view-transitions.html", name="Cross-document view transitions are here!", tag=Tags.CSS),
    Post(path="libvirt-vm-scaling.html", name="Scaling libvirt Linux VMs", tag=Tags.Linux),
    Post(path="python-turtles.html", name="Python turtles"),
    Post(path="wayland-keyboard.html", name="How to disable builtin keyboard in Wayland", tag=Tags.Linux),
    Post(path="odd-versioning-systems.html", name="Odd versioning systems"),
    Post(path="16-by-19-is-an-antipattern.html", name="16:9 is an antipattern"),
    Post(path="fun-with-imdb-using-duckdb.html", name="Fun with IMDb using DuckDB"),
    Post(path="gym-lockers.html", name="Finding locker at the gym in O(1)"),
    Post(path="css-position-relative-grid.html", name="Nested elements onto grid using relative position", tag=Tags.CSS),
    Post(path="new-version-announcement-post.html", name="Website Update!", tag=Tags.WebsiteUpdate),
])

if __name__ == "__main__":
    main()
