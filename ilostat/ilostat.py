from typing import Literal
import sqlite3
from ._dataflow import get_dataflows
from ._area import get_cl_areas
from ._area_dataflow import get_area_dataflows
from ._initialize import init_db
from ._validate_db import validate_db
from ._dimensions import get_dimensions
from ._query import ILOStatQuery
from .area_dimensions import filter_area_dimensions


from typing import Literal
import sqlite3


class ILOStat:
    """A class to interact with the ILOSTAT API, providing access to metadata,
    dataflows, and descriptions for various country and area data.
    """

    def __init__(self, language: Literal["en", "fr", "es"] = "en"):
        """
        Initializes the ILOStat instance with a specific language and checks
        if the metadata is valid. If not, initializes metadata.

        Parameters:
        - language: The language code ('en', 'fr', 'es') for data retrieval.
        """
        if language not in ["en", "fr", "es"]:
            raise ValueError("Language must be one of 'en', 'fr', or 'es'")

        self.language = language

        # Validate metadata; refresh if invalid
        metadata_valid = self.__validate_metadata()
        if not metadata_valid:
            print("Refreshing metadata...")
            self.__init_metadata()

        # Establish connection to the SQLite database
        self.__con = sqlite3.connect("store/ilo-prism.db", check_same_thread=False)

    def __del__(self):
        """Destructor to ensure the database connection is closed upon deletion."""
        self.close()

    def __validate_metadata(self) -> bool:
        """
        Checks if the metadata is valid in the database.

        Returns:
        - bool: True if metadata is valid, False otherwise.
        """
        return validate_db()

    def __init_metadata(self):
        """
        Initializes metadata in the database by creating required tables and
        populating data for areas, dataflows, and area-specific dataflows.
        """
        init_db()
        get_cl_areas()
        get_dataflows()
        get_area_dataflows()

    def close(self):
        """Closes the database connection if it is open."""
        if self.__con:
            self.__con.close()
            print("Database connection closed")

    def get_areas(self) -> list[tuple[str, str]]:
        """
        Retrieves a list of areas (name and code) based on the selected language.

        Returns:
        - list[tuple[str, str]]: A list of area names and their corresponding codes.
        """
        cursor = self.__con.cursor()
        try:
            cursor.execute(
                """
                SELECT cn.name, ca.code
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
        """
        Retrieves available dataflows for a specified country.

        Parameters:
        - country (str): The country code for which dataflows are retrieved.

        Returns:
        - list[tuple[str, str]]: A list of dataflows, each represented by a tuple
                                  containing the name and code.
        """
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

    def get_dataflow_label(self, dataflow: str):
        """
        Retrieves the label for a specified dataflow in a given language.

        Parameters:
        - dataflow (str): The code of the dataflow to retrieve the label for.

        Returns:
        - str: The label of the dataflow, if found.
        """
        cursor = self.__con.cursor()
        try:
            cursor.execute(
                """
                SELECT dn.name
                FROM dataflow AS d
                JOIN dataflow_name AS dn ON d.dataflow_uid = dn.dataflow_uid
                JOIN language AS l ON dn.language_uid = l.language_uid
                WHERE d.code = ? AND l.code = ?
                """,
                (dataflow, self.language),
            )
            result = cursor.fetchone()
            return result[0] if result else None  # Return the label if found, else None
        finally:
            cursor.close()  # Ensure cursor is closed

    def get_dataflow_description(self, dataflow: str):
        """
        Retrieves the description for a specified dataflow.

        Parameters:
        - dataflow (str): The code of the dataflow to retrieve the description for.

        Returns:
        - tuple: The description of the dataflow, if found.
        """
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
        """
        Retrieves the dimensions available for a specified dataflow.

        Parameters:
        - df (str): The dataflow code to retrieve dimensions for.

        Returns:
        - Dimensions data retrieved via the get_dimensions function.
        """
        return get_dimensions(df, self.language)

    def get_area_dimensions(self, area, dataflow):
        all_dimensions = self.get_dimensions(dataflow)
        filtered_dimensions = filter_area_dimensions(
            area=area, all_dimensions=all_dimensions, dataflow=dataflow
        )
        return filtered_dimensions

    def query(
        self, dataflow: str, dimensions: dict[str, str], params: dict[str, str] = None
    ):
        """
        Queries the ILOSTAT API based on specified dataflow, dimensions, and parameters.

        Parameters:
        - dataflow (str): The dataflow code to query.
        - dimensions (dict[str, str]): Key-value pairs representing dimension constraints.
        - params (dict[str, str]): Additional parameters for the query.

        Returns:
        - ILOStatQuery: An ILOStatQuery object containing the query result.
        """
        return ILOStatQuery(
            dataflow=dataflow,
            dimensions=dimensions,
            params=params,
            language=self.language,
        )


if __name__ == "__main__":
    # Example usage of the ILOStat class
    ilostat = ILOStat("en")
    dataflows = ilostat.get_dataflows("FRA")
    print(dataflows)
