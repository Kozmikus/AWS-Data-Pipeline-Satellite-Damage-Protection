# Queries and Their Results, Analysis
This document presents the results of various example queries executed on the satellite damage protection dataset, along with an analysis of the findings. This analysis aims to signify the importance of monitoring space weather events to mitigate potential risks to satellite operations.

> To find the queries executed, refer to the `sql_athena_queries.sql` file in the `code` directory.

## Example Queries and Results
### Query 1: Strongest Storms by Maximum Kp Index
#### SQL Query:
```sql
SELECT 
    g.gstID,
    g.startTime,
    -- extracting values from the unnested array
    max(k.kpindex) as Max_Kp_Index, 
    count(k.kpindex) as Duration_Hours_Observed
FROM "satelliteprotector_db_yzu8r3"."raw_nasa_gst" g
CROSS JOIN UNNEST(g.allkpindex) AS t(k) -- this is what flattens the array
GROUP BY g.gstID, g.startTime
ORDER BY Max_Kp_Index DESC;
```
#### Results:
| gstID      | startTime           | Max_Kp_Index | Duration_Hours_Observed |
|------------|---------------------|---------------|-------------------------|
| 1          | 2025-11-12T00:00:00 | 8.67          | 5                       |
| 2          | 2025-06-01T06:00:00 | 8.0           | 12                      |
| 3          | 2025-11-12T18:00:00 | 7.33          | 4                       |
| 4          | 2025-09-30T03:00:00 | 7.33          | 8                       |
| 5          | 2025-11-05T21:00:00 | 6.67          | 3                       |
| 6          | 2025-09-15T00:00:00 | 6.67          | 1                       |
| 7          | 2025-12-03T18:00:00 | 6.67          | 1                       |
| 8          | 2025-06-13T00:00:00 | 6.33          | 5                       |
| 9          | 2025-12-10T21:00:00 | 6.33          | 2                       |
| 10         | 2025-11-08T00:00:00 | 6.33          | 1                       |
| 11         | 2025-09-01T21:00:00 | 6.0           | 1                       |
| 12         | 2025-08-09T15:00:00 | 6.0           | 1                       |
| 13         | 2025-10-18T18:00:00 | 6.0           | 1                       |
| 14         | 2026-01-10T18:00:00 | 6.0           | 2                       |
| 15         | 2025-09-09T21:00:00 | 5.67          | 1                       |

#### Analysis:

The query results indicate that several geomagnetic storms have reached high Kp index values, with the strongest storm peaking at a Kp index of 8.67. The duration of these storms varies, with some lasting only an hour while others persist for up to 12 hours. Storms with higher Kp indices than 5 are particularly significant as they can have substantial effects on satellite operations, including increased drag on low Earth orbit (LEO) satellites and potential disruptions to communication systems, like radio communications. The continued monitoring of these events is crucial for implementing protective measures to safeguard satellite functionality.

### Query 2: Potential Radio Blackout Caused by Strong Solar Flares
#### SQL Query:
```sql
SELECT 
    flrid,
    begintime,
    peaktime,
    endtime,
    classtype,
    sourcelocation,
    activeregionnum -- extracting the region number for historical tracking could proove useful
FROM "satelliteprotector_db_yzu8r3"."raw_nasa_flr"
WHERE classtype LIKE 'X%' OR classtype LIKE 'M%'
ORDER BY peaktime DESC;
```
#### Results:
| flrid | begintime           | peaktime           | endtime            | classtype | sourcelocation | activeregionnum |
|-------|---------------------|--------------------|--------------------|-----------|----------------|------------------|
| 1      | 2026-01-11T21:53:00 | 2026-01-11T23:14:00 | 2026-01-12T00:31:00 | M3.3      | S10E90         |                  |
| 2      | 2025-12-31T13:12:00 | 2025-12-31T13:51:00 | 2025-12-31T14:11:00 | M7.1      | N24E20         | 14324            |
| 3      | 2025-12-29T06:34:00 | 2025-12-29T06:51:00 | 2025-12-29T06:56:00 | M1.0      | S10E40         | 14325            |
| ...   | ...                 | ...                | ...                | ...       | ...            | ...              |
#### Analysis:
The results from this query highlight several significant solar flare events, particularly those classified as M-class (Moderate) and X-class (Major) flares. These flares are known to have the potential to cause high-frequency (HF) radio blackouts, which can severely impact satellite communication systems. One event recorded is an M3.3 flare, which poses a risk to satellite operations while not being the most intense. The data also includes the source locations of these flares, which could help in understanding their potential impact on Earth-facing satellites. Monitoring these solar flare events is essential for predicting and mitigating harm of satellite infrastructure.

### Query 3: "*Correlation*" between Major Solar Flares and Geomagnetic Storms
#### SQL Query:
```sql
/* looking for geomagnetic storms that started within 1 to 4 days after a major solar flare (M or X class).*/
WITH MajorFlaresCTE AS (
    SELECT 
        flrid,
        peaktime,
        classtype,
        sourcelocation
    FROM "raw_nasa_flr"
    WHERE classtype LIKE 'M%' OR classtype LIKE 'X%'
),
GeomStormsCTE AS (
    SELECT 
        gstid,
        starttime,
        -- calculating the max Kp (how strong the strom is)
        MAX(o.kpindex) as max_kp
    FROM "raw_nasa_gst"
    CROSS JOIN UNNEST(allkpindex) AS t(o) -- flattening the Kp index array
    GROUP BY gstid, starttime
)
SELECT 
    f.classtype AS flare_class,
    f.peaktime AS flare_time,
    s.starttime AS storm_start_time,
    s.max_kp AS storm_severity,
    -- calculating the delay in hours between flare and storm in ISO8601 format
    -- have to use the specific function to convert the string to timestamp and
    -- meaningfully calculate the difference
    DATE_DIFF('hour', from_iso8601_timestamp(f.peaktime), from_iso8601_timestamp(s.starttime)) AS delay_hours
FROM MajorFlaresCTE f
JOIN GeomStormsCTE s 
    -- specifically looking for storms that started between 1 to 4 days after the flare
    ON from_iso8601_timestamp(s.starttime) BETWEEN 
        DATE_ADD('hour', 24, from_iso8601_timestamp(f.peaktime)) 
    AND 
        DATE_ADD('hour', 96, from_iso8601_timestamp(f.peaktime))
ORDER BY f.peaktime DESC;
```
#### Results:
| flare_class | flare_time          | storm_start_time   | storm_severity | delay_hours |
|-------------|---------------------|--------------------|----------------|--------------|
| M1.5                | 2025-12-09T15:14Z  | 6.33  |2025-12-10T21:00Z | 29           |
| M1.6                | 2025-12-09T07:47Z  | 6.33  |2025-12-10T21:00Z | 37           |
| M1.1                | 2025-12-09T01:38Z  | 6.33  |2025-12-10T21:00Z | 43           |
| ...         | ...                 | ...                | ...            | ...          |
#### Analysis:
This query is the most complex out of the three, aiming to identify a potential relationship between major solar flares and subsequent geomagnetic storms. It is known that solar flares can trigger geomagnetic storms, but the exact timing and intensity relationship is much more complex. The results indicate that several geomagnetic storms commenced within 1 to 4 days following some significant solar flare events. The delay in hours between the events is also calculated, providing insights into the temporal relationship between these phenomena. The variance of Kp index values among these storms suggests differing intensities, but with also differing solar flare intensities. This correlation analysis is vital for understanding how solar activity influences space weather conditions that can affect satellite operations on Earth. Additionally, preventive modelling and preventive decision-making can be enhanced by studying these relationships further.