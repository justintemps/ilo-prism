import sqlite3
from ilostat.dataflow import get_dataflows
from ilostat.area import get_cl_areas
from ilostat.area_dataflow import get_area_dataflows
from ilostat.initialize import init_db
from enum import Enum


class Language(Enum):
    en = "en"
    fr = "fr"
    es = "es"


class ILOStat:
    def __init__(self, language: Language):
        # Validate the language
        if language not in Language:
            raise ValueError("Invalid language")

        metadata_downloaded = self.__check_metadata()

        if not metadata_downloaded:
            print("Updated metadata not found. Downloading metadata.")
            self.__init_metadata()

    def __init_metadata(self):
        init_db()
        get_dataflows()
        get_cl_areas()
        get_area_dataflows()

    def __check_metadata(self):
        '''Check if the metadata is up to date'''
        con = sqlite3.connect("store/ilo-prism.db")
        cur = con.cursor()

        # Check if the language table exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='language'")
        language_table = cur.fetchall()
        if not language_table:
            return False

        # Check if the language table is empty
        cur.execute("SELECT * FROM language")
        languages = cur.fetchall()
        if not languages:
            return False

        # Check if the dataflow table is empty
        cur.execute("SELECT * FROM dataflow")
        dataflows = cur.fetchall()
        if not dataflows:
            return False

        # Check if the area table is empty
        cur.execute("SELECT * FROM cl_area")
        areas = cur.fetchall()
        if not areas:
            return False

        # Check if the area_dataflow table is empty
        cur.execute("SELECT * FROM cl_area_dataflow")
        area_dataflows = cur.fetchall()
        if not area_dataflows:
            return False

        return True


if __name__ == "__main__":
    ilostat = ILOStat("fr")
