import io
import base64
import os
import re
import html
import json
import random
import time
from datetime import date, datetime, timedelta

import streamlit as st
from dotenv import load_dotenv
from groq import BadRequestError, Groq, RateLimitError
from PIL import Image, ImageOps
from pypdf import PdfReader


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="auto",
)


# =========================================================
# DESIGN SYSTEM (CSS)
# =========================================================

st.markdown(
    """
<style>

/* ---------- PAGE ---------- */

.stApp {
    background-image:
        radial-gradient(circle at 0% 0%, rgba(124, 58, 237, 0.12), transparent 32%),
        radial-gradient(circle at 100% 0%, rgba(14, 165, 233, 0.10), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(236, 72, 153, 0.07), transparent 40%);
    background-attachment: fixed;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1320px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

header[data-testid="stHeader"] {
    background: transparent !important;
    backdrop-filter: none !important;
    box-shadow: none !important;
}

footer {
    visibility: hidden;
}


/* ---------- HERO ---------- */

.hero {
    position: relative;
    overflow: hidden;
    border-radius: 28px;
    padding: 2.6rem 2.8rem;
    color: #FFFFFF;
    background: linear-gradient(120deg, #312E81, #6D28D9, #DB2777, #0EA5E9);
    background-size: 300% 300%;
    animation: heroShift 16s ease infinite;
    box-shadow: 0 25px 60px -22px rgba(109, 40, 217, 0.6);
}

@keyframes heroShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.hero-blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(42px);
    opacity: 0.45;
    animation: floaty 9s ease-in-out infinite;
}

.hero-blob.b1 { width: 260px; height: 260px; background: #F472B6; top: -90px; right: 20%; }
.hero-blob.b2 { width: 210px; height: 210px; background: #38BDF8; bottom: -100px; left: 6%; animation-delay: -3s; }
.hero-blob.b3 { width: 170px; height: 170px; background: #FDE68A; top: 35%; right: -50px; opacity: 0.3; animation-delay: -6s; }

@keyframes floaty {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-18px) scale(1.06); }
}

.hero-grid {
    position: relative;
    display: grid;
    grid-template-columns: 1.1fr 1fr;
    gap: 2.2rem;
    align-items: center;
}

.hero-eyebrow {
    display: inline-block;
    padding: 0.35rem 0.95rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.25);
    font-size: 0.85rem;
    font-weight: 600;
    backdrop-filter: blur(6px);
}

.hero-title {
    font-family: "Outfit", sans-serif;
    font-size: clamp(2rem, 4.2vw, 3.4rem);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -0.02em;
    margin: 0.9rem 0 0.7rem;
}

.hero-title .hl {
    background: linear-gradient(90deg, #FDE68A, #FBCFE8);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.hero-sub {
    font-size: 1.05rem;
    line-height: 1.6;
    opacity: 0.9;
    max-width: 580px;
    margin: 0;
}

.hero-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-top: 1.4rem;
}

.chip {
    padding: 0.45rem 0.95rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.22);
    font-size: 0.9rem;
    font-weight: 600;
    backdrop-filter: blur(6px);
}

.hero-side {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.1rem;
}

.ring {
    width: 132px;
    height: 132px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22);
}

.ring-inner {
    width: 106px;
    height: 106px;
    border-radius: 50%;
    background: rgba(30, 27, 75, 0.88);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.ring-inner b {
    font-family: "Outfit", sans-serif;
    font-size: 2.4rem;
    line-height: 1;
}

.ring-inner small {
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    opacity: 0.75;
    margin-top: 0.2rem;
}

.tip {
    width: 100%;
    padding: 1rem 1.2rem;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.22);
    backdrop-filter: blur(10px);
}

.tip-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    opacity: 0.8;
}

.tip-title {
    font-weight: 700;
    font-size: 1.05rem;
    margin: 0.25rem 0;
}

.tip-text {
    font-size: 0.88rem;
    line-height: 1.5;
    opacity: 0.9;
}

@media (max-width: 900px) {
    .hero { padding: 1.8rem 1.4rem; }
    .hero-grid { grid-template-columns: 1fr; }
}


/* ---------- SECTION HEADERS & STEPS ---------- */

.sec-head {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin: 0.2rem 0 0.4rem;
}

.sec-icon {
    width: 44px;
    height: 44px;
    flex-shrink: 0;
    border-radius: 14px;
    display: grid;
    place-items: center;
    font-size: 1.35rem;
    background: linear-gradient(135deg, #6366F1, #A855F7);
    box-shadow: 0 10px 22px -10px rgba(124, 58, 237, 0.8);
}

.sec-title {
    font-family: "Outfit", sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    line-height: 1.2;
}

.sec-sub {
    font-size: 0.9rem;
    opacity: 0.65;
}

.step-label {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-weight: 700;
    font-size: 0.95rem;
    margin-top: 0.4rem;
}

.step-label span {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 0.8rem;
    color: #FFFFFF;
    background: linear-gradient(135deg, #6366F1, #EC4899);
}

.mode-info {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.75rem 1rem;
    border-radius: 14px;
    background: rgba(124, 58, 237, 0.07);
    border: 1px dashed rgba(124, 58, 237, 0.3);
    font-size: 0.92rem;
}

.mode-info b {
    font-weight: 700;
}

.mode-badge {
    display: inline-block;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #FFFFFF;
    background: linear-gradient(135deg, #6366F1, #A855F7);
}


/* ---------- GLASS CARDS (keyed containers) ---------- */

[class*="st-key-card_"] {
    border-radius: 24px !important;
    border: 1px solid rgba(124, 58, 237, 0.16) !important;
    background: rgba(124, 58, 237, 0.035);
    backdrop-filter: blur(14px);
    box-shadow: 0 20px 45px -28px rgba(76, 29, 149, 0.45);
    padding: 1.5rem 1.6rem !important;
}


/* ---------- TABS ---------- */

[data-testid="stTabs"] [role="tablist"] {
    gap: 0.35rem;
    padding: 0.4rem;
    border-radius: 18px;
    background: rgba(124, 58, 237, 0.07);
    border: 1px solid rgba(124, 58, 237, 0.13);
    overflow-x: auto;
}

[data-testid="stTab"] {
    height: auto;
    border-radius: 13px;
    padding: 0.55rem 1.1rem !important;
    transition: all 0.2s ease;
}

[data-testid="stTab"]:hover {
    background: rgba(124, 58, 237, 0.1);
}

[data-testid="stTab"][aria-selected="true"] {
    background: linear-gradient(135deg, #6366F1, #A855F7) !important;
    box-shadow: 0 8px 20px -10px rgba(124, 58, 237, 0.9);
}

[data-testid="stTab"][aria-selected="true"],
[data-testid="stTab"][aria-selected="true"] * {
    color: #FFFFFF !important;
}

[data-testid="stTab"] p {
    font-size: 0.98rem;
    font-weight: 650;
}

[data-testid="stTabs"] [role="tablist"] > div:not([data-testid="stTab"]) {
    display: none;
}


/* ---------- BUTTONS ---------- */

button[data-testid="stBaseButton-secondary"] {
    font-weight: 600;
    border-color: rgba(124, 58, 237, 0.22) !important;
    transition: all 0.2s ease;
}

button[data-testid="stBaseButton-secondary"]:hover {
    transform: translateY(-2px);
    border-color: #7C3AED !important;
    box-shadow: 0 10px 22px -12px rgba(124, 58, 237, 0.7);
}

button[data-testid="stBaseButton-primary"] {
    border: none !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    background: linear-gradient(110deg, #4F46E5, #7C3AED 45%, #DB2777) !important;
    background-size: 200% auto !important;
    box-shadow: 0 12px 28px -12px rgba(124, 58, 237, 0.8);
    transition: all 0.3s ease;
}

button[data-testid="stBaseButton-primary"]:hover {
    background-position: right center !important;
    transform: translateY(-2px);
    box-shadow: 0 18px 34px -12px rgba(219, 39, 119, 0.7);
}

.st-key-generate_btn button {
    animation: pulseGlow 2.8s ease-in-out infinite;
}

@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 12px 28px -12px rgba(124, 58, 237, 0.8); }
    50% { box-shadow: 0 14px 42px -6px rgba(219, 39, 119, 0.7); }
}

[class*="st-key-quick_"] button,
[class*="st-key-suggest_"] button {
    border-radius: 999px !important;
    min-height: 38px;
    padding: 0.3rem 1rem;
    background: rgba(124, 58, 237, 0.06);
}


/* ---------- PILLS & SEGMENTED CONTROLS ---------- */

button[data-variant="pills"],
button[data-variant="segmented_control"] {
    font-weight: 600;
    background: rgba(124, 58, 237, 0.05) !important;
    border-color: rgba(124, 58, 237, 0.22) !important;
    transition: all 0.2s ease;
}

button[data-variant="pills"] {
    border-radius: 999px !important;
    padding: 0.5rem 1rem !important;
}

button[data-variant="pills"]:hover {
    transform: translateY(-2px);
    border-color: #7C3AED !important;
    box-shadow: 0 8px 20px -10px rgba(124, 58, 237, 0.6);
}

button[data-variant="pills"][data-selected="true"],
button[data-variant="segmented_control"][data-selected="true"] {
    background: linear-gradient(135deg, #6366F1, #A855F7) !important;
    border-color: transparent !important;
    color: #FFFFFF !important;
    box-shadow: 0 10px 24px -10px rgba(124, 58, 237, 0.85);
}

button[data-variant="pills"][data-selected="true"] *,
button[data-variant="segmented_control"][data-selected="true"] * {
    color: #FFFFFF !important;
}


/* ---------- INPUTS ---------- */

textarea {
    font-size: 1rem !important;
    line-height: 1.6 !important;
}

[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed rgba(124, 58, 237, 0.35);
    border-radius: 18px;
    background: rgba(124, 58, 237, 0.04);
}

[data-testid="stExpander"] details {
    border-radius: 16px;
    border-color: rgba(124, 58, 237, 0.2);
}

[data-testid="stAlert"] {
    border-radius: 14px;
}

[data-testid="stMetric"] {
    padding: 0.9rem 1.1rem;
    border-radius: 18px;
    background: rgba(124, 58, 237, 0.06);
    border: 1px solid rgba(124, 58, 237, 0.14);
}

[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 0.9rem 1rem;
    background: rgba(124, 58, 237, 0.05);
}


/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.12);
}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
    min-height: 46px;
    color: #FFFFFF !important;
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(255, 255, 255, 0.16) !important;
    border-color: #C4B5FD !important;
}

.brand {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    color: #FFFFFF;
}

.brand-logo {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    display: grid;
    place-items: center;
    font-size: 1.4rem;
    background: linear-gradient(135deg, #6366F1, #EC4899);
    box-shadow: 0 10px 22px -8px rgba(236, 72, 153, 0.7);
}

.brand-name {
    font-family: "Outfit", sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    line-height: 1.1;
}

.brand-sub {
    font-size: 0.78rem;
    opacity: 0.7;
}

.profile {
    padding: 1.1rem;
    border-radius: 20px;
    color: #FFFFFF;
    background: linear-gradient(145deg, rgba(99, 102, 241, 0.35), rgba(236, 72, 153, 0.22));
    border: 1px solid rgba(255, 255, 255, 0.14);
}

.profile-top {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 1.6rem;
    background: linear-gradient(135deg, #FDE68A, #F472B6);
    color: #1E1B4B;
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.25);
}

.p-rank {
    font-weight: 700;
    font-size: 1rem;
}

.p-level {
    font-size: 0.78rem;
    opacity: 0.75;
}

.xpbar {
    height: 10px;
    margin-top: 0.9rem;
    border-radius: 999px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.14);
}

.xpbar div {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #FDE68A, #F472B6);
}

.xp-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    opacity: 0.8;
    margin-top: 0.35rem;
}

.mini-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
    margin-top: 0.9rem;
}

.mini-stats div {
    padding: 0.6rem;
    border-radius: 14px;
    text-align: center;
    background: rgba(255, 255, 255, 0.08);
}

.mini-stats b {
    display: block;
    font-size: 1.1rem;
}

.mini-stats small {
    font-size: 0.7rem;
    opacity: 0.75;
}


/* ---------- EMPTY STATES ---------- */

.empty {
    text-align: center;
    padding: 2.2rem 1rem;
}

.empty-emoji {
    font-size: 3.4rem;
    display: inline-block;
    animation: floaty 4s ease-in-out infinite;
}

.empty-title {
    font-family: "Outfit", sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 0.6rem;
}

.empty-sub {
    opacity: 0.65;
    margin-top: 0.3rem;
}

.steps {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.7rem;
    margin-top: 1.3rem;
}

.step {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.95rem;
    border-radius: 999px;
    font-size: 0.88rem;
    font-weight: 600;
    background: rgba(124, 58, 237, 0.07);
    border: 1px solid rgba(124, 58, 237, 0.16);
}

.step span {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 0.72rem;
    color: #FFFFFF;
    background: linear-gradient(135deg, #6366F1, #A855F7);
}


/* ---------- FEATURE CARDS ---------- */

.features {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
}

.feature {
    position: relative;
    overflow: hidden;
    padding: 1.35rem;
    border-radius: 20px;
    background: rgba(124, 58, 237, 0.045);
    border: 1px solid rgba(124, 58, 237, 0.14);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.feature:hover {
    transform: translateY(-6px);
    box-shadow: 0 22px 40px -22px rgba(124, 58, 237, 0.6);
}

.feature::before {
    content: "";
    position: absolute;
    inset: 0 0 auto 0;
    height: 4px;
}

.f-icon {
    width: 50px;
    height: 50px;
    border-radius: 15px;
    display: grid;
    place-items: center;
    font-size: 1.5rem;
    margin-bottom: 0.85rem;
}

.feature.c1::before, .feature.c1 .f-icon { background: linear-gradient(135deg, #6366F1, #A855F7); }
.feature.c2::before, .feature.c2 .f-icon { background: linear-gradient(135deg, #10B981, #0EA5E9); }
.feature.c3::before, .feature.c3 .f-icon { background: linear-gradient(135deg, #F59E0B, #EC4899); }
.feature.c4::before, .feature.c4 .f-icon { background: linear-gradient(135deg, #0EA5E9, #6366F1); }

.f-title {
    font-weight: 700;
    font-size: 1.05rem;
}

.f-text {
    font-size: 0.9rem;
    line-height: 1.5;
    opacity: 0.72;
    margin-top: 0.25rem;
}

@media (max-width: 900px) {
    .features { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 520px) {
    .features { grid-template-columns: 1fr; }
}


/* ---------- QUIZ ---------- */

.q-head {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
}

.q-num {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    font-weight: 800;
    color: #FFFFFF;
    background: linear-gradient(135deg, #6366F1, #EC4899);
}

.q-text {
    font-size: 1.05rem;
    font-weight: 600;
    line-height: 1.5;
    padding-top: 0.35rem;
}

.score-card {
    display: flex;
    align-items: center;
    gap: 1.6rem;
    padding: 1.6rem;
    border-radius: 24px;
    color: #FFFFFF;
    background: linear-gradient(120deg, #312E81, #6D28D9, #DB2777);
    box-shadow: 0 22px 50px -24px rgba(109, 40, 217, 0.7);
    flex-wrap: wrap;
}

.score-ring {
    width: 130px;
    height: 130px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    flex-shrink: 0;
}

.score-inner {
    width: 104px;
    height: 104px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(30, 27, 75, 0.9);
}

.score-inner b {
    font-family: "Outfit", sans-serif;
    font-size: 2rem;
    line-height: 1;
}

.score-inner small {
    opacity: 0.75;
    margin-top: 0.2rem;
}

.score-title {
    font-family: "Outfit", sans-serif;
    font-size: 1.7rem;
    font-weight: 800;
}

.score-sub {
    opacity: 0.88;
    margin-top: 0.2rem;
}


/* ---------- FLASHCARDS ---------- */

.flashcard {
    position: relative;
    overflow: hidden;
    min-height: 270px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2.2rem 2.6rem;
    border-radius: 28px;
    font-size: 1.4rem;
    font-weight: 600;
    line-height: 1.5;
    color: #FFFFFF;
    background:
        radial-gradient(circle at 15% 20%, rgba(255, 255, 255, 0.18), transparent 35%),
        linear-gradient(135deg, #4F46E5, #7C3AED, #DB2777);
    box-shadow: 0 25px 55px -25px rgba(124, 58, 237, 0.75);
    animation: flipIn 0.45s ease;
}

.flashcard.back {
    font-size: 1.18rem;
    font-weight: 500;
    background:
        radial-gradient(circle at 85% 20%, rgba(255, 255, 255, 0.18), transparent 35%),
        linear-gradient(135deg, #059669, #0EA5E9, #6366F1);
}

.flashcard .side {
    display: block;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    opacity: 0.8;
    margin-bottom: 1rem;
}

.flashcard .tap {
    position: absolute;
    bottom: 0.9rem;
    font-size: 0.75rem;
    font-weight: 500;
    opacity: 0.65;
}

@keyframes flipIn {
    from { transform: perspective(900px) rotateY(-80deg); opacity: 0; }
    to { transform: perspective(900px) rotateY(0); opacity: 1; }
}


/* ---------- PROGRESS ---------- */

.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
}

.stat {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    padding: 1.1rem 1.2rem;
    border-radius: 20px;
    background: rgba(124, 58, 237, 0.05);
    border: 1px solid rgba(124, 58, 237, 0.14);
}

.stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 15px;
    display: grid;
    place-items: center;
    font-size: 1.4rem;
    flex-shrink: 0;
}

.stat:nth-child(1) .stat-icon { background: linear-gradient(135deg, #6366F1, #A855F7); }
.stat:nth-child(2) .stat-icon { background: linear-gradient(135deg, #F59E0B, #EC4899); }
.stat:nth-child(3) .stat-icon { background: linear-gradient(135deg, #EF4444, #F59E0B); }
.stat:nth-child(4) .stat-icon { background: linear-gradient(135deg, #10B981, #0EA5E9); }

.stat b {
    display: block;
    font-family: "Outfit", sans-serif;
    font-size: 1.6rem;
    line-height: 1.1;
}

.stat small {
    opacity: 0.65;
    font-size: 0.82rem;
}

@media (max-width: 900px) {
    .stats { grid-template-columns: repeat(2, 1fr); }
}

.badges {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
}

.badge {
    position: relative;
    overflow: hidden;
    padding: 1.2rem 0.9rem;
    border-radius: 20px;
    text-align: center;
    border: 1px solid rgba(148, 163, 184, 0.35);
}

.badge.earned {
    background: linear-gradient(145deg, rgba(99, 102, 241, 0.16), rgba(236, 72, 153, 0.14));
    border-color: rgba(168, 85, 247, 0.6);
    box-shadow: 0 14px 30px -18px rgba(168, 85, 247, 0.8);
}

.badge.earned::after {
    content: "";
    position: absolute;
    top: 0;
    left: -60%;
    width: 40%;
    height: 100%;
    background: linear-gradient(100deg, transparent, rgba(255, 255, 255, 0.35), transparent);
    animation: shine 3.5s ease-in-out infinite;
}

@keyframes shine {
    0% { left: -60%; }
    60%, 100% { left: 130%; }
}

.badge.locked {
    opacity: 0.45;
    filter: grayscale(1);
}

.badge .icon {
    font-size: 2.2rem;
}

.badge .name {
    font-weight: 700;
    margin-top: 0.35rem;
}

.badge .desc {
    font-size: 0.78rem;
    opacity: 0.75;
    margin-top: 0.15rem;
}


/* ---------- HERO ENTRANCE + QUOTES ---------- */

.hero-eyebrow, .hero-title, .hero-sub, .hero-chips, .hero-side {
    animation: riseIn 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) both;
}

.hero-title { animation-delay: 0.1s; }
.hero-sub { animation-delay: 0.2s; }
.hero-chips { animation-delay: 0.3s; }
.hero-side { animation-delay: 0.35s; }

@keyframes riseIn {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}

.quote-card {
    position: relative;
    width: 100%;
    padding: 1.2rem 1.3rem 1rem;
    border-radius: 20px;
    background: rgba(15, 12, 50, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.22);
    backdrop-filter: blur(10px);
    overflow: hidden;
}

.quote-mark {
    position: absolute;
    top: -18px;
    right: 14px;
    font-family: Georgia, serif;
    font-size: 6rem;
    line-height: 1;
    opacity: 0.18;
}

.quotes {
    position: relative;
    min-height: 118px;
}

.quote {
    position: absolute;
    inset: 0;
    opacity: 0;
    animation: quoteCycle 35s infinite both;
}

.q-body {
    font-family: "Outfit", sans-serif;
    font-size: 1.12rem;
    font-weight: 600;
    line-height: 1.45;
}

.q-author {
    margin-top: 0.5rem;
    font-size: 0.85rem;
    opacity: 0.75;
}

@keyframes quoteCycle {
    0% { opacity: 0; transform: translateY(14px); filter: blur(4px); }
    2% { opacity: 1; transform: translateY(0); filter: blur(0); }
    19% { opacity: 1; transform: translateY(0); filter: blur(0); }
    21% { opacity: 0; transform: translateY(-14px); filter: blur(4px); }
    100% { opacity: 0; }
}

.q-dots {
    display: flex;
    gap: 6px;
    margin-top: 0.6rem;
}

.q-dots span {
    width: 6px;
    height: 6px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.35);
    animation: dotCycle 35s infinite backwards;
}

@keyframes dotCycle {
    0% { width: 6px; background: rgba(255, 255, 255, 0.35); }
    0.5%, 19.5% { width: 20px; background: #FFFFFF; }
    20%, 100% { width: 6px; background: rgba(255, 255, 255, 0.35); }
}

@media (max-width: 520px) {
    .quotes { min-height: 128px; }
    .tips { min-height: 120px; }
    .scene { max-width: 340px; }
}


/* ---------- HERO: SPARKLES, ROTATING SUBJECTS, TIPS ---------- */

.hero {
    padding: 2.6rem 2.8rem 2.4rem;
}

.spark {
    position: absolute;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #FFFFFF;
    box-shadow: 0 0 12px 3px rgba(255, 255, 255, 0.8);
    animation: twinkle 4s ease-in-out infinite both;
}

@keyframes twinkle {
    0%, 100% { opacity: 0; transform: scale(0.3); }
    50% { opacity: 1; transform: scale(1); }
}

.hero-rotate {
    font-family: "Outfit", sans-serif;
    font-size: clamp(1.15rem, 2vw, 1.5rem);
    font-weight: 600;
    margin-bottom: 0.7rem;
}

.rotator {
    display: inline-block;
    height: 1.3em;
    line-height: 1.3em;
    overflow: hidden;
    vertical-align: bottom;
    padding: 0 0.7rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.18);
    border: 1px solid rgba(255, 255, 255, 0.28);
}

.rot-track {
    display: flex;
    flex-direction: column;
    animation: rotateWords 12s cubic-bezier(0.7, 0, 0.3, 1) infinite;
}

.rot-track span {
    height: 1.3em;
    line-height: 1.3em;
    font-weight: 800;
    color: #FDE68A;
}

@keyframes rotateWords {
    0%, 13.3% { transform: translateY(0); }
    16.7%, 30% { transform: translateY(-1.3em); }
    33.3%, 46.7% { transform: translateY(-2.6em); }
    50%, 63.3% { transform: translateY(-3.9em); }
    66.7%, 80% { transform: translateY(-5.2em); }
    83.3%, 96.7% { transform: translateY(-6.5em); }
    100% { transform: translateY(-7.8em); }
}

.hero-left .quote-card {
    margin-top: 1.3rem;
}

.hero-hint {
    display: inline-block;
    margin-top: 1.1rem;
    font-weight: 600;
    font-size: 0.92rem;
    opacity: 0.9;
    animation: hintBounce 2s ease-in-out infinite;
}

@keyframes hintBounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(5px); }
}

.tips {
    position: relative;
    min-height: 92px;
}

.tip-item {
    position: absolute;
    inset: 0;
    opacity: 0;
    animation: tipCycle 36s infinite both;
}

@keyframes tipCycle {
    0% { opacity: 0; transform: translateX(16px); }
    2% { opacity: 1; transform: translateX(0); }
    24% { opacity: 1; transform: translateX(0); }
    26% { opacity: 0; transform: translateX(-16px); }
    100% { opacity: 0; }
}

.tip .tip-title {
    margin-top: 0.3rem;
}


/* ---------- ANIMATED TUTOR SCENE (image) ---------- */

.scene {
    display: block;
    width: 100%;
    max-width: 460px;
    height: auto;
    margin: 0 auto -0.4rem;
    filter: drop-shadow(0 22px 30px rgba(20, 10, 60, 0.35));
}


/* ---------- LANDING SCREEN ---------- */

.st-key-hero_box {
    position: relative;
    overflow: hidden;
    min-height: calc(100dvh - 6.5rem);
    justify-content: center;
    padding: 2rem 2.6rem !important;
    border-radius: 28px;
    color: #FFFFFF;
    background: linear-gradient(120deg, #312E81, #6D28D9, #DB2777, #0EA5E9);
    background-size: 300% 300%;
    animation: heroShift 16s ease infinite;
    box-shadow: 0 25px 60px -22px rgba(109, 40, 217, 0.6);
}

.st-key-hero_box::before,
.st-key-hero_box::after {
    content: "";
    position: absolute;
    border-radius: 50%;
    filter: blur(46px);
    opacity: 0.45;
    pointer-events: none;
    animation: floaty 9s ease-in-out infinite;
}

.st-key-hero_box::before {
    width: 300px;
    height: 300px;
    top: -110px;
    right: 24%;
    background: #F472B6;
}

.st-key-hero_box::after {
    width: 240px;
    height: 240px;
    bottom: -110px;
    left: 5%;
    background: #38BDF8;
    animation-delay: -4s;
}

.st-key-hero_box > * {
    position: relative;
    z-index: 1;
}

.st-key-hero_box,
.st-key-hero_box p,
.st-key-hero_box div,
.st-key-hero_box span {
    color: #FFFFFF;
}

.hero-left,
.hero-right {
    position: relative;
}

.st-key-hero_box .hero-title {
    font-size: clamp(2.1rem, 3.8vw, 3.4rem);
    margin: 0.8rem 0 0.6rem;
}

.st-key-hero_box .quote-card {
    margin-top: 0.2rem;
}

.st-key-hero_box .scene {
    width: auto;
    max-width: 100%;
    max-height: 44vh;
    margin: 0 auto 0.6rem;
}

.st-key-get_started button[data-testid="stBaseButton-primary"] {
    min-height: 58px;
    padding: 0 2.6rem !important;
    border-radius: 999px !important;
    background: #FFFFFF !important;
    box-shadow: 0 16px 36px -12px rgba(15, 12, 50, 0.55);
    animation: startPulse 2.4s ease-in-out infinite;
}

.st-key-get_started button[data-testid="stBaseButton-primary"] * {
    color: #6D28D9 !important;
    font-size: 1.18rem !important;
    font-weight: 800 !important;
}

.st-key-get_started button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-3px) scale(1.03);
}

@keyframes startPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.55), 0 16px 36px -12px rgba(15, 12, 50, 0.55); }
    50% { box-shadow: 0 0 0 14px rgba(255, 255, 255, 0), 0 16px 36px -12px rgba(15, 12, 50, 0.55); }
}

.trust {
    font-size: 0.85rem;
    font-weight: 600;
    opacity: 0.85;
    margin-bottom: 0.6rem;
}

@media (max-width: 640px) {
    .st-key-hero_box {
        min-height: calc(100dvh - 5rem);
        padding: 1.5rem 1.3rem !important;
    }

    .st-key-hero_box .quote-card,
    .st-key-hero_box .tip {
        display: none;
    }

    .st-key-hero_box .scene {
        max-height: 30vh;
    }
}


/* ---------- COMPACT HEADER ---------- */

.mini-hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.9rem 1.6rem;
    border-radius: 22px;
    color: #FFFFFF;
    background: linear-gradient(120deg, #312E81, #6D28D9, #DB2777, #0EA5E9);
    background-size: 300% 300%;
    animation: heroShift 16s ease infinite;
    box-shadow: 0 18px 40px -22px rgba(109, 40, 217, 0.6);
}

.mini-greet {
    font-size: 0.85rem;
    font-weight: 600;
    opacity: 0.85;
}

.mini-title {
    font-family: "Outfit", sans-serif;
    font-size: clamp(1.3rem, 2.4vw, 1.8rem);
    font-weight: 800;
    line-height: 1.2;
}

.mini-title .hl {
    background: linear-gradient(90deg, #FDE68A, #FBCFE8);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.mini-hero-bot {
    height: 72px;
    width: auto;
    flex-shrink: 0;
}


/* ---------- CHAT WELCOME ---------- */

.tutor-hello {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1.2rem;
    padding: 1rem 0 0.4rem;
    flex-wrap: wrap;
    text-align: left;
}

.mini-bot {
    width: 120px;
    height: auto;
    filter: drop-shadow(0 14px 18px rgba(76, 29, 149, 0.3));
}

.hello-bubble {
    display: inline-block;
    padding: 0.7rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    font-family: "Outfit", sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #FFFFFF;
    background: linear-gradient(135deg, #6366F1, #A855F7);
    box-shadow: 0 12px 26px -12px rgba(124, 58, 237, 0.8);
    animation: riseIn 0.7s ease both;
}

.hello-sub {
    margin-top: 0.6rem;
    max-width: 340px;
    opacity: 0.7;
}

.st-key-card_chat [data-testid="stChatInput"] {
    margin-top: 0.6rem;
}


/* ---------- INPUT BOX WITH GENERATE BUTTON ---------- */

.st-key-inputbox {
    border-radius: 20px !important;
    border: 1.5px solid rgba(124, 58, 237, 0.28) !important;
    background: rgba(124, 58, 237, 0.04);
    padding: 0.6rem 0.8rem 0.7rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.st-key-inputbox:focus-within {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.14);
}

.st-key-inputbox [data-testid="stTextAreaRootElement"],
.st-key-inputbox textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.st-key-generate_btn button {
    min-height: 46px;
    padding: 0 2rem !important;
    border-radius: 999px !important;
    font-size: 1.02rem !important;
}


/* ---------- HIDDEN HELPER FRAMES ---------- */

[class*="st-key-pagejs_"] {
    position: absolute;
    width: 0;
    height: 0;
    overflow: hidden;
}


/* ---------- FIT TO SCREEN: LANDING ---------- */

[data-testid="stMainBlockContainer"]:has(.st-key-hero_box) {
    padding-top: 2.2rem;
    padding-bottom: 0 !important;
}

.st-key-hero_box {
    flex: 0 0 auto !important;
    height: calc(100dvh - 4.5rem) !important;
    min-height: 0 !important;
    padding: clamp(0.9rem, 3.4vh, 2rem) clamp(1.2rem, 3vw, 2.6rem) !important;
}

.st-key-hero_box [data-testid="stVerticalBlock"] {
    gap: min(1rem, 1.7vh);
}

.st-key-hero_box .hero-eyebrow {
    font-size: 0.8rem;
    padding: 0.3rem 0.85rem;
}

.st-key-hero_box .hero-title {
    font-size: clamp(1.6rem, min(3.6vw, 6.2vh), 3.4rem);
    margin: min(0.8rem, 1.5vh) 0 min(0.6rem, 1.2vh);
}

.st-key-hero_box .hero-rotate {
    font-size: clamp(0.95rem, min(1.7vw, 3vh), 1.45rem);
    white-space: nowrap;
    margin-bottom: min(0.7rem, 1.2vh);
}

.st-key-hero_box .hero-sub {
    font-size: clamp(0.88rem, min(1.2vw, 2.3vh), 1.05rem);
}

.st-key-get_started button[data-testid="stBaseButton-primary"] {
    min-height: clamp(42px, 7vh, 58px);
}

.st-key-hero_box .trust {
    margin-bottom: 0;
}

.st-key-hero_box .quote-card {
    padding: min(1rem, 1.8vh) 1.2rem min(0.8rem, 1.4vh);
}

.st-key-hero_box .q-body {
    font-size: clamp(0.9rem, 2.2vh, 1.1rem);
}

.st-key-hero_box .quotes {
    min-height: clamp(62px, 11vh, 110px);
}

.st-key-hero_box .scene {
    max-height: 40vh;
}

.st-key-hero_box .tip {
    padding: min(1rem, 1.8vh) 1.2rem;
}

.st-key-hero_box .tips {
    min-height: 98px;
}

.st-key-hero_box .tip-text {
    font-size: 0.85rem;
}

@media (max-height: 560px) {
    .st-key-hero_box .quote-card,
    .st-key-hero_box .tip,
    .st-key-hero_box .trust {
        display: none;
    }
}

@media (max-width: 640px) {
    .st-key-hero_box {
        padding: 1.2rem 1.2rem !important;
    }

    .st-key-hero_box .hero-title {
        font-size: clamp(1.6rem, min(8vw, 5.4vh), 2.3rem);
    }

    .st-key-hero_box .hero-rotate {
        font-size: clamp(0.95rem, 4.4vw, 1.2rem);
    }

    .st-key-hero_box .scene {
        max-height: 27vh;
    }
}


/* ---------- FIT TO SCREEN: SIDEBAR ---------- */

[data-testid="stSidebarHeader"] {
    height: 2.8rem;
    min-height: 0;
    padding-top: 0.6rem;
    padding-bottom: 0;
}

[data-testid="stSidebarUserContent"] {
    padding-top: 0.2rem !important;
    padding-bottom: 1rem !important;
}

[data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
    gap: 0.8rem;
}

.brand-logo {
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
}

.profile {
    padding: 0.85rem;
    border-radius: 18px;
}

.avatar {
    width: 40px;
    height: 40px;
    font-size: 1.3rem;
}

.p-rank {
    font-size: 0.95rem;
}

.mini-stats {
    grid-template-columns: repeat(4, 1fr);
    gap: 0.4rem;
    margin-top: 0.7rem;
}

.mini-stats div {
    padding: 0.45rem 0.2rem;
    border-radius: 12px;
}

.mini-stats b {
    font-size: 0.95rem;
    white-space: nowrap;
}

.mini-stats small {
    font-size: 0.62rem;
}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
    min-height: 40px;
}


/* ---------- FOOTER ---------- */

.app-footer {
    text-align: center;
    font-size: 0.85rem;
    opacity: 0.6;
    padding: 2rem 0 0.5rem;
}

</style>
""",
    unsafe_allow_html=True,
)



