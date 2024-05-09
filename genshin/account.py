import typing
from datetime import datetime

# TODO: Show pity

# TODO: Maybe display in a grid similar to that in-game? From current list it is hard
# to infer which characters I don't have, and for my account it is more relevant information.
# Also this list is useless since it doesn't show which characters I use / have build.


def main():
    print(PAGE.format(
        weapons=generate_weapons(),
        characters=generate_characters(),
        characters_count=len(CHARACTERS),
    ))


def generate_characters() -> str:
    grouped = {}
    for c in CHARACTERS:
        q = round((c.date.month - 1) / 4) + 1
        target = f"Q{q} {c.date.year}"
        if target not in grouped:
            grouped[target] = []
        grouped[target].append(c)

    return "\n".join(
        """
            <section>
                <h3>{group_name}</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, 100px); justify-content: center">
                    {characters}
                </div>
            </section>
        """.format(
            group_name=group_name,
            characters="\n".join(f'<img style="width: 100%" src="{c.icon_url}" alt="{c.name}">' for c in group)
        )
        for group_name, group in grouped.items()
    )

def generate_weapons() -> str:
    return "\n".join(f'<img style="width: 100%" src="{c.icon_url}" alt="{c.name}">' for c in FIVE_STAR_WEAPONS)


class Wish:
    def __init__(self, name: str, date: datetime|str|None = None, *, pity: typing.Optional[int] = None, weapon: bool = False):
        self.name = name
        if isinstance(date, str):
            self.date = datetime.strptime(date, "%Y-%m-%d")
        else:
            self.date = date
        self.pity = pity
        self.weapon = weapon

    @property
    def icon_url(self) -> str:
        strip_prefix = [
            'Shikanoin Heizou',
            'Sangonomiya Kokomi',
            'Kaedehara Kazuha',
            'Kujou Sara',
            'Kamisato Ayato',
            'Kamisato Ayaka',
            'Arataki Itto',
        ]
        strip_suffix = [
            'Raiden Shogun'
        ]

        if not self.weapon:
            if self.name in strip_prefix:
                name = self.name.split()[-1]
            elif self.name in strip_suffix:
                name = self.name.split()[0]
            else:
                name = self.name

            return f"https://rerollcdn.com/GENSHIN/Characters/1/{name}.png"

        name = self.name.replace(" ", "_")
        return f"https://rerollcdn.com/GENSHIN/Weapons/{name}.png"

    def __repr__(self) -> str:
        base = [repr(self.name), repr(self.date)]
        if self.pity is not None:
            base.append(str(self.pity))

        return f"Wish({','.join(base)})"

PAGE = """<!DOCTYPE html>
<html lang="en">
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
					<li><a href="/genshin/">genshin</a></li>
					<li>/</li>
					<li><a href="/genshin/account.html">account</a></li>
				</ul>
				<div contenteditable></div>
			</nav>
		</header>
		<main id="page" class="glass">
		<h1>My Genshin account</h1>
		<p>
			This are all of my characters listed by the time that I got them.
			Currently I have {characters_count} characters.
            Additionally I listed my 5* weapons - I'm not really a fan of weapon banner but I had some luck on it with Arlecchino and Lyney especially.
			You can find more information about some of the builds on my <a href="https://akasha.cv/profile/739467452">akasha profile</a>.
		</p>
		<p>
			This page was generated using this <a href="characters.py">Python script</a>.
		</p>
        <section>
            <h2>5* Weapons</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, 100px); justify-content: center">
                {weapons}
            </div>
        </section>
        <section>
            <h2>Characters</h2>
            {characters}
        </section>
        </main>
	</table>
</body>
</html>
"""

CHARACTERS = sorted([
    Wish("Arlecchino", "2024-05-02", pity=76),
    Wish("Chiori", "2024-03-22", pity=80),
    Wish("Xianyun", "2024-02-18", pity=75),
    Wish("Gaming", "2024-02-05"),
    Wish("Chevreuse", "2024-01-13"),
    Wish("Navia", "2023-12-20", pity=58),
    Wish("Furina", "2023-11-08", pity=78),
    Wish("Charlotte", "2023-11-08"),
    Wish("Freminet", "2023-09-12"),
    Wish("Lyney", "2023-09-03", pity=82),
    Wish("Lynette", "2023-08-16"),
    Wish("Kirara", "2023-05-24"),
    Wish("Kaveh", "2023-05-05"),
    Wish("Mika", "2023-07-08"),
    Wish("Dehya", "2023-06-26"),
    Wish("Yaoyao", "2023-02-03"),
    Wish("Wanderer", "2022-12-10"),
    Wish("Faruzan", "2022-12-08"),
    Wish("Layla", "2023-03-02"),
    Wish("Nahida", "2023-04-15"),
    Wish("Cyno", "2023-03-19"),
    Wish("Candace", "2023-12-20"),
    Wish("Dori", "2022-09-09"),
    Wish("Tighnari", "2022-11-04"),
    Wish("Collei", "2022-08-24"),
    Wish("Shikanoin Heizou", "2023-06-17"),
    Wish("Kuki Shinobu", "2022-09-28"),
    Wish("Yelan", "2022-06-05"),
    Wish("Kamisato Ayato", "2022-04-09"),
    Wish("Yun Jin", "2022-04-09"),
    Wish("Arataki Itto", "2022-06-22"),
    Wish("Gorou", "2022-12-10"),
    Wish("Thoma", "2022-02-22"),
    Wish("Sangonomiya Kokomi", "2023-07-26", pity=43),
    Wish("Raiden Shogun", "2023-01-07"),
    Wish("Kujou Sara", "2022-04-01"),
    Wish("Sayu", "2022-04-21"),
    Wish("Kamisato Ayaka", "2022-05-20"),
    Wish("Kaedehara Kazuha", "2023-06-26", pity=45),
    Wish("Yanfei", "2022-05-31"),
    Wish("Rosaria", "2022-05-08"),
    Wish("Xiao", "2023-02-03"),
    Wish("Ganyu", "2022-09-09"),
    Wish("Zhongli", "2022-08-24"),
    Wish("Xinyan", "2022-06-13"),
    Wish("Diona", "2022-08-24"),
    Wish("Venti", "2022-10-14"),
    Wish("Keqing", "2023-10-01"),
    Wish("Mona", "2023-02-03"),
    Wish("Qiqi", "2022-04-21"),
    Wish("Jean", "2022-05-13"),
    Wish("Sucrose", "2022-03-31"),
    Wish("Chongyun", "2022-11-02"),
    Wish("Noelle", "2022-02-03"),
    Wish("Bennett", "2022-05-08"),
    Wish("Fischl", "2022-08-02"),
    Wish("Ningguang", "2022-05-21"),
    Wish("Xingqiu", "2022-04-17"),
    Wish("Beidou", "2022-02-07"),
    Wish("Xiangling", "2022-02-05"),
    Wish("Razor", "2022-04-24"),
    Wish("Barbara", "2022-02-13"),
    Wish("Lisa", "2022-02-03"),
    Wish("Kaeya", "2022-02-03"),
    Wish("Amber", "2022-02-03"),
], key=lambda x: (x.date, x.name), reverse=True)

assert all(char.date is not None for char in CHARACTERS)

FIVE_STAR_WEAPONS = sorted([
    Wish("Aquila Favonia", weapon=True),
    Wish("Crimson Moon's Semblance", pity=67, weapon=True),
    Wish("Skyward Harp", weapon=True),
    Wish("The First Great Magic", pity=3, weapon=True),
], key=lambda x: x.name)

if __name__ == "__main__":
    main()
