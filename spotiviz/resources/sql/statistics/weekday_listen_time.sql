/*
 * Get the average number of song listens and hours played for each day of the
 * week. The weekday is given as an integer 0-6, where Sunday is 0.
 */

WITH DailyListens AS (SELECT STRFTIME('%Y-%m-%d', end_time)  AS date,
                             COUNT(artist_name)              AS listens,
                             SUM(ms_played) / 1000 / 60 / 60 AS avg_listen_hours
                      FROM StreamingHistory
                      GROUP BY date)
SELECT STRFTIME('%w', D.day)                         AS weekday,
       ROUND(AVG(IFNULL(DL.listens, 0)), 3)          AS avg_listens,
       ROUND(AVG(IFNULL(DL.avg_listen_hours, 0)), 3) AS avg_listen_hours
FROM ListenDates D
         LEFT JOIN DailyListens DL ON D.day = DL.date
GROUP BY weekday;