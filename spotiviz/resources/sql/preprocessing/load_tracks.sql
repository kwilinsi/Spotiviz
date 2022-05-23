/*
 * This script populates the Tracks table in the project database. This is done
 * by querying the StreamingHistoryRaw table for unique names.
 */

INSERT INTO Tracks (artist_id, name)
SELECT DISTINCT A.id AS artist_id, track_name AS name
FROM StreamingHistoryRaw
         LEFT JOIN Artists A ON A.name = artist_name
WHERE NOT (track_name IS 'Unknown Track'
    AND artist_name IS 'Unknown Artist')
ORDER BY artist_id, name;