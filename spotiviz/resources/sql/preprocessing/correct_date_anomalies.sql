/*
 * Sometimes Spotify downloads are weird, and they don't have data for exactly
 * 1 year. Instead, they have data for a little over a year, like 1 year and
 * 2 days or something. When that happens, a ListenDate entry can be marked as
 * BOTH having listen data AND missing, which obviously doesn't make sense.
 *
 * This script fixes those anomalies. Whenever a date has a listen, its
 * is_missing status is set to False.
 */

UPDATE ListenDates
SET is_missing = FALSE
WHERE has_listen = TRUE;
