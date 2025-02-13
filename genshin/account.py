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

    write_account_page()
    write_characters_page()

def write_account_page():
    with open("account.html", "w") as f:
        print(PAGE.format(
            five_star_weapons=generate_five_star_weapons(),
            characters=generate_characters(),
            characters_count=len(CHARACTERS),
            elements=''.join(generate_elements()),
            weapons=''.join(generate_weapons()),
            regions=''.join(generate_regions()),
            versions=''.join(generate_versions()),
            five_star_vs_four_star=''.join(generate_five_star_vs_four_star()),
        ), file=f)

def write_characters_page():
    characters = '\n'.join(f"""<img class="icon" src="{c.icon_url}" alt={c.name} title="{c.name}" data-version="{'.'.join(map(str, c.release))}" data-benched="{c.benched}">"""
                           for c in sorted(CHARACTERS, key=lambda x: (x.release, x.benched, x.name)))

    script = "const versions = [" + ',\n'.join(f'"{v}"' for v in VERSIONS) + "]" + \
    """
    function onInput(e) {
        const min = versions[min_version.value];
        const max = versions[max_version.value];
        if (e.target == max_version && max < min) min_version.value = max_version.value;
        if (e.target == min_version && min > max) max_version.value = min_version.value;

        document.querySelector("label[for=min_version] span").textContent = min;
        document.querySelector("label[for=max_version] span").textContent = max;

        for (const icon of document.querySelectorAll(".icon")) {
        console.log(icon.dataset.version, min, max);
            if (min <= icon.dataset.version && icon.dataset.version <= max) {
                icon.classList.remove("hide");
            } else {
                icon.classList.add("hide");
            }
            if (icon.dataset.benched.toLowerCase() == "true") {
                icon.classList.add('benched');
            }
        }
    }

    min_version.addEventListener("input", onInput);
    max_version.addEventListener("input", onInput);
    onInput({ target: null });
    """

    style = """
    .hide {
        display: none;
    }
    .benched {
        filter: grayscale(0.75) brightness(60%);
    }
    tr, th, td {
        border: 1px solid black;
    }
    """

    def generate_table():
        yield '<tr>'
        yield '<td></td>'
        for weapon in WEAPON_ORDER:
            yield f'<th>{weapon}</th>'
        yield '</tr>'
        for element in Element:
            yield '<tr>'
            yield f'<th>{element}</th>'
            for weapon in WEAPON_ORDER:
                yield '<td>'
                for c in CHARACTERS:
                    if c.weapon == weapon and c.element == element and (not c.benched or c.name in ["Gaming", "Kinich", "Rosaria", "Raiden Shogun", "Candace", "Kirara", "Ganyu", "Ningguang"]):
                        yield f'<img src="{c.icon_url}">'
                yield '</td>'
            yield '</tr>'

    table = '\n'.join(generate_table())

    with open("characters.html", "w") as f:
        print(f"""<!DOCTYPE html>
        <html>
            <head>
            <style>{style}</style>
            </head>
        <body>
            <input type="range" min="0" max="{len(VERSIONS)-1}" step="1" value="0" id="min_version" name="min_version">
            <label for="min_version">From: <span>1.0</span></label>
            <input type="range" min="0" max="{len(VERSIONS)-1}" step="1" value="{len(VERSIONS)-1}" id="max_version" name="max_version">
            <label for="max_version">To: <span>1.0</span></label>
            <div>
                {characters}
            </div>
            <table>
                {table}
            </table>
            <script>
                {script}
            </script>
        </body>
        </html>""", file=f)

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
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); justify-content: center; gap: 1ch">
                    {characters}
                </div>
            </div>
        """.format(
            usage = f"{100 * sum(1 for c in group if not c.benched) / len(group):.0f}%",
            versions=', '.join(f"{v}" for v in sorted(versions[group_name])),
            group_name=group_name,
            characters="\n".join(f'<div class="{c.classes}"><img style="width: 100%" src="{c.icon_url}" alt="{c.name}" title="{c.name}"></div>' for c in group)
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

def generate_five_star_weapons() -> str:
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

def generate_weapons():
    for i in range(2):
        yield '<details style="margin-bottom: 1rem"><summary>'
        if i == 0:
            yield 'How many characters who use given weapon do I often use?'
        else:
            yield 'How many characters who use given weapon do I own?'
        yield '</summary>'

        yield '<div style="display: grid; grid-template-columns: repeat(5, 1fr); grid-template-rows: auto auto; justify-content: center; text-align: center">'
        for weapon in WEAPON_ORDER:
            yield f'<div>'
            for character in sorted(CHARACTERS, key=lambda c: c.name):
                if character.weapon == weapon and (i == 1 or not character.benched):
                    yield f'<img style="width: 33.3%"src="{character.icon_url}" title="{character.name}">\n'
            yield f'</div>'
        yield '</div>'
        yield f'</details>'

        yield '<div style="display: grid; grid-template-columns: repeat(5, 1fr); grid-template-rows: 4rem auto auto; justify-content: center; text-align: center; margin-bottom: 1rem">'
        weapon_count = {}
        for weapon in WEAPON_ORDER:
            weapon_count[weapon] = sum(1 for character in CHARACTERS if (i == 1 or not character.benched) and character.weapon == weapon)

        m = max(weapon_count.values())

        for weapon in WEAPON_ORDER:
            p = weapon_count[weapon]/m*100
            yield f'<div style="background: linear-gradient(to top, white 0%, transparent {p}%);">{weapon_count[weapon]}</div>\n'

        for weapon in WEAPON_ORDER:
            yield f'<img style="width: 40%; display: block; margin-inline: auto" src="{weapon.icon_url}" alt="{weapon}">'

        yield '</div>'

def generate_regions():
    for i in range(2):
        yield '<details style="margin-bottom: 1rem"><summary>'
        if i == 0:
            yield 'How many characters from given region do I often use?'
        else:
            yield 'How many characters from given region do I own?'
        yield '</summary>'

        yield '<div style="display: grid; grid-template-columns: repeat(6, 1fr); grid-template-rows: auto auto; justify-content: center; text-align: center">'
        for region in REGION_ORDER:
            yield f'<div>'
            for character in sorted(CHARACTERS, key=lambda c: c.name):
                if character.region == region and (i == 1 or not character.benched):
                    yield f'<img style="width: 33.3%"src="{character.icon_url}" title="{character.name}">\n'
            yield f'</div>'
        yield '</div>'
        yield f'</details>'

        yield '<div style="display: grid; grid-template-columns: repeat(6, 1fr); grid-template-rows: 4rem auto auto; justify-content: center; text-align: center; margin-bottom: 1rem">'
        region_count = {}
        for region in REGION_ORDER:
            region_count[region] = sum(1 for character in CHARACTERS if (i == 1 or not character.benched) and character.region == region)

        m = max(region_count.values())

        for region in REGION_ORDER:
            p = region_count[region]/m*100
            yield f'<div style="background: linear-gradient(to top, white 0%, transparent {p}%);">{region_count[region]}</div>\n'

        for region in REGION_ORDER:
            yield f'<img style="width: 60%; margin-inline: auto; display: block" src="{region.icon_url}" alt="{region}">'
            # yield f'<strong>{region.icon_url}</strong>'

        yield '</div>'

def generate_versions():
    versions = sorted(set(c.release[0] for c in CHARACTERS if not c.benched))

    for i in range(2):
        yield '<details style="margin-bottom: 1rem"><summary>'
        if i == 0:
            yield 'How many characters from given major version do I often use?'
        else:
            yield 'How many characters from given major version do I own?'
        yield '</summary>'

        yield f'<div style="display: grid; grid-template-columns: repeat({len(versions)}, 1fr); grid-template-rows: auto auto; justify-content: center; text-align: center">'
        for version in versions:
            yield f'<div>'
            for character in sorted(CHARACTERS, key=lambda c: c.name):
                if character.release[0] == version and (i == 1 or not character.benched):
                    yield f'<img style="width: 33.3%"src="{character.icon_url}" title="{character.name}">\n'
            yield f'</div>'
        yield '</div>'
        yield f'</details>'

        yield f'<div style="display: grid; grid-template-columns: repeat({len(versions)}, 1fr); grid-template-rows: 4rem auto auto; justify-content: center; text-align: center; margin-bottom: 1rem">'
        version_count = {}
        for version in versions:
            version_count[version] = sum(1 for character in CHARACTERS if (i == 1 or not character.benched) and character.release[0] == version)

        m = max(version_count.values())

        for version in versions:
            p = version_count[version]/m*100
            yield f'<div style="background: linear-gradient(to top, white 0%, transparent {p}%);">{version_count[version]}</div>\n'

        for version in versions:
            yield f'<strong>{version}</strong>'

        yield '</div>'

def generate_five_star_vs_four_star():
    five_stars_used  = sum(1 for c in CHARACTERS if not c.benched and c.five_star)
    five_stars_total = sum(1 for c in CHARACTERS if c.five_star)
    four_stars_used  = sum(1 for c in CHARACTERS if not c.benched and not c.five_star)
    four_stars_total = sum(1 for c in CHARACTERS if not c.five_star)

    u4 = four_stars_used / (five_stars_used + four_stars_used) * 100
    t4 = four_stars_total / (five_stars_total + four_stars_total) * 100

    yield '<div class="fvf">'
    yield f'<h3 style="grid-column: span 2; margin-top: 0.5rem">Used</h3>'
    yield f'<div style="grid-column: span 2; width: 100%; height: 1rem; background: linear-gradient(to right, rgb(148,112,187) 0%, rgb(148,112,187) {u4}%, rgba(200,124,36) {u4}%)"></div>'
    yield f'<div>Four stars: {four_stars_used}</div>'
    yield f'<div style="text-align: right">Five stars: {five_stars_used}</div>'

    yield f'<h3 style="grid-column: span 2">Total</h3>'
    yield f'<div style="grid-column: span 2; width: 100%; height: 1rem; background: linear-gradient(to right, rgb(148,112,187) 0%, rgb(148,112,187) {t4}%, rgba(200,124,36) {t4}%)"></div>'
    yield f'<div>Four stars: {four_stars_total}</div>'
    yield f'<div style="text-align: right">Five stars: {five_stars_total}</div>'
    yield '</div>'

class Element(enum.StrEnum):
    ANEMO = "Anemo"
    CRYO = "Cryo"
    DENDRO = "Dendro"
    ELECTRO = "Electro"
    GEO = "Geo"
    HYDRO = "Hydro"
    PYRO = "Pyro"

class WeaponType(enum.StrEnum):
    BOW = "Bow"
    CATALYST = "Catalyst"
    CLAYMORE = "Claymore"
    POLEARM = "Polearm"
    SWORD = "Sword"

    @property
    def icon_url(self):
        return f"{self.lower()}.webp"

WEAPON_ORDER = [WeaponType.SWORD, WeaponType.POLEARM, WeaponType.CLAYMORE, WeaponType.BOW, WeaponType.CATALYST]

class Role(enum.StrEnum):
    ON_FIELD = "On-Field"
    OFF_FIELD = "Off-Field"
    DPS = "DPS"
    SUPPORT = "Support"
    SURVIVABILITY = "Survivability"

class Region(enum.StrEnum):
    FONTAINE = "Fontaine"
    INAZUMA = "Inazuma"
    LIYUE = "Liyue"
    MONDSTADT = "Mondstadt"
    NATLAN = "Natlan"
    SUMERU = "Sumeru"

    @property
    def icon_url(self):
        return f"{str(self.lower())}.webp"

REGION_ORDER = [Region.MONDSTADT, Region.LIYUE, Region.INAZUMA, Region.SUMERU, Region.FONTAINE, Region.NATLAN]

class Wish:
    def __init__(self,
                 release_version: str,
                 name: str, date: datetime|str|None = None, *,
                 pity: typing.Optional[int] = None,
                 weapon: bool = False,
                 weapon_type: WeaponType|None = None,
                 benched: bool = True,
                 favourite: bool = False,
                 five_star: bool = False,
                 ):
        self.name = name
        self.release = list(map(int, release_version.split('.')))
        if isinstance(date, str):
            self.date = datetime.strptime(date, "%Y-%m-%d")
        else:
            self.date = date
        self.pity = pity
        self.is_weapon = weapon
        self.benched = benched
        self.favourite = favourite
        self.weapon_type = weapon_type
        self.five_star = five_star

    @property
    def icon_url(self) -> str:
        name = self.name.replace(" ", "_")
        if not self.is_weapon:
            return f"icons/{name}.webp"
        return f"https://rerollcdn.com/GENSHIN/Weapons/{name}.png"

    @property
    def classes(self) -> str:
        classes = []
        if self.benched: classes.append('benched')
        if self.favourite: classes.append('favourite')
        return ' '.join(classes)

    @property
    def element(self) -> Element:
        assert self.name in CHARACTERS_ELEMENT, f"{self.name} doesn't have an element in CHARACTERS_ELEMENT table"
        return CHARACTERS_ELEMENT[self.name]

    @property
    def weapon(self) -> WeaponType:
        assert self.name in CHARACTERS_WEAPON, f"{self.name} doesn't have a weapon in CHARACTERS_WEAPON table"
        return CHARACTERS_WEAPON[self.name]

    @property
    def region(self) -> Region:
        assert self.name in CHARACTERS_REGION, f"{self.name} doesn't have a region in CHARACTERS_REGION table"
        return CHARACTERS_REGION[self.name]

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
.fvf {{
    display: grid;
    grid-template-columns: 1fr 1fr;
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

        <details>
            <summary>More statistics</summary>
            <section>
                <h2>Weapons</h2>
                {weapons}
            </section>

            <section>
                <h2>Regions</h2>
                {regions}
            </section>

            <section>
                <h2>Versions</h2>
                {versions}
            </section>
        </details>

        <section>
            <h2 style="margin-bottom: 0">Five star vs four stars</h2>
            {five_star_vs_four_star}
        </section>

        <section>
            <h2>5* Weapons</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, 80px); justify-content: center">
                {five_star_weapons}
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
    Wish("5.3", "Lan Yan", "2025-01-21"),
    Wish("5.3", 'Citlali', '2025-01-01', benched=False, favourite=True, five_star=True),
    Wish("5.2", 'Ororon', '2024-11-21', benched=False, favourite=True),
    Wish("5.2", 'Chasca', '2024-11-21', benched=False, five_star=True),
    Wish("5.1", 'Xilonen', '2024-10-21', benched=False, five_star=True, favourite=True),
    Wish("5.0", 'Kinich', '2024-09-27', five_star=True),
    Wish("5.0", 'Kachina', '2024-08-28'),
    Wish("4.7", 'Sethos', '2024-06-05'),
    Wish("4.7", "Clorinde", "2025-02-10", favourite=True, five_star=True),
    Wish("4.6", "Arlecchino", "2024-05-02", pity=76, benched=False, favourite=True, five_star=True),
    Wish("4.5", "Chiori", "2024-03-22", pity=80, benched=False, favourite=True, five_star=True),
    Wish("4.4", "Xianyun", "2024-02-18", pity=75, benched=False, five_star=True, favourite=True),
    Wish("4.4", "Gaming", "2024-02-05", favourite=True),
    Wish("4.3", "Navia", "2023-12-20", pity=58, benched=False, favourite=True, five_star=True),
    Wish("4.3", "Chevreuse", "2024-01-13", benched=False),
    Wish("4.2", "Furina", "2023-11-08", pity=78, benched=False, favourite=True, five_star=True),
    Wish("4.2", "Charlotte", "2023-11-08"),
    Wish("4.0", "Lyney", "2023-09-03", pity=82, benched=False, five_star=True),
    Wish("4.0", "Lynette", "2023-08-16", favourite=True),
    Wish("4.0", "Freminet", "2023-09-12"),
    Wish("3.7", "Kirara", "2023-05-24", favourite=True),
    Wish("3.6", "Kaveh", "2023-05-05"),
    Wish("3.5", "Mika", "2023-07-08"),
    Wish("3.5", "Dehya", "2023-06-26", five_star=True),
    Wish("3.4", "Yaoyao", "2023-02-03", benched=False, favourite=True),
    Wish("3.3", "Wanderer", "2022-12-10", benched=False, five_star=True),
    Wish("3.3", "Faruzan", "2022-12-08", benched=False),
    Wish("3.2", "Nahida", "2023-04-15", benched=False, favourite=True, five_star=True),
    Wish("3.2", "Layla", "2023-03-02", favourite=True),
    Wish("3.1", 'Nilou', '2024-07-20', five_star=True),
    Wish("3.1", "Cyno", "2023-03-19", five_star=True),
    Wish("3.1", "Candace", "2023-12-20", favourite=True),
    Wish("3.0", "Tighnari", "2022-11-04", five_star=True),
    Wish("3.0", "Dori", "2022-09-09"),
    Wish("3.0", "Collei", "2022-08-24"),
    Wish("2.8", "Shikanoin Heizou", "2023-06-17"),
    Wish("2.7", "Yelan", "2022-06-05", benched=False, favourite=True, five_star=True),
    Wish("2.7", "Kuki Shinobu", "2022-09-28", benched=False, favourite=True),
    Wish("2.6", "Kamisato Ayato", "2022-04-09", benched=False, five_star=True),
    Wish("2.4", "Yun Jin", "2022-04-09"),
    Wish("2.3", "Gorou", "2022-12-10"),
    Wish("2.3", "Arataki Itto", "2022-06-22", favourite=True, five_star=True),
    Wish("2.2", "Thoma", "2022-02-22", benched=False),
    Wish("2.1", "Sangonomiya Kokomi", "2023-07-26", pity=43, benched=False, favourite=True, five_star=True),
    Wish("2.1", "Raiden Shogun", "2023-01-07", five_star=True),
    Wish("2.1", "Kujou Sara", "2022-04-01"),
    Wish("2.0", "Sayu", "2022-04-21", favourite=True),
    Wish("2.0", "Kamisato Ayaka", "2022-05-20", benched=False, five_star=True),
    Wish("1.6", "Kaedehara Kazuha", "2023-06-26", pity=45, benched=False, five_star=True),
    Wish("1.5", "Yanfei", "2022-05-31"),
    Wish("1.4", "Rosaria", "2022-05-08"),
    Wish("1.3", "Xiao", "2023-02-03", benched=False, five_star=True),
    Wish("1.2", "Ganyu", "2022-09-09", five_star=True),
    Wish("1.1", "Zhongli", "2022-08-24", benched=False, five_star=True),
    Wish("1.1", "Xinyan", "2022-06-13"),
    Wish("1.1", "Diona", "2022-08-24"),
    Wish("1.0", "Xingqiu", "2022-04-17", benched=False),
    Wish("1.0", "Xiangling", "2022-02-05", benched=False),
    Wish("1.0", "Venti", "2022-10-14", five_star=True),
    Wish("1.0", "Sucrose", "2022-03-31", benched=False, favourite=True),
    Wish("1.0", "Razor", "2022-04-24"),
    Wish("1.0", "Qiqi", "2022-04-21", benched=False, favourite=True, five_star=True),
    Wish("1.0", "Noelle", "2022-02-03"),
    Wish("1.0", "Ningguang", "2022-05-21"),
    Wish("1.0", "Mona", "2023-02-03", five_star=True),
    Wish("1.0", "Lisa", "2022-02-03"),
    Wish("1.0", "Keqing", "2023-10-01", five_star=True),
    Wish("1.0", "Kaeya", "2022-02-03"),
    Wish("1.0", "Jean", "2022-05-13", five_star=True),
    Wish("1.0", "Fischl", "2022-08-02", benched=False, favourite=True),
    Wish("1.0", "Chongyun", "2022-11-02"),
    Wish("1.0", "Bennett", "2022-05-08", benched=False),
    Wish("1.0", "Beidou", "2022-02-07", benched=False, favourite=True),
    Wish("1.0", "Barbara", "2022-02-13"),
    Wish("1.0", "Amber", "2022-02-03"),
], key=lambda x: (x.date, x.name), reverse=True)

assert all(char.date is not None for char in CHARACTERS)

FIVE_STAR_WEAPONS = sorted([
    Wish("0.0", "Aquila Favonia", weapon=True, weapon_type=WeaponType.SWORD),
    Wish("0.0", "Crimson Moon's Semblance", pity=67, weapon=True, weapon_type=WeaponType.POLEARM),
    Wish("0.0", "Skyward Harp", weapon=True, weapon_type=WeaponType.BOW),
    Wish("0.0", "The First Great Magic", pity=3, weapon=True, weapon_type=WeaponType.BOW),
    Wish("0.0", 'Peak Patrol Song', weapon=True, weapon_type=WeaponType.SWORD),
    Wish("0.0", 'Primordial Jade Winged-Spear', weapon=True, weapon_type=WeaponType.POLEARM),
    Wish("0.0", 'Uraku Misugiri', weapon=True, weapon_type=WeaponType.SWORD),
], key=lambda x: (WEAPON_ORDER.index(x.weapon_type), x.name))

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
    "Lan Yan": Element.ANEMO,
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

CHARACTERS_WEAPON = {
"Keqing": WeaponType.SWORD,
"Albedo": WeaponType.SWORD,
"Alhaitham": WeaponType.SWORD,
"Aloy": WeaponType.BOW,
"Amber": WeaponType.BOW,
"Arataki Itto": WeaponType.CLAYMORE,
"Arlecchino": WeaponType.POLEARM,
"Baizhu": WeaponType.CATALYST,
"Barbara": WeaponType.CATALYST,
"Beidou": WeaponType.CLAYMORE,
"Bennett": WeaponType.SWORD,
"Candace": WeaponType.POLEARM,
"Charlotte": WeaponType.CATALYST,
"Chasca": WeaponType.BOW,
"Chevreuse": WeaponType.POLEARM,
"Chiori": WeaponType.SWORD,
"Chongyun": WeaponType.CLAYMORE,
"Citlali": WeaponType.CATALYST,
"Clorinde": WeaponType.SWORD,
"Collei": WeaponType.BOW,
"Cyno": WeaponType.POLEARM,
"Dehya": WeaponType.CLAYMORE,
"Diluc": WeaponType.CLAYMORE,
"Diona": WeaponType.BOW,
"Dori": WeaponType.CLAYMORE,
"Emilie": WeaponType.POLEARM,
"Eula": WeaponType.CLAYMORE,
"Faruzan": WeaponType.BOW,
"Fischl": WeaponType.BOW,
"Freminet": WeaponType.CLAYMORE,
"Furina": WeaponType.SWORD,
"Gaming": WeaponType.CLAYMORE,
"Ganyu": WeaponType.BOW,
"Gorou": WeaponType.BOW,
"Hu Tao": WeaponType.POLEARM,
"Jean": WeaponType.SWORD,
"Kachina": WeaponType.POLEARM,
"Kaedehara Kazuha": WeaponType.SWORD,
"Kaeya": WeaponType.SWORD,
"Kamisato Ayaka": WeaponType.SWORD,
"Kamisato Ayato": WeaponType.SWORD,
"Kaveh": WeaponType.CLAYMORE,
"Kinich": WeaponType.CLAYMORE,
"Kirara": WeaponType.SWORD,
"Klee": WeaponType.CATALYST,
"Kujou Sara": WeaponType.BOW,
"Kuki Shinobu": WeaponType.SWORD,
"Lan Yan": WeaponType.CATALYST,
"Layla": WeaponType.SWORD,
"Lisa": WeaponType.CATALYST,
"Lynette": WeaponType.SWORD,
"Lyney": WeaponType.BOW,
"Mavuika": WeaponType.CLAYMORE,
"Mika": WeaponType.POLEARM,
"Mona": WeaponType.CATALYST,
"Mualani": WeaponType.CATALYST,
"Nahida": WeaponType.CATALYST,
"Navia": WeaponType.CLAYMORE,
"Neuvillette": WeaponType.CATALYST,
"Nilou": WeaponType.SWORD,
"Ningguang": WeaponType.CATALYST,
"Noelle": WeaponType.CLAYMORE,
"Ororon": WeaponType.BOW,
"Qiqi": WeaponType.SWORD,
"Raiden Shogun": WeaponType.POLEARM,
"Razor": WeaponType.CLAYMORE,
"Rosaria": WeaponType.POLEARM,
"Sangonomiya Kokomi": WeaponType.CATALYST,
"Sayu": WeaponType.CLAYMORE,
"Sethos": WeaponType.BOW,
"Shenhe": WeaponType.POLEARM,
"Shikanoin Heizou": WeaponType.CATALYST,
"Sigewinne": WeaponType.BOW,
"Sucrose": WeaponType.CATALYST,
"Tartaglia": WeaponType.BOW,
"Tighnari": WeaponType.BOW,
"Thoma": WeaponType.POLEARM,
"Venti": WeaponType.BOW,
"Wanderer": WeaponType.CATALYST,
"Wriothesley": WeaponType.CATALYST,
"Xiangling": WeaponType.POLEARM,
"Xianyun": WeaponType.CATALYST,
"Xiao": WeaponType.POLEARM,
"Xilonen": WeaponType.SWORD,
"Xingqiu": WeaponType.SWORD,
"Xinyan": WeaponType.CLAYMORE,
"Yae Miko": WeaponType.CATALYST,
"Yanfei": WeaponType.CATALYST,
"Yaoyao": WeaponType.POLEARM,
"Yelan": WeaponType.BOW,
"Yoimiya": WeaponType.BOW,
"Yumemizuki Mizuki": WeaponType.CATALYST,
"Yun Jin": WeaponType.POLEARM,
"Zhongli": WeaponType.POLEARM,
}


CHARACTERS_REGION = {
        "Lan Yan": Region.LIYUE,
    "Albedo": Region.MONDSTADT,
    "Alhaitham": Region.SUMERU,
    "Amber": Region.MONDSTADT,
    "Arataki Itto": Region.INAZUMA,
    "Arlecchino": Region.FONTAINE,
    "Baizhu": Region.LIYUE,
    "Barbara": Region.MONDSTADT,
    "Beidou": Region.LIYUE,
    "Bennett": Region.MONDSTADT,
    "Candace": Region.SUMERU,
    "Charlotte": Region.FONTAINE,
    "Chasca": Region.NATLAN,
    "Chevreuse": Region.FONTAINE,
    "Chiori": Region.FONTAINE,
    "Chongyun": Region.LIYUE,
    "Citlali": Region.NATLAN,
    "Clorinde": Region.FONTAINE,
    "Collei": Region.SUMERU,
    "Cyno": Region.SUMERU,
    "Dehya": Region.SUMERU,
    "Diluc": Region.MONDSTADT,
    "Diona": Region.MONDSTADT,
    "Dori": Region.SUMERU,
    "Emilie": Region.FONTAINE,
    "Eula": Region.MONDSTADT,
    "Faruzan": Region.SUMERU,
    "Fischl": Region.MONDSTADT,
    "Freminet": Region.FONTAINE,
    "Furina": Region.FONTAINE,
    "Gaming": Region.LIYUE,
    "Ganyu": Region.LIYUE,
    "Gorou": Region.INAZUMA,
    "Hu Tao": Region.LIYUE,
    "Jean": Region.MONDSTADT,
    "Kachina": Region.NATLAN,
    "Kaedehara Kazuha": Region.INAZUMA,
    "Kaeya": Region.MONDSTADT,
    "Kamisato Ayaka": Region.INAZUMA,
    "Kamisato Ayato": Region.INAZUMA,
    "Kaveh": Region.SUMERU,
    "Keqing": Region.LIYUE,
    "Kinich": Region.NATLAN,
    "Kirara": Region.INAZUMA,
    "Klee": Region.MONDSTADT,
    "Kujou Sara": Region.INAZUMA,
    "Kuki Shinobu": Region.INAZUMA,
    "Layla": Region.SUMERU,
    "Lisa": Region.MONDSTADT,
    "Lynette": Region.FONTAINE,
    "Lyney": Region.FONTAINE,
    "Mika": Region.MONDSTADT,
    "Mona": Region.MONDSTADT,
    "Mualani": Region.NATLAN,
    "Nahida": Region.SUMERU,
    "Navia": Region.FONTAINE,
    "Neuvillette": Region.FONTAINE,
    "Nilou": Region.SUMERU,
    "Ningguang": Region.LIYUE,
    "Noelle": Region.MONDSTADT,
    "Ororon": Region.NATLAN,
    "Qiqi": Region.LIYUE,
    "Raiden Shogun": Region.INAZUMA,
    "Razor": Region.MONDSTADT,
    "Rosaria": Region.MONDSTADT,
    "Sangonomiya Kokomi": Region.INAZUMA,
    "Sayu": Region.INAZUMA,
    "Sethos": Region.SUMERU,
    "Shenhe": Region.LIYUE,
    "Shikanoin Heizou": Region.INAZUMA,
    "Sigewinne": Region.FONTAINE,
    "Sucrose": Region.MONDSTADT,
    #"Tartaglia": Region.SNEZHNAYA,
    "Thoma": Region.INAZUMA,
    "Tighnari": Region.SUMERU,
    "Venti": Region.MONDSTADT,
    "Wanderer": Region.SUMERU,
    "Wriothesley": Region.FONTAINE,
    "Xiangling": Region.LIYUE,
    "Xianyun": Region.LIYUE,
    "Xiao": Region.LIYUE,
    "Xilonen": Region.NATLAN,
    "Xingqiu": Region.LIYUE,
    "Xinyan": Region.LIYUE,
    "Yae Miko": Region.INAZUMA,
    "Yanfei": Region.LIYUE,
    "Yaoyao": Region.SUMERU,
    "Yelan": Region.LIYUE,
    "Yoimiya": Region.INAZUMA,
    "Yun Jin": Region.LIYUE,
    "Zhongli": Region.LIYUE,
}


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
))

def bag(iterable):
    b = {}
    for (k, v) in iterable:
        if k not in b:
            b[k] = []
        b[k].append(v)
    return b

# TODO: turn into table
got = set((c.weapon, c.element) for c in CHARACTERS if not c.benched)

for element in Element:
    for weapon in WeaponType:
        if (weapon, element) in got:
            continue
        print(f"{element} {weapon}:", ', '.join(c.name for c in CHARACTERS if c.benched and c.weapon == weapon and c.element == element))

if __name__ == "__main__":
    main()
