/*
 * Get the total number of non-missing days.
 */

SELECT COUNT(day) AS days
FROM ListenDates
WHERE is_missing = FALSE;