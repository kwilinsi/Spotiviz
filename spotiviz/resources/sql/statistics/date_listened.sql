/*
 * Get the total number of days for which there is at least one listen.
 */

SELECT COUNT(day) AS days
FROM ListenDates
WHERE has_listen = TRUE;