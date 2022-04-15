/*
 * Get the average numbers of hours spent listening to Spotify per day. This is
 * the total listening in hours (hours_total.sql), divided by the total number
 * of non-missing days (date_present.sql).
 *
 * Note that this includes days with no Spotify listening.
 *
 * This is rounded to four decimal places.
 */

SELECT ROUND(hours / days, 4) AS avg_hours_per_day,
       ROUND(hours, 4)        AS hours,
       days

FROM (SELECT CAST(SUM(ms_played) AS REAL) / 1000 / 60 / 60 AS hours
      FROM StreamingHistory),
     (SELECT COUNT(day) AS days
      FROM ListenDates
      WHERE is_missing = FALSE);
