Connect to the database
con = sqlite3.connect("store/ilo-prism.db")
cur = con.cursor()

LANGUAGE = "en"

COUNTRY = "FRA"

# Get the list of dataflows that contain the country
# Return the name of the dataflow in the specified language
cur.execute('''
    SELECT dn.name
    FROM cl_area AS ca
    JOIN cl_area_dataflow AS cad ON ca.cl_area_uid = cad.cl_area_uid
    JOIN dataflow AS d ON cad.dataflow_uid = d.dataflow_uid
    JOIN dataflow_name AS dn ON d.dataflow_uid = dn.dataflow_uid
    JOIN language AS l ON dn.language_uid = l.language_uid
    WHERE ca.code = ? AND l.code = ?
''', (COUNTRY, LANGUAGE))

dataflows = cur.fetchall()
for dataflow in dataflows:
    print(dataflow[0])
