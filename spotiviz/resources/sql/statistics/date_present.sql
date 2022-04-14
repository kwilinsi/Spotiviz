/*
 * Get the total number of days for which there is at least one listen present.
 */

SELECT COUNT(day) days
FROM ListenDates
WHERE has_listen = TRUE;