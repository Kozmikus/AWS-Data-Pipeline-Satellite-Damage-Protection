-- Query 1., Strongest Storms by Maximum Kp Index
/* flattening the nested Kp Index array in GST to find the maximum intensity 
of each storm and length in hours */

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

-- Query 2., Potential Radio Blackout Caused by Strong Solar Flares
/* filtering for Major (X-Class) and Moderate (M-Class) flares as these are the 
events likely to cause HF Radio blackouts. */
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

-- Query 3., "Correlation" between Major Solar Flares and Geomagnetic Storms
/* looking for geomagnetic storms that started within 1 to 4 days after a major solar flare
(M or X class).*/
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