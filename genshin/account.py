import typing
from datetime import datetime
import enum

# TODO: Show pity

# TODO: Maybe display in a grid similar to that in-game? From current list it is hard
# to infer which characters I don't have, and for my account it is more relevant information.
# Also this list is useless since it doesn't show which characters I use / have build.


def main():
    print(PAGE.format(
        weapons=generate_weapons(),
        characters=generate_characters(),
        characters_count=len(CHARACTERS),
        elements=''.join(generate_elements())
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
            characters="\n".join(f'<img style="width: 100%" class="{c.classes}" src="{c.icon_url}" alt="{c.name}">' for c in group)
        )
        for group_name, group in grouped.items()
    )

def generate_weapons() -> str:
    return "\n".join(f'<img style="width: 100%" src="{c.icon_url}" alt="{c.name}">' for c in FIVE_STAR_WEAPONS)

def generate_elements():
    for i in range(2):
        if i == 0:
            yield '<p>How many characters from given element do I often use?</p>'
        else:
            yield '<p>How many characters from given element do I own?</p>'

        yield '<div style="display: grid; grid-template-columns: repeat(7, 1fr); grid-template-rows: 4rem auto; justify-content: center; text-align: center">'
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
            yield f'<div style="background: linear-gradient(to top, #{COLORS[element]} 0%, transparent {p}%);">{element_count[element]}</div>'

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

class Wish:
    def __init__(self,
                 name: str, date: datetime|str|None = None, *,
                 pity: typing.Optional[int] = None,
                 weapon: bool = False,
                 benched: bool = True,
                 ):
        self.name = name
        if isinstance(date, str):
            self.date = datetime.strptime(date, "%Y-%m-%d")
        else:
            self.date = date
        self.pity = pity
        self.weapon = weapon
        self.benched = benched

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
		<script src="/scramble.js"></script>
		<script src="/glass-light.js"></script>
		<link rel="stylesheet" href="/common.css" />
        <style>
.benched {{
	filter: grayscale(0.75) brightness(60%);
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
			This page was generated using this <a href="characters.py">Python script</a>.
		</p>

        <section>
            <h2>Elements</h2>
            {elements}
        </section>

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
    Wish('Xilonen', '2024-10-21', benched=False),
    Wish('Kinich', '2024-09-27'),
    Wish('Kachina', '2024-08-28'),
    Wish('Nilou', '2024-07-20'),
    Wish('Sethos', '2024-06-05'),
    Wish("Arlecchino", "2024-05-02", pity=76, benched=False),
    Wish("Chiori", "2024-03-22", pity=80, benched=False),
    Wish("Xianyun", "2024-02-18", pity=75, benched=False),
    Wish("Gaming", "2024-02-05"),
    Wish("Chevreuse", "2024-01-13", benched=False),
    Wish("Navia", "2023-12-20", pity=58, benched=False),
    Wish("Furina", "2023-11-08", pity=78, benched=False),
    Wish("Charlotte", "2023-11-08"),
    Wish("Freminet", "2023-09-12"),
    Wish("Lyney", "2023-09-03", pity=82),
    Wish("Lynette", "2023-08-16"),
    Wish("Kirara", "2023-05-24"),
    Wish("Kaveh", "2023-05-05"),
    Wish("Mika", "2023-07-08"),
    Wish("Dehya", "2023-06-26"),
    Wish("Yaoyao", "2023-02-03", benched=False),
    Wish("Wanderer", "2022-12-10", benched=False),
    Wish("Faruzan", "2022-12-08", benched=False),
    Wish("Layla", "2023-03-02"),
    Wish("Nahida", "2023-04-15", benched=False),
    Wish("Cyno", "2023-03-19"),
    Wish("Candace", "2023-12-20"),
    Wish("Dori", "2022-09-09"),
    Wish("Tighnari", "2022-11-04"),
    Wish("Collei", "2022-08-24"),
    Wish("Shikanoin Heizou", "2023-06-17"),
    Wish("Kuki Shinobu", "2022-09-28", benched=False),
    Wish("Yelan", "2022-06-05", benched=False),
    Wish("Kamisato Ayato", "2022-04-09", benched=False),
    Wish("Yun Jin", "2022-04-09"),
    Wish("Arataki Itto", "2022-06-22"),
    Wish("Gorou", "2022-12-10"),
    Wish("Thoma", "2022-02-22", benched=False),
    Wish("Sangonomiya Kokomi", "2023-07-26", pity=43, benched=False),
    Wish("Raiden Shogun", "2023-01-07"),
    Wish("Kujou Sara", "2022-04-01"),
    Wish("Sayu", "2022-04-21"),
    Wish("Kamisato Ayaka", "2022-05-20"),
    Wish("Kaedehara Kazuha", "2023-06-26", pity=45, benched=False),
    Wish("Yanfei", "2022-05-31"),
    Wish("Rosaria", "2022-05-08"),
    Wish("Xiao", "2023-02-03"),
    Wish("Ganyu", "2022-09-09"),
    Wish("Zhongli", "2022-08-24", benched=False),
    Wish("Xinyan", "2022-06-13"),
    Wish("Diona", "2022-08-24"),
    Wish("Venti", "2022-10-14"),
    Wish("Keqing", "2023-10-01"),
    Wish("Mona", "2023-02-03"),
    Wish("Qiqi", "2022-04-21", benched=False),
    Wish("Jean", "2022-05-13"),
    Wish("Sucrose", "2022-03-31"),
    Wish("Chongyun", "2022-11-02"),
    Wish("Noelle", "2022-02-03"),
    Wish("Bennett", "2022-05-08", benched=False),
    Wish("Fischl", "2022-08-02", benched=False),
    Wish("Ningguang", "2022-05-21"),
    Wish("Xingqiu", "2022-04-17", benched=False),
    Wish("Beidou", "2022-02-07", benched=False),
    Wish("Xiangling", "2022-02-05", benched=False),
    Wish("Razor", "2022-04-24"),
    Wish("Barbara", "2022-02-13"),
    Wish("Lisa", "2022-02-03"),
    Wish("Kaeya", "2022-02-03"),
    Wish("Amber", "2022-02-03"),
], key=lambda x: (x.date, x.name), reverse=True)

assert all(char.date is not None for char in CHARACTERS)

FIVE_STAR_WEAPONS = sorted([
    Wish('Uraku Misugiri', weapon=True),
    Wish('Peak Patrol Song', weapon=True),
    Wish("Aquila Favonia", weapon=True),
    Wish("Crimson Moon's Semblance", pity=67, weapon=True),
    Wish("Skyward Harp", weapon=True),
    Wish("The First Great Magic", pity=3, weapon=True),
], key=lambda x: x.name)

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

if __name__ == "__main__":
    main()