# =========================================================
# CONSTANTS
# =========================================================

PROGRESS_COOKIE = "study_buddy_progress"

MAX_SOURCE_CHARS = 15000

MAX_PHOTOS = 10

IMAGE_TYPES = ("png", "jpg", "jpeg", "webp")

LANGUAGES = [
    "English",
    "Urdu",
    "Arabic",
    "Hindi",
    "French",
    "Spanish",
]

MODES = {
    "💡 Explain Topic": "Understand any topic step by step.",
    "📝 Summarize Notes": "Turn long notes into clear revision points.",
    "❓ Generate Quiz": "Test yourself with an interactive quiz.",
    "🃏 Flashcards": "Create flip cards to memorise key ideas.",
    "🗺️ Mind Map": "See the whole topic as a visual map.",
    "📅 Study Plan": "Get a day-by-day plan to master a topic.",
    "🎭 Explain with Analogy": "Learn through creative real-life comparisons.",
    "🧑‍🏫 Feynman Check": "Explain it yourself and let the AI grade your understanding.",
}

JSON_MODES = {
    "❓ Generate Quiz",
    "🃏 Flashcards",
    "🗺️ Mind Map",
    "🧑‍🏫 Feynman Check",
}

PERSONA_HINTS = {
    "😊 Friendly Tutor": "Answers your questions clearly with examples.",
    "🤔 Socratic Coach": "Guides you to the answer with hints and questions instead of telling you.",
    "🎯 Strict Examiner": "Tests you with exam questions. Type your answer and it marks you out of 10.",
    "🧒 Explain Like I'm 5": "Answers in super simple words and fun comparisons.",
}

