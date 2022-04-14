/*
 * Get the average numbers of hours spent listening to Spotify per day. This is
 * the total listening in hours (hours_total.sql), divided by the number of
 * days for which there is at least one listen (date_listened.sql).
 *
 * Note that this does not include days without any listens. It will typically
 * be greater than the overall average listen time.
 *
 * This is rounded to four decimal places.
 */

SELECT ROUND(hours, 4)        AS hours,
       days,
       ROUND(hours / days, 4) AS avg_hours_per_listen_day

FROM (SELECT CAST(SUM(ms_played) AS REAL) / 1000 / 60 / 60 AS hours
      FROM StreamingHistory),
     (SELECT COUNT(day) AS days
      FROM ListenDates
      WHERE has_listen = TRUE);
