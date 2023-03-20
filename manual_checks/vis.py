from echo_dataset import dst

# import holoviews.operation.datashader as hd
import holoviews as hv
from bokeh.plotting import show


path = "../data/2019/SCH72_2019241/ACOUSTIC/GRIDDED"
name = "SCH72_2019241"
year = 2019

cruise_cfg = dst.CruiseConfig(
    path=path,
    name=name,
    year=year,
    require_annotations=True,
    require_bottom=True,
    settings=None,
)
cruise = dst.CruiseBase(conf=cruise_cfg)
category = cruise.categories[0]
data = cruise.crop(0, 0, cruise.num_pings, cruise.num_ranges)
# data = cruise.crop(0, 0, 500, 1000)
sv = data["echogram"].sv
annotations = data["annotations"].sel({"category": category})

plot_data = sv.sel({"frequency": 38000})

clipping = {"NaN": "#00000000"}
hv.extension("bokeh", logo=False)
hv.opts.defaults(
    hv.opts.Image(
        logz=True,
        active_tools=["xwheel_zoom"],
        invert_yaxis=True,
        clipping_colors=clipping,
    )
)
vdims = ["sv"]
kdims = ["ping_time", "range"]
hv_dataset = hv.Dataset(plot_data, vdims=vdims, kdims=kdims)
hv_image = hv.Image(hv_dataset)
hv.render(hv_image).opts()

# hv_dyn_large = hd.regrid(hv_image)


# fig, ax = plt.subplots()
# # ax.set_aspect(cruise.num_pings / cruise.num_ranges)
# ax.imshow(plot_data, interpolation="nearest", aspect="auto")
# fig.show()

print(data)
