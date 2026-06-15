from __future__ import annotations

import random
from typing import Any

import streamlit as st

from game_logic import (
    DEGREES,
    MAJORS,
    UNIVERSITIES,
    campus_identity,
    evaluate_roster,
    score_credential,
)
from story_generator import ai_available, generate_story

st.set_page_config(page_title="Campus Draft", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    .block-container{max-width:1150px;padding-top:1.2rem;padding-bottom:3rem}
    .game-title{font-size:3.1rem;font-weight:950;line-height:1;text-align:center;margin:.35rem 0}
    .subtitle{text-align:center;color:#6b7280;margin-bottom:1.5rem}
    .pill{display:inline-block;padding:.34rem .76rem;border-radius:999px;background:#eef2ff;font-weight:750}
    .major-box{border:1px solid #d1d5db;border-radius:18px;padding:1.05rem;text-align:center;margin:1rem 0 1.35rem}
    .major-label{font-size:.78rem;color:#6b7280;text-transform:uppercase;letter-spacing:.09em}
    .major-name{font-size:2rem;font-weight:950}
    .school-card{border:1px solid #d1d5db;border-radius:18px;padding:1rem;min-height:238px;background:white}
    .school-name{font-size:1.18rem;font-weight:850;min-height:58px}
    .chip{display:inline-block;background:#f3f4f6;border-radius:999px;padding:.24rem .52rem;margin:.16rem .08rem;font-size:.76rem}
    .result-hero{border:2px solid #111827;border-radius:22px;padding:1.4rem;text-align:center;margin-bottom:1.1rem}
    .result-tier{font-size:2.35rem;font-weight:950}.result-money{font-size:1.2rem;color:#4b5563}
    .roster-card{border:1px solid #e5e7eb;border-radius:14px;padding:.8rem;margin:.35rem 0}
    .footer{text-align:center;color:#9ca3af;font-size:.76rem;margin-top:2rem}
    </style>
    """,
    unsafe_allow_html=True,
)


def reset_game() -> None:
    defaults = {
        "started": False,
        "round_index": 0,
        "roster": [],
        "current_major": None,
        "current_schools": [],
        "major_reroll_used": False,
        "school_reroll_used": False,
        "finished": False,
        "result": None,
        "identity": None,
        "identity_description": None,
        "story": None,
        "story_used_ai": False,
    }
    for key, value in defaults.items():
        st.session_state[key] = value


def make_roll() -> None:
    used_majors = {item["major"] for item in st.session_state.roster}
    available_majors = [m for m in MAJORS if m not in used_majors] or list(MAJORS)
    st.session_state.current_major = random.choice(available_majors)

    # Use three different school tiers when practical. This creates a real tradeoff
    # instead of three prestige clones.
    tier_buckets: dict[str, list[str]] = {}
    for name, data in UNIVERSITIES.items():
        tier_buckets.setdefault(data["tier"], []).append(name)
    chosen_tiers = random.sample(list(tier_buckets), k=min(3, len(tier_buckets)))
    schools = [random.choice(tier_buckets[tier]) for tier in chosen_tiers]
    while len(schools) < 3:
        candidate = random.choice(list(UNIVERSITIES))
        if candidate not in schools:
            schools.append(candidate)
    st.session_state.current_schools = schools


def start_game() -> None:
    reset_game()
    st.session_state.started = True
    make_roll()


def choose_school(university: str) -> None:
    degree = DEGREES[st.session_state.round_index]
    major = st.session_state.current_major
    st.session_state.roster.append({
        "degree": degree,
        "major": major,
        "university": university,
        "score": score_credential(university, major, degree),
    })
    st.session_state.round_index += 1
    if st.session_state.round_index >= len(DEGREES):
        st.session_state.finished = True
        st.session_state.result = evaluate_roster(st.session_state.roster)
        identity, description = campus_identity(st.session_state.roster)
        st.session_state.identity = identity
        st.session_state.identity_description = description
        story, used_ai = generate_story(st.session_state.roster, st.session_state.result, identity)
        st.session_state.story = story
        st.session_state.story_used_ai = used_ai
    else:
        make_roll()


def reroll_major() -> None:
    current = st.session_state.current_major
    used = {item["major"] for item in st.session_state.roster}
    choices = [m for m in MAJORS if m != current and m not in used]
    st.session_state.current_major = random.choice(choices or [m for m in MAJORS if m != current])
    st.session_state.major_reroll_used = True


def reroll_schools() -> None:
    old = set(st.session_state.current_schools)
    pool = [u for u in UNIVERSITIES if u not in old]
    st.session_state.current_schools = random.sample(pool, 3)
    st.session_state.school_reroll_used = True


def regenerate_story() -> None:
    story, used_ai = generate_story(st.session_state.roster, st.session_state.result, st.session_state.identity)
    st.session_state.story = story
    st.session_state.story_used_ai = used_ai


if "started" not in st.session_state:
    reset_game()

st.markdown('<div class="game-title">CAMPUS DRAFT</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Draft your education. Build a life. Discover where it takes you.</div>', unsafe_allow_html=True)

if not st.session_state.started:
    _, center, _ = st.columns([1, 1.6, 1])
    with center:
        st.markdown(
            f"""
            ### How it works
            1. Receive a degree level and random major.
            2. Choose one university from three options.
            3. Fill Undergraduate, Master's, and PhD.
            4. Receive a career, industry, campus identity, wealth range, and career story.

            **Current pool:** {len(UNIVERSITIES)} universities and {len(MAJORS)} majors.  
            You receive **one major reroll** and **one university reroll**.
            """
        )
        st.button("Start Draft", type="primary", use_container_width=True, on_click=start_game)

elif st.session_state.finished:
    result = st.session_state.result
    st.markdown(
        f"""
        <div class="result-hero">
          <div style="font-size:.82rem;text-transform:uppercase;letter-spacing:.1em">Your final outcome</div>
          <div class="result-tier">{result['career_title']}</div>
          <div class="result-money">Estimated net worth: {result['wealth']}</div>
          <div style="margin-top:.55rem"><b>{result['industry']}</b> · {result['career_style']}</div>
          <div style="margin-top:.3rem"><b>Campus identity:</b> {st.session_state.identity}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(min(result["total_score"] / 310, 1.0), text=f"Career score: {result['total_score']} / 310")

    st.subheader("Your Education Roster")
    cols = st.columns(3)
    for col, item in zip(cols, st.session_state.roster):
        with col:
            st.markdown(
                f"""
                <div class="school-card">
                  <span class="pill">{item['degree']}</span>
                  <div class="school-name" style="margin-top:.75rem">{item['university']}</div>
                  <div><b>{item['major']}</b></div>
                  <div style="margin-top:.65rem;color:#6b7280">Credential score: {item['score']['total']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Your Career Story")
        st.write(st.session_state.story)
        label = "Regenerate AI Story" if ai_available() else "AI story unavailable — using built-in story"
        st.button(label, disabled=not ai_available(), on_click=regenerate_story)
        if st.session_state.story_used_ai:
            st.caption("Story generated with AI. The score and outcomes were calculated by the game.")
        else:
            st.caption("Story generated by the built-in fallback. Add an API key to enable AI stories.")

    with right:
        st.subheader("Why you got this result")
        st.metric("Base credential score", result["base_score"])
        st.metric("Major synergy", f"+{result['synergy_bonus']}")
        st.metric("Luck modifier", f"{result['luck']:+d}")
        if result["synergy_notes"]:
            for note in result["synergy_notes"]:
                st.write(f"• {note}")
        st.info(f"**{st.session_state.identity}:** {st.session_state.identity_description}")
        st.warning(result["twist"])

    with st.expander("See every credential score component"):
        for item in st.session_state.roster:
            st.markdown(f"#### {item['degree']}: {item['major']} at {item['university']}")
            for component, value in item["score"].items():
                if component != "total":
                    st.write(f"{component}: **{value} points**")

    c1, c2 = st.columns(2)
    with c1:
        st.button("Play Again", type="primary", use_container_width=True, on_click=start_game)
    with c2:
        text_result = (
            "CAMPUS DRAFT RESULT\n"
            f"Career: {result['career_title']}\nIndustry: {result['industry']}\n"
            f"Estimated net worth: {result['wealth']}\nCampus identity: {st.session_state.identity}\n"
            f"Career score: {result['total_score']}/310\n\n"
            + "\n".join(f"{x['degree']}: {x['major']} — {x['university']}" for x in st.session_state.roster)
            + f"\n\n{st.session_state.story}\n"
        )
        st.download_button("Download Result", data=text_result, file_name="campus_draft_result.txt", use_container_width=True)

else:
    round_number = st.session_state.round_index + 1
    degree = DEGREES[st.session_state.round_index]
    top1, top2 = st.columns([2, 1])
    with top1:
        st.markdown(f'<span class="pill">Round {round_number} of 3 · {degree}</span>', unsafe_allow_html=True)
    with top2:
        st.progress(st.session_state.round_index / 3, text=f"{st.session_state.round_index}/3 credentials locked")

    st.markdown(
        f'<div class="major-box"><div class="major-label">Your rolled major</div><div class="major-name">{st.session_state.current_major}</div></div>',
        unsafe_allow_html=True,
    )

    r1, r2 = st.columns(2)
    with r1:
        st.button("🎲 Reroll Major" if not st.session_state.major_reroll_used else "Major reroll used", disabled=st.session_state.major_reroll_used, use_container_width=True, on_click=reroll_major)
    with r2:
        st.button("🔄 Reroll Universities" if not st.session_state.school_reroll_used else "University reroll used", disabled=st.session_state.school_reroll_used, use_container_width=True, on_click=reroll_schools)

    st.subheader("Choose your university")
    school_cols = st.columns(3)
    for col, university in zip(school_cols, st.session_state.current_schools):
        school = UNIVERSITIES[university]
        preview = score_credential(university, st.session_state.current_major, degree)
        with col:
            st.markdown(
                f"""
                <div class="school-card">
                  <div class="school-name">{university}</div>
                  <span class="chip">Total fit: {preview['total']}</span>
                  <span class="chip">Program: {preview['Program fit']}</span>
                  <span class="chip">Degree: {preview['Degree-level fit']}</span>
                  <span class="chip">Opportunity: {preview['Opportunity access']}</span>
                  <span class="chip">Network: {preview['Network']}</span>
                  <span class="chip">Prestige: {preview['Prestige']}</span>
                  <div style="margin-top:.55rem;color:#6b7280;font-size:.78rem">Strengths: {', '.join(school['strengths'][:4])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(f"Draft {university}", key=f"draft-{round_number}-{university}", type="primary", use_container_width=True, on_click=choose_school, args=(university,))

    if st.session_state.roster:
        st.divider()
        st.subheader("Current roster")
        for item in st.session_state.roster:
            st.markdown(f"<div class='roster-card'><b>{item['degree']}</b> · {item['major']} at {item['university']} · Score {item['score']['total']}</div>", unsafe_allow_html=True)

st.markdown('<div class="footer">Unofficial entertainment prototype. Ratings are game-design estimates and outcomes are fictional, not real-world predictions.</div>', unsafe_allow_html=True)
