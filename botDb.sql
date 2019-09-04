CREATE TABLE  IF NOT EXISTS log (
id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
dt DATETIME,
msg TEXT
);

CREATE TABLE  IF NOT EXISTS did (
id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
cid INT not null,
did TEXT not null,
dt DATETIME
);

CREATE TABLE  IF NOT EXISTS user (
id INT NOT NULL PRIMARY KEY, -- to cid
username TEXT,
first_name TEXT,
last_name TEXT
);