import pandas as pd  # type: ignore[import]
import streamlit as st  # type: ignore[import]

st.set_page_config(page_title="Stabilus Gas Spring Finder", layout="wide")

@st.cache_data
def load_data(path="data.csv"):
    df = pd.read_csv(path, dtype=str)
    # normalize header names with fits
    df.columns = [c.strip() for c in df.columns]

    # convert numeric columns with comma decimal support
    numeric_cols = [
        "Extended Length (in)",
        "Compressed Length (in)",
        "Tube Dia (mm)",
        "Rod Dia (mm)",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(',', '.', regex=False)
                .str.replace(' ', '', regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def main():
    st.title("Stabilus Lift Support Reference")
    st.markdown(
        "Use the sliders and/or selects to filter by Extended Length, Compressed Length, Tube Diameter, and Rod Diameter. "
        "Matching Brand Numbers are shown below."
    )

    df = load_data("data.csv")

    if df.empty:
        st.error("No data loaded from data.csv. Check file path and content.")
        return

    numeric_cols = {
        "Extended Length (in)": "Extended Length",
        "Compressed Length (in)": "Compressed Length",
        "Tube Dia (mm)": "Tube Diameter",
        "Rod Dia (mm)": "Rod Diameter",
    }

    st.sidebar.header("Filter Options")

    def reset_filters():
        for col in numeric_cols:
            st.session_state[f"{col}_select"] = "All"

    st.sidebar.button("Reset Filters", on_click=reset_filters)

    filters = {}
    for col, label in numeric_cols.items():
        if col not in df.columns:
            continue
        values = sorted(df[col].dropna().unique())
        options = ["All"] + values
        selected = st.sidebar.selectbox(
            label,
            options,
            index=0,
            key=f"{col}_select",
        )
        filters[col] = selected

    filtered = df.copy()
    for col, selected in filters.items():
        if selected != "All":
            filtered = filtered[filtered[col] == selected]

    st.sidebar.write("**Results count:**", len(filtered))

    st.subheader("Filtered rows")
    st.dataframe(filtered)

    st.markdown("---")
    st.caption("Source: data.csv")


if __name__ == "__main__":
    main()
