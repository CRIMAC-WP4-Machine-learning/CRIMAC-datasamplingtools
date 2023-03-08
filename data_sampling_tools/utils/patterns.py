import re


__all__ = ["generate_data_filename_patterns"]


def generate_data_filename_patterns(
    config: dict[str, any]
) -> list[re.Pattern, re.Pattern, re.Pattern]:
    out = list()
    keys = ["survey_suffix", "labels_suffix", "bottom_suffix", "schools_suffix"]
    for k in keys:
        if config[k].endswith("csv"):
            pattern = rf".*_{config[k]}"
        else:
            pattern = rf".*_{config[k]}(\.zarr)$"
        out.append(re.compile(pattern))
    return out
