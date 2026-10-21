"""
Milestone 1.3: Statistical Analysis & Analytical Querying (CSV Output Only).

Reads  : pubmed_supplements.db -> supplement_trials_processed
Writes : Saves analytical findings as clean CSV files in 'analysis_outputs/'

Usage:
    python analyze_supplements.py
"""

import os
import sqlite3
import pandas as pd

DB_PATH = "pubmed_supplements.db"
OUTPUT_DIR = "analysis_outputs"


def milestone1_3():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found. Run Milestone 1.2 first.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    con = sqlite3.connect(DB_PATH)

    print(f"Loading data from {DB_PATH} -> supplement_trials_processed...")
    try:
        df = pd.read_sql("SELECT * FROM supplement_trials_processed", con)
    except Exception as e:
        print(f"Error loading table: {e}")
        con.close()
        return

    con.close()

    if df.empty:
        print(
            "The 'supplement_trials_processed' table is empty. Process some abstracts first!"
        )
        return

    print(f"Loaded {len(df)} records. Running statistical aggregations...\n")

    # =========================================================================
    # QUESTION 1: Frequency distribution of timing windows by supplement class
    # =========================================================================
    if "chemical_class" in df.columns and "timing_window" in df.columns:
        q1_df = (
            df.groupby(["chemical_class", "timing_window"]).size().unstack(fill_value=0)
        )
        q1_path = os.path.join(OUTPUT_DIR, "q1_timing_distribution.csv")
        q1_df.to_csv(q1_path)
        print(f" [Saved] Q1 Timing Distribution -> {q1_path}")

    # =========================================================================
    # QUESTION 2: Absorption limits & saturation / transporter competition
    # =========================================================================
    if "absorption_limit_stated" in df.columns and "interactions_noted" in df.columns:
        limits_df = df[
            (
                df["absorption_limit_stated"].notnull()
                & (df["absorption_limit_stated"].str.lower() != "none")
            )
            | (
                df["interactions_noted"].notnull()
                & (df["interactions_noted"].str.lower() != "none")
            )
        ][
            [
                "pmid",
                "supplement_name",
                "absorption_limit_stated",
                "interactions_noted",
                "limit_evidence",
            ]
        ]

        q2_path = os.path.join(OUTPUT_DIR, "q2_absorption_limits_interactions.csv")
        limits_df.to_csv(q2_path, index=False)
        print(
            f" [Saved] Q2 Limits & Interactions -> {q2_path} ({len(limits_df)} records)"
        )

    # =========================================================================
    # QUESTION 3: Lipophilic vs. Hydrophilic Fed vs. Fasted Split
    # =========================================================================
    if "chemical_class" in df.columns and "administration_state" in df.columns:

        def classify_solubility(c_class):
            if not isinstance(c_class, str):
                return "Unclassified"
            c_class_lower = c_class.lower()
            if any(
                term in c_class_lower for term in ["fat-soluble", "omega-3", "lipid"]
            ):
                return "Lipophilic (Fat-Soluble)"
            elif any(
                term in c_class_lower
                for term in ["water-soluble", "mineral", "amino acid"]
            ):
                return "Hydrophilic / Polar"
            else:
                return "Other / Unclassified"

        df["solubility_group"] = df["chemical_class"].apply(classify_solubility)
        fed_fasted_df = df[df["administration_state"].isin(["Fed", "Fasted"])]

        if not fed_fasted_df.empty:
            q3_table = (
                pd.crosstab(
                    fed_fasted_df["solubility_group"],
                    fed_fasted_df["administration_state"],
                    normalize="index",
                )
                * 100
            )

            q3_path = os.path.join(
                OUTPUT_DIR, "q3_solubility_fed_fasted_percentage.csv"
            )
            q3_table.round(1).to_csv(q3_path)
            print(f" [Saved] Q3 Solubility Split Percentage -> {q3_path}")
        else:
            print(
                " [Notice] Question 3: No rows with explicit 'Fed' or 'Fasted' states found yet."
            )

    print(
        f"\nMilestone 1.3 complete! All analytical findings saved cleanly as CSVs in '{OUTPUT_DIR}/'."
    )


if __name__ == "__main__":
    milestone1_3()
