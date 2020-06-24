import os
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime
import matplotlib.pyplot as plt
from common.mbr import MBR
from common.grid import Grid


def merge_to_one(root_path):
    files = list(filter(lambda x: x.startswith("new_"), os.listdir(root_path)))  # filter no data files
    trajs = pd.DataFrame(columns=("lat", "lng", "occ", "time", "oid"))
    oid = 1
    for file in files:
        print("\r{}/{} done".format(oid, len(files)), end="")
        traj = pd.read_table(os.path.join(root_path, file),
                             sep=" ", names=["lat", "lng", "occ", "time"])  # [latitude, longitude, occupancy, time]
        traj["time"] = traj.apply(lambda x: datetime.fromtimestamp(x["time"]), axis=1)
        traj["oid"] = oid
        traj[["oid", "lat", "lng", "time", "occ"]].to_csv(root_path + "/new/{}.csv".format(oid), sep=",", index=False)
        trajs = trajs.append(traj)
        oid += 1
    trajs[["oid", "lat", "lng", "time", "occ"]].to_csv("./data/trajs.csv", sep=",", index=False)


def find_bbox(file_path):
    trajs = pd.read_csv(file_path)
    # lat:(32.8697, 50.30546) lng:(-127.08143, -115.56218)
    print("lat: ({}, {})\nlng: ({}, {})".format(trajs["lat"].min(), trajs["lat"].max(),
                                                trajs["lng"].min(), trajs["lng"].max()))


def heat_map(file_path, grid):
    res = np.zeros((grid.row_num, grid.col_num), dtype=np.int32)
    data = pd.read_csv(file_path)
    print(data.head())
    for i in range(len(data)):
        lat = data["lat"][i]
        lng = data["lng"][i]
        try:
            row_idx, col_idx = grid.get_matrix_idx(lat, lng)
            res[row_idx, col_idx] += 1
        except IndexError:
            # print('({0}, {1}) is out of mbr, skip'.format(lat, lng))
            continue
    sns.set()
    sns.heatmap(res, square=True)
    plt.show()


if __name__ == '__main__':
    # merge_to_one("./data/taxi-sf")
    # find_bbox("./data/trajs.csv")
    san_mbr = MBR(37.474, 122.637, 38.025, -121.926)  # 60km * 60km
    san_grid = Grid(san_mbr, 600, 600)
    heat_map("./data/trajs.csv", san_grid)

    print("ok")
