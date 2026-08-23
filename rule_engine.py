from pathlib import Path
import re
import pandas as pd


# LOCATION OF DATA FILES
DATA_DIR = Path(__file__).resolve().parent / "data"

# LOAD ALL CSV FILES
def load_data():
    crops = pd.read_csv(DATA_DIR / "crop.csv")
    moisture = pd.read_csv(DATA_DIR / "moisture.csv")
    recommendations = pd.read_csv(DATA_DIR / "recomendation.csv")
    storage = pd.read_csv(DATA_DIR / "storage.csv")
    duration = pd.read_csv(DATA_DIR / "storage_duration.csv",Nencoding="cp1252")

    # Remove spaces around column names
    for df in [
        crops,
        moisture,
        recommendations,
        storage,
        duration
    ]:
        df.columns = df.columns.str.strip()

        # Remove unnecessary spaces from text
        for column in df.columns:
            if df[column].dtype == "object":
                df[column] = (df[column].astype(str).str.strip())

    return (
        crops,
        moisture,
        recommendations,
        storage,
        duration
    )


# NORMALIZE CROP NAMES
def normalize_crop(value):
    value = str(value).strip().lower()
    if value in ["maize", "corn"]:
        return "Maize"

    if value in ["beans", "bean", "cowpea"]:
        return "Beans"

    return value.title()


# NORMALIZE VARIETY NAMES
def normalize_variety(value):
    value = str(value).strip().lower()
    aliases = {
        "white maize": "White",
        "yellow maize": "Yellow",
        "brown beans": "Brown",
        "white beans": "White",
        "black-eyed beans": "Black-eyed cowpea",
        "black-eyed cowpea": "Black-eyed cowpea",
        "flint corn": "Flint corn (Indian corn)",

    }

    return aliases.get(
        value,
        str(value).strip()
    )


# CONVERT MOISTURE VALUES TO NUMBERS
def parse_bound(value):
    value = str(value).strip()
    value = value.replace("%", "")
    match = re.search(
        r"[-+]?\d+(?:\.\d+)?",
        value
    )

    if match:
        return float(
            match.group()
        )
    return None


# CHECK MOISTURE
def check_moisture(
    crop,
    variety,
    moisture_value,
    moisture_df
):
    crop = normalize_crop(crop)
    variety = normalize_variety(variety)

    # Find matching crop and variety
    subset = moisture_df[
        (
            moisture_df["Crop"]
            .map(normalize_crop)
            == crop
        )
        &
        (
            moisture_df[
                "Variety / Type"
            ]
            .astype(str)
            .str.strip()
            .str.lower()
            == variety.lower()
        )
    ].copy()

    # No matching rule
    if subset.empty:
        return {

            "status":
                "No rule available",

            "action":
                "Manual review required",

            "message":
                f"No moisture rule is available "
                f"for {crop} - {variety}."
        }

    # Check every moisture rule
    for _, row in subset.iterrows():
        minimum = parse_bound(
            row["Moisture Min (%)"]
        )

        maximum_text = str(
            row["Moisture Max (%)"]
        ).strip()

        maximum = parse_bound(
            maximum_text
        )

        # Example: >15
        if ">" in maximum_text:
            if (
                minimum is not None
                and moisture_value >= minimum
            ):

                return {

                    "status":
                        row["Status"],

                    "action":
                        row["Action"],

                    "message":
                        f"Moisture level is "
                        f"{moisture_value:.1f}%."
                }

        # Normal range
        else:
            if (
                minimum is not None
                and maximum is not None
                and minimum
                <= moisture_value
                <= maximum
            ):

                return {

                    "status":
                        row["Status"],

                    "action":
                        row["Action"],

                    "message":
                        f"Moisture level is "
                        f"{moisture_value:.1f}%."
                }

    # Moisture does not fall into any rule
    return {
        "status": "No rule available",
        "action": "Manual review required",
        "message": 
            f"No moisture rule covers "
            f"{moisture_value:.1f}%."
    }


# NORMALIZE STORAGE METHODS
def normalize_storage_method(value):
    value = str(value).strip().lower()
    aliases = {

        "hermetic bag":
            "hermetic",

        "hermetic":
            "hermetic",

        "pics bag":
            "pics bag",

        "sack":
            "sack",

        "silo":
            "silo",

        "warehouse":
            "warehouse",

        "traditional room":
            "traditional room"
    }

    return aliases.get(
        value,
        value
    )


# CHECK STORAGE METHOD
def check_storage(
    crop,
    storage_method,
    storage_df
):
    crop = normalize_crop(crop)
    method = normalize_storage_method(
        storage_method
    )

    subset = storage_df[
        (
            storage_df["Crop"]
            .map(normalize_crop)
            == crop
        )
        &
        (
            storage_df[
                "Storage Method"
            ]
            .map(normalize_storage_method)
            == method
        )
    ]

    if subset.empty:
        return {
            "suitability":
                "Unknown",

            "risk":
                "Unknown",

            "notes":
                "No storage rule is available."
        }

    row = subset.iloc[0]

    return {
        "suitability":
            row["Suitability"],

        "risk":
            row["Risk"],

        "notes":
            row["Notes"]
    }


