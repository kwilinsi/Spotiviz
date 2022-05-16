/*
 * Get the number of distinct tracks in the entire StreamingHistory. This does
 * not include the 'Unknown Track' entry.
 */

SELECT COUNT(DISTINCT id) as tracks
FROM Tracks;
