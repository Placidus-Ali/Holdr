import streamlit as st
from pathlib import Path
from rule_engine import load_data, assess


# PAGE SETTINGS
BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "Holdr.jpg"

st.set_page_config(
    page_title="Holdr",
    page_icon=str(LOGO_PATH),
    layout="centered"
)

# PAGE TITLE & LOGO
col1, col2 = st.columns([1, 6])
with col1:
    st.image(str(LOGO_PATH), width=70)
with col2:
    st.title("Holdr")

# LOAD DATA
try:
    (
        crops_df,
        moisture_df,
        recommendations_df,
        storage_df,
        duration_df
    ) = load_data()

except Exception as error:
    st.error("The application could not load the data files.")
    st.exception(error)
    st.stop()

# CROP SELECTION
crop = st.selectbox(
    "Crop",
    [
        "Maize",
        "Beans"
    ]
)

# VARIETY SELECTION
crop_rows = crops_df[crops_df["Crop"].astype(str).str.strip().str.lower()== crop.lower()]
varieties = (crop_rows["Variety"].astype(str).str.strip().tolist())

if not varieties:
    st.warning("No varieties have been added for this crop.")
    st.stop()

variety = st.selectbox("Variety / Type", varieties)

# MOISTURE INPUT
moisture = st.number_input(
    "Moisture level (%)", min_value=0.0, max_value=100.0, value=13.0, step=0.1,
    help=("Enter the moisture reading from your grain moisture meter.")
)
# DAYS SINCE HARVEST
days_since_harvest = st.number_input(
    "How many days ago was it harvested?", min_value=0, max_value=3650, value=3, step=1,
    help=("For example, enter 5 if the crop was harvested 5 days ago.")
)
# STORAGE METHOD
storage_rows = storage_df[storage_df["Crop"].astype(str).str.strip().str.lower() == crop.lower()]
storage_methods = (storage_rows["Storage Method"].astype(str).str.strip().tolist())
if not storage_methods:
    st.warning("No storage methods have been added for this crop.")
    st.stop()
storage_method = st.selectbox("Storage method", storage_methods)


# ASSESS BUTTON
st.divider()
if st.button("🔍 Assess Grain", type="primary", use_container_width=True):
    # Run rule engine
    result = assess(
        crop=crop,
        variety=variety,
        moisture=moisture,
        days_since_harvest = days_since_harvest,
        storage_method = storage_method
    )


    
    # RESULTS
    risk = result["risk_result"]["risk"]
    recommendation = result["risk_result"]["recommendation"]


    # MAIN RECOMMENDATION
    if risk == "Low":
        st.success(
            f"🟢 {recommendation.upper()}"
        )
    elif risk == "Medium":
        st.warning(
            f"🟡 {recommendation.upper()}"
        )
    elif risk == "High":
        st.error(
            f"🔴 {recommendation.upper()}"
        )
    else:
        st.info(
            f"ℹ️ {recommendation.upper()}"
        )

    
    # FARMER INFORMATION
    st.subheader("Your Assessment")
    col1, col2 = st.columns(2)
    with col1:
        st.write(
            f"**Crop:** {result['crop']}"
        )

        st.write(
            f"**Variety:** {result['variety']}"
        )

        st.write(
            f"**Moisture:** "
            f"{result['moisture']:.1f}%"
        )


    with col2:
        st.write(
            f"**Harvested:** "
            f"{result['days_since_harvest']} "
            f"days ago"
        )

        st.write(
            f"**Storage:** "
            f"{result['storage_method']}"
        )


    
    # MOISTURE RESULT
    st.subheader(
        "💧 Moisture Assessment"
    )

    moisture_result = result[
        "moisture_result"
    ]

    st.write(
        f"**Status:** "
        f"{moisture_result['status']}"
    )

    st.write(
        f"**Action:** "
        f"{moisture_result['action']}"
    )

    st.write(
        moisture_result["message"]
    )

    
    # RISK RESULT    
    st.subheader(
        "⚠️ Storage Risk"
    )

    risk_result = result[
        "risk_result"
    ]

    st.write(
        f"**Risk level:** "
        f"{risk_result['risk']}"
    )

    st.write(
        f"**Recommendation:** "
        f"{risk_result['recommendation']}"
    )

    st.write(
        f"**Reason:** "
        f"{risk_result['reason']}"
    )


    # STORAGE INFORMATION
    st.subheader(
        "📦 Storage Assessment"
    )

    storage_result = result[
        "storage_result"
    ]

    st.write(
        f"**Suitability:** "
        f"{storage_result['suitability']}"
    )

    st.write(
        f"**Storage risk:** "
        f"{storage_result['risk']}"
    )

    st.write(
        f"**Notes:** "
        f"{storage_result['notes']}"
    )

    
    # STORAGE DURATION
    duration_result = result[
        "duration_result"
    ]

    if duration_result["duration"]:

        st.subheader(
            "⏱️ Recommended Storage Duration"
        )

        st.write(
            "**Additional storage:** "
            f"{duration_result['duration']}"
        )

        if duration_result[
            "match"
        ] == "exact":

            st.success(
                "This recommendation is based on an exact Days Since Crop was Harvested ")

        elif duration_result[
            "match"
        ] == "closest":
            st.warning("The exact number of days since Harvest is not currently in the duration dataset.")
            st.write(
                "The system therefore used the closest available rule based on "
                f"{duration_result['based_on_days']} "
                "days since harvest."
            )


    else:
        st.info(
            duration_result["message"]
        )


   
    # DISCLAIMER    
    st.divider()
    st.caption(
        """
        Holdr is a rule-based agricultural decision-support system. Recommendations
        are based on the agricultural rules contained in the supplied datasets.
        """
    )

print("Deployment Completed")