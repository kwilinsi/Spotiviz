/*
 * Get the total number of days for which there is at least one listen present.
 */

SELECT COUNT(DISTINCT DATE(end_time)) as days
FROM StreamingHistory;