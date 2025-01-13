import typing
from datetime import datetime, timedelta
import enum
import collections

# TODO: Show pity

# TODO: Maybe display in a grid similar to that in-game? From current list it is hard
# to infer which characters I don't have, and for my account it is more relevant information.
# Also this list is useless since it doesn't show which characters I use / have build.

# TODO: Add sort by date, sort by how many used
# TODO: Add weapon stats - how often do I use characters from given weapon type, how much I own etc

def main():
    global versions
    versions = collections.defaultdict(set)

    for c, n in zip(VERSIONS, VERSIONS[1:]):
        start  = c.start
        finish = n.start - timedelta(days=1)
        start_q = (start.month - 1) // 3 + 1
        finish_q = (finish.month - 1) // 3 + 1
        versions[f"Q{start_q} {start.year}"] |= {c}
        versions[f"Q{finish_q} {finish.year}"] |= {c}

    print(PAGE.format(
        weapons=generate_weapons(),
        characters=generate_characters(),
        characters_count=len(CHARACTERS),
        elements=''.join(generate_elements())
    ))

def generate_characters() -> str:
    global versions
    grouped = {}

    for c in CHARACTERS:
        for v in VERSIONS:
            if c.date < v.start:
                break
            version = v

        target = f"{version.major}.{version.minor}"
        if target not in grouped:
            grouped[target] = []
        grouped[target].append(c)

    characters = "\n".join(
        """
            <div style="display: grid; grid-template-columns: 3ch auto; align-items: center; border-style: solid; padding: 1ch; border-width: 0 1px 1px 0">
                <h3 style="padding: 0; margin: 0">{group_name}</h3>
                <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 1ch">
                    {characters}
                </div>
            </div>
        """.format(
            usage = f"{100 * sum(1 for c in group if not c.benched) / len(group):.0f}%",
            versions=', '.join(f"{v}" for v in sorted(versions[group_name])),
            group_name=group_name,
            characters="\n".join(f'<div class="{c.classes}"><img src="{c.icon_url}" alt="{c.name}" title="{c.name}"></div>' for c in group)
        )
        for group_name, group in grouped.items()
    )

    usage = 100 * sum(1 for g in grouped.values() for c in g if not c.benched) / sum(len(g) for g in grouped)
    return f"""
        <h2>Characters ({usage:.0f}% used)</h2>
        <p>⭐ - favourite characters (by design/gameplay/personality)</p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; border-style: solid; border-width: 1px 0 0 1px">
            {characters}
        </div>
    """

def generate_weapons() -> str:
    return "\n".join(f'<img style="width: 100%" src="{c.icon_url}" alt="{c.name}">' for c in FIVE_STAR_WEAPONS)

def generate_elements():
    for i in range(2):
        yield '<details style="margin-bottom: 1rem"><summary>'
        if i == 0:
            yield 'How many characters from given element do I often use?'
        else:
            yield 'How many characters from given element do I own?'
        yield '</summary>'

        yield '<div style="display: grid; grid-template-columns: repeat(7, 1fr); grid-template-rows: auto auto; justify-content: center; text-align: center">'
        for element in Element:
            yield f'<div>'
            for character in sorted(CHARACTERS, key=lambda c: c.name):
                if character.element == element and (i == 1 or not character.benched):
                    yield f'<img style="width: 33.3%"src="{character.icon_url}" title="{character.name}">\n'
            yield f'</div>'
        yield '</div>'
        yield f'</details>'

        yield '<div style="display: grid; grid-template-columns: repeat(7, 1fr); grid-template-rows: 4rem auto auto; justify-content: center; text-align: center; margin-bottom: 1rem">'
        element_count = {}
        for element in Element:
            element_count[element] = sum(1 for character in CHARACTERS if (i == 1 or not character.benched) and character.element == element)

        COLORS = {
                Element.ANEMO: '359697',
                Element.CRYO: '4682B4',
                Element.DENDRO: '608a00',
                Element.ELECTRO: '945dc4',
                Element.GEO: 'debd6c',
                Element.HYDRO: '00BFFF',
                Element.PYRO: 'EC4923',
        }

        m = max(element_count.values())

        for element in Element:
            p = element_count[element]/m*100
            yield f'<div style="background: linear-gradient(to top, #{COLORS[element]} 0%, transparent {p}%);">{element_count[element]}</div>\n'

        for element in Element:
            yield f'<strong>{element}</strong>'

        yield '</div>'


