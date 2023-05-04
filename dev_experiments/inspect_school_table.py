from matplotlib import pyplot as plt
import xarray as xr
import pandas as pd
import numpy as np
import cv2 as cv

from pathlib import Path
import os


project_root = Path(os.getcwd()).parent
data_dir = "data"
interpath = "ACOUSTIC/GRIDDED"
trip_name = "SCH72_2019242"
year = "2019"
data_root = project_root / data_dir / year / trip_name / interpath

sv_path = data_root / (trip_name + "_sv.zarr")
annotation_path = data_root / (trip_name + "_labels.zarr")
filtered_annotation_path = data_root / (trip_name + "_labels_filtered.zarr")
schools_path = data_root / (trip_name + "_labels.parquet.csv")
filtered_schools_path = data_root / (trip_name + "_labels_filtered.csv")

sv = xr.open_zarr(store=sv_path)
annotation = xr.open_zarr(store=annotation_path)
annotation_filtered = xr.open_zarr(store=filtered_annotation_path)
schools = pd.read_csv(filepath_or_buffer=schools_path)
schools_filtered = pd.read_csv(filepath_or_buffer=filtered_schools_path)

main_frequency = 38000
unique_categories = schools.category.unique()

for cat in unique_categories:
    if cat not in annotation.category:
        continue
    for i, s in schools[schools.category == cat].iterrows():
        ping_time_slice = slice(s.startpingindex, s.endpingindex + 1)
        range_slice = slice(s.upperdepthindex, s.lowerdepthindex + 1)
        sv_window = sv.isel(
            {"ping_time": ping_time_slice, "range": range_slice}
        ).sel(frequency=main_frequency).sv.to_numpy()
        ann_window = annotation.isel(
            {"ping_time": ping_time_slice, "range": range_slice}
        ).sel(category=cat).annotation.to_numpy()
        ann_filtered_window = annotation_filtered.isel(
            {"ping_time": ping_time_slice, "range": range_slice}
        ).sel(category=cat).annotation.to_numpy()
        fig, ax = plt.subplots(ncols=3)
        ax[0].imshow(sv_window, cmap="seismic")
        ax[0].set_title("SV")
        ax[1].imshow(ann_window, vmin=-2, vmax=2, cmap="Pastel1")
        ax[1].set_title("Orig")
        ax[2].imshow(ann_filtered_window, vmin=-2, vmax=2, cmap="Pastel1")
        ax[2].set_title("New")
        fig.suptitle(f"Category {cat}")
        fig.tight_layout()
        fig.savefig(project_root / "out" / f"orig_schools_vis_{cat}_{i}.png")
        plt.close()

for cat in unique_categories:
    if cat not in annotation.category:
        continue
    for i, s in schools_filtered[schools_filtered.category == cat].iterrows():
        ping_time_slice = slice(s.startpingindex, s.endpingindex)
        range_slice = slice(s.upperdepthindex, s.lowerdepthindex)
        sv_window = sv.isel(
            {"ping_time": ping_time_slice, "range": range_slice}
        ).sel(frequency=main_frequency).sv.to_numpy()
        ann_window = annotation.isel(
            {"ping_time": ping_time_slice, "range": range_slice}
        ).sel(category=cat).annotation.to_numpy()
        ann_filtered_window = annotation_filtered.isel(
            {"ping_time": ping_time_slice, "range": range_slice}
        ).sel(category=cat).annotation.to_numpy()
        fig, ax = plt.subplots(ncols=3)
        ax[0].imshow(sv_window, cmap="seismic")
        ax[0].set_title("SV")
        ax[1].imshow(ann_window, vmin=-2, vmax=2, cmap="Pastel1")
        ax[1].set_title("Orig")
        ax[2].imshow(ann_filtered_window, vmin=-2, vmax=2, cmap="Pastel1")
        ax[2].set_title("New")
        fig.suptitle(f"Category {cat}")
        fig.tight_layout()
        fig.savefig(project_root / "out" / f"new_schools_vis_{cat}_{i}.png")
        plt.close()
