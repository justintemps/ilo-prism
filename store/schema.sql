DROP TABLE IF EXISTS cl_area_name;
DROP TABLE IF EXISTS dataflow_name;
DROP TABLE IF EXISTS dataflow_description;
DROP TABLE IF EXISTS cl_area_dataflow;
DROP TABLE IF EXISTS cl_area;
DROP TABLE IF EXISTS dataflow;
DROP TABLE IF EXISTS language;

-- Table for languages
CREATE TABLE language (
  language_uid INTEGER PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL
);

-- Insert languages
INSERT INTO language (code, name)
VALUES ('en', 'english'), ('fr', 'français'), ('es', 'español');

-- Main table for areas
CREATE TABLE cl_area (
  cl_area_uid INTEGER PRIMARY KEY,
  code TEXT NOT NULL UNIQUE
);

-- Table for area translations
CREATE TABLE cl_area_name (
  cl_area_name_uid INTEGER PRIMARY KEY,
  cl_area_uid INTEGER NOT NULL,
  language_uid INTEGER NOT NULL,
  name TEXT NOT NULL,
  FOREIGN KEY (cl_area_uid) REFERENCES cl_area(cl_area_uid),
  FOREIGN KEY (language_uid) REFERENCES language(language_uid)
);

-- A dataflow in ILOSTAT
CREATE TABLE dataflow (
  dataflow_uid INTEGER PRIMARY KEY,
  code TEXT NOT NULL UNIQUE
);

-- Table for dataflow translations
CREATE TABLE dataflow_name (
  dataflow_name_uid INTEGER PRIMARY KEY,
  dataflow_uid INTEGER NOT NULL,
  language_uid INTEGER NOT NULL,
  name TEXT NOT NULL,
  FOREIGN KEY (dataflow_uid) REFERENCES dataflow(dataflow_uid),
  FOREIGN KEY (language_uid) REFERENCES language(language_uid)
);

-- Table for dataflow descriptions
CREATE TABLE dataflow_description (
  dataflow_description_uid INTEGER PRIMARY KEY,
  dataflow_uid INTEGER NOT NULL,
  language_uid INTEGER NOT NULL,
  description TEXT NOT NULL,
  FOREIGN KEY (dataflow_uid) REFERENCES dataflow(dataflow_uid),
  FOREIGN KEY (language_uid) REFERENCES language(language_uid)
);

-- An area that is included in a dataflow in ILOSTAT
CREATE TABLE cl_area_dataflow (
  area_dataflow_uid INTEGER PRIMARY KEY,
  cl_area_uid INTEGER NOT NULL,
  dataflow_uid INTEGER NOT NULL,
  FOREIGN KEY (cl_area_uid) REFERENCES cl_area(cl_area_uid),
  FOREIGN KEY (dataflow_uid) REFERENCES dataflow(dataflow_uid)
);