class Element(enum.StrEnum):
    ANEMO = "Anemo"
    CRYO = "Cryo"
    DENDRO = "Dendro"
    ELECTRO = "Electro"
    GEO = "Geo"
    HYDRO = "Hydro"
    PYRO = "Pyro"

class WeaponType:
    BOW = "Bow"
    CATALYST = "Catalyst"
    CLAYMORE = "Claymore"
    POLEARM = "Polearm"
    SWORD = "Sword"

class Region(enum.StrEnum):
    FONTAINE = "Fontaine"
    INAZUMA = "Inazuma"
    LIYUE = "Liyue"
    MONDSTADT = "Mondstadt"
    NATLAN = "Natlan"
    SNEZHNAYA = "Snezhnaya"
    SUMERU = "Sumeru"


class Wish:
    def __init__(self,
                 name: str, date: datetime|str|None = None, *,
                 pity: typing.Optional[int] = None,
                 weapon: bool = False,
                 weapon_type: WeaponType|None = None,
                 benched: bool = True,
                 favourite: bool = False,
                 ):
        self.name = name
        if isinstance(date, str):
            self.date = datetime.strptime(date, "%Y-%m-%d")
        else:
            self.date = date
        self.pity = pity
        self.weapon = weapon
        self.benched = benched
        self.favourite = favourite
        self.weapon_type = weapon_type

    @property
    def icon_url(self) -> str:
        name = self.name.replace(" ", "_")
        if not self.weapon:
            return f"icons/{name}.webp"
        return f"https://rerollcdn.com/GENSHIN/Weapons/{name}.png"

    @property
    def classes(self) -> str:
        classes = []
        if self.benched: classes.append('benched')
        if self.favourite: classes.append('favourite')
        return ' '.join(classes)

    @property
    def element(self) -> str:
        assert self.name in CHARACTERS_ELEMENT, f"{self.name} doesn't have an element in CHARACTERS_ELEMENT table"
        return CHARACTERS_ELEMENT[self.name]

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
		<link rel="stylesheet" href="/common.css" />
        <style>
.benched img {{
	filter: grayscale(0.75) brightness(60%);
}}
[data-tooltip]:hover::after {{
  display: block;
  position: absolute;
  content: attr(data-tooltip);
  border: 1px solid black;
  background: #eee;
  padding: .25em;
}}

