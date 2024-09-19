import sdmx


def get_dimensions(df: str, lang: str):
    # Create an SDMX Client client
    ilostat = sdmx.Client("ILO")

    # Get the response from ILOSTAT
    ilostat_msg = ilostat.dataflow(df)

    # Get the dataflow
    dataflow = ilostat_msg.dataflow[df]

    # Get the dsd
    dsd = dataflow.structure

    # Get the dimensions
    dims = dsd.dimensions.components

    # Get rid of REF_AREA because we already know the country
    dims = [dim for dim in dims if dim.id != 'REF_AREA']

    # The eventual return value
    dimensions = []

    for dim in dims:
        # Initialize the dimension objct
        dimension = {
            "dimension": (),
            "items": []
        }

        # Get the codelist
        cl = dsd.dimensions.get(dim).local_representation.enumerated

        if cl:
            dimension["dimension"] = (cl.id, cl.name.localizations[lang])

            for item in cl.items:
                items = (cl.items[item].name.localizations[lang], item)
                dimension["items"].append(items)

            dimensions.append(dimension)

    return dimensions


if __name__ == "__main__":
    print(get_dimensions("DF_EAP_3EAP_SEX_AGE_DSB_NB", "en"))
