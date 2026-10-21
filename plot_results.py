"""
Plotting Script for Supplement Trial Analysis.
Generates clean visual charts with question titles at the top.
"""

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator

DB_PATH = "pubmed_supplements.db"
OUTPUT_DIR = "charts"


def classify_solubility(c_class):
    if not isinstance(c_class, str):
        return "Unclassified"
    c = c_class.lower()
    if any(term in c for term in ["fat-soluble", "omega-3", "lipid"]):
        return "Lipophilic (Fat-Soluble)"
    if any(term in c for term in ["water-soluble", "mineral", "amino acid"]):
        return "Hydrophilic / Polar"
    return "Other / Unclassified"


def save_chart(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"[Saved] -> {path}")


def plot_question_1(df):
    """Q1: When is the best time to take supplements?"""
    if "timing_window" not in df.columns:
        return
    counts = (
        df[df["timing_window"].isin(["Morning", "Evening"])]["timing_window"]
        .value_counts()
        .reindex(["Morning", "Evening"], fill_value=0)
    )
    if counts.sum() == 0:
        return

    plt.figure(figsize=(7, 6))
    ax = sns.barplot(
        x=counts.index,
        y=counts.values,
        hue=counts.index,
        palette=["#F4B942", "#4B6CB7"],
        legend=False,
    )
    for container in ax.containers:
        ax.bar_label(container, fontsize=12, fontweight="bold")
    plt.title(
        "Question 1: When is the best time to take supplements?",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Time of Day", fontsize=11, labelpad=10)
    plt.ylabel("Number of Trials", fontsize=11)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    save_chart("question_1_morning_vs_evening.png")


def plot_question_2(df):
    """Q2: Is there a cap?"""
    needed = {"absorption_limit_stated", "interactions_noted"}
    if not needed.issubset(df.columns):
        return

    def has_text(s):
        s = s.fillna("").astype(str).str.strip().str.lower()
        return ~s.isin(["", "none"])

    mentioned = has_text(df["absorption_limit_stated"]) | has_text(
        df["interactions_noted"]
    )
    counts = (
        mentioned.map({True: "Yes", False: "No"})
        .value_counts()
        .reindex(["Yes", "No"], fill_value=0)
    )
    if counts.sum() == 0:
        return

    plt.figure(figsize=(7, 6))
    ax = sns.barplot(
        x=counts.index,
        y=counts.values,
        hue=counts.index,
        palette=["#2E8B57", "#9AA5B1"],
        legend=False,
    )
    for container in ax.containers:
        ax.bar_label(container, fontsize=12, fontweight="bold")
    plt.title(
        "Question 2: Is there a cap? Can I take 20 supplements at once and absorb them all?",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel(
        "Trial states an absorption limit or interaction", fontsize=11, labelpad=10
    )
    plt.ylabel("Number of Trials", fontsize=11)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    save_chart("question_2_absorption_limits.png")


def plot_question_3(df):
    """Q3: Does morning mean before or after a meal for best absorption?"""
    if "administration_state" not in df.columns:
        return
    counts = (
        df[df["administration_state"].isin(["Fed", "Fasted"])]["administration_state"]
        .value_counts()
        .reindex(["Fed", "Fasted"], fill_value=0)
    )
    if counts.sum() == 0:
        return

    plt.figure(figsize=(7, 6))
    ax = sns.barplot(
        x=counts.index,
        y=counts.values,
        hue=counts.index,
        palette=["#E07A5F", "#3D85C6"],
        legend=False,
    )
    for container in ax.containers:
        ax.bar_label(container, fontsize=12, fontweight="bold")
    plt.title(
        "Question 3: Does morning mean before or after a meal for best absorption?",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel(
        "Administration State (Fed = with or after a meal, Fasted = before a meal or empty stomach)",
        fontsize=10,
        labelpad=10,
    )
    plt.ylabel("Number of Trials", fontsize=11)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    save_chart("question_3_fed_vs_fasted.png")


def milestone1_4():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database '{DB_PATH}' not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM supplement_trials_processed", con)
    con.close()

    if df.empty:
        print("Database table is empty.")
        return

    sns.set_theme(style="whitegrid")
    plot_question_1(df)
    plot_question_2(df)
    plot_question_3(df)
    print(f"\nCharts successfully generated and saved in the '{OUTPUT_DIR}/' folder!")


if __name__ == "__main__":
    milestone1_4()
