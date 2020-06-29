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


def heat_map(traj_dir):
    san_mbr = MBR(37.6988, -122.5173, 37.8089, -122.3784)  # 12km * 12km
    san_grid = Grid(san_mbr, 800, 800)
    res = np.zeros((san_grid.row_num, san_grid.col_num), dtype=np.int32)
    files = list(os.listdir(traj_dir))
    for i in range(len(files)):
        traj = pd.read_csv(os.path.join(traj_dir, files[i]))
        for j in range(len(traj)):
            lat = traj["lat"][j]
            lng = traj["lng"][j]
            try:
                row_idx, col_idx = san_grid.get_matrix_idx(lat, lng)
                res[row_idx, col_idx] += 1
            except IndexError:
                # print('({}, {}) is out of mbr, skip'.format(lat, lng))
                continue
        print("\r{}/{} done".format(i + 1, len(files)), end=" ")
    sns.set()
    res[res == 0] = 1  # 防止log运算出错
    sns.heatmap(np.log(res), square=True, vmin=0)
    plt.savefig("./data/san_rn_{}_{}.pdf".format(san_grid.row_num, san_grid.col_num))
    plt.show()


def sort_by_time(traj_dir):
    files = list(os.listdir(traj_dir))
    for i in range(len(files)):
        traj = pd.read_csv(os.path.join(traj_dir, files[i]))
        traj.sort_values(by="time", inplace=True)
        traj.to_csv("./data/new.csv", index=False)
        traj.to_csv("./data/trajs/{}".format(files[i]), index=False)
        print("\r{}/{} done".format(i + 1, len(files)), end=" ")


def convert_to_wkt(traj_dir):
    # TODO
    files = list(os.listdir(traj_dir))
    for i in range(len(files)):
        traj = pd.read_csv(os.path.join(traj_dir, files[i]))
        print("\r{}/{} done".format(i + 1, len(files)), end=" ")


def empty_rate(traj_dir):
    def count_occ(o: list) -> int:
        count = 1 if o[0] == 1 else 0
        for k in range(1, len(o)):
            if o[k] == 1 and o[k - 1] != 1:
                count += 1
        return count

    files = list(os.listdir(traj_dir))
    for i in range(len(files)):
        print("{}/{} start to analyze {}".format(i + 1, len(files), files[i]))
        traj = pd.read_csv(os.path.join(traj_dir, files[i]))
        start_date = datetime.strptime(traj["time"][0], "%Y-%m-%d %H:%M:%S").date()
        occ = []
        for j in range(len(traj)):
            occ.append(traj["occ"][j])
            cur_date = datetime.strptime(traj["time"][j], "%Y-%m-%d %H:%M:%S").date()
            if cur_date != start_date:
                print("{}: occupy count {}".format(start_date, count_occ(occ)))
                start_date = cur_date
                occ.clear()
        print("{}: occupy count {}".format(start_date, count_occ(occ)))  # 打印最后一天信息


if __name__ == '__main__':
    # merge_to_one("./data/taxi-sf")
    # find_bbox("./data/trajs.csv")
    # sort_by_time("./data/taxi")
    heat_map("./data/taxi")
    empty_rate("./data/trajs")

    print("\nok")
