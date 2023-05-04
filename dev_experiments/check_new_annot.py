from matplotlib import pyplot as plt
import xarray as xr
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
    / "data/2019/SCH72_2019242/ACOUSTIC/GRIDDED/test_labels.zarr"
)
annotation = xr.open_zarr(store=annot_path)
new_annotation = xr.open_zarr(store=new_annot_path)

for cat in annotation.category.data:
    if cat < 2:
        continue
    ann = annotation.sel(category=cat).annotation.to_numpy().astype(np.uint8)
    contours, _ = cv.findContours(
        image=ann, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE
    )
    for i, c in enumerate(contours):
        c = c.squeeze()
        box = [c[:, 1].min(), c[:, 0].min(), c[:, 1].max(), c[:, 0].max()]
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
        new_ann = (
            new_annotation.sel(category=cat)
            .isel(
                {
                    "ping_time": slice(box[0], box[2]),
                    "range": slice(box[1], box[3]),
                }
            )
            .annotation.to_numpy()
        )

        fig, ax = plt.subplots(ncols=2)
        ax[0].imshow(orig_ann, vmin=0, vmax=1, cmap="Reds")
        ax[0].set_title("Original")
        ax[1].imshow(new_ann, vmin=0, vmax=1, cmap="Reds")
        ax[1].set_title("New")
        fig.tight_layout()
        fig.savefig(project_root / "out" / f"annot_validation_box_{i}.png")
        plt.close(fig)