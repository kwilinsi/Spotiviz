/*
 * Get the number of days between the first listen and the last listen.
 * Equivalent to the duration between date_min and date_max.
 */

SELECT CAST(JULIANDAY(MAX(day)) - JULIANDAY(MIN(day)) AS INT) AS day_range
FROM ListenDates;