TUTOR_PERSONAS = {
    "😊 Friendly Tutor": (
        "You are a warm, encouraging tutor. Explain clearly, "
        "use examples and check the student's understanding."
    ),
    "🤔 Socratic Coach": (
        "You never give the full answer straight away. Guide the "
        "student with one probing question at a time and give hints "
        "only when they are stuck."
    ),
    "🎯 Strict Examiner": (
        "You are a rigorous examiner. If the student asks a question, "
        "answer it accurately and concisely first. Otherwise, test them: "
        "ask one exam-style question at a time, wait for their answer, "
        "then mark it out of 10 and point out every mistake precisely."
    ),
    "🧒 Explain Like I'm 5": (
        "You explain everything with very simple words, short "
        "sentences and fun everyday comparisons a child would understand."
    ),
}

BADGES = [
    ("🌱", "First Steps", "Complete your first study session",
     lambda p: p["sessions"] >= 1),
    ("🔥", "On Fire", "Reach a 3-day study streak",
     lambda p: p["best_streak"] >= 3),
    ("🏆", "Quiz Master", "Score 100% on a quiz",
     lambda p: any(q["percentage"] == 100 for q in p["quiz_scores"])),
    ("🧠", "Memory Builder", "Master 25 flashcards",
     lambda p: p["cards_known"] >= 25),
    ("🧭", "Explorer", "Try 5 different study modes",
     lambda p: len(p["modes_used"]) >= 5),
    ("🧑‍🏫", "Teacher", "Score 80+ on a Feynman Check",
     lambda p: p["feynman_best"] >= 80),
    ("⭐", "Scholar", "Complete 25 study sessions",
     lambda p: p["sessions"] >= 25),
]

DEFAULT_PROGRESS = {
    "sessions": 0,
    "streak": 0,
    "best_streak": 0,
    "last_study_date": None,
    "quiz_scores": [],
    "cards_known": 0,
    "modes_used": [],
    "feynman_best": 0,
    "topics": [],
}


# =========================================================
# PROGRESS (SAVED IN EACH STUDENT'S OWN BROWSER)
# =========================================================

# Progress lives in a cookie on the student's device, so every friend
# who opens the app gets their own private streak, badges and scores.

def encode_progress(progress):

    compact = {
        **progress,
        "quiz_scores": [q["percentage"] for q in progress["quiz_scores"]][-30:],
        "topics": [topic[:60] for topic in progress["topics"][:8]],
    }

    raw = json.dumps(compact, separators=(",", ":")).encode("utf-8")

    return base64.urlsafe_b64encode(raw).decode("ascii")


def load_progress():

    progress = json.loads(json.dumps(DEFAULT_PROGRESS))

    try:
        saved = json.loads(
            base64.urlsafe_b64decode(st.context.cookies[PROGRESS_COOKIE])
        )
        saved["quiz_scores"] = [
            {"percentage": int(score)} for score in saved.get("quiz_scores", [])
        ]
        progress.update(
            {key: value for key, value in saved.items() if key in DEFAULT_PROGRESS}
        )
    except (KeyError, ValueError, TypeError):
        pass

    return progress


def save_progress():

    # The cookie is written at the end of the run (see save_progress_cookie).
    st.session_state.progress_dirty = True


def earned_badges(progress):

    return {
        name
        for _, name, _, check in BADGES
        if check(progress)
    }


def current_streak(progress):

    last = progress["last_study_date"]

    if last in (
        date.today().isoformat(),
        (date.today() - timedelta(days=1)).isoformat(),
    ):
        return progress["streak"]

    return 0


def record_activity(mode=None, topic=None):

    progress = st.session_state.progress
    badges_before = earned_badges(progress)

    today = date.today()
    last = progress["last_study_date"]

    if last != today.isoformat():

        if last == (today - timedelta(days=1)).isoformat():
            progress["streak"] += 1
        else:
            progress["streak"] = 1

        progress["last_study_date"] = today.isoformat()

    progress["best_streak"] = max(
        progress["best_streak"],
        progress["streak"],
    )

    if mode:
        progress["sessions"] += 1

        if mode not in progress["modes_used"]:
            progress["modes_used"].append(mode)

    if topic:
        progress["topics"].insert(0, topic[:80])
        progress["topics"] = progress["topics"][:20]

    save_progress()

    for icon, name, _, _ in BADGES:
        if name in earned_badges(progress) - badges_before:
            st.toast(f"Badge unlocked: {name}", icon=icon)


# =========================================================
# SESSION STATE
# =========================================================

session_defaults = {
    "study_input": "",
    "latest": None,
    "history": [],
    "quiz": None,
    "quiz_id": 0,
    "quiz_result": None,
    "cards": [],
    "card_index": 0,
    "card_flipped": False,
    "card_hint": False,
    "cards_known_set": set(),
    "chat_messages": [],
    "source_text": "",
    "source_name": "",
}

for state_key, state_value in session_defaults.items():
    if state_key not in st.session_state:
        st.session_state[state_key] = state_value

