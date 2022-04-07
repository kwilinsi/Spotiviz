/*
 * Get the number of days between the first listen and the last listen.
 * Equivalent to the duration between date_min and date_max.
 */

SELECT CAST((JulianDay(MAX(end_time)) - JulianDay(MIN(end_time))) AS INT)
           as date_range
FROM StreamingHistory;
