from echo_dataset import eds


path = "../data/2018/SCH72_2019241/ACOUSTIC/GRIDDED"
name = "SCH72_2019241"
year = 2019
window_size = (256, 256)

cruise_cfg = eds.CruiseConfig(
    path=path,
    name=name,
    year=year,
    require_annotations=True,
    require_bottom=True,
    settings=None,
)
cruise = eds.Cruise(conf=cruise_cfg)


sampler = CompoundSampler(
    samplers=[
        RandomSchoolSampler(window_size=window_size),
        RandomBackgroundSampler(window_size=window_size),
    ]
)