if "progress" not in st.session_state:
    st.session_state.progress = load_progress()


# =========================================================
# CALLBACKS
# =========================================================

def start_app():

    st.session_state.started = True


def go_home():

    st.session_state.started = False


def new_study():

    st.session_state.started = True
    st.session_state.study_input = ""
    st.session_state.latest = None
    st.session_state.quiz = None
    st.session_state.quiz_result = None
    st.session_state.quiz_id += 1


def clear_history():

    st.session_state.history = []


def clear_chat():

    st.session_state.chat_messages = []


def reset_progress():

    st.session_state.progress = json.loads(json.dumps(DEFAULT_PROGRESS))
    save_progress()


def move_card(step):

    cards = st.session_state.cards
    known = st.session_state.cards_known_set
    only_review = st.session_state.get("review_only", False)

    index = st.session_state.card_index

    for _ in range(len(cards)):
        index = (index + step) % len(cards)

        if not (only_review and index in known):
            break

    st.session_state.card_index = index
    st.session_state.card_flipped = False
    st.session_state.card_hint = False


def flip_card():

    st.session_state.card_flipped = not st.session_state.card_flipped


def show_hint():

    st.session_state.card_hint = True


def mark_card(known):

    index = st.session_state.card_index
    known_set = st.session_state.cards_known_set

    if known and index not in known_set:
        known_set.add(index)
        st.session_state.progress["cards_known"] += 1
        save_progress()

    if not known:
        known_set.discard(index)

    move_card(1)


def shuffle_cards():

    random.shuffle(st.session_state.cards)
    st.session_state.cards_known_set = set()
    st.session_state.card_index = 0
    st.session_state.card_flipped = False
    st.session_state.card_hint = False


# =========================================================
# MOTIVATIONAL QUOTES & DAILY STUDY HACKS
# =========================================================

