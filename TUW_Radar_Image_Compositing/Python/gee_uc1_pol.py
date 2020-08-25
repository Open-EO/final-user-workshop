import openeo

# Connect to backend via basic authentication
con = openeo.connect("https://earthengine.openeo.org/v1.0")
con.authenticate_basic("group1", "test123")

datacube = con.load_collection("COPERNICUS/S1_GRD",
                               spatial_extent={"west": 16.06, "south": 48.1, "east": 16.65,
                                               "north": 48.31, "crs": "EPSG:4326"},
                               temporal_extent=["2017-03-01", "2017-04-01"],
                               bands=["VV", "VH"])

mean = datacube.mean_time()

vh = openeo.internal.graph_building.PGNode("array_element", arguments={"data": {"from_parameter": "data"}, "label": "VH"})
vv = openeo.internal.graph_building.PGNode("array_element", arguments={"data": {"from_parameter": "data"}, "label": "VV"})
reducer = openeo.internal.graph_building.PGNode("subtract", arguments={"x": {"from_node": vh}, "y": {"from_node": vv}})

datacube = mean.reduce_dimension(dimension="bands", reducer=reducer)

# B

blue = datacube.add_dimension(name="bands", label="B", type="bands")

# G

green = mean.filter_bands(["VH"])
green = green.rename_labels(dimension="bands", target=["G"])

# R

red = mean.filter_bands(["VV"])
red = red.rename_labels(dimension="bands", target=["R"])

# RGB

datacube = red.merge(green).merge(blue)

datacube = datacube.save_result(format="GTIFF-THUMB")

# Send Job to backend
job = datacube.send_job()

res = job.start_and_wait().download_results()