.favourite {{
    position: relative;
}}
.favourite::after {{
    content: "⭐";
    position: absolute;
    top: 0;
    right: 0;
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
		<h1>My Genshin account</h1>
		<p>
			Currently I have {characters_count} characters and a few 5 star weapons.
			You can find more information about some of the builds on my <a href="https://akasha.cv/profile/739467452">akasha profile</a>.
        </p>
        <p>
            Characters that are gray and dimm are considered as benched - I either didn't use them in a while or didn't built them at all.
		</p>
		<p>
			This page was generated using this <a href="account.py">Python script</a>.
		</p>

        <section>
            <h2>Elements</h2>
            {elements}
        </section>

        <section>
            <h2>5* Weapons</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, 80px); justify-content: center">
                {weapons}
            </div>
        </section>
        <section>
            {characters}
        </section>
        </main>
	</table>
</body>
</html>
"""

CHARACTERS = sorted([
    Wish('Citlali', '2025-01-01', benched=False, favourite=True),
    Wish('Ororon', '2024-11-21', benched=False, favourite=True),
    Wish('Chasca', '2024-11-21', benched=False),
    Wish('Xilonen', '2024-10-21', benched=False),
    Wish('Kinich', '2024-09-27'),
    Wish('Kachina', '2024-08-28'),
    Wish('Nilou', '2024-07-20'),
    Wish('Sethos', '2024-06-05'),
    Wish("Arlecchino", "2024-05-02", pity=76, benched=False, favourite=True),
    Wish("Chiori", "2024-03-22", pity=80, benched=False, favourite=True),
    Wish("Xianyun", "2024-02-18", pity=75, benched=False),
    Wish("Gaming", "2024-02-05", favourite=True),
    Wish("Chevreuse", "2024-01-13", benched=False),
    Wish("Navia", "2023-12-20", pity=58, benched=False, favourite=True),
    Wish("Furina", "2023-11-08", pity=78, benched=False, favourite=True),
    Wish("Charlotte", "2023-11-08"),
    Wish("Freminet", "2023-09-12"),
    Wish("Lyney", "2023-09-03", pity=82, benched=False),
    Wish("Lynette", "2023-08-16", favourite=True),
    Wish("Kirara", "2023-05-24", favourite=True),
    Wish("Kaveh", "2023-05-05"),
    Wish("Mika", "2023-07-08"),
    Wish("Dehya", "2023-06-26"),
    Wish("Yaoyao", "2023-02-03", benched=False, favourite=True),
    Wish("Wanderer", "2022-12-10", benched=False),
    Wish("Faruzan", "2022-12-08", benched=False),
    Wish("Layla", "2023-03-02", favourite=True),
    Wish("Nahida", "2023-04-15", benched=False, favourite=True),
    Wish("Cyno", "2023-03-19"),
    Wish("Candace", "2023-12-20"),
    Wish("Dori", "2022-09-09"),
    Wish("Tighnari", "2022-11-04"),
    Wish("Collei", "2022-08-24"),
    Wish("Shikanoin Heizou", "2023-06-17"),
    Wish("Kuki Shinobu", "2022-09-28", benched=False, favourite=True),
    Wish("Yelan", "2022-06-05", benched=False, favourite=True),
    Wish("Kamisato Ayato", "2022-04-09", benched=False),
    Wish("Yun Jin", "2022-04-09"),
    Wish("Arataki Itto", "2022-06-22", favourite=True),
    Wish("Gorou", "2022-12-10"),
    Wish("Thoma", "2022-02-22", benched=False),
    Wish("Sangonomiya Kokomi", "2023-07-26", pity=43, benched=False, favourite=True),
    Wish("Raiden Shogun", "2023-01-07"),
    Wish("Kujou Sara", "2022-04-01"),
    Wish("Sayu", "2022-04-21", favourite=True),
    Wish("Kamisato Ayaka", "2022-05-20"),
    Wish("Kaedehara Kazuha", "2023-06-26", pity=45, benched=False),
    Wish("Yanfei", "2022-05-31"),
    Wish("Rosaria", "2022-05-08"),
    Wish("Xiao", "2023-02-03", benched=False),
    Wish("Ganyu", "2022-09-09"),
    Wish("Zhongli", "2022-08-24", benched=False),
    Wish("Xinyan", "2022-06-13"),
    Wish("Diona", "2022-08-24"),
    Wish("Venti", "2022-10-14"),
    Wish("Keqing", "2023-10-01"),
    Wish("Mona", "2023-02-03"),
    Wish("Qiqi", "2022-04-21", benched=False, favourite=True),
    Wish("Jean", "2022-05-13"),
    Wish("Sucrose", "2022-03-31", benched=False),
    Wish("Chongyun", "2022-11-02"),
    Wish("Noelle", "2022-02-03"),
    Wish("Bennett", "2022-05-08", benched=False),
    Wish("Fischl", "2022-08-02", benched=False, favourite=True),
    Wish("Ningguang", "2022-05-21"),
    Wish("Xingqiu", "2022-04-17", benched=False),
    Wish("Beidou", "2022-02-07", benched=False, favourite=True),
    Wish("Xiangling", "2022-02-05", benched=False),
    Wish("Razor", "2022-04-24"),
    Wish("Barbara", "2022-02-13"),
    Wish("Lisa", "2022-02-03"),
    Wish("Kaeya", "2022-02-03"),
    Wish("Amber", "2022-02-03"),
], key=lambda x: (x.date, x.name), reverse=True)

assert all(char.date is not None for char in CHARACTERS)

FIVE_STAR_WEAPONS = sorted([
    Wish("Aquila Favonia", weapon=True, weapon_type=WeaponType.SWORD),
    Wish("Crimson Moon's Semblance", pity=67, weapon=True, weapon_type=WeaponType.POLEARM),
    Wish("Skyward Harp", weapon=True, weapon_type=WeaponType.BOW),
    Wish("The First Great Magic", pity=3, weapon=True, weapon_type=WeaponType.BOW),
    Wish('Peak Patrol Song', weapon=True, weapon_type=WeaponType.SWORD),
    Wish('Primordial Jade Winged-Spear', weapon=True, weapon_type=WeaponType.POLEARM),
    Wish('Uraku Misugiri', weapon=True, weapon_type=WeaponType.SWORD),
], key=lambda x: ([WeaponType.SWORD, WeaponType.POLEARM, WeaponType.CLAYMORE, WeaponType.BOW, WeaponType.CATALYST].index(x.weapon_type), x.name))

CHARACTERS_ELEMENT = {
    "Albedo": Element.GEO,
    "Alhaitham": Element.DENDRO,
    "Aloy": Element.CRYO,
    "Amber": Element.PYRO,
    "Arataki Itto": Element.GEO,
    "Arlecchino": Element.PYRO,
    "Baizhu": Element.DENDRO,
    "Barbara": Element.HYDRO,
    "Beidou": Element.ELECTRO,
    "Bennett": Element.PYRO,
    "Candace": Element.HYDRO,
    "Charlotte": Element.CRYO,
    "Chasca": Element.ANEMO,
    "Chevreuse": Element.PYRO,
    "Chiori": Element.GEO,
    "Chongyun": Element.CRYO,
    "Citlali": Element.CRYO,
    "Clorinde": Element.ELECTRO,
    "Collei": Element.DENDRO,
    "Cyno": Element.ELECTRO,
    "Dehya": Element.PYRO,
    "Diluc": Element.PYRO,
    "Diona": Element.CRYO,
    "Dori": Element.ELECTRO,
    "Emilie": Element.DENDRO,
    "Eula": Element.CRYO,
    "Faruzan": Element.ANEMO,
    "Fischl": Element.ELECTRO,
    "Freminet": Element.CRYO,
    "Furina": Element.HYDRO,
    "Gaming": Element.PYRO,
    "Ganyu": Element.CRYO,
    "Gorou": Element.GEO,
    "Hu Tao": Element.PYRO,
    "Jean": Element.ANEMO,
    "Kachina": Element.GEO,
    "Kaedehara Kazuha": Element.ANEMO,
    "Kaeya": Element.CRYO,
    "Kamisato Ayaka": Element.CRYO,
    "Kamisato Ayato": Element.HYDRO,
    "Kaveh": Element.DENDRO,
    "Keqing": Element.ELECTRO,
    "Kinich": Element.DENDRO,
    "Kirara": Element.DENDRO,
    "Klee": Element.PYRO,
    "Kujou Sara": Element.ELECTRO,
    "Kuki Shinobu": Element.ELECTRO,
    "Layla": Element.CRYO,
    "Lisa": Element.ELECTRO,
    "Lynette": Element.ANEMO,
    "Lyney": Element.PYRO,
    "Mika": Element.CRYO,
    "Mona": Element.HYDRO,
    "Mualani": Element.HYDRO,
    "Nahida": Element.DENDRO,
    "Navia": Element.GEO,
    "Neuvillette": Element.HYDRO,
    "Nilou": Element.HYDRO,
    "Ningguang": Element.GEO,
    "Noelle": Element.GEO,
    "Ororon": Element.ELECTRO,
    "Qiqi": Element.CRYO,
    "Raiden Shogun": Element.ELECTRO,
    "Razor": Element.ELECTRO,
    "Rosaria": Element.CRYO,
    "Sangonomiya Kokomi": Element.HYDRO,
    "Sayu": Element.ANEMO,
    "Sethos": Element.ELECTRO,
    "Shenhe": Element.CRYO,
    "Shikanoin Heizou": Element.ANEMO,
    "Sigewinne": Element.HYDRO,
    "Sucrose": Element.ANEMO,
    "Tartaglia": Element.HYDRO,
    "Thoma": Element.PYRO,
    "Tighnari": Element.DENDRO,
    "Venti": Element.ANEMO,
    "Wanderer": Element.ANEMO,
    "Wriothesley": Element.CRYO,
    "Xiangling": Element.PYRO,
    "Xianyun": Element.ANEMO,
    "Xiao": Element.ANEMO,
    "Xilonen": Element.GEO,
    "Xingqiu": Element.HYDRO,
    "Xinyan": Element.PYRO,
    "Yae Miko": Element.ELECTRO,
    "Yanfei": Element.PYRO,
    "Yaoyao": Element.DENDRO,
    "Yelan": Element.HYDRO,
    "Yoimiya": Element.PYRO,
    "Yun Jin": Element.GEO,
    "Zhongli": Element.GEO,
}

"""
CHARACTERS_REGION = {
    "Albedo": Region.MONDSTADT,
    "Alhaitham": Region.SUMERU,
    "Amber": Region.MONDSTADT,
    "Arataki Itto": Region.INAZUMA,
    "Arlecchino": Region.SNEZHNAYA,
    "Baizhu": Region.LIYUE,
    "Barbara": Region.MONDSTADT,
    "Beidou": Region.LIYUE,
    "Bennett": Region.MONDSTADT,
    "Candace": Region.SUMERU,
    "Charlotte": Region.FONTAINE,
    "Chasca": Region.NATLAN,
    "Chevreuse": Region.FONTAINE,
    "Chiori": Region.INAZUMA,
    "Chongyun": Region.,
    "Citlali": Region.,
    "Clorinde": Region.,
    "Collei": Region.,
    "Cyno": Region.,
    "Dehya": Region.,
    "Diluc": Region.,
    "Diona": Region.,
    "Dori": Region.,
    "Emilie": Region.,
    "Eula": Region.,
    "Faruzan": Region.,
    "Fischl": Region.,
    "Freminet": Region.,
    "Furina": Region.,
    "Gaming": Region.,
    "Ganyu": Region.,
    "Gorou": Region.,
    "Hu Tao": Region.,
    "Jean": Region.,
    "Kachina": Region.,
    "Kaedehara Kazuha": Region.,
    "Kaeya": Region.,
    "Kamisato Ayaka": Region.,
    "Kamisato Ayato": Region.,
    "Kaveh": Region.,
    "Keqing": Region.,
    "Kinich": Region.,
    "Kirara": Region.,
    "Klee": Region.,
    "Kujou Sara": Region.,
    "Kuki Shinobu": Region.,
    "Layla": Region.,
    "Lisa": Region.,
    "Lynette": Region.,
    "Lyney": Region.,
    "Mika": Region.,
    "Mona": Region.,
    "Mualani": Region.,
    "Nahida": Region.,
    "Navia": Region.,
    "Neuvillette": Region.,
    "Nilou": Region.,
    "Ningguang": Region.,
    "Noelle": Region.,
    "Ororon": Region.,
    "Qiqi": Region.,
    "Raiden Shogun": Region.,
    "Razor": Region.,
    "Rosaria": Region.,
    "Sangonomiya Kokomi": Region.,
    "Sayu": Region.,
    "Sethos": Region.,
    "Shenhe": Region.,
    "Shikanoin Heizou": Region.,
    "Sigewinne": Region.,
    "Sucrose": Region.,
    "Tartaglia": Region.,
    "Thoma": Region.,
    "Tighnari": Region.,
    "Venti": Region.,
    "Wanderer": Region.,
    "Wriothesley": Region.,
    "Xiangling": Region.,
    "Xianyun": Region.,
    "Xiao": Region.,
    "Xilonen": Region.,
    "Xingqiu": Region.,
    "Xinyan": Region.,
    "Yae Miko": Region.,
    "Yanfei": Region.,
    "Yaoyao": Region.,
    "Yelan": Region.,
    "Yoimiya": Region.,
    "Yun Jin": Region.,
    "Zhongli": Region.,
}
"""

class Version:
    def __init__(self, major: int, minor: int, start: str):
        self.major = major
        self.minor = minor
        self.start = datetime.fromisoformat(start)

    def __lt__(self, other):
        return (self.major, self.minor) < (other.major, other.minor)

    def __eq__(self, other):
        return (self.major, self.minor) == (self.major, self.minor)

    def __str__(self):
        return f"{self.major}.{self.minor}"

    def __hash__(self):
        return (self.major, self.minor).__hash__()



# Paste in console:
# [...document.querySelectorAll('h3:has([id*="Version_"]) + table[data-index-number] tr:has([data-sort-value])')].map(x => `Version(${x.querySelector('td').textContent.trim().replace(".", ", ")}, "${x.querySelector('[data-sort-value]').dataset.sortValue}"),`).join('\n')
# on https://genshin-impact.fandom.com/wiki/Version

VERSIONS = sorted((
    Version(5, 3, "2025-01-01"),
    Version(5, 2, "2024-11-20"),
    Version(5, 1, "2024-10-09"),
    Version(5, 0, "2024-08-28"),
    Version(4, 8, "2024-07-17"),
    Version(4, 7, "2024-06-05"),
    Version(4, 6, "2024-04-24"),
    Version(4, 5, "2024-03-13"),
    Version(4, 4, "2024-01-31"),
    Version(4, 3, "2023-12-20"),
    Version(4, 2, "2023-11-08"),
    Version(4, 1, "2023-09-27"),
    Version(4, 0, "2023-08-16"),
    Version(3, 8, "2023-07-05"),
    Version(3, 7, "2023-05-24"),
    Version(3, 6, "2023-04-12"),
    Version(3, 5, "2023-03-01"),
    Version(3, 4, "2023-01-18"),
    Version(3, 3, "2022-12-07"),
    Version(3, 2, "2022-11-02"),
    Version(3, 1, "2022-09-28"),
    Version(3, 0, "2022-08-24"),
    Version(2, 8, "2022-07-13"),
    Version(2, 7, "2022-05-31"),
    Version(2, 6, "2022-03-30"),
    Version(2, 5, "2022-02-16"),
    Version(2, 4, "2022-01-05"),
    Version(2, 3, "2021-11-24"),
    Version(2, 2, "2021-10-13"),
    Version(2, 1, "2021-09-01"),
    Version(2, 0, "2021-07-21"),
    Version(1, 6, "2021-06-09"),
    Version(1, 5, "2021-04-28"),
    Version(1, 4, "2021-03-17"),
    Version(1, 3, "2021-02-03"),
    Version(1, 2, "2020-12-23"),
    Version(1, 1, "2020-11-11"),
    Version(1, 0, "2020-09-28"),
    Version(0, 9.9, "2020-07-02"),
    Version(0, 7.1, "2020-03-18"),
))

if __name__ == "__main__":
    main()
