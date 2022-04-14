/*
 * Get the maximum day of the listens. This is the last day on which a listen
 * was recorded.
 */

SELECT MAX(day) AS date_min
FROM ListenDates;
