from typing import Literal
import sqlite3
from ilostat._dataflow import get_dataflows
from ilostat._area import get_cl_areas
from ilostat._area_dataflow import get_area_dataflows
from ilostat._initialize import init_db
from ilostat._validate_db import validate_db
from ilostat._dimensions import get_dimensions


class ILOStat:
    '''A class to interact with the ILOSTAT API'''

    def __init__(self, language: Literal["en", "fr", "es"] = "en"):

        if language not in ["en", "fr", "es"]:
            raise ValueError("Language must be one of 'en', 'fr', or 'es'")

        self.language = language

        metadata_valid = self.__validate_metadata()

        if not metadata_valid:
            print("Refreshing metadata...")
            self.__init_metadata()

        self.__con = sqlite3.connect(
            "store/ilo-prism.db", check_same_thread=False)
        self.__cur = self.__con.cursor()  # Fixed: Use self.__con instead of self.con

    def __del__(self):
        self.close()

    def __validate_metadata(self):
        return validate_db()

    def __init_metadata(self):
        init_db()
        get_cl_areas()
        get_dataflows()
        get_area_dataflows()

    def close(self):
        '''Close the database connection'''
        if self.__con:
            self.__con.close()
            print("Database connection closed")

    def get_areas(self) -> list[tuple[str, str]]:
        self.__cur.execute('''
            SELECT  cn.name, ca.code
            FROM cl_area AS ca
            JOIN cl_area_name AS cn ON ca.cl_area_uid = cn.cl_area_uid
            JOIN language AS l ON cn.language_uid = l.language_uid
            WHERE l.code = ?
        ''', (self.language,))
        return self.__cur.fetchall()

    def get_dataflows(self, country: str):
        self.__cur.execute('''
            SELECT dn.name, d.code
            FROM cl_area AS ca
            JOIN cl_area_dataflow AS cad ON ca.cl_area_uid = cad.cl_area_uid
            JOIN dataflow AS d ON cad.dataflow_uid = d.dataflow_uid
            JOIN dataflow_name AS dn ON d.dataflow_uid = dn.dataflow_uid
            JOIN language AS l ON dn.language_uid = l.language_uid
            WHERE ca.code = ? AND l.code = ?
        ''', (country, self.language))
        return self.__cur.fetchall()

    def get_dataflow_description(self, dataflow: str):
        self.__cur.execute('''
            SELECT dd.description
            FROM dataflow AS d
            JOIN dataflow_description AS dd ON d.dataflow_uid = dd.dataflow_uid
            JOIN language AS l ON dd.language_uid = l.language_uid
            WHERE d.code = ? AND l.code = ?
        ''', (dataflow, self.language))
        return self.__cur.fetchone()

    def get_dimensions(self, df: str):
        return get_dimensions(df, self.language)


if __name__ == "__main__":
    ilostat = ILOStat("en")
    dataflows = print(ilostat.get_dataflows("FRA"))
