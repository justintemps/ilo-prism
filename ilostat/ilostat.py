from typing import Literal
import sqlite3
from ._dataflow import get_dataflows
from ._area import get_cl_areas
from ._area_dataflow import get_area_dataflows
from ._initialize import init_db
from ._validate_db import validate_db
from ._dimensions import get_dimensions
from ._query import ILOStatQuery


class ILOStat:
    """A class to interact with the ILOSTAT API"""

    def __init__(self, language: Literal["en", "fr", "es"] = "en"):

        if language not in ["en", "fr", "es"]:
            raise ValueError("Language must be one of 'en', 'fr', or 'es'")

        self.language = language

        metadata_valid = self.__validate_metadata()

        if not metadata_valid:
            print("Refreshing metadata...")
            self.__init_metadata()

        self.__con = sqlite3.connect("store/ilo-prism.db", check_same_thread=False)

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
        """Close the database connection"""
        if self.__con:
            self.__con.close()
            print("Database connection closed")

    def get_areas(self) -> list[tuple[str, str]]:
        """Get a list of areas (name, code) based on the selected language"""
        cursor = self.__con.cursor()
        try:
            cursor.execute(
                """
                SELECT  cn.name, ca.code
                FROM cl_area AS ca
                JOIN cl_area_name AS cn ON ca.cl_area_uid = cn.cl_area_uid
                JOIN language AS l ON cn.language_uid = l.language_uid
                WHERE l.code = ?
            """,
                (self.language,),
            )
            results = cursor.fetchall()
        finally:
            cursor.close()  # Ensure cursor is closed
        return results

    def get_dataflows(self, country: str):
        """Get dataflows for a specific country"""
        cursor = self.__con.cursor()
        try:
            cursor.execute(
                """
                SELECT dn.name, d.code
                FROM cl_area AS ca
                JOIN cl_area_dataflow AS cad ON ca.cl_area_uid = cad.cl_area_uid
                JOIN dataflow AS d ON cad.dataflow_uid = d.dataflow_uid
                JOIN dataflow_name AS dn ON d.dataflow_uid = dn.dataflow_uid
                JOIN language AS l ON dn.language_uid = l.language_uid
                WHERE ca.code = ? AND l.code = ?
                ORDER BY dn.name ASC;
                """,
                (country, self.language),
            )
            return cursor.fetchall()
        finally:
            cursor.close()  # Ensure cursor is closed

    def get_dataflow_description(self, dataflow: str):
        """Get the description of a dataflow"""
        cursor = self.__con.cursor()
        try:
            cursor.execute(
                """
                SELECT dd.description
                FROM dataflow AS d
                JOIN dataflow_description AS dd ON d.dataflow_uid = dd.dataflow_uid
                JOIN language AS l ON dd.language_uid = l.language_uid
                WHERE d.code = ? AND l.code = ?
                """,
                (dataflow, self.language),
            )
            return cursor.fetchone()
        finally:
            cursor.close()  # Ensure cursor is closed

    def get_dimensions(self, df: str):
        """Get the dimensions for a dataflow"""
        return get_dimensions(df, self.language)

    def query(self, dataflow: str, dimensions: dict[str, str], params: dict[str, str]):
        return ILOStatQuery(
            dataflow=dataflow,
            dimensions=dimensions,
            params=params,
            language=self.language,
        )


if __name__ == "__main__":
    ilostat = ILOStat("en")
    dataflows = ilostat.get_dataflows("FRA")
    print(dataflows)
