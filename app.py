import random
from dataclasses import dataclass
from typing import Dict, List

import streamlit as st

st.set_page_config(
    page_title="Campus Draft",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Data
# -----------------------------
DEGREES = ["Undergraduate", "Master's", "PhD"]

MAJORS = {
    "Business": {"business": 0.35, "entrepreneurship": 0.30, "network": 0.20, "prestige": 0.15},
    "Computer Science": {"technology": 0.40, "entrepreneurship": 0.25, "research": 0.20, "prestige": 0.15},
    "Engineering": {"technology": 0.30, "research": 0.30, "entrepreneurship": 0.20, "network": 0.20},
    "Psychology": {"research": 0.35, "academics": 0.25, "leadership": 0.20, "network": 0.20},
    "Archaeology": {"research": 0.40, "academics": 0.30, "leadership": 0.15, "network": 0.15},
    "Economics": {"business": 0.30, "academics": 0.25, "network": 0.25, "prestige": 0.20},
    "Biology": {"research": 0.40, "academics": 0.30, "technology": 0.15, "network": 0.15},
    "Communications": {"network": 0.35, "leadership": 0.30, "social": 0.20, "business": 0.15},
    "Political Science": {"leadership": 0.35, "network": 0.30, "academics": 0.20, "prestige": 0.15},
    "Sports Management": {"athletics": 0.35, "business": 0.25, "network": 0.25, "leadership": 0.15},
}

UNIVERSITIES: Dict[str, Dict[str, int]] = {
    "Stanford University": {"academics": 98, "business": 96, "technology": 99, "research": 97, "entrepreneurship": 100, "network": 98, "leadership": 78, "social": 72, "athletics": 84, "prestige": 99},
    "Harvard University": {"academics": 100, "business": 98, "technology": 91, "research": 99, "entrepreneurship": 95, "network": 100, "leadership": 84, "social": 68, "athletics": 68, "prestige": 100},
    "MIT": {"academics": 99, "business": 90, "technology": 100, "research": 100, "entrepreneurship": 98, "network": 94, "leadership": 72, "social": 58, "athletics": 45, "prestige": 99},
    "University of Michigan": {"academics": 92, "business": 92, "technology": 91, "research": 93, "entrepreneurship": 89, "network": 94, "leadership": 87, "social": 89, "athletics": 97, "prestige": 94},
    "University of Wisconsin": {"academics": 89, "business": 84, "technology": 86, "research": 93, "entrepreneurship": 82, "network": 87, "leadership": 84, "social": 92, "athletics": 94, "prestige": 88},
    "University of Alabama": {"academics": 76, "business": 82, "technology": 72, "research": 73, "entrepreneurship": 78, "network": 88, "leadership": 91, "social": 97, "athletics": 100, "prestige": 80},
    "University of Central Florida": {"academics": 78, "business": 82, "technology": 86, "research": 80, "entrepreneurship": 88, "network": 84, "leadership": 94, "social": 91, "athletics": 82, "prestige": 75},
    "University of North Florida": {"academics": 70, "business": 73, "technology": 69, "research": 65, "entrepreneurship": 76, "network": 74, "leadership": 98, "social": 78, "athletics": 64, "prestige": 61},
    "Arizona State University": {"academics": 82, "business": 86, "technology": 84, "research": 86, "entrepreneurship": 94, "network": 87, "leadership": 92, "social": 93, "athletics": 86, "prestige": 80},
    "University of Arizona": {"academics": 84, "business": 80, "technology": 79, "research": 91, "entrepreneurship": 81, "network": 82, "leadership": 88, "social": 90, "athletics": 87, "prestige": 82},
    "Babson College": {"academics": 84, "business": 99, "technology": 74, "research": 68, "entrepreneurship": 100, "network": 91, "leadership": 89, "social": 72, "athletics": 58, "prestige": 85},
    "New York University": {"academics": 91, "business": 96, "technology": 87, "research": 89, "entrepreneurship": 93, "network": 99, "leadership": 82, "social": 88, "athletics": 38, "prestige": 94},
    "Howard University": {"academics": 84, "business": 84, "technology": 77, "research": 80, "entrepreneurship": 87, "network": 93, "leadership": 97, "social": 90, "athletics": 72, "prestige": 86},
    "Georgia Tech": {"academics": 93, "business": 86, "technology": 98, "research": 96, "entrepreneurship": 94, "network": 90, "leadership": 78, "social": 70, "athletics": 81, "prestige": 93},
    "University of Miami": {"academics": 86, "business": 87, "technology": 80, "research": 88, "entrepreneurship": 86, "network": 94, "leadership": 86, "social": 95, "athletics": 92, "prestige": 88},
    "Florida State University": {"academics": 82, "business": 81, "technology": 76, "research": 84, "entrepreneurship": 80, "network": 88, "leadership": 91, "social": 96, "athletics": 96, "prestige": 84},
    "University of Florida": {"academics": 91, "business": 89, "technology": 89, "research": 94, "entrepreneurship": 87, "network": 91, "leadership": 87, "social": 89, "athletics": 95, "prestige": 92},
    "USC": {"academics": 91, "business": 94, "technology": 89, "research": 90, "entrepreneurship": 96, "network": 99, "leadership": 85, "social": 94, "athletics": 98, "prestige": 95},
}

CAREER_TIERS = [
    (0, "Salaried Professional", "$85,000"),
    (185, "High-Income Professional", "$240,000"),
    (205, "Founder", "$2.5 million"),
    (225, "Millionaire", "$8 million"),
    (245, "Multimillionaire", "$45 million"),
    (265, "Centimillionaire", "$320 million"),
    (282, "Billionaire", "$2.4 billion"),
]

SYNERGY_BONUSES = {
    frozenset(["Business", "Computer Science"]): 9,
    frozenset(["Business", "Engineering"]): 8,
    frozenset(["Economics", "Computer Science"]): 7,
    frozenset(["Psychology", "Communications"]): 6,
    frozenset(["Political Science", "Business"]): 6,
    frozenset(["Sports Management", "Business"]): 6,
    frozenset(["Archaeology", "Business"]): 4,
    frozenset(["Biology", "Business"]): 5,
}

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {max-width: 1100px; padding-top: 1.4rem; padding-bottom: 3rem;}
    .game-title {font-size: 3.2rem; font-weight: 900; line-height: 1; text-align:center; margin: .4rem 0;}
    .subtitle {text-align:center; color:#6b7280; margin-bottom:1.6rem;}
    .round-pill {display:inline-block; padding:.35rem .8rem; border-radius:999px; background:#eef2ff; font-weight:700;}
    .major-box {border:1px solid #d1d5db; border-radius:16px; padding:1.1rem; text-align:center; margin:1rem 0 1.5rem;}
    .major-label {font-size:.82rem; color:#6b7280; text-transform:uppercase; letter-spacing:.08em;}
    .major-name {font-size:2rem; font-weight:900;}
    .school-card {border:1px solid #d1d5db; border-radius:18px; padding:1rem; min-height:185px; background:white;}
    .school-name {font-size:1.25rem; font-weight:850; min-height:58px;}
    .score-chip {display:inline-block; background:#f3f4f6; border-radius:999px; padding:.25rem .55rem; margin:.18rem .12rem; font-size:.78rem;}
    .roster-card {border:1px solid #e5e7eb; border-radius:14px; padding:.8rem; margin:.35rem 0;}
    .result-hero {border:2px solid #111827; border-radius:22px; padding:1.4rem; text-align:center; margin-bottom:1.2rem;}
    .result-tier {font-size:2.5rem; font-weight:950;}
    .result-money {font-size:1.3rem; color:#4b5563;}
    .footer-note {text-align:center; color:#9ca3af; font-size:.78rem; margin-top:2rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Game logic
# -----------------------------
def reset_game() -> None:
    st.session_state.started = False
    st.session_state.round_index = 0
    st.session_state.roster = []
    st.session_state.current_major = None
    st.session_state.current_schools = []
    st.session_state.major_reroll_used = False
    st.session_state.school_reroll_used = False
    st.session_state.finished = False


def make_roll() -> None:
    used_majors = {item["major"] for item in st.session_state.roster}
    available_majors = [m for m in MAJORS if m not in used_majors] or list(MAJORS)
    st.session_state.current_major = random.choice(available_majors)
    st.session_state.current_schools = random.sample(list(UNIVERSITIES), 3)


def start_game() -> None:
    reset_game()
    st.session_state.started = True
    make_roll()


def credential_score(university: str, major: str, degree: str) -> float:
    ratings = UNIVERSITIES[university]
    score = sum(ratings[attribute] * weight for attribute, weight in MAJORS[major].items())

    if degree == "Undergraduate":
        score += ratings["leadership"] * 0.05 + ratings["social"] * 0.03
    elif degree == "Master's":
        score += ratings["network"] * 0.05 + ratings["business"] * 0.03
    else:
        score += ratings["research"] * 0.06 + ratings["academics"] * 0.02

    return round(min(score, 100), 1)


def choose_school(university: str) -> None:
    degree = DEGREES[st.session_state.round_index]
    major = st.session_state.current_major
    score = credential_score(university, major, degree)
    st.session_state.roster.append(
        {"degree": degree, "major": major, "university": university, "score": score}
    )
    st.session_state.round_index += 1

    if st.session_state.round_index >= len(DEGREES):
        st.session_state.finished = True
    else:
        make_roll()


def reroll_major() -> None:
    current = st.session_state.current_major
    choices = [m for m in MAJORS if m != current and m not in {r["major"] for r in st.session_state.roster}]
    st.session_state.current_major = random.choice(choices or [m for m in MAJORS if m != current])
    st.session_state.major_reroll_used = True


def reroll_schools() -> None:
    old = set(st.session_state.current_schools)
    pool = [u for u in UNIVERSITIES if u not in old]
    st.session_state.current_schools = random.sample(pool, 3)
    st.session_state.school_reroll_used = True


def synergy_bonus(roster: List[dict]) -> int:
    majors = [item["major"] for item in roster]
    total = 0
    for i in range(len(majors)):
        for j in range(i + 1, len(majors)):
            total += SYNERGY_BONUSES.get(frozenset([majors[i], majors[j]]), 0)
    if len(set(majors)) == 3:
        total += 2
    return total


def career_result(roster: List[dict]) -> tuple[str, str, int]:
    base = sum(item["score"] for item in roster)
    bonus = synergy_bonus(roster)
    # Small deterministic-feeling luck factor keeps repeat plays less predictable.
    luck = random.Random("|".join(item["university"] + item["major"] for item in roster)).randint(-4, 6)
    total = round(base + bonus + luck)

    selected = CAREER_TIERS[0]
    for threshold, title, net_worth in CAREER_TIERS:
        if total >= threshold:
            selected = (threshold, title, net_worth)
    return selected[1], selected[2], total


def campus_identity(roster: List[dict]) -> tuple[str, str]:
    undergrad = roster[0]
    ratings = UNIVERSITIES[undergrad["university"]]
    major = undergrad["major"]

    archetypes = {
        "Academic Weapon": ratings["academics"] + ratings["research"] + (12 if major in ["Biology", "Archaeology", "Psychology"] else 0),
        "Fraternity/Sorority President": ratings["social"] + ratings["network"] + ratings["leadership"] * 0.7,
        "Football Captain": ratings["athletics"] * 1.5 + ratings["leadership"],
        "Student-Body President": ratings["leadership"] * 1.5 + ratings["network"],
        "Student Founder": ratings["entrepreneurship"] * 1.5 + ratings["business"],
        "Campus Celebrity": ratings["social"] * 1.3 + ratings["network"] + ratings["athletics"] * 0.4,
    }
    identity = max(archetypes, key=archetypes.get)

    descriptions = {
        "Academic Weapon": "You treated office hours like a second home and somehow made group projects productive.",
        "Fraternity/Sorority President": "You knew everyone, ran the social calendar, and converted relationships into opportunity.",
        "Football Captain": "You became the face of school spirit and learned to lead while everyone was watching.",
        "Student-Body President": "You mastered campus politics, public speaking, and getting five committees to agree on anything.",
        "Student Founder": "You were pitching ideas before your classmates had picked a concentration.",
        "Campus Celebrity": "Professors recognized you, students followed you, and every event somehow ended up on your calendar.",
    }
    return identity, descriptions[identity]


def build_summary(roster: List[dict], tier: str, identity: str) -> str:
    undergrad, masters, phd = roster
    return (
        f"You started as a {identity.lower()} studying {undergrad['major']} at "
        f"{undergrad['university']}, expanded your network through {masters['major']} at "
        f"{masters['university']}, and finished with deep expertise in {phd['major']} at "
        f"{phd['university']}. The final verdict: {tier.lower()}."
    )


if "started" not in st.session_state:
    reset_game()

# -----------------------------
# UI
# -----------------------------
st.markdown('<div class="game-title">CAMPUS DRAFT</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Draft your education. Discover your career. See who you became on campus.</div>', unsafe_allow_html=True)

if not st.session_state.started:
    left, center, right = st.columns([1, 1.5, 1])
    with center:
        st.markdown(
            """
            ### How it works
            1. A degree level and random major are revealed.
            2. Choose one university from three options.
            3. Fill Undergraduate, Master's, and PhD.
            4. Receive your career tier, estimated net worth, and campus identity.

            You get **one major reroll** and **one university reroll** per game.
            """
        )
        st.button("Start Draft", type="primary", use_container_width=True, on_click=start_game)

elif st.session_state.finished:
    tier, net_worth, total_score = career_result(st.session_state.roster)
    identity, identity_description = campus_identity(st.session_state.roster)
    summary = build_summary(st.session_state.roster, tier, identity)

    st.markdown(
        f"""
        <div class="result-hero">
            <div style="font-size:.85rem; text-transform:uppercase; letter-spacing:.1em;">Your final outcome</div>
            <div class="result-tier">{tier}</div>
            <div class="result-money">Estimated net worth: {net_worth}</div>
            <div style="margin-top:.6rem;"><b>Campus identity:</b> {identity}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(min(total_score / 300, 1.0), text=f"Career score: {total_score} / 300")

    st.subheader("Your Education Roster")
    cols = st.columns(3)
    for col, item in zip(cols, st.session_state.roster):
        with col:
            st.markdown(
                f"""
                <div class="school-card">
                    <div class="round-pill">{item['degree']}</div>
                    <div class="school-name" style="margin-top:.8rem;">{item['university']}</div>
                    <div><b>{item['major']}</b></div>
                    <div style="margin-top:.7rem; color:#6b7280;">Credential score: {item['score']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader(identity)
    st.write(identity_description)
    st.info(summary)

    c1, c2 = st.columns(2)
    with c1:
        st.button("Play Again", type="primary", use_container_width=True, on_click=start_game)
    with c2:
        st.download_button(
            "Download Result",
            data=(
                "CAMPUS DRAFT RESULT\n"
                f"Career: {tier}\nEstimated net worth: {net_worth}\n"
                f"Campus identity: {identity}\nCareer score: {total_score}/300\n\n"
                + "\n".join(
                    f"{r['degree']}: {r['major']} — {r['university']}" for r in st.session_state.roster
                )
                + f"\n\n{summary}\n"
            ),
            file_name="campus_draft_result.txt",
            use_container_width=True,
        )

else:
    round_number = st.session_state.round_index + 1
    degree = DEGREES[st.session_state.round_index]

    top1, top2 = st.columns([2, 1])
    with top1:
        st.markdown(f'<span class="round-pill">Round {round_number} of 3 · {degree}</span>', unsafe_allow_html=True)
    with top2:
        st.progress(st.session_state.round_index / 3, text=f"{st.session_state.round_index}/3 credentials locked")

    st.markdown(
        f"""
        <div class="major-box">
            <div class="major-label">Your rolled major</div>
            <div class="major-name">{st.session_state.current_major}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    reroll1, reroll2 = st.columns(2)
    with reroll1:
        st.button(
            "🎲 Reroll Major" if not st.session_state.major_reroll_used else "Major reroll used",
            disabled=st.session_state.major_reroll_used,
            use_container_width=True,
            on_click=reroll_major,
        )
    with reroll2:
        st.button(
            "🔄 Reroll Universities" if not st.session_state.school_reroll_used else "University reroll used",
            disabled=st.session_state.school_reroll_used,
            use_container_width=True,
            on_click=reroll_schools,
        )

    st.subheader("Choose your university")
    school_cols = st.columns(3)
    for col, university in zip(school_cols, st.session_state.current_schools):
        ratings = UNIVERSITIES[university]
        preview = credential_score(university, st.session_state.current_major, degree)
        with col:
            st.markdown(
                f"""
                <div class="school-card">
                    <div class="school-name">{university}</div>
                    <span class="score-chip">Major fit: {preview}</span>
                    <span class="score-chip">Network: {ratings['network']}</span>
                    <span class="score-chip">Leadership: {ratings['leadership']}</span>
                    <span class="score-chip">Social: {ratings['social']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                f"Draft {university}",
                key=f"draft-{round_number}-{university}",
                type="primary",
                use_container_width=True,
                on_click=choose_school,
                args=(university,),
            )

    if st.session_state.roster:
        st.divider()
        st.subheader("Current roster")
        for item in st.session_state.roster:
            st.markdown(
                f"<div class='roster-card'><b>{item['degree']}</b> · {item['major']} at {item['university']} · Score {item['score']}</div>",
                unsafe_allow_html=True,
            )

st.markdown(
    '<div class="footer-note">Unofficial prototype for entertainment. Outcomes are fictional and ratings are game-design estimates, not real-world predictions.</div>',
    unsafe_allow_html=True,
)
