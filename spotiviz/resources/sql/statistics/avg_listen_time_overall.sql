/*
 * Get the average numbers of hours spent listening to Spotify per day. This is
 * the total listening in hours (hours_total.sql), divided by the total number
 * of days from the first to last listen (date_range.sql).
 *
 * Note that this includes days with no Spotify listening.
 *
 * This is rounded to four decimal places.
 */

SELECT ROUND(H.hours, 4)          as hours,
       D.days                     as days,
       ROUND(H.hours / D.days, 4) as
                                     avg_hours_per_day
FROM (SELECT CAST(SUM(ms_played) AS REAL) / 1000 / 60 / 60 as hours
      FROM StreamingHistory) as H,
     (SELECT CAST((JulianDay(MAX(end_time)) - JulianDay(MIN(end_time))) AS INT)
                 as days
      FROM StreamingHistory) as D;
