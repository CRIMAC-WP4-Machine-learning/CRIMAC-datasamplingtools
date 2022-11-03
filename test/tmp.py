# import echo_dataset
#
# print(echo_dataset.CONFIG)


# import xarray as xr
#
#
# # xr.open_zarr(self.sv_path, chunks={'frequency': 'auto'})
# sv_path = "../data/sandeel_survey/2019/test_survey_0/ACOUSTIC/GRIDDED/SCH72_2019241_sv.zarr"
# sv = xr.open_zarr(sv_path, chunks={'frequency': 'auto'})
# window = 50 # H, W
# x1, y1 = 0, 0
# x2, y2 = x1 + window, y1 + window
# crop = sv.isel(
#     {
#         "frequency": slice(len(sv.frequency)),
#         "ping_time": slice(x1, x2),
#         "range": slice(y1, y2)
#     }
# )
# print(sv.range)


# from echo_dataset.core import CruiseConfig, Cruise
#
# import random
#
#
# conf = CruiseConfig(
#     path="../data/2018/SCH72_2019241/ACOUSTIC/GRIDDED",
#     name="test_cruise",
#     year=2018,
#     require_annotations=True
# )
# c = Cruise(conf)
# width = 256
# height = 256
# x_min, y_min = 0, 0
# x_max = c.echogram.sizes["ping_time"] - width
# y_max = c.echogram.sizes["range"] - height
# x1 = random.randint(x_min, x_max)
# y1 = random.randint(y_min, y_max)
# x2 = x1 + width
# y2 = y1 + height
#
# window = c.crop(x1, y1, x2, y2)
# print(window)


# from echo_dataset.core.data_summary import DataSummary
#
#
# s = DataSummary(
#     data_root="../data",
#     data_format="zarr"
# )
# print()


from echo_dataset.core import Cruise, EchoDataset, CruiseConfig, RandomSchoolSampler


paths = [
    "../data/2018/SCH72_2019241/ACOUSTIC/GRIDDED",
    "../data/2018/SYNTH_34322/ACOUSTIC/GRIDDED",
    "../data/2019/SYNTH_9393784/ACOUSTIC/GRIDDED"
]
# paths = [
#     "../data/sandeel_survey/2018/test_survey_0/ACOUSTIC/GRIDDED",
#     "../data/sandeel_survey/2018/test_survey_1/ACOUSTIC/GRIDDED",
#     "../data/sandeel_survey/2019/SCH72_2019241/ACOUSTIC/GRIDDED"
# ]
names = [
    "cruise 1",
    None,
    "cruise 3"
]
years = [
    2019,
    2018,
    None
]

cruises = list()
for i in range(len(paths)):
    cfg = CruiseConfig(
        path=paths[i],
        name=names[i],
        year=years[i],
        require_annotations=True,
        require_bottom=False,
        settings=None
    )
    cruises.append(Cruise(cfg))

sampler = RandomSchoolSampler(window_size=(256, 256))

ds = EchoDataset(
    cruises=cruises,
    sampler=sampler,
    pseudo_length=1,
    cfg="./config.yaml"
)
print(ds)

a = ds[0]
b = ds[1]

for k, v in a.items():
    print(k)
    print(v)
    print()

for k, v in b.items():
    print(k)
    print(v)
    print()