QUOTES = [
    ("The expert in anything was once a beginner.", "Helen Hayes"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("Education is the most powerful weapon you can use to change the world.", "Nelson Mandela"),
    ("The beautiful thing about learning is that nobody can take it away from you.", "B.B. King"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("Success is the sum of small efforts, repeated day in and day out.", "Robert Collier"),
    ("Live as if you were to die tomorrow. Learn as if you were to live forever.", "Mahatma Gandhi"),
    ("The more that you read, the more things you will know.", "Dr. Seuss"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("An investment in knowledge pays the best interest.", "Benjamin Franklin"),
    ("Seek knowledge from the cradle to the grave.", "Proverb"),
    ("Tell me and I forget. Teach me and I remember. Involve me and I learn.", "Benjamin Franklin"),
    ("Mistakes are proof that you are trying.", "Jennifer Lim"),
    ("Small progress is still progress.", "Unknown"),
    ("Push yourself, because no one else is going to do it for you.", "Unknown"),
]

QUOTES_SHOWN = 5
QUOTE_SECONDS = 7

TIPS_SHOWN = 4
TIP_SECONDS = 9

STUDY_TIPS = [
    ("🍅", "The Pomodoro Technique", "Study for 25 minutes, then take a 5-minute break. After four rounds, rest for 20 minutes."),
    ("🔁", "Spaced Repetition", "Review new material after 1 day, 3 days and 7 days to lock it into long-term memory."),
    ("🧠", "Active Recall", "Close your notes and try to remember. Testing yourself beats re-reading every time."),
    ("🧑‍🏫", "Teach It Back", "If you can explain it simply to a friend, you really understand it. Try the Feynman Check!"),
    ("🗺️", "Map It Out", "Mind maps help your brain see how ideas connect instead of memorising isolated facts."),
    ("🔀", "Interleave Topics", "Mix different subjects in one session. It feels harder, but you remember more."),
    ("😴", "Sleep On It", "Your brain consolidates memories while you sleep. An all-nighter erases much of your hard work."),
    ("📵", "Deep Focus Mode", "Put your phone in another room. Even a silent phone on the desk reduces concentration."),
    ("✍️", "Write By Hand", "Writing key points by hand helps you process and remember them better than typing."),
    ("🎯", "Set One Goal", "Start each session with one clear goal, like 'I can explain how DNS works'."),
]

# A fresh random set of quotes and study hacks every time the app is opened.
if "quotes" not in st.session_state:
    st.session_state.quotes = random.sample(QUOTES, QUOTES_SHOWN)

if "tips" not in st.session_state:
    st.session_state.tips = random.sample(STUDY_TIPS, TIPS_SHOWN)


def section_header(icon, title, subtitle=""):

    st.html(
        '<div class="sec-head">'
        f'<span class="sec-icon">{icon}</span>'
        f'<div><div class="sec-title">{title}</div>'
        f'<div class="sec-sub">{subtitle}</div></div>'
        "</div>"
    )


def step_label(number, text):

    st.html(f'<div class="step-label"><span>{number}</span>{text}</div>')


def empty_state(emoji, title, subtitle, steps=None):

    steps_html = ""

    if steps:
        steps_html = '<div class="steps">' + "".join(
            f'<div class="step"><span>{i}</span>{step}</div>'
            for i, step in enumerate(steps, start=1)
        ) + "</div>"

    st.html(
        '<div class="empty">'
        f'<div class="empty-emoji">{emoji}</div>'
        f'<div class="empty-title">{title}</div>'
        f'<div class="empty-sub">{subtitle}</div>'
        f"{steps_html}"
        "</div>"
    )


# =========================================================
# SIDEBAR
# =========================================================

load_dotenv()


def find_api_key():

    key = os.getenv("GROQ_API_KEY")

    if not key:
        try:
            key = st.secrets["GROQ_API_KEY"]
        except Exception:
            key = None

    return key


with st.sidebar:

    st.html(
        '<div class="brand">'
        '<div class="brand-logo">🎓</div>'
        '<div><div class="brand-name">Study Buddy</div>'
        '<div class="brand-sub">Your AI learning workspace</div></div>'
        "</div>"
    )

    progress = st.session_state.progress

    st.html(
        '<div class="profile">'
        '<div class="profile-top">'
        '<div class="avatar">🧑‍🎓</div>'
        '<div><div class="p-rank">My Study Stats</div>'
        '<div class="p-level">Keep your streak alive!</div></div>'
        "</div>"
        '<div class="mini-stats">'
        f"<div><b>🔥 {current_streak(progress)}</b><small>streak</small></div>"
        f"<div><b>🎖 {len(earned_badges(progress))}</b><small>badges</small></div>"
        f"<div><b>📚 {progress['sessions']}</b><small>sessions</small></div>"
        f"<div><b>🧩 {len(progress['quiz_scores'])}</b><small>quizzes</small></div>"
        "</div>"
        "</div>"
    )

    if st.session_state.get("started"):
        st.button(
            "🏠 Home",
            width="stretch",
            on_click=go_home,
        )

    with st.container(horizontal=True, gap="small"):

        st.button(
            "＋ New",
            width="stretch",
            on_click=new_study,
            help="Start a fresh study session",
        )

        st.button(
            "🗑 Clear",
            width="stretch",
            on_click=clear_history,
            help="Clear this visit's study history",
        )

    st.selectbox(
        "🌍 Answer language",
        LANGUAGES,
        key="language",
    )

    with st.expander("📲 Install on your phone"):
        st.markdown(
            "Tap the **📲 Install app** button at the bottom-right of the screen.\n\n"
            "Or do it from your browser:\n\n"
            "**Android (Chrome):** tap the **⋮** at the top-right of Chrome "
            "(the browser, not the app) → **Install app**.\n\n"
            "**iPhone (Safari):** tap **Share** ⬆️ → **Add to Home Screen**.\n\n"
            "**Laptop (Chrome / Edge):** click the install icon at the right "
            "end of the address bar."
        )


api_key = find_api_key()

if not api_key:

    # Only the app owner can fix this, by adding GROQ_API_KEY to .env or the host's secrets.
    empty_state(
        "🛠️",
        "Study Buddy is taking a short break",
        "The app isn't fully set up yet. Please try again a little later.",
    )

    st.stop()


client = Groq(api_key=api_key, max_retries=1)


def call_groq(**request):

    # The free Groq plan allows a limited number of tokens per minute, shared by
    # everyone using the app. When it is reached, wait as asked and try again.
    for attempt in range(6):

        try:
            return client.chat.completions.create(**request)

        except RateLimitError as error:

            if attempt == 5:
                raise

            match = re.search(r"try again in (?:(\d+)m)?([\d.]+)(ms|s)", str(error))
            wait = 5.0

            if match:
                minutes, amount, unit = match.groups()
                wait = int(minutes or 0) * 60 + float(amount) / (1000 if unit == "ms" else 1)

            time.sleep(min(wait + 0.5, 20))

MODEL = "openai/gpt-oss-120b"

# The main model only reads text, so photos are read by a vision model first.
VISION_MODEL = "qwen/qwen3.8-27b"


# =========================================================
# AI HELPERS
# =========================================================

def system_prompt(extra=""):

    return (
        "You are AI Study Buddy, a professional, friendly and "
        "accurate educational tutor. "
        f"Always write your answers in {st.session_state.language}. "
        f"{extra}"
    )


def ask_ai(prompt, json_mode=False, temperature=0.4):

    messages = [
        {
            "role": "system",
            "content": system_prompt(
                "When asked for JSON, keep all JSON keys in English."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    # Groq sometimes rejects long JSON answers ("Failed to validate JSON").
    # Retry once in JSON mode, then let parse_json clean up a plain answer.
    attempts = [{"type": "json_object"}, {"type": "json_object"}, None] if json_mode else [None]

    for i, response_format in enumerate(attempts):

        options = {"response_format": response_format} if response_format else {}

        if json_mode:
            # Quizzes, cards and maps need little "thinking"; this halves token use.
            options["reasoning_effort"] = "low"

        try:
            response = call_groq(
                model=MODEL,
                messages=messages,
                temperature=temperature,
                **options,
            )
        except BadRequestError as error:
            if "json" in str(error).lower() and i < len(attempts) - 1:
                continue
            raise

        return response.choices[0].message.content or ""


def stream_ai(messages, temperature=0.5):

    stream = call_groq(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content

        if delta:
            yield delta


def parse_json(raw_text):

    cleaned = raw_text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if match:
        cleaned = match.group(0)

    return json.loads(cleaned)


def read_photo(file_bytes):

    # Shrink big phone photos so they stay within the API's image size limit.
    image = Image.open(io.BytesIO(file_bytes))
    image = ImageOps.exif_transpose(image).convert("RGB")
    image.thumbnail((1600, 1600))

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")

    response = call_groq(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "This is a photo of a student's study material "
                            "(notes, a textbook page, a worksheet or a diagram). "
                            "Transcribe all the text exactly, keeping headings and "
                            "lists. If there are diagrams, charts or formulas, "
                            "describe them clearly. Reply with the content only."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                    },
                ],
            }
        ],
        temperature=0.1,
    )

    text = response.choices[0].message.content or ""

    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


@st.cache_data(show_spinner=False)
def extract_text(file_name, file_bytes):

    if file_name.lower().endswith(IMAGE_TYPES):
        return read_photo(file_bytes)

    if file_name.lower().endswith(".pdf"):

        reader = PdfReader(io.BytesIO(file_bytes))

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    return file_bytes.decode("utf-8", errors="ignore")


def add_history(mode, question, answer):

    st.session_state.history.insert(
        0,
        {
            "mode": mode,
            "question": question,
            "answer": answer,
            "time": datetime.now().strftime("%d %b %Y - %I:%M %p"),
        },
    )


# =========================================================
# PROMPT BUILDER
# =========================================================

def build_prompt(
    selected_mode,
    text,
    selected_difficulty,
    selected_length,
    source="",
    extra=None,
):

    extra = extra or {}

    source_block = ""

    if source:
        source_block = (
            "\n\nUse this study material as your main source:\n"
            f'"""\n{source}\n"""\n'
        )

    if selected_mode == "💡 Explain Topic":

        return f"""
Explain the following topic to a {selected_difficulty} learner.

Topic:
{text}
{source_block}
Response length: {selected_length}

Requirements:
- Start with a simple definition.
- Explain step by step with clear headings.
- Give real-world examples.
- Highlight important concepts in bold.
- Add a "Common mistakes" section.
- Finish with a short recap.
"""

    if selected_mode == "📝 Summarize Notes":

        return f"""
Summarize the following notes for a {selected_difficulty} learner.

Notes:
{text}
{source_block}
Response length: {selected_length}

Requirements:
- Identify the main ideas and use clear headings.
- Remove unnecessary details.
- Use bullet points and highlight key terms.
- Add a small table of key terms and definitions.
- Finish with 5 quick revision points.
"""

    if selected_mode == "❓ Generate Quiz":

        count = extra.get("questions", 5)

        return f"""
Create exactly {count} multiple-choice questions about:

{text}
{source_block}
Difficulty: {selected_difficulty}

Return ONLY valid JSON with exactly this structure:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": 0,
            "explanation": "One short sentence"
        }}
    ]
}}

Rules:
- Exactly {count} questions with exactly 4 options each.
- If the study material is short, also ask about closely related core ideas
  of the same topic so you still reach {count} different questions.
- answer is the index (0, 1, 2 or 3) of the correct option.
- Vary the position of the correct answer.
- Keep each explanation to one short sentence (under 20 words).
"""

    if selected_mode == "🃏 Flashcards":

        return f"""
Create exactly 10 revision flashcards about:

{text}
{source_block}
Difficulty: {selected_difficulty}

Return ONLY valid JSON with exactly this structure:

{{
    "cards": [
        {{
            "front": "A short question or term",
            "back": "A clear, concise answer",
            "hint": "A small clue that does not give the answer away"
        }}
    ]
}}

Rules:
- Focus on the most important concepts.
- Keep the front short (one line).
- Keep the back under 40 words.
"""

    if selected_mode == "🗺️ Mind Map":

        return f"""
Create a mind map of the topic:

{text}
{source_block}
Difficulty: {selected_difficulty}

Return ONLY valid JSON with exactly this structure:

{{
    "center": "Main topic",
    "branches": [
        {{
            "name": "Sub-topic",
            "children": ["Key idea", "Key idea", "Key idea"]
        }}
    ]
}}

Rules:
- 4 to 6 branches.
- 2 to 4 children per branch.
- Every label must be 5 words or fewer.
"""

    if selected_mode == "📅 Study Plan":

        days = extra.get("days", 7)
        minutes = extra.get("minutes", 60)

        return f"""
Create a {days}-day study plan for a {selected_difficulty} learner
who can study {minutes} minutes per day.

Goal / topic:
{text}
{source_block}
Response length: {selected_length}

Requirements:
- Start with a one-paragraph overview of the learning path.
- For each day, give: a title, learning goals, activities with
  time estimates, and a small self-check task.
- Build difficulty gradually and schedule revision days.
- Present the daily schedule as a Markdown table first, then details.
- Finish with tips for staying motivated.
"""

    if selected_mode == "🎭 Explain with Analogy":

        return f"""
Explain the following topic to a {selected_difficulty} learner
using creative analogies from everyday life.

Topic:
{text}
{source_block}
Response length: {selected_length}

Requirements:
- Give 3 different, memorable analogies (e.g. cooking, sports, city life).
- For the best analogy, add a Markdown table mapping each part of the
  analogy to the real concept.
- Explain where the analogy breaks down.
- Finish with a one-sentence "remember it like this" summary.
"""

    # Feynman Check
    return f"""
A {selected_difficulty} student is trying to explain the topic
"{extra.get('topic', '')}" in their own words (the Feynman technique).
{source_block}
Student's explanation:
\"\"\"
{text}
\"\"\"

Evaluate how well they understand the topic.

Return ONLY valid JSON with exactly this structure:

{{
    "score": 0,
    "verdict": "One encouraging sentence summarising their understanding",
    "strengths": ["What they explained well"],
    "gaps": ["Important ideas they missed or explained vaguely"],
    "misconceptions": ["Anything that is factually wrong"],
    "improved_explanation": "A clear, simple model explanation in Markdown"
}}

Rules:
- score is an integer from 0 to 100.
- Be honest but kind. Use empty lists when there is nothing to say.
"""


# =========================================================
# RESPONSE PARSERS
# =========================================================

def parse_quiz(raw_text, expected):

    questions = parse_json(raw_text).get("questions", [])

    valid = []

    for question in questions:

        options = question.get("options", [])

        if not question.get("question") or len(options) != 4:
            continue

        answer_index = int(question.get("answer", -1))

        if answer_index not in (0, 1, 2, 3):
            continue

        question["answer"] = answer_index
        valid.append(question)

    if not valid:
        raise ValueError("No valid questions returned.")

    return {"questions": valid[:expected]}


QUIZ_BATCH = 15


def generate_quiz(prompt, count):

    # Big quizzes are written in batches of up to 15 questions: smaller
    # answers are faster and far less likely to come back broken or short.
    questions = []

    for _ in range(count // QUIZ_BATCH + 5):

        missing = count - len(questions)

        if missing <= 0:
            break

        batch = min(missing, QUIZ_BATCH)
        batch_prompt = re.sub(rf"(?i)exactly {count}\b", f"exactly {batch}", prompt)
        batch_prompt = re.sub(rf"reach {count}\b", f"reach {batch}", batch_prompt)

        if questions:
            batch_prompt += (
                "\n\nThese questions already exist. Do NOT repeat or rephrase them:\n"
                + "\n".join(f"- {q['question']}" for q in questions)
            )

        try:
            new_questions = parse_quiz(ask_ai(batch_prompt, json_mode=True), batch)["questions"]
        except (ValueError, KeyError, TypeError):
            if questions:
                continue
            raise

        seen = {q["question"].strip().lower() for q in questions}
        questions += [
            q for q in new_questions
            if q["question"].strip().lower() not in seen
        ]

    if not questions:
        raise ValueError("No valid questions returned.")

    return {"questions": questions[:count]}


def parse_cards(raw_text):

    cards = [
        card
        for card in parse_json(raw_text).get("cards", [])
        if card.get("front") and card.get("back")
    ]

    if not cards:
        raise ValueError("No valid flashcards returned.")

    return cards


def parse_mindmap(raw_text):

    data = parse_json(raw_text)

    if not data.get("center") or not data.get("branches"):
        raise ValueError("Mind map is missing its center or branches.")

    return data


def parse_feynman(raw_text):

    data = parse_json(raw_text)

    data["score"] = max(0, min(100, int(data.get("score", 0))))

    return data


# =========================================================
# RENDERERS
# =========================================================

def mindmap_to_dot(data):

    def quote(label):
        return '"' + str(label).replace('"', "'") + '"'

    colors = [
        "#6366F1", "#0EA5E9", "#10B981",
        "#F59E0B", "#EC4899", "#A855F7",
    ]

    lines = [
        "digraph G {",
        'graph [rankdir=LR, bgcolor="transparent", pad=0.3, nodesep=0.25, ranksep=0.7];',
        'node [shape=box, style="rounded,filled", fontname="Helvetica", fontcolor="white", color="none"];',
        'edge [color="#A5B4FC", arrowhead=none, penwidth=1.8];',
        f'root [label={quote(data["center"])}, fillcolor="#4C1D95", fontsize=18, shape=ellipse];',
    ]

    for i, branch in enumerate(data["branches"]):

        color = colors[i % len(colors)]
        branch_id = f"b{i}"

        lines.append(
            f'{branch_id} [label={quote(branch.get("name", ""))}, fillcolor="{color}", fontsize=14];'
        )
        lines.append(f"root -> {branch_id};")

        for j, child in enumerate(branch.get("children", [])):

            child_id = f"b{i}c{j}"

            lines.append(
                f'{child_id} [label={quote(child)}, fillcolor="#F8FAFC", '
                f'fontcolor="#1E293B", color="{color}", penwidth=2, fontsize=12];'
            )
            lines.append(f"{branch_id} -> {child_id};")

    lines.append("}")

    return "\n".join(lines)


def mindmap_to_markdown(data):

    lines = [f"# {data['center']}", ""]

    for branch in data["branches"]:

        lines.append(f"- **{branch.get('name', '')}**")

        for child in branch.get("children", []):
            lines.append(f"  - {child}")

    return "\n".join(lines)


def score_ring(percentage, label, sublabel):

    degrees = percentage * 3.6

    return (
        '<div class="score-ring" style="background:conic-gradient('
        f'#FDE68A 0deg, #F472B6 {degrees}deg, rgba(255,255,255,0.18) {degrees}deg)">'
        f'<div class="score-inner"><b>{label}</b><small>{sublabel}</small></div>'
        "</div>"
    )


def score_verdict(percentage):

    if percentage == 100:
        return "🏆 Perfect score!", "Flawless. You've completely mastered this topic."
    if percentage >= 80:
        return "🔥 Brilliant work!", "You clearly know this well. Review the few you missed."
    if percentage >= 50:
        return "💪 Good effort!", "You're getting there. Use the mistake coach to close the gaps."

    return "🌱 Keep growing!", "Every expert started here. Review the explanations and try again."


def render_feynman(data):

    score = data["score"]
    title, _ = score_verdict(score)

    st.html(
        '<div class="score-card">'
        + score_ring(score, score, "out of 100")
        + f'<div><div class="score-title">{title}</div>'
        f'<div class="score-sub">{html.escape(data.get("verdict", ""))}</div></div>'
        "</div>"
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(
            "**✅ Strengths**\n\n"
            + "\n".join(f"- {s}" for s in data.get("strengths", []) or ["—"])
        )

    with col2:
        st.warning(
            "**🧩 Gaps**\n\n"
            + "\n".join(f"- {s}" for s in data.get("gaps", []) or ["None, nice work!"])
        )

    with col3:
        st.error(
            "**⚠️ Misconceptions**\n\n"
            + "\n".join(f"- {s}" for s in data.get("misconceptions", []) or ["None found"])
        )

    st.markdown("### ✨ A clearer explanation")
    st.markdown(data.get("improved_explanation", ""))


def to_plain_text(markdown_text):

    # Turns Markdown into clean text that opens nicely in Notepad or on a phone.
    lines = []

    for line in markdown_text.splitlines():

        stripped = line.strip()

        if re.fullmatch(r"\|?[\s:|-]+\|?", stripped) and "-" in stripped:
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)", stripped)

        if heading:
            title = heading.group(2).strip()
            lines += ["", title.upper() if len(heading.group(1)) <= 2 else title, ""]
            continue

        line = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m.group(1) or m.group(2), line)
        line = re.sub(r"(?<!\w)[*_](\S.*?)[*_](?!\w)", r"\1", line)
        line = line.replace("`", "")
        line = re.sub(r"^(\s*)[-*+]\s+", r"\1• ", line)

        if stripped.startswith("|"):
            line = "  ".join(cell.strip() for cell in stripped.strip("|").split("|"))

        lines.append(line)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def render_latest():

    latest = st.session_state.latest

    if not latest:

        empty_state(
            "🚀",
            "Your AI study material will appear here",
            "Pick a mode, type a topic and press Generate.",
            ["Choose a mode", "Enter a topic", "Press Generate"],
        )

        return

    kind = latest["kind"]
    data = latest["data"]

    st.html(f'<span class="mode-badge">{latest.get("mode", "")}</span>')

    if kind == "text":

        st.markdown(data)

        st.download_button(
            "⬇ Download Study Notes",
            data=to_plain_text(data),
            file_name="AI_Study_Buddy_Notes.txt",
            mime="text/plain",
            width="stretch",
        )

    elif kind == "quiz":

        empty_state(
            "🧩",
            "Your quiz is ready!",
            "Open the <b>🧩 Quiz</b> tab above to test yourself.",
        )

    elif kind == "cards":

        empty_state(
            "🃏",
            f"{len(data)} flashcards are ready!",
            "Open the <b>🃏 Flashcards</b> tab above to start revising.",
        )

    elif kind == "mindmap":

        st.graphviz_chart(mindmap_to_dot(data), width="stretch")

        outline = mindmap_to_markdown(data)

        with st.expander("📄 Text outline"):
            st.markdown(outline)

        st.download_button(
            "⬇ Download Mind Map Outline",
            data=to_plain_text(outline),
            file_name="AI_Study_Buddy_Mind_Map.txt",
            mime="text/plain",
            width="stretch",
        )

    elif kind == "feynman":

        render_feynman(data)


# =========================================================
# PAGE HELPERS (SCROLLING + PWA)
# =========================================================

def run_in_page(script):

    # Runs our own trusted JavaScript in the main app page from a hidden frame.
    st.session_state.script_nonce = st.session_state.get("script_nonce", 0) + 1
    nonce = st.session_state.script_nonce

    with st.container(key=f"pagejs_{nonce}"):
        st.iframe(f"<script>/* {nonce} */\n{script}</script>", height=1)


def scroll_to(key):

    run_in_page(
        f"""
const doc = window.parent.document;
let tries = 0;
const go = () => {{
    const el = doc.querySelector(".st-key-{key}");
    if (el) {{
        el.scrollIntoView({{ behavior: "smooth", block: "start" }});
    }} else if (tries++ < 20) {{
        setTimeout(go, 150);
    }}
}};
setTimeout(go, 300);
"""
    )


PWA_SCRIPT = """
const w = window.parent;
const d = w.document;

if (!w.__studyBuddyPwa) {
    w.__studyBuddyPwa = true;

    const appUrl = w.location.href.split(/[?#]/)[0].replace(/[^/]*$/, "");
    const base = appUrl + "app/static/";

    const add = (tag, attrs) => {
        const el = d.createElement(tag);
        Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
        d.head.appendChild(el);
    };

    add("link", { rel: "manifest", href: base + "manifest.json" });
    add("link", { rel: "apple-touch-icon", href: base + "apple-touch-icon.png" });
    add("meta", { name: "theme-color", content: "#6D28D9" });
    add("meta", { name: "mobile-web-app-capable", content: "yes" });
    add("meta", { name: "apple-mobile-web-app-capable", content: "yes" });
    add("meta", { name: "apple-mobile-web-app-title", content: "Study Buddy" });
    add("meta", { name: "apple-mobile-web-app-status-bar-style", content: "black-translucent" });

    const installed =
        w.matchMedia("(display-mode: standalone)").matches || w.navigator.standalone;

    const ua = w.navigator.userAgent;
    const isIOS = /iphone|ipad|ipod/i.test(ua);
    const isAndroid = /android/i.test(ua);

    const helpText = () => {
        if (!w.isSecureContext) {
            return "To install, open the app's secure https:// link in Chrome or Safari.";
        }
        if (isIOS) {
            return "In Safari, tap the Share button ⬆️ at the bottom of the screen, then choose “Add to Home Screen”.";
        }
        if (isAndroid) {
            return "In Chrome, tap the ⋮ button at the top-right of the browser (not inside the app), then choose “Install app” or “Add to Home screen”.";
        }
        return "In Chrome or Edge, click the install icon at the right end of the address bar, or open the browser's ⋮ menu (top-right of the browser window) and choose “Install Study Buddy”.";
    };

    const showHelp = () => {
        let box = d.getElementById("sb-install-help");
        if (box) { box.remove(); return; }

        box = d.createElement("div");
        box.id = "sb-install-help";
        box.style.cssText = [
            "position:fixed", "left:18px", "bottom:76px", "z-index:999999",
            "max-width:290px", "padding:14px 16px", "border-radius:16px",
            "font:500 14px/1.5 'Plus Jakarta Sans',sans-serif", "color:#1E1B4B",
            "background:#FFFFFF", "box-shadow:0 18px 40px -12px rgba(30,27,75,.45)",
        ].join(";");
        box.innerHTML = "<b>📲 Install Study Buddy</b><br>";
        box.appendChild(d.createTextNode(helpText()));

        const close = d.createElement("div");
        close.textContent = "Got it";
        close.style.cssText = "margin-top:10px;font-weight:700;color:#7C3AED;cursor:pointer";
        close.onclick = () => box.remove();
        box.appendChild(close);

        d.body.appendChild(box);
    };

    const showInstallButton = () => {
        if (installed || d.getElementById("sb-install")) return;

        const button = d.createElement("button");
        button.id = "sb-install";
        button.textContent = "📲 Install app";
        button.style.cssText = [
            "position:fixed", "left:18px", "bottom:18px", "z-index:999999",
            "padding:12px 20px", "border:none", "border-radius:999px",
            "font:600 15px 'Plus Jakarta Sans',sans-serif", "color:#fff", "cursor:pointer",
            "background:linear-gradient(135deg,#6366F1,#DB2777)",
            "box-shadow:0 12px 30px -10px rgba(124,58,237,.8)",
        ].join(";");

        button.onclick = async () => {
            const prompt = w.__studyBuddyInstall;

            if (!prompt) {
                showHelp();
                return;
            }

            prompt.prompt();
            const choice = await prompt.userChoice;
            w.__studyBuddyInstall = null;

            if (choice.outcome === "accepted") button.remove();
        };

        d.body.appendChild(button);
    };

    // Show the button straight away; it uses the browser's own install
    // prompt when available and otherwise explains how to install.
    showInstallButton();

    w.addEventListener("beforeinstallprompt", (event) => {
        event.preventDefault();
        w.__studyBuddyInstall = event;
    });

    w.addEventListener("appinstalled", () => {
        const button = d.getElementById("sb-install");
        if (button) button.remove();
    });
}
"""


# =========================================================
# HERO
# =========================================================

# The robot tutor is shared by the hero scene and the chat welcome.
BOT_DEFS = """
<defs>
<linearGradient id="sbBoard" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#1E1B4B"/><stop offset="1" stop-color="#312E81"/>
</linearGradient>
<linearGradient id="sbBot" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#E0E7FF"/>
</linearGradient>
<linearGradient id="sbFace" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#4F46E5"/><stop offset="1" stop-color="#9333EA"/>
</linearGradient>
</defs>
"""

BOT_SVG = """
<ellipse class="sb-bot-shadow" cx="95" cy="222" rx="36" ry="7" fill="rgba(15,12,50,0.28)"/>
<g class="sb-bot">
<line x1="95" y1="58" x2="95" y2="42" stroke="#E0E7FF" stroke-width="4" stroke-linecap="round"/>
<circle class="sb-antenna" cx="95" cy="37" r="6" fill="#F472B6"/>
<rect x="53" y="78" width="9" height="18" rx="4" fill="#A5B4FC"/>
<rect x="128" y="78" width="9" height="18" rx="4" fill="#A5B4FC"/>
<rect x="60" y="58" width="70" height="56" rx="18" fill="url(#sbBot)"/>
<rect x="68" y="66" width="54" height="40" rx="12" fill="url(#sbFace)"/>
<g class="sb-eyes">
<circle cx="84" cy="84" r="5.5" fill="#FFFFFF"/>
<circle cx="106" cy="84" r="5.5" fill="#FFFFFF"/>
</g>
<path d="M86 95 Q95 102 104 95" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round"/>
<rect x="88" y="113" width="14" height="9" rx="3" fill="#C7D2FE"/>
<rect x="66" y="120" width="58" height="64" rx="18" fill="url(#sbBot)"/>
<circle class="sb-chest" cx="95" cy="146" r="8" fill="#22D3EE"/>
<rect x="80" y="162" width="30" height="6" rx="3" fill="#C7D2FE"/>
<rect x="48" y="128" width="18" height="38" rx="9" fill="#E0E7FF"/>
<g class="sb-arm">
<rect x="118" y="127" width="42" height="12" rx="6" fill="#E0E7FF"/>
<line x1="158" y1="133" x2="196" y2="106" stroke="#FDE68A" stroke-width="4.5" stroke-linecap="round"/>
<circle cx="197" cy="105" r="4" fill="#F472B6"/>
</g>
<rect x="74" y="186" width="42" height="14" rx="7" fill="#A5B4FC"/>
</g>
"""

SCENE_CSS = """.sb-bot {
    animation: botFloat 3.2s ease-in-out infinite;
}

@keyframes botFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-9px); }
}

.sb-bot-shadow {
    transform-box: fill-box;
    transform-origin: center;
    animation: shadowPulse 3.2s ease-in-out infinite;
}

@keyframes shadowPulse {
    50% { transform: scaleX(0.75); opacity: 0.55; }
}

.sb-eyes {
    transform-box: fill-box;
    transform-origin: center;
    animation: blink 4s infinite;
}

@keyframes blink {
    0%, 92%, 100% { transform: scaleY(1); }
    95% { transform: scaleY(0.1); }
}

.sb-antenna {
    animation: antennaGlow 1.6s ease-in-out infinite;
}

@keyframes antennaGlow {
    50% { fill: #FDE68A; }
}

.sb-chest {
    animation: chestPulse 2s ease-in-out infinite;
}

@keyframes chestPulse {
    50% { fill: #A78BFA; }
}

.sb-arm {
    transform-box: view-box;
    transform-origin: 122px 133px;
    animation: pointAtBoard 2.4s ease-in-out infinite;
}

@keyframes pointAtBoard {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(-14deg); }
}

.sb-head {
    transform-box: fill-box;
    transform-origin: 50% 90%;
    animation: nod 3s ease-in-out infinite;
}

@keyframes nod {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(5deg); }
}

.chalk, .draw, .bulb, .bubble {
    animation-duration: 9s;
    animation-iteration-count: infinite;
    animation-fill-mode: both;
}

.chalk { animation-name: chalkIn; }
.c1 { animation-delay: 0.3s; }
.c2 { animation-delay: 1.3s; }
.c3 { animation-delay: 3.6s; }

@keyframes chalkIn {
    0% { opacity: 0; transform: translateX(-8px); }
    6% { opacity: 1; transform: translateX(0); }
    85% { opacity: 1; }
    92%, 100% { opacity: 0; }
}

.draw {
    stroke-dasharray: 160;
    animation-name: drawLine;
    animation-delay: 2.3s;
}

@keyframes drawLine {
    0% { stroke-dashoffset: 160; opacity: 1; }
    12% { stroke-dashoffset: 0; }
    85% { stroke-dashoffset: 0; opacity: 1; }
    92%, 100% { stroke-dashoffset: 0; opacity: 0; }
}

.bulb, .bubble {
    transform-box: fill-box;
    transform-origin: center;
    animation-name: popIn;
}

.bulb { animation-delay: 4.1s; }
.bubble { animation-delay: 4.6s; }

@keyframes popIn {
    0% { opacity: 0; transform: scale(0.3); }
    5% { opacity: 1; transform: scale(1.15); }
    8% { transform: scale(1); }
    85% { opacity: 1; transform: scale(1); }
    92%, 100% { opacity: 0; transform: scale(0.8); }
}

.float-icon {
    transform-box: fill-box;
    transform-origin: center;
    animation: floaty 6s ease-in-out infinite;
}

.f2 { animation-delay: -1.5s; }
.f3 { animation-delay: -3s; }
.f4 { animation-delay: -4.5s; }

@keyframes floaty {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-10px) scale(1.06); }
}
"""

WAVE_CSS = """
.sb-arm { animation: wave 1.6s ease-in-out infinite; }

@keyframes wave {
    0%, 100% { transform: rotate(0deg); }
    25% { transform: rotate(-28deg); }
    50% { transform: rotate(-8deg); }
    75% { transform: rotate(-28deg); }
}
"""


def svg_image(svg, css_class, alt):

    # st.html strips inline <svg>, so animated SVGs are embedded as images.
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")

    return f'<img class="{css_class}" alt="{alt}" src="data:image/svg+xml;base64,{encoded}">'


HERO_SCENE = f"""
<svg viewBox="0 0 420 320" xmlns="http://www.w3.org/2000/svg">
<style>{SCENE_CSS}</style>
{BOT_DEFS}
<ellipse cx="215" cy="300" rx="195" ry="13" fill="rgba(15,12,50,0.22)"/>

<g>
<rect x="150" y="14" width="258" height="158" rx="18" fill="#FDE68A"/>
<rect x="158" y="22" width="242" height="142" rx="12" fill="url(#sbBoard)"/>
<text class="chalk c1" x="206" y="58" fill="#FFFFFF" font-size="22" font-weight="700" font-family="Outfit, sans-serif">E = mc²</text>
<text class="chalk c2" x="206" y="90" fill="#C7D2FE" font-size="17" font-weight="600" font-family="Outfit, sans-serif">a² + b² = c²</text>
<path class="draw" d="M206 146 L232 128 L258 137 L286 108 L314 118" stroke="#F472B6" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<text class="chalk c3" x="326" y="148" fill="#34D399" font-size="24" font-weight="800">✓</text>
<g class="bulb">
<circle cx="360" cy="62" r="17" fill="#FDE68A"/>
<rect x="353" y="78" width="14" height="10" rx="3" fill="#E0E7FF"/>
<path d="M360 36 V30 M384 62 H390 M336 62 H330 M377 45 L381 41 M343 45 L339 41" stroke="#FDE68A" stroke-width="3" stroke-linecap="round"/>
</g>
</g>

{BOT_SVG}

<g>
<rect x="246" y="266" width="150" height="12" rx="6" fill="#FDE68A"/>
<rect x="258" y="278" width="8" height="22" rx="3" fill="#FCD34D"/>
<rect x="376" y="278" width="8" height="22" rx="3" fill="#FCD34D"/>
<rect x="290" y="222" width="62" height="48" rx="22" fill="#F472B6"/>
<g class="sb-head">
<circle cx="321" cy="200" r="23" fill="#FCD9B8"/>
<path d="M298 197 Q300 175 321 175 Q342 175 344 197 Q334 186 321 188 Q308 186 298 197 Z" fill="#1E1B4B"/>
<circle cx="313" cy="202" r="2.6" fill="#1E1B4B"/>
<circle cx="329" cy="202" r="2.6" fill="#1E1B4B"/>
<path d="M314 211 Q321 216 328 211" stroke="#1E1B4B" stroke-width="2.4" fill="none" stroke-linecap="round"/>
<polygon points="321,160 350,171 321,182 292,171" fill="#1E1B4B"/>
<path d="M346 172 V188" stroke="#FDE68A" stroke-width="2.5"/>
<circle cx="346" cy="190" r="3" fill="#FDE68A"/>
</g>
<rect x="298" y="254" width="46" height="13" rx="3" fill="#FFFFFF"/>
<line x1="321" y1="254" x2="321" y2="267" stroke="#C7D2FE" stroke-width="2"/>
</g>

<g class="bubble">
<rect x="214" y="186" width="72" height="30" rx="15" fill="#FFFFFF"/>
<polygon points="276,212 290,222 270,214" fill="#FFFFFF"/>
<text x="250" y="206" text-anchor="middle" fill="#4C1D95" font-size="13" font-weight="800" font-family="Outfit, sans-serif">Aha! 💡</text>
</g>

<text class="float-icon f1" x="18" y="266" font-size="26">📚</text>
<text class="float-icon f2" x="14" y="62" font-size="22">⚛️</text>
<text class="float-icon f3" x="392" y="222" font-size="22">✏️</text>
<text class="float-icon f4" x="200" y="262" font-size="20">🧪</text>
</svg>
"""

MINI_BOT = f"""
<svg viewBox="40 22 170 208" xmlns="http://www.w3.org/2000/svg">
<style>{SCENE_CSS}{WAVE_CSS}</style>
{BOT_DEFS}{BOT_SVG}
</svg>
"""

SUBJECTS = [
    "⚛️ Physics",
    "💻 Coding",
    "🧬 Biology",
    "➗ Maths",
    "🏛️ History",
    "🧪 Chemistry",
]

hour = datetime.now().hour

if hour < 12:
    greeting = "Good morning"
elif hour < 17:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

quotes_html = "".join(
    f'<div class="quote" style="animation-delay:{i * QUOTE_SECONDS}s">'
    f'<div class="q-body">{html.escape(text)}</div>'
    f'<div class="q-author">— {html.escape(author)}</div>'
    "</div>"
    for i, (text, author) in enumerate(st.session_state.quotes)
)

dots_html = "".join(
    f'<span style="animation-delay:{i * QUOTE_SECONDS}s"></span>'
    for i in range(QUOTES_SHOWN)
)

tips_html = "".join(
    f'<div class="tip-item" style="animation-delay:{i * TIP_SECONDS}s">'
    f'<div class="tip-title">{icon} {title}</div>'
    f'<div class="tip-text">{text}</div>'
    "</div>"
    for i, (icon, title, text) in enumerate(st.session_state.tips)
)

subjects_html = "".join(
    f"<span>{subject}</span>" for subject in SUBJECTS + SUBJECTS[:1]
)

def spark_html(positions):

    return "".join(
        f'<span class="spark" style="left:{left}%;top:{top}%;animation-delay:{delay}s"></span>'
        for left, top, delay in positions
    )


def save_progress_cookie():

    if st.session_state.pop("progress_dirty", False):
        value = encode_progress(st.session_state.progress)
        run_in_page(
            f'window.parent.document.cookie = "{PROGRESS_COOKIE}={value}; '
            'path=/; max-age=31536000; SameSite=Lax";'
        )


def page_scripts():

    save_progress_cookie()
    run_in_page(PWA_SCRIPT)


# =========================================================
# LANDING SCREEN (fits one screen, "Get started" opens the app)
# =========================================================

if not st.session_state.get("started"):

    with st.container(key="hero_box"):

        left, right = st.columns([1.1, 1], gap="large", vertical_alignment="center")

        with left:

            st.html(
                f"""
<div class="hero-left">
{spark_html([(1, 2, 0), (88, 4, 1.4), (96, 70, 2.6)])}
<span class="hero-eyebrow">✨ {greeting}, learner!</span>
<div class="hero-title">What will you <span class="hl">master</span> today?</div>
<div class="hero-rotate">Today, let's learn
<span class="rotator"><span class="rot-track">{subjects_html}</span></span></div>
<p class="hero-sub">Your AI tutor explains, quizzes, maps and checks any topic with you, step by step.</p>
</div>
"""
            )

            st.button(
                "🚀 Get started",
                key="get_started",
                type="primary",
                on_click=start_app,
            )

            st.html(
                f"""
<div class="quote-card">
<div class="quote-mark">“</div>
<div class="quotes">{quotes_html}</div>
<div class="q-dots">{dots_html}</div>
</div>
"""
            )

        with right:

            st.html(
                f"""
<div class="hero-right">
{spark_html([(4, 88, 0.8), (94, 6, 2.0)])}
{svg_image(HERO_SCENE, "scene", "An AI robot tutor teaching a student at a chalkboard")}
<div class="tip">
<div class="tip-label">💡 Study hack</div>
<div class="tips">{tips_html}</div>
</div>
</div>
"""
            )

    page_scripts()
    st.stop()


# =========================================================
# COMPACT HEADER (inside the app)
# =========================================================

st.html(
    f"""
<div class="mini-hero">
<div>
<div class="mini-greet">✨ {greeting}, learner!</div>
<div class="mini-title">What will you <span class="hl">master</span> today?</div>
</div>
{svg_image(MINI_BOT, "mini-hero-bot", "Your AI tutor")}
</div>
"""
)


# =========================================================
# MAIN TABS
# =========================================================

TAB_STUDIO = "🏠 Study Studio"
TAB_CHAT = "💬 Tutor Chat"
TAB_QUIZ = "🧩 Quiz"
TAB_CARDS = "🃏 Flashcards"
TAB_PROGRESS = "📈 Progress"
TAB_HISTORY = "📚 History"

# After generating a quiz or flashcards, jump straight to that tab.
jump_to_tab = st.session_state.pop("goto_tab", None)

if jump_to_tab:
    st.session_state.main_tab = jump_to_tab

(
    dashboard_tab,
    chat_tab,
    quiz_tab,
    cards_tab,
    progress_tab,
    history_tab,
) = st.tabs(
    [TAB_STUDIO, TAB_CHAT, TAB_QUIZ, TAB_CARDS, TAB_PROGRESS, TAB_HISTORY],
    key="main_tab",
    on_change="rerun",
)

if jump_to_tab:
    scroll_to("main_tab")

if st.session_state.pop("scroll_to_response", False):
    scroll_to("card_response")


# =========================================================
# DASHBOARD
# =========================================================

with dashboard_tab:

    # =====================================================
    # STUDY STUDIO CARD
    # =====================================================

    with st.container(border=True, key="card_studio"):

        section_header(
            "🎛️",
            "Study Studio",
            "Three quick steps to your personalised study material.",
        )

        step_label(1, "Pick your study mode")

        mode = st.pills(
            "Study mode",
            list(MODES),
            default="💡 Explain Topic",
            required=True,
            label_visibility="collapsed",
        ) or "💡 Explain Topic"

        st.html(
            f'<div class="mode-info"><b>{mode}</b>'
            f"<span>— {MODES[mode]}</span></div>"
        )

        step_label(2, "Set your level")

        control1, control2 = st.columns(2)

        with control1:
            difficulty = st.segmented_control(
                "Difficulty",
                ["Beginner", "Intermediate", "Advanced"],
                default="Beginner",
                required=True,
                format_func=lambda d: {
                    "Beginner": "🌱 Beginner",
                    "Intermediate": "🌿 Intermediate",
                    "Advanced": "🌳 Advanced",
                }[d],
                width="stretch",
            ) or "Beginner"

        with control2:
            response_length = st.segmented_control(
                "Response length",
                ["Short", "Medium", "Detailed"],
                default="Medium",
                required=True,
                format_func=lambda l: {
                    "Short": "⚡ Short",
                    "Medium": "📄 Medium",
                    "Detailed": "📚 Detailed",
                }[l],
                width="stretch",
            ) or "Medium"

        extra = {}

        if mode == "❓ Generate Quiz":
            extra["questions"] = st.slider("Number of questions", 3, 40, 5)

        elif mode == "📅 Study Plan":
            p1, p2 = st.columns(2)
            extra["days"] = p1.number_input("Days available", 1, 60, 7)
            extra["minutes"] = p2.number_input("Minutes per day", 15, 480, 60, step=15)

        elif mode == "🧑‍🏫 Feynman Check":
            extra["topic"] = st.text_input(
                "Which topic are you explaining?",
                placeholder="Example: How photosynthesis works",
            )

        if mode == "🧑‍🏫 Feynman Check":
            step_label(3, "Explain the topic in your own words")
            placeholder = "Pretend you're teaching a friend who has never heard of it..."
        else:
            step_label(3, "Tell your tutor what to study")
            placeholder = 'Type any topic or question, e.g. "How do vaccines work?"'

        # =================================================
        # STUDY MATERIAL UPLOAD
        # =================================================

        with st.expander("📎 Add your notes or photos (optional): PDF, TXT, MD, JPG, PNG"):

            uploads = st.file_uploader(
                "Upload lecture notes, book pages or photos of your notebook. "
                "You can pick several files at once.",
                type=["pdf", "txt", "md", *IMAGE_TYPES],
                accept_multiple_files=True,
            )

            photos = [f for f in uploads if f.name.lower().endswith(IMAGE_TYPES)]
            skipped = photos[MAX_PHOTOS:]
            files = [f for f in uploads if f not in skipped]

            if photos:
                with st.container(horizontal=True, gap="small"):
                    for photo in photos[:MAX_PHOTOS]:
                        st.image(photo, width=90)

            parts = []

            for file in files:

                try:
                    spinner = (
                        f"📷 Reading {file.name}..."
                        if file in photos
                        else f"📄 Reading {file.name}..."
                    )

                    with st.spinner(spinner):
                        text = extract_text(file.name, file.getvalue())

                except Exception as upload_error:
                    text = ""
                    st.error(f"Could not read **{file.name}**: {upload_error}")

                if text.strip():
                    parts.append(f"--- {file.name} ---\n{text.strip()}")
                elif file in photos:
                    st.warning(f"No readable text found in **{file.name}**.")

            if skipped:
                st.warning(
                    f"Only the first {MAX_PHOTOS} photos are used. "
                    f"{len(skipped)} photo(s) were skipped."
                )

            combined = "\n\n".join(parts)

            st.session_state.source_text = combined[:MAX_SOURCE_CHARS]

            if len(files) == 1:
                st.session_state.source_name = files[0].name
            else:
                st.session_state.source_name = f"{len(files)} files"

            if combined:
                st.success(
                    f"Using **{len(parts)} file(s)** "
                    f"({len(combined):,} characters) as your study source."
                )

                if len(combined) > MAX_SOURCE_CHARS:
                    st.caption(
                        f"Only the first {MAX_SOURCE_CHARS:,} "
                        "characters will be used."
                    )

        # =================================================
        # INPUT BOX WITH GENERATE BUTTON
        # =================================================

        with st.container(border=True, key="inputbox"):

            st.text_area(
                "Your topic or notes",
                key="study_input",
                placeholder=placeholder,
                height=130,
                label_visibility="collapsed",
            )

            with st.container(
                horizontal=True,
                horizontal_alignment="distribute",
                vertical_alignment="center",
            ):

                st.caption("💡 Be specific for better results.")

                generate_button = st.button(
                    "Generate",
                    key="generate_btn",
                    type="primary",
                )

    # =====================================================
    # GENERATION + RESPONSE
    # =====================================================

    st.write("")

    with st.container(border=True, key="card_response"):

        section_header("🧠", "AI Response", "Your personalised study material.")

        clean_input = st.session_state.study_input.strip()
        source = st.session_state.source_text

        if generate_button and mode == "🧑‍🏫 Feynman Check" and not (
            clean_input and extra.get("topic", "").strip()
        ):

            st.warning("Enter the topic and your own explanation first.")
            render_latest()

        elif generate_button and not (clean_input or source):

            st.warning("Please enter a topic, notes or upload a file first.")
            render_latest()

        elif generate_button:

            topic_text = clean_input or f"the uploaded study material ({st.session_state.source_name})"

            prompt = build_prompt(
                mode,
                topic_text,
                difficulty,
                response_length,
                source,
                extra,
            )

            history_title = extra.get("topic") or topic_text

            try:

                if mode not in JSON_MODES:

                    scroll_to("card_response")

                    st.html(f'<span class="mode-badge">{mode}</span>')

                    answer = st.write_stream(
                        stream_ai(
                            [
                                {"role": "system", "content": system_prompt()},
                                {"role": "user", "content": prompt},
                            ],
                            temperature=0.4,
                        )
                    )

                    st.session_state.latest = {"kind": "text", "data": answer, "mode": mode}
                    add_history(mode, history_title, answer)
                    record_activity(mode, history_title)
                    st.session_state.scroll_to_response = True
                    st.rerun()

                scroll_to("card_response")

                spinner_text = "✨ AI is creating your study material..."

                if mode == "❓ Generate Quiz" and extra["questions"] > 15:
                    spinner_text = f"✨ Writing {extra['questions']} questions. This can take up to a minute..."

                with st.spinner(spinner_text):

                    if mode == "❓ Generate Quiz":
                        quiz = generate_quiz(prompt, extra["questions"])
                    else:
                        raw = ask_ai(prompt, json_mode=True)

                if mode == "❓ Generate Quiz":

                    st.session_state.quiz = quiz
                    st.session_state.quiz_id += 1
                    st.session_state.quiz_result = None
                    st.session_state.quiz_topic = history_title
                    st.session_state.latest = {"kind": "quiz", "data": None, "mode": mode}
                    add_history(mode, history_title, "Interactive quiz generated.")
                    record_activity(mode, history_title)
                    st.session_state.goto_tab = TAB_QUIZ

                elif mode == "🃏 Flashcards":

                    cards = parse_cards(raw)
                    st.session_state.cards = cards
                    st.session_state.card_index = 0
                    st.session_state.card_flipped = False
                    st.session_state.card_hint = False
                    st.session_state.cards_known_set = set()
                    st.session_state.latest = {"kind": "cards", "data": cards, "mode": mode}
                    add_history(
                        mode,
                        history_title,
                        "\n\n".join(f"**{c['front']}** — {c['back']}" for c in cards),
                    )
                    record_activity(mode, history_title)
                    st.session_state.goto_tab = TAB_CARDS

                elif mode == "🗺️ Mind Map":

                    mindmap = parse_mindmap(raw)
                    st.session_state.latest = {"kind": "mindmap", "data": mindmap, "mode": mode}
                    add_history(mode, history_title, mindmap_to_markdown(mindmap))
                    record_activity(mode, history_title)
                    st.session_state.scroll_to_response = True

                else:

                    feedback = parse_feynman(raw)
                    progress = st.session_state.progress
                    progress["feynman_best"] = max(progress["feynman_best"], feedback["score"])
                    st.session_state.latest = {"kind": "feynman", "data": feedback, "mode": mode}
                    add_history(
                        mode,
                        history_title,
                        f"Score: {feedback['score']}/100 — {feedback.get('verdict', '')}",
                    )
                    record_activity(mode, history_title)
                    st.session_state.scroll_to_response = True

                st.rerun()

            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as parse_error:

                st.error("The AI returned an invalid response. Please generate it again.")
                st.caption(f"Technical detail: {parse_error}")

            except Exception as error:

                st.error("😕 Sorry, the AI had trouble with that. Please press **Generate** again.")
                st.caption(f"Technical detail: {error}")

        else:

            render_latest()

    # =====================================================
    # FEATURE CARDS
    # =====================================================

    st.write("")

    section_header("🚀", "Why students love Study Buddy", "Tools that make studying feel like a game.")

    st.html(
        """
<div class="features">
<div class="feature c1"><div class="f-icon">🗺️</div><div class="f-title">Visual Mind Maps</div>
<div class="f-text">See how every idea in a topic connects in one colourful picture.</div></div>
<div class="feature c2"><div class="f-icon">🧑‍🏫</div><div class="f-title">Feynman Check</div>
<div class="f-text">Teach it back in your own words and get a score on your understanding.</div></div>
<div class="feature c3"><div class="f-icon">💬</div><div class="f-title">4 Tutor Personalities</div>
<div class="f-text">Chat with a Socratic coach, a strict examiner or a friendly tutor.</div></div>
<div class="feature c4"><div class="f-icon">📎</div><div class="f-title">Your Own Notes</div>
<div class="f-text">Upload a PDF and turn your lecture notes into quizzes and flashcards.</div></div>
</div>
"""
    )


# =========================================================
# AI TUTOR CHAT TAB
# =========================================================

CHAT_SUGGESTIONS = [
    "🎯 Quiz me on SQL joins, one question at a time",
    "🤔 Why is the sky blue?",
    "📐 Help me understand derivatives",
    "📝 Give me tips for my exams next week",
]


def queue_chat(message):

    st.session_state.pending_chat = message


with chat_tab:

    with st.container(border=True, key="card_chat"):

        section_header("💬", "Chat with your AI Tutor", "Ask anything. Pick a personality that fits your mood.")

        c1, c2, c3 = st.columns([1.4, 1.4, 1], vertical_alignment="bottom")

        with c1:
            persona = st.selectbox("Tutor personality", list(TUTOR_PERSONAS))
            st.caption(PERSONA_HINTS[persona])

        with c2:
            use_source = st.toggle(
                "Answer from my uploaded notes",
                value=bool(st.session_state.source_text),
                disabled=not st.session_state.source_text,
                help="Upload notes or photos in the Study Studio to enable this.",
            )

        with c3:
            st.button("🧹 Clear chat", width="stretch", on_click=clear_chat)

        chat_box = st.container(
            height=420 if st.session_state.chat_messages else "content",
            border=False,
        )

        with chat_box:

            if not st.session_state.chat_messages:

                st.html(
                    '<div class="tutor-hello">'
                    + svg_image(MINI_BOT, "mini-bot", "Your AI tutor waving hello") +
                    '<div><div class="hello-bubble">Hi! I\'m your AI tutor 👋</div>'
                    '<div class="hello-sub">Type any question in the box below, or tap an idea to get started.</div></div>'
                    "</div>"
                )

                with st.container(horizontal=True, horizontal_alignment="center", gap="small"):
                    for i, suggestion in enumerate(CHAT_SUGGESTIONS):
                        st.button(
                            suggestion,
                            key=f"suggest_{i}",
                            on_click=queue_chat,
                            args=(suggestion[2:],),
                        )

            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🤖"):
                    st.markdown(message["content"])

        user_message = (
            st.chat_input("Ask your tutor anything...")
            or st.session_state.pop("pending_chat", None)
        )

    if user_message:

        st.session_state.chat_messages.append(
            {"role": "user", "content": user_message}
        )

        extra_instructions = TUTOR_PERSONAS[persona]

        if use_source and st.session_state.source_text:
            extra_instructions += (
                "\n\nBase your answers on this study material "
                "and say when something is not covered by it:\n"
                f'"""\n{st.session_state.source_text}\n"""'
            )

        messages = [
            {"role": "system", "content": system_prompt(extra_instructions)}
        ] + st.session_state.chat_messages[-20:]

        with chat_box:

            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(user_message)

            with st.chat_message("assistant", avatar="🤖"):
                try:
                    reply = st.write_stream(stream_ai(messages, temperature=0.6))
                except Exception as error:
                    reply = f"⚠️ Something went wrong: {error}"
                    st.error(reply)

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": reply}
        )

        record_activity()
        st.rerun()


# =========================================================
# QUIZ TAB
# =========================================================

with quiz_tab:

    if not st.session_state.quiz:

        with st.container(border=True, key="card_quiz_empty"):
            empty_state(
                "🧩",
                "No quiz yet. Ready to test yourself?",
                "Go to <b>🏠 Study Studio</b>, pick <b>❓ Generate Quiz</b>, enter a topic and generate.",
                ["Pick a topic", "Answer the questions", "See your score"],
            )

    else:

        questions = st.session_state.quiz["questions"]

        section_header(
            "🧩",
            f"Quiz: {html.escape(st.session_state.get('quiz_topic', 'Your topic')[:70])}",
            f"{len(questions)} questions • choose one answer for each",
        )

        user_answers = []

        with st.form(key=f"quiz_form_{st.session_state.quiz_id}", border=False):

            for index, question in enumerate(questions):

                with st.container(border=True, key=f"card_q{index}"):

                    st.html(
                        '<div class="q-head">'
                        f'<span class="q-num">{index + 1}</span>'
                        f'<span class="q-text">{html.escape(question["question"])}</span>'
                        "</div>"
                    )

                    user_answers.append(
                        st.radio(
                            "Choose your answer",
                            question["options"],
                            index=None,
                            key=f"quiz_{st.session_state.quiz_id}_{index}",
                            label_visibility="collapsed",
                        )
                    )

            submit_quiz = st.form_submit_button(
                "✅ Submit Quiz",
                type="primary",
                width="stretch",
            )

        if submit_quiz:

            if None in user_answers:

                st.warning("Please answer all questions first.")

            else:

                details = []

                for index, question in enumerate(questions):

                    correct = question["options"][question["answer"]]
                    selected = user_answers[index]

                    details.append(
                        {
                            "number": index + 1,
                            "question": question["question"],
                            "selected": selected,
                            "correct": correct,
                            "is_correct": selected == correct,
                            "explanation": question.get(
                                "explanation", "No explanation available."
                            ),
                        }
                    )

                score = sum(d["is_correct"] for d in details)
                percentage = int(score / len(questions) * 100)

                first_submit = st.session_state.quiz_result is None

                st.session_state.quiz_result = {
                    "score": score,
                    "total": len(questions),
                    "percentage": percentage,
                    "details": details,
                    "review": None,
                }

                if first_submit:
                    st.session_state.progress["quiz_scores"].append(
                        {
                            "topic": st.session_state.get("quiz_topic", "Quiz")[:60],
                            "percentage": percentage,
                            "date": date.today().isoformat(),
                        }
                    )
                    record_activity()

                    if percentage == 100:
                        st.balloons()

        if st.session_state.quiz_result:

            result = st.session_state.quiz_result
            title, message = score_verdict(result["percentage"])

            st.write("")

            st.html(
                '<div class="score-card">'
                + score_ring(result["percentage"], f"{result['percentage']}%", f"{result['score']}/{result['total']}")
                + f'<div><div class="score-title">{title}</div>'
                f'<div class="score-sub">{message}</div>'
                f'<div class="hero-chips"><span class="chip">✅ {result["score"]} correct</span>'
                f'<span class="chip">❌ {result["total"] - result["score"]} to review</span></div></div>'
                "</div>"
            )

            st.write("")

            for detail in result["details"]:

                with st.expander(
                    f"{'✅' if detail['is_correct'] else '❌'}  Question {detail['number']}: "
                    f"{detail['question'][:80]}",
                    expanded=not detail["is_correct"],
                ):

                    if not detail["is_correct"]:
                        st.error("**Your answer:** " + detail["selected"])

                    st.success("**Correct answer:** " + detail["correct"])
                    st.caption("💡 " + detail["explanation"])

            mistakes = [d for d in result["details"] if not d["is_correct"]]

            if mistakes:

                st.write("")

                if st.button("🧠 Coach me on my mistakes", type="primary", width="stretch"):

                    mistake_text = "\n".join(
                        f"- Q: {d['question']} | My answer: {d['selected']} "
                        f"| Correct: {d['correct']}"
                        for d in mistakes
                    )

                    with st.spinner("Analysing your mistakes..."):
                        try:
                            result["review"] = ask_ai(
                                "I got these quiz questions wrong:\n"
                                f"{mistake_text}\n\n"
                                "For each one, explain why my answer was wrong, "
                                "why the correct answer is right, and give a memory "
                                "trick. Then list the weak areas I should revise "
                                "and suggest 2 practice questions (with answers "
                                "hidden at the end)."
                            )
                        except Exception as error:
                            st.error(f"Something went wrong: {error}")

                if result.get("review"):
                    with st.container(border=True, key="card_review"):
                        section_header("🧠", "Your personal mistake review", "Learn from every wrong answer.")
                        st.markdown(result["review"])


# =========================================================
# FLASHCARDS TAB
# =========================================================

with cards_tab:

    cards = st.session_state.cards

    if not cards:

        with st.container(border=True, key="card_cards_empty"):
            empty_state(
                "🃏",
                "No flashcards yet",
                "Go to <b>🏠 Study Studio</b>, pick <b>🃏 Flashcards</b>, enter a topic and generate a deck.",
                ["Generate a deck", "Flip &amp; recall", "Master every card"],
            )

    else:

        known_set = st.session_state.cards_known_set
        index = st.session_state.card_index % len(cards)
        card = cards[index]

        section_header(
            "🃏",
            "Flip Flashcards",
            f"Card {index + 1} of {len(cards)} • Mastered {len(known_set)}",
        )

        st.progress(len(known_set) / len(cards))

        if len(known_set) == len(cards):
            st.success("🎉 You've mastered every card in this deck!")

        if st.session_state.card_flipped:
            side, content, css_class = "Answer", card["back"], "flashcard back"
        else:
            side, content, css_class = "Question", card["front"], "flashcard"

        status = " • ✅ mastered" if index in known_set else ""

        st.html(
            f'<div class="{css_class}">'
            f'<span class="side">{side} {index + 1}/{len(cards)}{status}</span>'
            f"{html.escape(content)}"
            '<span class="tap">Press 🔄 Flip to turn the card</span>'
            "</div>"
        )

        if st.session_state.card_hint and card.get("hint") and not st.session_state.card_flipped:
            st.info(f"💡 Hint: {card['hint']}")

        n1, n2, n3, n4 = st.columns(4)

        n1.button("⬅ Previous", width="stretch", on_click=move_card, args=(-1,))
        n2.button("🔄 Flip", width="stretch", type="primary", on_click=flip_card)
        n3.button("💡 Hint", width="stretch", on_click=show_hint, disabled=not card.get("hint"))
        n4.button("Next ➡", width="stretch", on_click=move_card, args=(1,))

        k1, k2, k3 = st.columns(3)

        k1.button("✅ I knew it", width="stretch", on_click=mark_card, args=(True,))
        k2.button("🔁 Review again", width="stretch", on_click=mark_card, args=(False,))
        k3.button("🔀 Shuffle deck", width="stretch", on_click=shuffle_cards)

        st.toggle("Skip cards I've already mastered", key="review_only")

        deck_text = "\n\n".join(
            f"Q: {c['front']}\nA: {c['back']}" for c in cards
        )

        st.download_button(
            "⬇ Download deck",
            data=deck_text,
            file_name="AI_Study_Buddy_Flashcards.txt",
            mime="text/plain",
            width="stretch",
        )


# =========================================================
# PROGRESS TAB
# =========================================================

with progress_tab:

    progress = st.session_state.progress
    scores = [q["percentage"] for q in progress["quiz_scores"]]
    average = f"{sum(scores) // len(scores)}%" if scores else "—"

    section_header("📈", "Your Learning Journey", "Saved on this computer")

    st.html(
        '<div class="stats">'
        f'<div class="stat"><div class="stat-icon">🔥</div><div><b>{current_streak(progress)}</b><small>Day streak</small></div></div>'
        f'<div class="stat"><div class="stat-icon">🎖</div><div><b>{len(earned_badges(progress))}/{len(BADGES)}</b><small>Badges</small></div></div>'
        f'<div class="stat"><div class="stat-icon">📚</div><div><b>{progress["sessions"]}</b><small>Study sessions</small></div></div>'
        f'<div class="stat"><div class="stat-icon">🎯</div><div><b>{average}</b><small>Average quiz score</small></div></div>'
        "</div>"
    )

    st.write("")

    section_header("🎖", "Badges", f"{len(earned_badges(progress))} of {len(BADGES)} unlocked")

    earned = earned_badges(progress)

    st.html(
        '<div class="badges">'
        + "".join(
            f'<div class="badge {"earned" if name in earned else "locked"}">'
            f'<div class="icon">{icon}</div>'
            f'<div class="name">{name}</div>'
            f'<div class="desc">{desc}</div>'
            "</div>"
            for icon, name, desc, _ in BADGES
        )
        + "</div>"
    )

    st.write("")

    left, right = st.columns([2, 1])

    with left:

        with st.container(border=True, key="card_chart"):

            section_header("📊", "Quiz scores", "Watch yourself improve over time.")

            if progress["quiz_scores"]:
                st.area_chart(
                    {"Score %": [q["percentage"] for q in progress["quiz_scores"]]},
                    y_label="Score %",
                    x_label="Quiz attempt",
                    color="#7C3AED",
                )
            else:
                empty_state("📊", "No quiz scores yet", "Complete a quiz to see your score trend.")

    with right:

        with st.container(border=True, key="card_topics"):

            section_header("🕘", "Recent topics", "What you've been studying.")

            if progress["topics"]:
                for topic in progress["topics"][:8]:
                    st.write(f"• {topic}")
            else:
                empty_state("🌱", "Nothing yet", "Your studied topics will appear here.")

    st.write("")

    with st.expander("⚠️ Reset progress"):
        st.write("This permanently deletes your streak, badges and quiz history.")
        st.button("Reset all progress", on_click=reset_progress)


# =========================================================
# HISTORY TAB
# =========================================================

with history_tab:

    if not st.session_state.history:

        with st.container(border=True, key="card_history_empty"):
            empty_state(
                "📚",
                "No study history yet",
                "Everything you generate in this session will be saved here.",
            )

    else:

        section_header("📚", "Study History", "Review and export your learning sessions from this visit.")

        search = st.text_input(
            "Search history",
            placeholder="🔎 Filter by topic or mode...",
            label_visibility="collapsed",
        )

        items = [
            item
            for item in st.session_state.history
            if search.lower() in (item["question"] + item["mode"]).lower()
        ]

        for item in items[:20]:

            with st.expander(f"{item['mode']} • {item['question'][:70]}  ·  {item['time']}"):

                st.markdown("**Your Input**")
                st.write(item["question"])

                st.markdown("**AI Response**")
                st.markdown(item["answer"])

        export = "\n\n---\n\n".join(
            f"## {item['mode']} — {item['question']}\n"
            f"*{item['time']}*\n\n{item['answer']}"
            for item in st.session_state.history
        )

        st.download_button(
            "⬇ Export all history",
            data=to_plain_text(export),
            file_name="AI_Study_Buddy_History.txt",
            mime="text/plain",
            width="stretch",
        )


# =========================================================
# FOOTER
# =========================================================

page_scripts()

st.html(
    '<div class="app-footer">Made with 💜 for curious minds · Powered by Groq ⚡ · '
    "AI can make mistakes, so double-check important facts.</div>"
)
