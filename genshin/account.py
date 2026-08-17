import typing
from datetime import datetime, timedelta
import enum
import collections
import math

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
            weapons_count=len(FIVE_STAR_WEAPONS),
            elements=''.join(generate_elements()),
            weapons=''.join(generate_weapons()),
            regions=''.join(generate_regions()),
            versions=''.join(generate_versions()),
            five_star_vs_four_star=''.join(generate_five_star_vs_four_star()),
        ), file=f)

def write_characters_page():
    characters = '\n'.join(f"""<img class="icon" src="{c.icon_url}" alt={c.name} title="{c.name}" data-version="{'.'.join(map(str, c.release))}" data-benched="{c.benched}" data-element="{c.element.lower()}">"""
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

        let matched = 0;

        for (const icon of document.querySelectorAll(".icon")) {
            const hide = icon.dataset.version < min || max < icon.dataset.version
                || !document.getElementById(icon.dataset.element).checked;

            if (hide) {
                icon.classList.add("hide");
            } else {
                ++matched;
                icon.classList.remove("hide");
            }
            if (icon.dataset.benched.toLowerCase() == "true") {
                icon.classList.add('benched');
            }
        }

        document.getElementById('matched_benched').innerText = matched;
    }

    min_version.addEventListener("input", onInput);
    max_version.addEventListener("input", onInput);

    for (const el of document.querySelectorAll('input[name="element"]')) {
        el.addEventListener('input', onInput);
    }


    document.getElementById('enable_all').addEventListener('click', () => {
        for (const el of document.querySelectorAll('input[name="element"]')) {
            el.checked = true;
        }
        onInput({ target: null });
    });
    document.getElementById('disable_all').addEventListener('click', () => {
        for (const el of document.querySelectorAll('input[name="element"]')) {
            el.checked = false;
        }
        onInput({ target: null });
    });

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
                <button id="enable_all">Enable all</button>
                <button id="disable_all">Disable all</button>
                <input type="checkbox" checked id="anemo" name="element"><label for="anemo">Anemo</label>
                <input type="checkbox" checked id="cryo" name="element"><label for="cryo">Cryo</label>
                <input type="checkbox" checked id="dendro" name="element"><label for="dendro">Dendro</label>
                <input type="checkbox" checked id="electro" name="element"><label for="electro">Electro</label>
                <input type="checkbox" checked id="geo" name="element"><label for="geo">Geo</label>
                <input type="checkbox" checked id="hydro" name="element"><label for="hydro">Hydro</label>
                <input type="checkbox" checked id="pyro" name="element"><label for="pyro">Pyro</label>
            </div>
            <p>Characters matching criteria: <span id="matched_benched"></span></p>
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
            characters="\n".join(f'<div class="{c.classes}"><img style="width: 100%" src="{c.icon_url}" alt="{c.name}" data-date="{c.date.date()}" title="Got {c.name} on {c.date.date()}"></div>' for c in group)
        )
        for group_name, group in grouped.items()
    )

    usage = 100 * sum(1 for g in grouped.values() for c in g if not c.benched) / sum(len(g) for g in grouped)

    avg_wish_date_nb = datetime.fromtimestamp(sum(c.date.timestamp() for c in CHARACTERS if not c.benched) / sum(1 for c in CHARACTERS if not c.benched))
    avg_wish_date = datetime.fromtimestamp(sum(c.date.timestamp() for c in CHARACTERS) / len(CHARACTERS))
    avg_wish_version_nb = next(v for v in reversed(VERSIONS) if avg_wish_date_nb > v.start)
    avg_wish_version = next(v for v in reversed(VERSIONS) if avg_wish_date > v.start)

    time_between_chars = [(curr.date - next.date).days for (curr, next) in zip(CHARACTERS, CHARACTERS[1:])]
    avg_time_between_chars = math.floor(sum(time_between_chars) / len(CHARACTERS))
    max_time_between_chars = max(time_between_chars)


    return f"""
        <h2>Characters ({usage:.0f}% used)</h2>
        <p>Average wish date for my used characters is <time datetime="{avg_wish_date_nb}">{avg_wish_date_nb.date()}</time> which happened in version {avg_wish_version_nb}.
        For all characters it's <time datetime="{avg_wish_date}">{avg_wish_date.date()}</a> (version {avg_wish_version}).
        On average I get new character every {avg_time_between_chars} days (max {max_time_between_chars} days).</p>
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

        yield '<div style="display: grid; grid-template-columns: repeat(7, 1fr); grid-template-rows: auto auto; justify-content: center; text-align: center">'
        for region in REGION_ORDER:
            yield f'<div>'
            for character in sorted(CHARACTERS, key=lambda c: c.name):
                if character.region == region and (i == 1 or not character.benched):
                    yield f'<img style="width: 33.3%"src="{character.icon_url}" title="{character.name}">\n'
            yield f'</div>'
        yield '</div>'
        yield f'</details>'

        yield '<div style="display: grid; grid-template-columns: repeat(7, 1fr); grid-template-rows: 4rem auto auto; justify-content: center; text-align: center; margin-bottom: 1rem">'
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
    NOD_KRAI = "Nod-Krai"

    @property
    def icon_url(self):
        return f"{str(self.lower())}.webp"

REGION_ORDER = [Region.MONDSTADT, Region.LIYUE, Region.INAZUMA, Region.SUMERU, Region.FONTAINE, Region.NATLAN, Region.NOD_KRAI]

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
                 constellation: int = 0,
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
        self.constellation = constellation

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
			Currently I have {characters_count} characters and {weapons_count} 5 star weapons.
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
"Zhongli": WeaponType.POLEARM,
    "Zhongli": Region.LIYUE,
    "Zhongli": Element.GEO,
"Yun Jin": WeaponType.POLEARM,
    "Yun Jin": Region.LIYUE,
    "Yun Jin": Element.GEO,
"Yumemizuki Mizuki": WeaponType.CATALYST,
    "Yumemizuki Mizuki",
"Yoimiya": WeaponType.BOW,
    "Yoimiya": Region.INAZUMA,
    "Yoimiya": Element.PYRO,
"Yelan": WeaponType.BOW,
    "Yelan": Region.LIYUE,
    "Yelan": Element.HYDRO,
"Yaoyao": WeaponType.POLEARM,
    "Yaoyao": Region.SUMERU,
    "Yaoyao": Element.DENDRO,
"Yanfei": WeaponType.CATALYST,
    "Yanfei": Region.LIYUE,
    "Yanfei": Element.PYRO,
"Yae Miko": WeaponType.CATALYST,
    "Yae Miko": Region.INAZUMA,
    "Yae Miko": Element.ELECTRO,
"Xinyan": WeaponType.CLAYMORE,
    "Xinyan": Region.LIYUE,
    "Xinyan": Element.PYRO,
"Xingqiu": WeaponType.SWORD,
    "Xingqiu": Region.LIYUE,
    "Xingqiu": Element.HYDRO,
"Xilonen": WeaponType.SWORD,
    "Xilonen": Region.NATLAN,
    "Xilonen": Element.GEO,
"Xiao": WeaponType.POLEARM,
    "Xiao": Region.LIYUE,
    "Xiao": Element.ANEMO,
"Xianyun": WeaponType.CATALYST,
    "Xianyun": Region.LIYUE,
    "Xianyun": Element.ANEMO,
"Xiangling": WeaponType.POLEARM,
    "Xiangling": Region.LIYUE,
    "Xiangling": Element.PYRO,
"Wriothesley": WeaponType.CATALYST,
    "Wriothesley": Region.FONTAINE,
    "Wriothesley": Element.CRYO,
    Wish("6.7", "Yae Miko", "2026-07-01", benched=False),
    Wish("6.7", "Sandrone", "2026-07-01", benched=False),
    Wish("6.6", "Prune", "2026-05-31"),
    Wish("6.6", "Nicole", "2026-06-04", benched=False),
    Wish("6.5", "Linnea", "2026-04-08", benched=False, five_star=True),
    Wish("6.5", "Jahoda", "2026-05-01", benched=False),
    Wish("6.5", "Illuga", "2026-04-15"),
    Wish("6.3", "Columbina", "2026-02-01", benched=False, five_star=True),
    Wish("6.2", "Durin", "2025-12-03", benched=False, five_star=True),
    Wish("6.1", "Nefer", "2025-10-24", benched=False, five_star=True),
    Wish("6.0", "Lauma", "2025-09-14", benched=False, five_star=True),
    Wish("6.0", "Aino", "2025-09-10", benched=False),
    Wish("5.7", "Emilie", "2025-07-14", benched=False, five_star=True),
    Wish("5.6", "Escoffier", "2025-05-07", benched=False, five_star=True),
    Wish("5.5", "Iansan", "2025-03-26", benched=False),
    Wish("5.3", "Lan Yan", "2025-01-21", constellation=6, benched=False),
    Wish("5.3", 'Citlali', '2025-01-01', benched=False, favourite=True, five_star=True),
    Wish("5.2", 'Ororon', '2024-11-21', benched=False, favourite=True, constellation=3),
    Wish("5.2", 'Chasca', '2024-11-21', benched=False, five_star=True, constellation=2),
    Wish("5.1", 'Xilonen', '2024-10-21', benched=False, five_star=True, favourite=True),
    Wish("5.0", 'Kinich', '2024-09-27', five_star=True, benched=False),
    Wish("5.0", 'Kachina', '2024-08-28', constellation=5),
    Wish("4.7", 'Sethos', '2024-06-05', constellation=2),
    Wish("4.7", "Clorinde", "2025-02-10", favourite=True, five_star=True, benched=False, constellation=2),
    Wish("4.6", "Arlecchino", "2024-05-02", pity=76, benched=False, favourite=True, five_star=True),
    Wish("4.5", "Chiori", "2024-03-22", pity=80, benched=False, favourite=True, five_star=True, constellation=1),
    Wish("4.4", "Xianyun", "2024-02-18", pity=75, benched=False, five_star=True, favourite=True),
    Wish("4.4", "Gaming", "2024-02-05", favourite=True, constellation=6),
    Wish("4.3", "Navia", "2023-12-20", pity=58, benched=False, favourite=True, five_star=True),
    Wish("4.3", "Chevreuse", "2024-01-13", benched=False, constellation=6),
    Wish("4.2", "Furina", "2023-11-08", pity=78, benched=False, favourite=True, five_star=True, constellation=1),
    Wish("4.2", "Charlotte", "2023-11-08"),
    Wish("4.0", "Lyney", "2023-09-03", pity=82, benched=False, five_star=True),
    Wish("4.0", "Lynette", "2023-08-16", favourite=True, constellation=6),
    Wish("4.0", "Freminet", "2023-09-12", constellation=4),
    Wish("3.7", "Kirara", "2023-05-24", favourite=True, constellation=4),
    Wish("3.6", "Kaveh", "2023-05-05", constellation=1),
    Wish("3.5", "Mika", "2023-07-08", constellation=2),
    Wish("3.5", "Dehya", "2023-06-26", five_star=True, constellation=3, benched=False),
    Wish("3.4", "Yaoyao", "2023-02-03", favourite=True, constellation=6),
    Wish("3.3", "Wanderer", "2022-12-10", five_star=True),
    Wish("3.3", "Faruzan", "2022-12-08", benched=False, constellation=6),
    Wish("3.2", "Nahida", "2023-04-15", favourite=True, five_star=True),
    Wish("3.2", "Layla", "2023-03-02", favourite=True, constellation=3, benched=False),
    Wish("3.1", 'Nilou', '2024-07-20', five_star=True),
    Wish("3.1", "Cyno", "2023-03-19", five_star=True),
    Wish("3.1", "Candace", "2023-12-20", favourite=True, constellation=4),
    Wish("3.0", "Tighnari", "2022-11-04", five_star=True, constellation=2),
    Wish("3.0", "Dori", "2022-09-09", constellation=5),
    Wish("3.0", "Collei", "2022-08-24", constellation=6),
    Wish("2.8", "Shikanoin Heizou", "2023-06-17", constellation=1),
    Wish("2.7", "Yelan", "2022-06-05", benched=False, favourite=True, five_star=True),
    Wish("2.7", "Kuki Shinobu", "2022-09-28", benched=False, favourite=True, constellation=6),
    Wish("2.6", "Kamisato Ayato", "2022-04-09", benched=False, five_star=True),
    Wish("2.4", "Yun Jin", "2022-04-09", constellation=6, benched=False),
    Wish("2.3", "Gorou", "2022-12-10", constellation=3),
    Wish("2.3", "Arataki Itto", "2022-06-22", favourite=True, five_star=True, constellation=1),
    Wish("2.2", "Thoma", "2022-02-22", constellation=6),
    Wish("2.1", "Sangonomiya Kokomi", "2023-07-26", pity=43, benched=False, favourite=True, five_star=True),
    Wish("2.1", "Raiden Shogun", "2023-01-07", five_star=True),
    Wish("2.1", "Kujou Sara", "2022-04-01", constellation=5),
    Wish("2.0", "Sayu", "2022-04-21", favourite=True, constellation=5),
    Wish("2.0", "Kamisato Ayaka", "2022-05-20", benched=False, five_star=True),
    Wish("1.6", "Kaedehara Kazuha", "2023-06-26", pity=45, benched=False, five_star=True),
    Wish("1.5", "Yanfei", "2022-05-31", constellation=2),
    Wish("1.4", "Rosaria", "2022-05-08", constellation=6, benched=False),
    Wish("1.3", "Xiao", "2023-02-03", benched=False, five_star=True),
    Wish("1.2", "Ganyu", "2022-09-09", five_star=True),
    Wish("1.1", "Zhongli", "2022-08-24", five_star=True),
    Wish("1.1", "Xinyan", "2022-06-13", constellation=6),
    Wish("1.1", "Diona", "2022-08-24", constellation=6),
    Wish("1.0", "Xingqiu", "2022-04-17", benched=False, constellation=6),
    Wish("1.0", "Xiangling", "2022-02-05", constellation=6),
    Wish("1.0", "Venti", "2022-10-14", five_star=True),
    Wish("1.0", "Sucrose", "2022-03-31", benched=False, favourite=True, constellation=1),
    Wish("1.0", "Razor", "2022-04-24", constellation=6),
    Wish("1.0", "Qiqi", "2022-04-21", favourite=True, five_star=True, constellation=3),
    Wish("1.0", "Noelle", "2022-02-03", constellation=6),
    Wish("1.0", "Ningguang", "2022-05-21", constellation=6),
    Wish("1.0", "Mona", "2023-02-03", five_star=True),
    Wish("1.0", "Lisa", "2022-02-03", constellation=3),
    Wish("1.0", "Keqing", "2023-10-01", five_star=True, constellation=1),
    Wish("1.0", "Kaeya", "2022-02-03", constellation=1),
    Wish("1.0", "Jean", "2022-05-13", five_star=True, constellation=1),
    Wish("1.0", "Fischl", "2022-08-02", benched=False, favourite=True, constellation=5),
    Wish("1.0", "Chongyun", "2022-11-02", constellation=3),
    Wish("1.0", "Bennett", "2022-05-08", benched=False, constellation=6),
    Wish("1.0", "Beidou", "2022-02-07", favourite=True, constellation=6),
    Wish("1.0", "Barbara", "2022-02-13", constellation=6),
    Wish("1.0", "Amber", "2022-02-03", constellation=4),
    Wish("0.0", "Vivid Notions", weapon=True, weapon_type=WeaponType.CATALYST),
    Wish("0.0", "Verdict", weapon=True, weapon_type=WeaponType.CLAYMORE),
    Wish("0.0", 'Uraku Misugiri', weapon=True, weapon_type=WeaponType.SWORD),
    Wish("0.0", "The First Great Magic", pity=3, weapon=True, weapon_type=WeaponType.BOW),
    Wish("0.0", "Symphonist of Scents", weapon=True, weapon_type=WeaponType.POLEARM),
    Wish("0.0", "Skyward Harp", weapon=True, weapon_type=WeaponType.BOW),
    Wish("0.0", "Reliquary of Truth", weapon=True, weapon_type=WeaponType.CATALYST),
    Wish("0.0", 'Primordial Jade Winged-Spear', weapon=True, weapon_type=WeaponType.POLEARM),
    Wish("0.0", 'Peak Patrol Song', weapon=True, weapon_type=WeaponType.SWORD),
    Wish("0.0", "Lumidouce Elegy", weapon=True, weapon_type=WeaponType.POLEARM),
    Wish("0.0", "Golden Frostbound Oath", weapon=True, weapon_type=WeaponType.BOW),
    Wish("0.0", "Crimson Moon's Semblance", pity=67, weapon=True, weapon_type=WeaponType.POLEARM),
    Wish("0.0", "Aquila Favonia", weapon=True, weapon_type=WeaponType.SWORD),
"Wanderer": WeaponType.CATALYST,
    "Wanderer": Region.SUMERU,
    "Wanderer": Element.ANEMO,
VERSIONS = sorted((
    Version(6, 6, "2026-05-20"),
    Version(6, 5, "2026-04-08"),
    Version(6, 4, "2026-02-25"),
    Version(6, 3, "2026-01-14"),
    Version(6, 2, "2025-12-03"),
    Version(6, 1, "2025-10-22"),
    Version(6, 0, "2025-09-10"),
    Version(5, 8, "2025-07-30"),
    Version(5, 7, "2025-06-18"),
    Version(5, 6, "2025-05-07"),
    Version(5, 5, "2025-03-26"),
    Version(5, 4, "2025-02-12"),
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
"Venti": WeaponType.BOW,
    "Venti": Region.MONDSTADT,
    "Venti": Element.ANEMO,
"Tighnari": WeaponType.BOW,
    "Tighnari": Region.SUMERU,
    "Tighnari": Element.DENDRO,
    "Tighnari",
"Thoma": WeaponType.POLEARM,
    "Thoma": Region.INAZUMA,
    "Thoma": Element.PYRO,
"Tartaglia": WeaponType.BOW,
    #"Tartaglia": Region.SNEZHNAYA,
    "Tartaglia": Element.HYDRO,
"Sucrose": WeaponType.CATALYST,
    "Sucrose": Region.MONDSTADT,
    "Sucrose": Element.ANEMO,
STANDARD_CHARACTERS = {
"Sigewinne": WeaponType.BOW,
    "Sigewinne": Region.FONTAINE,
    "Sigewinne": Element.HYDRO,
"Shikanoin Heizou": WeaponType.CATALYST,
    "Shikanoin Heizou": Region.INAZUMA,
    "Shikanoin Heizou": Element.ANEMO,
"Shenhe": WeaponType.POLEARM,
    "Shenhe": Region.LIYUE,
    "Shenhe": Element.CRYO,
"Sethos": WeaponType.BOW,
    "Sethos": Region.SUMERU,
    "Sethos": Element.ELECTRO,
        self.start = datetime.fromisoformat(start)
        self.minor = minor
        self.major = major
"Sayu": WeaponType.CLAYMORE,
    "Sayu": Region.INAZUMA,
    "Sayu": Element.ANEMO,
"Sangonomiya Kokomi": WeaponType.CATALYST,
    "Sangonomiya Kokomi": Region.INAZUMA,
    "Sangonomiya Kokomi": Element.HYDRO,
"Rosaria": WeaponType.POLEARM,
    "Rosaria": Region.MONDSTADT,
    "Rosaria": Element.CRYO,
        return (self.major, self.minor) == (self.major, self.minor)
        return (self.major, self.minor) < (other.major, other.minor)
        return (self.major, self.minor).__hash__()
        return f"{self.major}.{self.minor}"
"Razor": WeaponType.CLAYMORE,
    "Razor": Region.MONDSTADT,
    "Razor": Element.ELECTRO,
"Raiden Shogun": WeaponType.POLEARM,
    "Raiden Shogun": Region.INAZUMA,
    "Raiden Shogun": Element.ELECTRO,
"Qiqi": WeaponType.SWORD,
    "Qiqi": Region.LIYUE,
    "Qiqi": Element.CRYO,
    "Qiqi",
# Paste in console:
"Ororon": WeaponType.BOW,
    "Ororon": Region.NATLAN,
    "Ororon": Element.ELECTRO,
# on https://genshin-impact.fandom.com/wiki/Version
"Noelle": WeaponType.CLAYMORE,
    "Noelle": Region.MONDSTADT,
    "Noelle": Element.GEO,
"Ningguang": WeaponType.CATALYST,
    "Ningguang": Region.LIYUE,
    "Ningguang": Element.GEO,
"Nilou": WeaponType.SWORD,
    "Nilou": Region.SUMERU,
    "Nilou": Element.HYDRO,
"Neuvillette": WeaponType.CATALYST,
    "Neuvillette": Region.FONTAINE,
    "Neuvillette": Element.HYDRO,
        "Nefer": WeaponType.CATALYST,
        "Nefer": Region.NOD_KRAI,
        "Nefer": Element.DENDRO,
"Navia": WeaponType.CLAYMORE,
    "Navia": Region.FONTAINE,
    "Navia": Element.GEO,
"Nahida": WeaponType.CATALYST,
    "Nahida": Region.SUMERU,
    "Nahida": Element.DENDRO,
"Mualani": WeaponType.CATALYST,
    "Mualani": Region.NATLAN,
    "Mualani": Element.HYDRO,
"Mona": WeaponType.CATALYST,
    "Mona": Region.MONDSTADT,
    "Mona": Element.HYDRO,
"Mika": WeaponType.POLEARM,
    "Mika": Region.MONDSTADT,
    "Mika": Element.CRYO,
"Mavuika": WeaponType.CLAYMORE,
"Lyney": WeaponType.BOW,
    "Lyney": Region.FONTAINE,
    "Lyney": Element.PYRO,
"Lynette": WeaponType.SWORD,
    "Lynette": Region.FONTAINE,
    "Lynette": Element.ANEMO,
"Lisa": WeaponType.CATALYST,
    "Lisa": Region.MONDSTADT,
    "Lisa": Element.ELECTRO,
        "Linnea": WeaponType.BOW,
        "Linnea": Region.NOD_KRAI,
        "Linnea": Element.GEO,
"Layla": WeaponType.SWORD,
    "Layla": Region.SUMERU,
    "Layla": Element.CRYO,
        "Lauma": WeaponType.CATALYST,
        "Lauma": Region.NOD_KRAI,
        "Lauma": Element.DENDRO,
"Lan Yan": WeaponType.CATALYST,
        "Lan Yan": Region.LIYUE,
    "Lan Yan": Element.ANEMO,
"Kuki Shinobu": WeaponType.SWORD,
    "Kuki Shinobu": Region.INAZUMA,
    "Kuki Shinobu": Element.ELECTRO,
"Kujou Sara": WeaponType.BOW,
    "Kujou Sara": Region.INAZUMA,
    "Kujou Sara": Element.ELECTRO,
"Klee": WeaponType.CATALYST,
    "Klee": Region.MONDSTADT,
    "Klee": Element.PYRO,
"Kirara": WeaponType.SWORD,
    "Kirara": Region.INAZUMA,
    "Kirara": Element.DENDRO,
"Kinich": WeaponType.CLAYMORE,
    "Kinich": Region.NATLAN,
    "Kinich": Element.DENDRO,
], key=lambda x: (x.date, x.name), reverse=True)
], key=lambda x: (WEAPON_ORDER.index(x.weapon_type), x.name))
"Keqing": WeaponType.SWORD,
    "Keqing": Region.LIYUE,
    "Keqing": Element.ELECTRO,
    "Keqing",
"Kaveh": WeaponType.CLAYMORE,
    "Kaveh": Region.SUMERU,
    "Kaveh": Element.DENDRO,
"Kamisato Ayato": WeaponType.SWORD,
    "Kamisato Ayato": Region.INAZUMA,
    "Kamisato Ayato": Element.HYDRO,
"Kamisato Ayaka": WeaponType.SWORD,
    "Kamisato Ayaka": Region.INAZUMA,
    "Kamisato Ayaka": Element.CRYO,
"Kaeya": WeaponType.SWORD,
    "Kaeya": Region.MONDSTADT,
    "Kaeya": Element.CRYO,
"Kaedehara Kazuha": WeaponType.SWORD,
    "Kaedehara Kazuha": Region.INAZUMA,
    "Kaedehara Kazuha": Element.ANEMO,
"Kachina": WeaponType.POLEARM,
    "Kachina": Region.NATLAN,
    "Kachina": Element.GEO,
"Jean": WeaponType.SWORD,
    "Jean": Region.MONDSTADT,
    "Jean": Element.ANEMO,
    "Jean",
        "Jahoda": WeaponType.BOW,
        "Jahoda": Region.NOD_KRAI,
        "Jahoda": Element.ANEMO,
        "Illuga": WeaponType.POLEARM,
        "Illuga": Region.NOD_KRAI,
        "Illuga": Element.GEO,
"Iansan": WeaponType.POLEARM,
        "Iansan": Region.NATLAN,
    "Iansan": Element.ELECTRO,
"Hu Tao": WeaponType.POLEARM,
    "Hu Tao": Region.LIYUE,
    "Hu Tao": Element.PYRO,
"Gorou": WeaponType.BOW,
    "Gorou": Region.INAZUMA,
    "Gorou": Element.GEO,
"Ganyu": WeaponType.BOW,
    "Ganyu": Region.LIYUE,
    "Ganyu": Element.CRYO,
"Gaming": WeaponType.CLAYMORE,
    "Gaming": Region.LIYUE,
    "Gaming": Element.PYRO,
"Furina": WeaponType.SWORD,
    "Furina": Region.FONTAINE,
    "Furina": Element.HYDRO,
"Freminet": WeaponType.CLAYMORE,
    "Freminet": Region.FONTAINE,
    "Freminet": Element.CRYO,
FIVE_STAR_WEAPONS = sorted([
"Fischl": WeaponType.BOW,
    "Fischl": Region.MONDSTADT,
    "Fischl": Element.ELECTRO,
"Faruzan": WeaponType.BOW,
    "Faruzan": Region.SUMERU,
    "Faruzan": Element.ANEMO,
"Eula": WeaponType.CLAYMORE,
    "Eula": Region.MONDSTADT,
    "Eula": Element.CRYO,
"Escoffier": WeaponType.POLEARM,
        "Escoffier": Region.FONTAINE,
    "Escoffier": Element.CRYO,
"Emilie": WeaponType.POLEARM,
    "Emilie": Region.FONTAINE,
    "Emilie": Element.DENDRO,
        "Durin": WeaponType.SWORD,
        "Durin": Region.MONDSTADT,
        "Durin": Element.PYRO,
"Dori": WeaponType.CLAYMORE,
    "Dori": Region.SUMERU,
    "Dori": Element.ELECTRO,
# [...document.querySelectorAll('h3:has([id*="Version_"]) + table[data-index-number] tr:has([data-sort-value])')].map(x => `Version(${x.querySelector('td').textContent.trim().replace(".", ", ")}, "${x.querySelector('[data-sort-value]').dataset.sortValue}"),`).join('\n')
"Diona": WeaponType.BOW,
    "Diona": Region.MONDSTADT,
    "Diona": Element.CRYO,
"Diluc": WeaponType.CLAYMORE,
    "Diluc": Region.MONDSTADT,
    "Diluc": Element.PYRO,
"Dehya": WeaponType.CLAYMORE,
    "Dehya": Region.SUMERU,
    "Dehya": Element.PYRO,
    "Dehya",
    def __str__(self):
    def __lt__(self, other):
    def __init__(self, major: int, minor: int, start: str):
    def __hash__(self):
    def __eq__(self, other):
"Cyno": WeaponType.POLEARM,
    "Cyno": Region.SUMERU,
    "Cyno": Element.ELECTRO,
        "Columbina": WeaponType.CATALYST,
        "Columbina": Region.NOD_KRAI,
        "Columbina": Element.HYDRO,
"Collei": WeaponType.BOW,
    "Collei": Region.SUMERU,
    "Collei": Element.DENDRO,
"Clorinde": WeaponType.SWORD,
    "Clorinde": Region.FONTAINE,
    "Clorinde": Element.ELECTRO,
class Version:
"Citlali": WeaponType.CATALYST,
    "Citlali": Region.NATLAN,
    "Citlali": Element.CRYO,
"Chongyun": WeaponType.CLAYMORE,
    "Chongyun": Region.LIYUE,
    "Chongyun": Element.CRYO,
"Chiori": WeaponType.SWORD,
    "Chiori": Region.FONTAINE,
    "Chiori": Element.GEO,
"Chevreuse": WeaponType.POLEARM,
    "Chevreuse": Region.FONTAINE,
    "Chevreuse": Element.PYRO,
"Chasca": WeaponType.BOW,
    "Chasca": Region.NATLAN,
    "Chasca": Element.ANEMO,
"Charlotte": WeaponType.CATALYST,
    "Charlotte": Region.FONTAINE,
    "Charlotte": Element.CRYO,
CHARACTERS_WEAPON = {
CHARACTERS_REGION = {
CHARACTERS_ELEMENT = {
"Candace": WeaponType.POLEARM,
    "Candace": Region.SUMERU,
    "Candace": Element.HYDRO,
"Bennett": WeaponType.SWORD,
    "Bennett": Region.MONDSTADT,
    "Bennett": Element.PYRO,
"Beidou": WeaponType.CLAYMORE,
    "Beidou": Region.LIYUE,
    "Beidou": Element.ELECTRO,
"Barbara": WeaponType.CATALYST,
    "Barbara": Region.MONDSTADT,
    "Barbara": Element.HYDRO,
"Baizhu": WeaponType.CATALYST,
    "Baizhu": Region.LIYUE,
    "Baizhu": Element.DENDRO,
assert all(char.date is not None for char in CHARACTERS)
"Arlecchino": WeaponType.POLEARM,
    "Arlecchino": Region.FONTAINE,
    "Arlecchino": Element.PYRO,
"Arataki Itto": WeaponType.CLAYMORE,
    "Arataki Itto": Region.INAZUMA,
    "Arataki Itto": Element.GEO,
"Amber": WeaponType.BOW,
    "Amber": Region.MONDSTADT,
    "Amber": Element.PYRO,
"Aloy": WeaponType.BOW,
    "Aloy": Element.CRYO,
"Alhaitham": WeaponType.SWORD,
    "Alhaitham": Region.SUMERU,
    "Alhaitham": Element.DENDRO,
"Albedo": WeaponType.SWORD,
    "Albedo": Region.MONDSTADT,
    "Albedo": Element.GEO,
        "Aino": WeaponType.CLAYMORE,
        "Aino": Region.NOD_KRAI,
        "Aino": Element.HYDRO,
}
}
}
}



















))

# TODO: turn into table
print("Weapon and element combination that I don't use::")
got = set((c.weapon, c.element) for c in CHARACTERS if not c.benched)

for element in Element:
    for weapon in WeaponType:
        if (weapon, element) in got:
            continue
        print(f"{element} {weapon}:", ', '.join(c.name for c in CHARACTERS if c.benched and c.weapon == weapon and c.element == element))

print()
print(f"Avg constellation: {sum(c.constellation for c in CHARACTERS) / len(CHARACTERS):.2f}")
non_benched_4_stars = [c for c in CHARACTERS if not c.five_star and not c.benched]
print(f"Avg cons among all 4*: {sum(c.constellation for c in CHARACTERS if not c.benched) / sum(1 for c in CHARACTERS if not c.benched):.2f}")
print(f"Avg cons among non-benched 4*: {sum(c.constellation for c in non_benched_4_stars) / len(non_benched_4_stars):.2f}")

non_std_5_stars_with_cons = sum(1 for c in CHARACTERS if c.five_star and c.constellation > 0 and c.name not in STANDARD_CHARACTERS)
non_std_5_stars = sum(1 for c in CHARACTERS if c.five_star and c.name not in STANDARD_CHARACTERS)

print(f"Non-standard 5* with constellation: {non_std_5_stars_with_cons} of {non_std_5_stars} ({non_std_5_stars_with_cons / non_std_5_stars * 100:.2f}%)")
for c in sorted(CHARACTERS, key=lambda c: (6 - c.constellation, c.name)):
    if c.five_star and c.constellation > 0 and c.name not in STANDARD_CHARACTERS:
        print(f"- C{c.constellation} {c.name}")

non_std_5_stars_with_cons_nb = sum(1 for c in CHARACTERS if c.five_star and c.constellation > 0 and c.name not in STANDARD_CHARACTERS and not c.benched)
non_std_5_stars_nb = sum(1 for c in CHARACTERS if c.five_star and c.name not in STANDARD_CHARACTERS and not c.benched)
print(f"Non-standard non-benched 5* with constellation: {non_std_5_stars_with_cons_nb} of {non_std_5_stars_nb} ({non_std_5_stars_with_cons_nb / non_std_5_stars_nb * 100:.2f}%)")


def main2():
    pass

if __name__ == "__main__":
    main2()
