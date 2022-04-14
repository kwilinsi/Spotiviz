/*
 * Get the minimum day of the listens. This is the first day on which a listen
 * was recorded.
 */

SELECT MIN(day) AS date_min
FROM ListenDates;
