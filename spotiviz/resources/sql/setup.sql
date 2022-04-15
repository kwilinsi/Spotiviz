/*
 * These SQL instructions set up the sqlite database for the main Spotiviz installation.
 * This includes the Project table, which stores a list of all the current projects.
 */

DROP TABLE IF EXISTS Projects;

CREATE TABLE Projects
(
    name          TEXT PRIMARY KEY,
    database_path TEXT      NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
