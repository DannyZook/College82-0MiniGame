from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"
DEGREES = ["Undergraduate", "Master's", "PhD"]


def load_json(filename: str) -> dict[str, Any]:
    with (DATA_DIR / filename).open("r", encoding="utf-8") as handle:
        return json.load(handle)


MAJORS = load_json("majors.json")
UNIVERSITIES = load_json("universities.json")
SYNERGIES = load_json("synergies.json")

# Strength aliases let a school strength apply to related majors without a giant matrix.
CLUSTER_ALIASES = {
    "technology": {"technology", "engineering", "science"},
    "engineering": {"engineering", "technology", "science"},
    "science": {"science", "health", "marine_science", "environment"},
    "business": {"business", "finance", "entrepreneurship", "supply_chain"},
    "media": {"media", "communications", "journalism", "arts"},
    "arts": {"arts", "film", "music", "design"},
    "design": {"design", "architecture", "arts", "technology"},
    "public_affairs": {"public_affairs", "international_relations", "leadership"},
    "social_science": {"social_science", "public_affairs", "humanities"},
    "humanities": {"humanities", "archaeology", "arts"},
    "hospitality": {"hospitality", "business", "tourism"},
    "sports": {"sports", "business", "communications"},
    "agriculture": {"agriculture", "environment", "science"},
    "education": {"education", "social_science", "public_affairs"},
}

CAREER_BANDS = [
    (0, "Salaried Professional", "$70,000–$130,000"),
    (192, "High-Income Professional", "$180,000–$500,000"),
    (211, "Corporate Leader", "$1–$4 million"),
    (226, "Small-Business Owner", "$3–$12 million"),
    (239, "Startup Founder", "$8–$30 million"),
    (251, "Millionaire", "$15–$60 million"),
    (265, "Multimillionaire", "$60–$250 million"),
    (279, "Centimillionaire", "$250–$900 million"),
    (291, "Billionaire", "$1.1–$4.5 billion"),
]

CAMPUS_ARCHETYPES = {
    "Academic Weapon": "You treated office hours as a competitive sport and became the professor everyone trusted.",
    "Fraternity/Sorority President": "You ran the social calendar, managed personalities, and built a network before graduation.",
    "Football Captain": "You became the face of school spirit and learned to lead with everyone watching.",
    "Student-Body President": "You mastered campus politics, public speaking, and getting committees to agree.",
    "Student Founder": "You were testing business ideas while everyone else was still choosing electives.",
    "Research Prodigy": "You found your way into serious research early and became known for unusually ambitious work.",
    "Campus Celebrity": "Students recognized you everywhere and every major event somehow involved you.",
    "Party Legend": "Your social calendar was legendary, although your academic calendar occasionally suffered.",
    "Quiet Genius": "You stayed mostly out of the spotlight and repeatedly surprised people with what you built.",
    "Club Empire Builder": "You joined one organization, took it over, and somehow finished college running five of them.",
    "Resident Hall Mayor": "You knew everyone, solved every dispute, and became the unofficial authority of campus life.",
    "Creative Star": "Your projects, performances, or designs made you one of the most recognizable students in your program.",
}

CAREER_STYLES = [
    "Climbed the corporate ladder",
    "Built a startup with classmates",
    "Commercialized graduate research",
    "Created a regional business empire",
    "Became a specialist consultant",
    "Turned a creative project into a company",
    "Entered public service before moving into industry",
    "Built and sold two companies",
    "Took over a struggling organization and transformed it",
    "Became an investor after an operating career",
]

TWISTS = [
    "Your first company failed, but the second one became your breakthrough.",
    "You met your eventual cofounder during graduate school.",
    "You sold too early and watched the company become far larger without you.",
    "You became wealthy without becoming publicly famous.",
    "A professor introduced you to the person who changed your career.",
    "You returned to your undergraduate university as a major donor and guest lecturer.",
    "A campus side project unexpectedly became your main career.",
    "You chose control over rapid growth and built the company slowly.",
    "Your strongest advantage was not prestige; it was becoming indispensable wherever you went.",
    "You nearly abandoned your field before finding an unexpected commercial application for it.",
]


def deterministic_rng(roster: list[dict[str, Any]], salt: str = "") -> random.Random:
    raw = "|".join(f"{x['degree']}:{x['major']}:{x['university']}" for x in roster) + salt
    seed = int(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16], 16)
    return random.Random(seed)


def program_fit(university: str, major: str) -> float:
    school = UNIVERSITIES[university]
    info = MAJORS[major]
    cluster = info["cluster"]
    strengths = set(school["strengths"])
    related = CLUSTER_ALIASES.get(cluster, {cluster})

    if cluster in strengths:
        fit = 96
    elif strengths.intersection(related):
        fit = 85
    else:
        # Research and entrepreneurship can still make an unlisted program useful.
        fit = 56 + school["research"] * 0.12 + school["entrepreneurship"] * 0.08
    return min(round(fit, 1), 99)


def degree_fit(university: str, major: str, degree: str) -> float:
    school = UNIVERSITIES[university]
    major_info = MAJORS[major]
    if degree == "Undergraduate":
        value = 0.42 * school["opportunity"] + 0.25 * school["campus_life"] + 0.18 * school["network"] + 0.15 * school["cost_efficiency"]
    elif degree == "Master's":
        value = 0.34 * school["network"] + 0.27 * school["entrepreneurship"] + 0.22 * school["graduate_strength"] + 0.17 * major_info["career_utility"]
    else:
        value = 0.46 * school["research"] + 0.32 * school["graduate_strength"] + 0.22 * major_info["research_intensity"]
    return round(min(value, 100), 1)


