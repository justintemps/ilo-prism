DROP TABLE IF EXISTS area_dataflow CASCADE;
DROP TABLE IF EXISTS dataflow CASCADE;
DROP TABLE IF EXISTS cl_area CASCADE;

-- An area from the ILOSTAT codelist CL_AREA. Usually a country or region
CREATE TABLE cl_area (
  cl_area_uid INTEGER PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  name_en TEXT NOT NULL,
  name_fr TEXT NOT NULL,
  name_es TEXT NOT NULL,
);

-- A dataflow in ILOSTAT
CREATE TABLE dataflow (
  dataflow_uid INTEGER PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  description TEXT
);

-- An area that is included in a dataflow in ILOSTAT
CREATE TABLE cl_area_dataflow (
  area_dataflow_uid INTEGER NOT NULL,
  cl_area_uid INTEGER NOT NULL,
  dataflow_uid INTEGER NOT NULL,
  FOREIGN KEY (cl_area_uid) REFERENCES cl_area(cl_area_uid),
  FOREIGN KEY (dataflow_uid) REFERENCES dataflow(dataflow_uid),
);








