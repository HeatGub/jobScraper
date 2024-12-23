
-- SELECT salary FROM test WHERE salary NOT LIKE ('%brak widełek%') AND salary NOT LIKE ('%salary not specified%')
-- AND salary LIKE ('%gross%');


-- SELECT salary FROM test WHERE salary NOT LIKE ('%pełny%') AND salary NOT LIKE ('%full%');

-- SELECT salary FROM test WHERE salary REGEXP '^[0-9]+';


-- SELECT salaryMin, salaryMax, techstackExpected, techstackOptional FROM test2 WHERE techstackExpected LIKE ('');
-- SELECT techstackExpected, techstackOptional FROM test2 WHERE techstackExpected IS NULL;
-- SELECT salaryMin, salaryMax, techstackExpected, techstackOptional FROM test2;

-- SELECT * FROM test2 WHERE datetime > '2024-09-20 09:05:00';

---- LAST SEEN AGO WORKING BLOCK:
-- SELECT DATETIME('now', 'localtime'), datetimeLast, (JULIANDAY(strftime('%Y-%m-%d %H:%M:%S', DATETIME('now', 'localtime'))) - JULIANDAY(datetimeLast)) * 24 AS lastSeenHoursAgo FROM test4 
-- WHERE lastSeenHoursAgo < 24 ORDER BY lastSeenHoursAgo ASC;

-- SELECT datetimeFirst FROM test4 WHERE datetimeFirst > '2024-11-23 10:23';
-- SELECT techstackExpected, techstackOptional, requirements FROM test3 
-- WHERE 1=1 --just to leave WHERE here 
-- -- exclude keywords block, append AND NOT LIKE (...) 2x for a single keyword
-- AND techstackExpected NOT LIKE ('%javascript%')
-- AND requirements NOT LIKE ('%javascript%')
-- -- include keywords block (only records where keyword appears)
-- AND techstackExpected LIKE ('%SQL%')
-- AND requirements LIKE ('%SQL%')
-- ORDER BY datetimeLast DESC;
SELECT * FROM test4;

-- SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- SELECT datetimeLast, datetimeFirst, techstackExpected FROM test4 WHERE 1=1
-- AND datetimeLast > '2024-10-01';
-- ORDER BY datetimeLast, techstackExpected;
-- AND (JULIANDAY(strftime('%Y-%m-%d %H:%M:%S', DATETIME('now', 'localtime'))) - JULIANDAY(datetimeLast)) * 24 < 24
-- AND (techstackExpected LIKE ('%SQL%') OR requirements LIKE ('%SQL%'))
-- AND techstackExpected NOT LIKE ('%javascript%') AND requirements NOT LIKE ('%javascript%')
-- AND techstackExpected NOT LIKE ('%c++%') AND requirements NOT LIKE ('%c++%');


-- SELECT datetimeFirst, datetimeLast, (JULIANDAY(datetimeLast) - JULIANDAY(datetimeFirst)) * 24 * 60 AS difference_in_minutes, url, title, salaryMin, salaryMax FROM test4 WHERE 1=1
-- AND datetimeFirst > '2024-04-20'
-- AND datetimeLast > '2024-04-20'ORDER BY (salaryMin+SalaryMax)/2 ASC, difference_in_minutes DESC;


-- SELECT * FROM test4 WHERE
-- optionalRequirements IS NULL;

-- UPDATE test4 SET 
-- optionalRequirements
-- = '' WHERE
-- optionalRequirements 
-- IS NULL;
-- SELECT * FROM test4 WHERE
-- optionalRequirements IS NULL;

-- SELECT optionalRequirements FROM test4 WHERE optionalRequirements IS NULL;


-- SELECT datetimeLast FROM test4
-- WHERE ((datetimeLast LIKE ('%2024%') OR (datetimeLast LIKE ('%2024%') AND datetimeLast LIKE ('%2024-01-01%'))) AND (datetimeLast LIKE ('%2024-01%') OR datetimeLast LIKE ('%2024%')));
-- WHERE (datetimeLast LIKE ('%2024%') OR (datetimeLast LIKE ('%2024-%') AND datetimeLast LIKE ('%2024-01-01%'))) AND (datetimeLast LIKE ('%2024-01%') OR datetimeLast LIKE ('%2024%'));