# ASSESS STORAGE RISK
def assess_risk(
    moisture_result,
    storage_result
):

    moisture_status = str(
        moisture_result["status"]
    ).strip().lower()

    moisture_action = str(
        moisture_result["action"]
    ).strip().lower()

    storage_risk = str(
        storage_result["risk"]
    ).strip().lower()

    storage_suitability = str(
        storage_result["suitability"]
    ).strip().lower()


    # HIGH MOISTURE
    if (
        moisture_status == "high"
        or "dry" in moisture_action
    ):

        return {

            "risk":
                "High",

            "recommendation":
                "Dry before storage",

            "reason":
                "The moisture level is too high "
                "for safe storage under the "
                "current conditions."
        }


    # HIGH STORAGE RISK
    if (
        storage_risk == "high"
        or storage_risk == "very high"
    ):

        return {

            "risk":
                "High",

            "recommendation":
                "Improve storage",

            "reason":
                "The selected storage method "
                "has a high storage risk."
        }


    # SAFE STORAGE
    if (
        moisture_status == "safe"
        and storage_suitability == "high"
    ):

        return {

            "risk":
                "Low",

            "recommendation":
                "Store",

            "reason":
                "The moisture level is suitable "
                "and the selected storage method "
                "provides good protection."
        }


    # MODERATE MOISTURE
    if moisture_status == "moderate":

        return {

            "risk":
                "Medium",

            "recommendation":
                "Monitor or dry",

            "reason":
                "The moisture level is moderate. "
                "Further drying or monitoring "
                "is recommended before long-term "
                "storage."
        }


    # UNKNOWN
    return {

        "risk":
            "Unknown",

        "recommendation":
            "Manual review required",

        "reason":
            "There is not enough matching "
            "information in the current rules."
    }


# FIND STORAGE DURATION
def find_storage_duration(
    crop,
    moisture_result,
    storage_method,
    days_since_harvest,
    duration_df
):

    crop = normalize_crop(crop)

    method = normalize_storage_method(
        storage_method
    )

    # Match crop and storage method
    subset = duration_df[
        (
            duration_df["Crop"]
            .map(normalize_crop)
            == crop
        )
        &
        (
            duration_df[
                "Storage Method"
            ]
            .map(normalize_storage_method)
            == method
        )
    ].copy()


    if subset.empty:
        return {

            "duration":
                None,

            "match":
                "none",

            "message":
                "No storage-duration rule "
                "is available."
        }


    # Match moisture category
    moisture_status = str(
        moisture_result["status"]
    ).strip().lower()

    matching_rows = subset[
        subset[
            "Moisture Range"
        ]
        .astype(str)
        .str.lower()
        .str.contains(
            moisture_status,
            na=False
        )
    ]

    if not matching_rows.empty:
        subset = matching_rows


    # Convert days to numbers
    subset["DaysNum"] = pd.to_numeric(
        subset["Days Since Harvest"],
        errors="coerce"
    )

    subset = subset.dropna(
        subset=["DaysNum"]
    )


    if subset.empty:
        return {

            "duration":
                None,

            "match":
                "none",

            "message":
                "The storage-duration data "
                "could not be interpreted."
        }


    days_since_harvest = float(
        days_since_harvest
    )


    # EXACT MATCH
    exact = subset[
        subset["DaysNum"]
        == days_since_harvest
    ]


    if not exact.empty:
        row = exact.iloc[0]

        return {

            "duration":
                row["Additional Storage Days"],

            "match":
                "exact",

            "message":
                row["Recommended Action"]
        }


    
    # CLOSEST AVAILABLE RULE
    subset["difference"] = (
        subset["DaysNum"]
        - days_since_harvest
    ).abs()


    row = subset.loc[
        subset["difference"].idxmin()
    ]


    return {

        "duration":
            row["Additional Storage Days"],

        "match":
            "closest",

        "message":
            row["Recommended Action"],

        "based_on_days":
            int(row["DaysNum"])
    }


# MAIN ASSESSMENT FUNCTION
def assess(
    crop,
    variety,
    moisture,
    days_since_harvest,
    storage_method
):

    (
        crops,
        moisture_df,
        recommendations_df,
        storage_df,
        duration_df
    ) = load_data()


    # Check moisture
    moisture_result = check_moisture(
        crop,
        variety,
        float(moisture),
        moisture_df
    )


    # Check storage
    storage_result = check_storage(
        crop,
        storage_method,
        storage_df
    )


    # Determine risk/recommendation
    risk_result = assess_risk(
        moisture_result,
        storage_result
    )


    # Determine storage duration
    duration_result = find_storage_duration(
        crop,
        moisture_result,
        storage_method,
        float(days_since_harvest),
        duration_df
    )


    # Return everything to Streamlit
    return {

        "crop":
            normalize_crop(crop),

        "variety":
            variety,

        "moisture":
            float(moisture),

        "days_since_harvest":
            int(days_since_harvest),

        "storage_method":
            storage_method,

        "moisture_result":
            moisture_result,

        "storage_result":
            storage_result,

        "risk_result":
            risk_result,

        "duration_result":
            duration_result
    }
print("Everything is working")