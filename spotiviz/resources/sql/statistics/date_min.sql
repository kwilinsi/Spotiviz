/*
 * Get the minimum day of the listens. This is the first day on which a listen
 * was recorded.
 */

SELECT DATE(MIN(end_time)) as date_min
FROM StreamingHistory;
