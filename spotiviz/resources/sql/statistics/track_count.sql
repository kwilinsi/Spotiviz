/*
 * Get the number of distinct tracks in the entire StreamingHistory.
 */

SELECT COUNT(DISTINCT track_name) as tracks
FROM StreamingHistory;
