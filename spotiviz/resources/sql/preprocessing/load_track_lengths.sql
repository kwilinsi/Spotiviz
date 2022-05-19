/*
 * This script populates the TrackLengths table. It looks at the
 * StreamingHistory table to find every duration that each song was played for.
 *
 * For example, song A might have been played once for 60000 milliseconds,
 * one for 62000 milliseconds, and seven times for 80000 milliseconds. This
 * script would add three rows for song A, recording the frequency for each
 * duration (60000, 62000, and 80000).
 *
 * This information is used during the analysis stage to predict which songs
 * were skipped in the StreamingHistory.
 */

INSERT INTO TrackLengths (track_id, ms_played, frequency, percent_listens)

WITH TrackFrequency AS (
    SELECT track_id, COUNT() AS freq
    FROM StreamingHistory
    GROUP BY track_id
)
SELECT SH.track_id,
       SH.ms_played,
       COUNT()                                   AS frequency,
       ROUND(CAST(COUNT() AS REAL) / TF.freq, 4) AS percent_listens
FROM StreamingHistory AS SH
         LEFT JOIN TrackFrequency AS TF ON TF.track_id = SH.track_id
WHERE SH.track_id IS NOT null
GROUP BY SH.track_id, SH.ms_played
ORDER BY SH.track_id, SH.ms_played DESC;
