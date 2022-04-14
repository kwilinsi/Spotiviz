/*
 * Get the number of distinct artists in the entire StreamingHistory.
 */

SELECT COUNT(DISTINCT artist_name) as artists
FROM StreamingHistory;
