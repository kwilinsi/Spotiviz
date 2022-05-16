/*
 * Get the number of distinct artists in the entire StreamingHistory. This does
 * not include the 'Unknown Artist' entry.
 */

SELECT COUNT(DISTINCT id) as artists
FROM Artists;