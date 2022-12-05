DROP TABLE IF EXISTS todo;

CREATE TABLE todo (
  id TEXT PRIMARY KEY,
  `text` TEXT NOT NULL,
  `status` BOOL NOT NULL DEFAULT 0,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deadline TIMESTAMP NULL
);