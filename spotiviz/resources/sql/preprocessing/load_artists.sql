/*
 * This script populates the Artists tables in the project database. This is
 * done by querying the StreamingHistoryRaw table for unique names.
 */

INSERT INTO Artists (name)
SELECT DISTINCT artist_name AS name
FROM StreamingHistoryRaw
WHERE NOT (track_name IS 'Unknown Track'
    AND artist_name IS 'Unknown Artist')
ORDER BY name;
