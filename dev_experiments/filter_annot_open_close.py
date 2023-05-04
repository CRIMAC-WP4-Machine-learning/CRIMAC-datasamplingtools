from matplotlib import pyplot as plt
import xarray as xr
import pandas as pd
import numpy as np
import cv2 as cv

from pathlib import Path
import os


project_root = Path(os.getcwd()).parent
annot_path = (
    project_root / "data/2019/SCH72_2019242/ACOUSTIC/GRIDDED/SCH72_2019242_labels.zarr"
)
new_annot_path = (
    project_root
    / "data/2019/SCH72_2019242/ACOUSTIC/GRIDDED/SCH72_2019242_labels_thresholded.zarr"
)
annotation = xr.open_zarr(store=str(annot_path))
sv = xr.open_zarr(
    store=project_root
    / "data/2019/SCH72_2019242/ACOUSTIC/GRIDDED/SCH72_2019242_sv.zarr"
)

ann_store = np.zeros(annotation.annotation.shape)
columns = [
    "category",
    "startpingindex",
    "upperdepthindex",
    "endpingindex",
    "lowerdepthindex",
]
schools = pd.DataFrame(columns=columns)

ksize = 8
kernel = np.ones((ksize, ksize), np.uint8)
threshold = 3.67e-8
main_frequency = 38000

for count, cat in enumerate(annotation.category.data):
    if cat < 2:
        continue
    ann = np.nan_to_num(
        annotation.sel(category=cat).annotation.to_numpy(), copy=False
    ).astype(np.uint8)
    ann = cv.morphologyEx(src=ann, op=cv.MORPH_OPEN, kernel=kernel)
    contours, _ = cv.findContours(
        image=ann, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE
    )
    for i, c in enumerate(contours):
        c = c.squeeze()
        box = [c[:, 1].min(), c[:, 0].min(), c[:, 1].max(), c[:, 0].max()]
        schools = pd.concat(
            [schools, pd.DataFrame(data=[[cat, *box]], columns=columns)],
            ignore_index=True,
        )
        sv_window = (
            sv.sel(frequency=main_frequency)
            .isel(
                {
                    "ping_time": slice(box[0], box[2]),
                    "range": slice(box[1], box[3]),
                }
            )
            .sv.to_numpy()
        )
        filtered_ann = ann[box[0] : box[2], box[1] : box[3]]

        new_ann = sv_window * filtered_ann
        new_ann[new_ann < threshold] = 0
        new_ann[new_ann > 0] = 1
        new_ann = cv.morphologyEx(src=new_ann, op=cv.MORPH_CLOSE, kernel=kernel)
        new_ann = cv.morphologyEx(src=new_ann, op=cv.MORPH_OPEN, kernel=kernel)

        orig_ann = (
            annotation.sel(category=cat)
            .isel(
                {
                    "ping_time": slice(box[0], box[2]),
                    "range": slice(box[1], box[3]),
                }
            )
            .annotation.to_numpy()
        )

        fig, ax = plt.subplots(ncols=4)
        ax[0].imshow(orig_ann, vmin=0, vmax=1, cmap="Reds")
        ax[0].set_title("Original")
        ax[1].imshow(filtered_ann, vmin=0, vmax=1, cmap="Reds")
        ax[1].set_title("Filtered")
        ax[2].imshow(new_ann, vmin=0, vmax=1, cmap="Reds")
        ax[2].set_title("New")
        ax[3].imshow(sv_window, vmin=0, vmax=sv_window.max(), cmap="Reds")
        ax[3].set_title(f"SV, {main_frequency} hz")
        fig.tight_layout()
        fig.savefig(project_root / "out" / f"annot_from_mask_box_{i}.png")
        plt.close(fig)

        ann[box[0] : box[2], box[1] : box[3]] = new_ann
    ann_store[count] = ann.copy()
new_annotation = xr.open_zarr(store=new_annot_path).update(
    {"annotation": (("category", "ping_time", "range"), ann_store)}
)
new_annotation.to_zarr(store=new_annot_path.parent / "test_labels.zarr", mode="a")
schools.to_csv(path_or_buf=new_annot_path.parent / "test_schools.csv")
