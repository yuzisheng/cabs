import os
import pandas as pd
from datetime import datetime


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


if __name__ == '__main__':
    merge_to_one("./data/taxi-sf")
    print("ok")
