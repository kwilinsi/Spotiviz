/*
 * Get the total number of hours spent listening to Spotify. This is the
 * sum of every entry in the ms_played column, converted to hours. It is
 * rounded to 4 decimal places.
 */

SELECT ROUND(CAST(SUM(ms_played) AS REAL) / 1000 / 60 / 60, 4) as hours_total
FROM StreamingHistory;
