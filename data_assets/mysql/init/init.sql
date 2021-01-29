CREATE USER 'finuser'@'%' IDENTIFIED WITH mysql_native_password BY 'fin';
GRANT ALL PRIVILEGES ON * . * TO 'finuser'@'%';

CREATE TABLE IF NOT EXISTS sec_idx (
    cik INT,
    year INT,
    company TEXT,
    report_type TEXT,
    url TEXT,
    PRIMARY KEY (cik, year)
);