/*
 * Get the maximum day of the listens. This is the last day on which a listen
 * was recorded.
 */

SELECT DATE(MAX(end_time)) as date_max
FROM StreamingHistory;
