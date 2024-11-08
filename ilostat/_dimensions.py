import sdmx


def dims_with_multi_vals(dimensions: list):
    filtered_dims = []
    for dim in dimensions:
        if len(dim["values"]) > 1:
            filtered_dims.append(dim)
    return filtered_dims


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
                    "dimension": (dim.concept_identity.id, cl.name.localizations[lang]),
                    "values": [],
                }

                for value in dims[dim].values:
                    values = (cl.items[value].name.localizations[lang], value.value)
                    dimension["values"].append(values)

                dimensions.append(dimension)

    # Then get rid of dimensions with only one value. There's no point in showing them
    # if they don't give the user options to choose from
    dimensions = dims_with_multi_vals(dimensions)

    return dimensions


if __name__ == "__main__":
    print(get_dimensions("DF_EAP_3EAP_SEX_AGE_DSB_NB", "en"))
