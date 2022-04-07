/*
 * Get the average numbers of hours spent listening to Spotify per day. This is
 * the total listening in hours (hours_total.sql), divided by the number of
 * days for which there is at least one listen.
 *
 * Note that this does not include days without any listens. It will typically
 * be greater than the overall average listen time.
 *
 * This is rounded to four decimal places.
 */

SELECT ROUND(SUM(hours), 4)              as hours,
       COUNT(day)                        as days,
       ROUND(SUM(hours) / COUNT(day), 4) as avg_hours_per_listen_day
FROM (SELECT DATE(end_time)                                as day,
             CAST(SUM(ms_played) AS REAL) / 1000 / 60 / 60 as hours
      FROM StreamingHistory
      GROUP BY DATE(end_time));
