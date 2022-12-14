# Internet Brands Use Case Analysis for Senior Data Science: Boston Crimes Dataset
# ===================================

print(f"""Internet Brands Use Case Analysis
========================
Ali Khosro <br> [Source Code](../analysis.py) <br>  [Resume](https://alan-khosro.github.io/public/?file=resume)


Questions
----------------------------------
Use Boston Crime Dataset to answer each of the following questions:
- q1: Write a script that shows count of Auto Theft and Towed by Phase of Day (as index) vs Montn (as column)
- q2: Write script to get offense per district which has maximum occurrence in respective district
- q3: Add a column to data set which contains date of last incidents happened in respective district
- q4: Write a script to identify street having maximum number of incidents for every district
- q5: Create a subset of data, with only 10 recent incidents for each Street
""")

"""
cd ~/public/use-cases/boston-crimes
python3 analysis.py > output.analysis.md
"""

import pandas as pd
import calendar
import matplotlib.pyplot as plt


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.options.display.float_format = '{:.1f}'.format
pd.set_option('styler.format.precision', 1)
pd.set_option('styler.render.max_rows', 20)


df = pd.read_csv("input/crime.csv", encoding="latin1")
# codes = pd.read_csv("input/offense-codes.csv", encoding="latin1")

df.dtypes
df.describe()
df["DISTRICT"] = df["DISTRICT"].fillna("not available")
df["STREET"] = df["STREET"].str.strip()
df["OCCURRED_ON_DATE"] = pd.to_datetime(df["OCCURRED_ON_DATE"])

print(f"""Data Description
----------------------------------
{df.describe().style.to_html(exclude_styles=True)}

### Data Cleaning:
- stripped whitespaces from STREET column
- converted OCCURRED_ON_DATE to datetime format
- mapped missing DISTRICT to 'not available' as a separate district to avoid unnecessary complications due to missing data

""")



# q1: get count of autho theft and towed number by month and day phase
# ----------------------------------

### filter only ratgetted crimes: Auto Theft and Towed
targetted_crimes = ["Auto Theft", "Towed"]
crimes = df[df['OFFENSE_CODE_GROUP'].isin(targetted_crimes)]

### define day time phases and reorder them
day_phases = [0, 6, 11, 17, 20, 24]
phase_labels = ["Night", "Morning", "Noon", "Evening", "Night"]
crimes['phases'] = (
    pd.cut( # create bins by day phases
        crimes['HOUR'], bins=day_phases, labels = phase_labels, right=False, include_lowest=True, ordered=False
    ).cat.reorder_categories(["Morning", "Noon", "Evening", "Night"]) # reorder appropriately
)

### define month_name and order them properly as categorical type
crimes['month_name'] = crimes["MONTH"].astype("category").cat.rename_categories(list(calendar.month_abbr[1:]))

crime_summary = crimes.pivot_table(values="INCIDENT_NUMBER", index="phases", columns="month_name", aggfunc="count")

graph_name = "crime-count.png"
crime_summary.transpose().plot().get_figure().savefig(f'output/{graph_name}')


print(f"""Q1: Crime Count
----------------------------------
The below shows the crime counts for Auto Theft and Towed offenses:

{crime_summary.style.to_html(exclude_styles=True)}

![auto theft and towed graph]({graph_name})
""")


# q2: for each district, find offense that has max count 
# ----------------------------------

top_offenses = (
    df
    .groupby(['DISTRICT', 'OFFENSE_CODE', 'OFFENSE_DESCRIPTION'], as_index=False, sort=False)
    .size() # get row count in each group
    .sort_values(["DISTRICT", "size"], ascending=False) # sort by size in each district
    .groupby("DISTRICT")
    .head(1) # get the first row of each group
)

print(f"""Q2: Most Occurred Offense In A District
------------------------------
{top_offenses.style.to_html(exclude_styles=True)}
""")



# q3: Add a column that shows the previous incident data (by District)
# ------------------------------

df['last_incident_date'] = (
    df
    .sort_values(["DISTRICT", "OCCURRED_ON_DATE"])
    [["DISTRICT", "OCCURRED_ON_DATE"]]
    .groupby("DISTRICT")
    .shift(-1)
)

print(f"""Q3: Previous Incident Date In Each District
------------------------------
{df[["DISTRICT", "OCCURRED_ON_DATE", "OFFENSE_DESCRIPTION", "last_incident_date"]].style.to_html(exclude_styles=True)}
""")



# q4: for each district, what is the street with most incident
# ------------------------------

worst_streets = (
    df
    .groupby(['DISTRICT', 'STREET'], as_index=False, sort=False)
    .size() # get row count in each group
    .sort_values(["DISTRICT", "size"], ascending=False) # sort by size in each district
    .groupby("DISTRICT")
    .head(1) # get the first row of each group
)

print(f"""Q4: Streets With Highest Incidents In Each District
------------------------------
{worst_streets.style.to_html(exclude_styles=True)}
""")


# q5: recent incidents of each street
# ------------------------------

recent_incidents = (
    df
    .sort_values(["STREET", "OCCURRED_ON_DATE"], ascending=False)
    .groupby("STREET")
    .head(10)
)

print(f"""Q5: Recent Incidents For Each Street
------------------------------
{recent_incidents.style.to_html(exclude_styles=True)}
""")



