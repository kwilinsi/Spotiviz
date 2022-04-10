/*
 * This script is for cleaning the StreamingHistoryRaw table in each project database and storing the cleaned data
 * in the StreamingHistory table.
 *
 * ---------------
 *
 * The reason this is so complex is that Spotify only provides an endTime for each listen to the nearest *second*.
 * Sometimes, a song is skipped after playing for less than a second, which means two listens end up with the same
 * endTime. For this reason, we can't order the listens *purely* by their endTime.
 *
 * The main sorting of listens does still happen by endTime, but we need a tiebreaker. For this, we use the position of
 * the listen within its StreamingHistory file. If song A and song B are both played at 11:42 PM, whichever one comes
 * first in the StreamingHistory file will come first in the final, cleaned data.
 *
 * But this still isn't enough. It is possible (and very common) for two Spotify downloads to have an overlapping
 * timespan. If one download is from June and another is from August, they will both have data for the past April. And
 * if two songs, A and B, were played at 11:42 PM on a day that April, then we end up with duplicate records. We have 2
 * instances of song A, two instances of song B, and 4 songs happening during the same second.
 *
 * To remedy this, we sort first by endTime, and then by the StreamingHistory file that the listens come from, followed
 * by their position within that file. But this requires an order to StreamingHistory files. If we have
 * StreamingHistory4.json from download D and StreamingHistory5.json from download E, we need to know which comes first.
 * This is determined based on the start_time column in the StreamingHistories table, which is the endTime of the
 * first listen (stream) contained within that file. So if StreamingHistory4.json starts 2019-05-01, and
 * StreamingHistory5.json starts 2019-01-01, then StreamingHistory5.json will come first.

 * Of course, it's conceivable (though very improbable) that two StreamingHistory files could begin with exactly the
 * same listen on the same day and time. In this case, they would have the same start_time. Here, the order is
 * determined by the start_time of the download that they come from. The start_time of a download is the earliest
 * start_time of any of its member streaming histories (so typically the start_time of StreamingHistory0.json). For
 * example, consider download P, taken in April, and download Q, taken in May. Both downloads contain a streaming
 * history file that has a start_time of midnight on March 1st. Many of the songs between these streaming histories
 * will be duplicates (they overlap between the downloads). The ones from download P will take precedence, because P
 * will have an earlier start_time (some time in April of the year before, most likely). Note that if there's still a
 * tie after ordering by download start_times, there is most likely a duplicate download in play, and the download id
 * is used as a tiebreaker--thus, the download first added to the project takes precedence.
 *
 * ---------------
 *
 * This is how we come to sort the final listens in StreamingHistoryRaw. They are sorted by these parameters:
 * 1. end_time: the main sorting is done simply by the end of the listen.
 * 2. Streaming history file ranking: an index that properly orders each Streaming History based first on its
 *    start_time and second by the start_time of its parent Download.
 * 3. The position of the listen within the Streaming History file.
 *
 * From here, the streams are grouped by end_time, artist_name, track_name, and ms_played. This removes all duplicates
 * from the final list.
 *
 * Finally, a row_number() column is added called position, which stores a fixed index giving the order of each listen.
 * This makes ordering the listens much easier in the future.
 */

INSERT INTO StreamingHistory

WITH Merged AS (
    WITH SH AS (
        SELECT S.id,
               row_number() over (ORDER BY datetime(S.start_time), datetime(D.start_time)) as strm_hist_pos
        FROM StreamingHistories S
                 LEFT JOIN Downloads D on S.download_id = D.id
    )

    SELECT *,
           strm_hist_pos
    FROM StreamingHistoryRaw
             LEFT JOIN SH on StreamingHistoryRaw.history_id = SH.id
    ORDER BY history_id, position
)

SELECT row_number() over (ORDER BY end_time, strm_hist_pos, position) as position,
       end_time,
       artist_name,
       track_name,
       ms_played
FROM Merged

GROUP BY end_time, artist_name, track_name, ms_played
ORDER BY position;