def score_credential(university: str, major: str, degree: str) -> dict[str, float]:
    school = UNIVERSITIES[university]
    major_info = MAJORS[major]
    program = program_fit(university, major)
    degree_value = degree_fit(university, major, degree)

    # Prestige is intentionally only 6% of the credential score.
    breakdown = {
        "Program fit": program * 0.38,
        "Degree-level fit": degree_value * 0.22,
        "Career applicability": major_info["career_utility"] * 0.14,
        "Opportunity access": school["opportunity"] * 0.10,
        "Network": school["network"] * 0.10,
        "Prestige": school["prestige"] * 0.06,
    }
    total = round(sum(breakdown.values()), 1)
    return {"total": total, **{key: round(value, 1) for key, value in breakdown.items()}}


def synergy_bonus(roster: list[dict[str, Any]]) -> tuple[int, list[str]]:
    clusters = [MAJORS[item["major"]]["cluster"] for item in roster]
    total = 0
    notes: list[str] = []
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            key = "+".join(sorted((clusters[i], clusters[j])))
            bonus = int(SYNERGIES.get(key, 0))
            if bonus:
                total += bonus
                notes.append(f"{roster[i]['major']} + {roster[j]['major']} (+{bonus})")
    if len(set(clusters)) == 3:
        total += 2
        notes.append("Interdisciplinary range (+2)")
    return total, notes


def evaluate_roster(roster: list[dict[str, Any]]) -> dict[str, Any]:
    base = round(sum(item["score"]["total"] for item in roster), 1)
    synergy, synergy_notes = synergy_bonus(roster)
    rng = deterministic_rng(roster, "career")
    luck = rng.randint(-3, 5)
    total = round(base + synergy + luck)

    career_title, wealth = CAREER_BANDS[0][1], CAREER_BANDS[0][2]
    for threshold, title, range_text in CAREER_BANDS:
        if total >= threshold:
            career_title, wealth = title, range_text

    industries: list[str] = []
    for item in roster:
        industries.extend(MAJORS[item["major"]]["industries"])
    industry = max(set(industries), key=lambda x: (industries.count(x), x))

    founder_average = sum(MAJORS[item["major"]]["founder_potential"] for item in roster) / 3
    if founder_average > 82 and total >= 235:
        career_style = "Built a startup with classmates"
    elif roster[2]["score"]["Degree-level fit"] > 20 and MAJORS[roster[2]["major"]]["research_intensity"] > 80:
        career_style = "Commercialized graduate research"
    else:
        career_style = rng.choice(CAREER_STYLES)

    return {
        "base_score": base,
        "synergy_bonus": synergy,
        "synergy_notes": synergy_notes,
        "luck": luck,
        "total_score": total,
        "career_title": career_title,
        "wealth": wealth,
        "industry": industry,
        "career_style": career_style,
        "twist": rng.choice(TWISTS),
    }


def campus_identity(roster: list[dict[str, Any]]) -> tuple[str, str]:
    undergrad = roster[0]
    school = UNIVERSITIES[undergrad["university"]]
    major = MAJORS[undergrad["major"]]
    scores = {
        "Academic Weapon": school["research"] + major["research_intensity"] * 0.8,
        "Fraternity/Sorority President": school["campus_life"] + school["network"] * 0.7 + school["opportunity"] * 0.6,
        "Football Captain": school["athletics"] * 1.5 + school["opportunity"] * 0.5,
        "Student-Body President": school["opportunity"] * 1.4 + school["network"] * 0.7,
        "Student Founder": school["entrepreneurship"] * 1.2 + major["founder_potential"],
        "Research Prodigy": school["research"] * 1.25 + major["research_intensity"],
        "Campus Celebrity": school["campus_life"] * 1.15 + school["athletics"] * 0.55 + school["network"] * 0.5,
        "Party Legend": school["campus_life"] * 1.5 + school["athletics"] * 0.35 - major["research_intensity"] * 0.15,
        "Quiet Genius": school["research"] + major["research_intensity"] + (100 - school["campus_life"]) * 0.5,
        "Club Empire Builder": school["opportunity"] * 1.35 + school["campus_life"] * 0.65,
        "Resident Hall Mayor": school["opportunity"] + school["campus_life"] + school["network"] * 0.45,
        "Creative Star": (100 if major["cluster"] in {"arts", "design", "media"} else 45) + school["campus_life"] * 0.8,
    }
    # Deterministic jitter prevents the same high-opportunity school from always yielding one identity.
    rng = deterministic_rng(roster, "campus")
    adjusted = {key: value + rng.uniform(-9, 9) for key, value in scores.items()}
    identity = max(adjusted, key=adjusted.get)
    return identity, CAMPUS_ARCHETYPES[identity]


def fallback_story(roster: list[dict[str, Any]], result: dict[str, Any], identity: str) -> str:
    undergrad, masters, phd = roster
    return (
        f"You entered {undergrad['university']} as a {undergrad['major']} major and quickly became known as a {identity.lower()}. "
        f"A master's in {masters['major']} from {masters['university']} gave you the professional network to move into {result['industry'].lower()}. "
        f"Your PhD work in {phd['major']} at {phd['university']} supplied the final technical or research advantage. "
        f"You {result['career_style'].lower()}, eventually reaching the level of {result['career_title'].lower()} with an estimated net worth of {result['wealth']}. "
        f"{result['twist']}"
    )
