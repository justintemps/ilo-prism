import sdmx


def get_dimensions(df: str, lang: str):
    # Create an SDMX Client client
    ilostat = sdmx.Client("ILO")

    dataflow = ilostat.dataflow(df)

    dsd = dataflow.dataflow[df].structure

    # Get the constraints
    constraints = dataflow.constraint

    # The eventual return value
    dimensions = []

    for constraint in constraints:

        # Get the content region included in the constraints
        cr = constraints[constraint].data_content_region[0]

        # Get the members of the content region
        dims = cr.member

        # Get rid of REF_AREA because we already know the country
        dims.pop("REF_AREA", None)

        for dim in dims:

            # Get the codelist for this dimension
            cl = dim.local_representation.enumerated

            if cl:
                # Initialize the dimension objct
                dimension = {
                    "dimension": (cl.id, cl.name.localizations[lang]),
                    "values": []
                }

                for value in dims[dim].values:
                    values = (
                        cl.items[value].name.localizations[lang], value.value)
                    dimension["values"].append(values)

                dimensions.append(dimension)
    return dimensions


if __name__ == "__main__":
    print(get_dimensions("DF_EAP_3EAP_SEX_AGE_DSB_NB", "en"))
