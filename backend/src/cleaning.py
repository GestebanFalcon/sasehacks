from pandas import DataFrame
import pandas as pd

# [account_id, time, rating, review_text]

def clean_df(df: DataFrame):
    """Might throw on type conversion idk"""

    print(df.head())
    df_cleaned = df.copy()

    #extract duplicate values
    df_cleaned["time"] = pd.to_datetime(df_cleaned["time"], errors="coerce")
    df_cleaned["rating"] = pd.to_numeric(df_cleaned["rating"], errors="coerce")

    df_cleaned = (
        df_cleaned.sort_values("time")
        .drop_duplicates(subset=["account_id"], keep="last") #drops repeated ids, most recent kept?
        .reset_index(drop=True)
    )

    # drop no text reviews
    df_cleaned = (
        df_cleaned.dropna(subset=["review_text"])
    )

    return df_cleaned