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


def heat_map(traj_dir, grid):
    res = np.zeros((grid.row_num, grid.col_num), dtype=np.int32)
    files = list(os.listdir(traj_dir))
    for i in range(100):
        traj = pd.read_csv(os.path.join(traj_dir, files[i]))
        print("\r{}/{} done".format(i, len(files)), end=" ")
        for j in range(len(traj)):
            lat = traj["lat"][j]
            lng = traj["lng"][j]
            try:
                row_idx, col_idx = grid.get_matrix_idx(lat, lng)
                res[row_idx, col_idx] += 1
            except IndexError:
                # print('({}, {}) is out of mbr, skip'.format(lat, lng))
                continue
    sns.set()
    res[res == 0] = 1  # 防止log运算出错
    sns.heatmap(np.log(res), square=True, vmin=0)
    plt.savefig("./data/san_rn.pdf")
    plt.show()


if __name__ == '__main__':
    # merge_to_one("./data/taxi-sf")
    # find_bbox("./data/trajs.csv")
    san_mbr = MBR(37.6988, -122.5173, 37.8089, -122.3784)  # 12km * 12km
    san_grid = Grid(san_mbr, 1200, 1200)
    heat_map("./data/taxi", san_grid)

    print("\nok")
