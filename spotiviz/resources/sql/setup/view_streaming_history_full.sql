/*
 * This script creates the StreamingHistoryFull view, which is an extension
 * of the StreamingHistory table that includes the artist and track names. This
 * is done in a script, as SQLAlchemy does not appear to support creating views
 * through the ORM interface.
 */

CREATE VIEW StreamingHistoryFull AS
SELECT SH.position,
       SH.track_id,
       A.name AS artist,
       T.name AS track,
       SH.end_time,
       SH.ms_played
FROM StreamingHistory AS SH
         LEFT JOIN Tracks T on T.id = SH.track_id
         LEFT JOIN Artists A on A.id = T.artist_id;
