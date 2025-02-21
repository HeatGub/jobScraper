-- HERE YOU CAN RUN SQL QUERIES

SELECT name FROM sqlite_master WHERE type='table' ORDER BY name; -- EXISTING TABLES LIST

-- ALTER TABLE tableOld RENAME TO tableNew; --RENAME TABLE

-- SELECT (JULIANDAY(datetimeLast) - JULIANDAY(datetimeFirst)) FROM table1
-- ORDER BY (JULIANDAY(datetimeLast) - JULIANDAY(datetimeFirst)) * 24 * 60 DESC;