-- (datetimeFirst LIKE ('%2024-09-27%') OR datetimeFirst LIKE ('%2024-10-15%')) OR (datetimeFirst NOT LIKE ('%2024%') OR datetimeFirst NOT LIKE ('%2024%'));


-- SELECT datetimeFirst, datetimeLast FROM test4 WHERE datetimeLast > '2024-09-24 21:09:00' ORDER BY datetimeFirst;

-- SELECT * FROM test3 WHERE url LIKE ('%https://theprotocol.it/szczegoly/praca/programista-javascript---sapui5---sap-fiori-wroclaw-soltysowicka-13,oferta,aa3c0000-a366-0204-3551%');

-- SELECT * FROM test3 WHERE url LIKE ('%https://theprotocol.it/szczegoly/praca/programista-web-sql-warszawa,oferta,eecf0000-387c-b216-12ef-08dcdbaac54c?s=8321028996&searchId=44e94190-7aa%');

-- SELECT * FROM test3 WHERE (JULIANDAY(datetimeLast) - JULIANDAY(datetimeFirst)) * 24 > 1 ORDER BY datetimeLast DESC;


-- SELECT * FROM test3 WHERE datetimeFirst >= '2024-09-23 03:50:46'; --similar url
-- SELECT (JULIANDAY(datetimeLast) - JULIANDAY(datetimeFirst)) * 24 * 60 AS difference_in_minutes FROM test3 WHERE difference_in_minutes > 30;
-- SELECT * FROM test3 WHERE (JULIANDAY(datetimeLast) - JULIANDAY(datetimeFirst)) * 24 > 0;

-- SELECT datetimeFirst, datetimeLast, SUBSTRING(url, 0, LENGTH(url)-45) AS base FROM test3

-- SELECT SUBSTRING(url, 0, LENGTH(url)-59) FROM test3;

-- SELECT SUBSTRING(url, 0, LENGTH(url)-59) AS baseUrl, substring(url, -59) AS gibberish FROM test3; -- last 59 characters seem to be session related
-- GROUP BY gibberish;
-- SELECT SUBSTRING(url, LENGTH(url)-45, -56) FROM test3;

-- SELECT SUBSTRING(url, -59) AS gibberish FROM test3;
-- SELECT url from test3;




-- AND salary NOT LIKE ('%godz%') AND salary NOT LIKE ('%hr.%');
-- AND salary NOT LIKE ('%mth%') AND salary NOT LIKE ('%mies.%');


-- SELECT salary FROM test WHERE salary LIKE ('%brak widełek%') OR salary LIKE ('%salary not specified%');

-- SELECT datetime FROM test WHERE datetime > '2024-09-17 04:31';

-- SELECT salary, positionLevels, techstackExpected, techstackOptional, requirements, responsibilities FROM test 
-- WHERE salary NOT LIKE ('%brak widełek%') AND salary NOT LIKE ('%salary not specified%')
-- AND positionLevels LIKE ('%mid%');


-- SELECT datetime, title, salary, location, techstackExpected, techstackOptional, responsibilities, requirements, optionalRequirements FROM test
-- SELECT salary FROM test WHERE salary LIKE ('%salary not%') OR salary LIKE ('%brak widełek%')

-- SELECT 1 - (SELECT CAST(COUNT(salary) AS FLOAT) FROM test WHERE salary LIKE ('%salary not%') OR salary LIKE ('%brak widełek%')) 
-- / (SELECT CAST(COUNT(salary) AS FLOAT) FROM test) AS [% offers with salary];

-- SELECT title, salary, responsibilities, techstackExpected, positionLevels FROM test;
-- WHERE workModes LIKE '%remote%' OR workModes  LIKE '%zdalna%' OR workModes  LIKE '%hybr%';
-- SELECT location FROM test WHERE location LIKE '%Warszawa%';