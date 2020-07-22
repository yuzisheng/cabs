import os
import pandas as pd
from datetime import datetime
from common.mbr import MBR

san_mbr = MBR(37.6988, -122.5173, 37.8089, -122.3784)  # 12km * 12km


def merge_to_one(root_path):
    """ 将多个文件合并方便处理 """
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
    """ 找到所有轨迹的MBR """
    trajs = pd.read_csv(file_path)
    # lat:(32.8697, 50.30546) lng:(-127.08143, -115.56218)
    print("total {} gps points".format(len(trajs)))
    print("lat: ({}, {})\nlng: ({}, {})".format(trajs["lat"].min(), trajs["lat"].max(),
                                                trajs["lng"].min(), trajs["lng"].max()))


def sort_by_time(traj_dir):
    """ 对轨迹点按时间排序 """
    files = list(os.listdir(traj_dir))
    for i in range(len(files)):
        traj = pd.read_csv(os.path.join(traj_dir, files[i]))
        traj.sort_values(by="time", inplace=True)
        traj.to_csv("./data/new.csv", index=False)
        traj.to_csv("./data/trajs/{}".format(files[i]), index=False)
        print("\r{}/{} done".format(i + 1, len(files)), end=" ")


def filter_od(traj_dir):
    """ 找到乘客的起点及终点数据 即OD数据"""
    files = list(os.listdir(traj_dir))
    start_pos = pd.DataFrame(columns=("lat", "lng", "time"))
    end_pos = pd.DataFrame(columns=("lat", "lng", "time"))
    for i in range(len(files)):
        print("\r{}/{} start to filter od {}".format(i + 1, len(files), files[i]), end=" ")
        traj = pd.read_csv(os.path.join(traj_dir, files[i]))
        o = []  # 忽略第一个点 (因为可能并不是起始点)
        d = []
        for j in range(1, len(traj)):
            if not san_mbr.contains(traj["lat"][j], traj["lng"][j]):
                # 过滤掉不在MBR内的点
                continue
            if traj["occ"][j] == 1 and traj["occ"][j - 1] == 1:
                continue
            elif traj["occ"][j] == 1 and traj["occ"][j - 1] == 0:
                o.append([traj["lat"][j], traj["lng"][j], traj["time"][j]])
            elif traj["occ"][j] == 0 and traj["occ"][j - 1] == 1:
                d.append([traj["lat"][j], traj["lng"][j], traj["time"][j]])
            else:
                continue
        start_pos = start_pos.append(pd.DataFrame(o, columns=["lat", "lng", "time"]))
        end_pos = end_pos.append(pd.DataFrame(d, columns=["lat", "lng", "time"]))
    start_pos.to_csv("./data/start_pos.csv", sep=",", index=False)
    end_pos.to_csv("./data/end_pos.csv", sep=",", index=False)


if __name__ == '__main__':
    # merge_to_one("./data/trajs")
    # find_bbox("./data/trajs.csv")
    # sort_by_time("./data/trajs")
    filter_od("./data/trajs")
    print("\nok")
