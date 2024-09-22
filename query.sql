
-- SELECT salary FROM test WHERE salary NOT LIKE ('%brak widełek%') AND salary NOT LIKE ('%salary not specified%')
-- AND salary LIKE ('%gross%');


-- SELECT salary FROM test WHERE salary NOT LIKE ('%pełny%') AND salary NOT LIKE ('%full%');

-- SELECT salary FROM test WHERE salary REGEXP '^[0-9]+';


-- SELECT salaryMin, salaryMax, techstackExpected, techstackOptional FROM test2 WHERE techstackExpected LIKE ('');
-- SELECT techstackExpected, techstackOptional FROM test2 WHERE techstackExpected IS NULL;
-- SELECT salaryMin, salaryMax, techstackExpected, techstackOptional FROM test2;

-- SELECT * FROM test2 WHERE datetime > '2024-09-20 09:05:00';

-- SELECT techstackExpected FROM test3 WHERE datetime > '2024-09-20 09:05:00';

SELECT * FROM test3 WHERE datetimeLast >= '2024-09-22 03:50:46'; --similar url
SELECT (JULIANDAY(datetimeLast) - JULIANDAY(datetimeFirst)) * 24 * 60 AS difference_in_minutes FROM test3 WHERE difference_in_minutes > 30;
SELECT * FROM test3 WHERE (JULIANDAY(datetimeLast) - JULIANDAY(datetimeFirst)) * 24 > 0;



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