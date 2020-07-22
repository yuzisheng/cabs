import os
import pandas as pd
from datetime import datetime


def weekday(time):
    # Monday == 0 ... Sunday == 6
    return datetime.strptime(time, "%Y-%m-%d %H:%M:%S").date().weekday()


def weekday_yes_count(traj_dir):
    """计算一周每天的平均载客数量"""
    def count_occ(o: list) -> int:
        if len(o) == 0:
            return 0
        count = 1 if o[0] == 1 else 0
        for k in range(1, len(o)):
            if o[k] == 1 and o[k - 1] != 1:
                count += 1
        return count

    week_count = [0] * 7
    files = list(os.listdir(traj_dir))
    for i in range(0, len(files)):
        print("{}/{} start to analyze {}".format(i + 1, len(files), files[i]))
        traj = pd.read_csv(os.path.join(traj_dir, files[i]))
        start_date = datetime.strptime(traj["time"][0], "%Y-%m-%d %H:%M:%S").date()
        occ = []
        for j in range(len(traj)):
            if traj["time"][j][0:10] in ["2008-05-17", "2008-05-18", "2008-05-19"]:
                continue
            cur_date = datetime.strptime(traj["time"][j], "%Y-%m-%d %H:%M:%S").date()
            occ.append(traj["occ"][j])
            if cur_date != start_date:
                # print("{}({}): occupy count {}".format(start_date, start_date.weekday(), count_occ(occ)))
                week_count[start_date.weekday()] += count_occ(occ)
                start_date = cur_date
                occ.clear()
        # print("{}({}): occupy count {}".format(start_date, start_date.weekday(), count_occ(occ)))  # 打印最后一天信息
        week_count[start_date.weekday()] += count_occ(occ)
    print(week_count)


def day_yes_count(traj_dir):
    hour_count = [0] * 24
    files = list(os.listdir(traj_dir))
    for i in range(0, len(files)):
        print("{}/{} start to analyze {}".format(i + 1, len(files), files[i]))
        traj = pd.read_csv(os.path.join(traj_dir, files[i]))
        # hour (0-23)
        for j in range(1, len(traj)):
            if traj["occ"][j] == 1 and traj["occ"][j - 1] == 0:
                cur_hour = datetime.strptime(traj["time"][j], "%Y-%m-%d %H:%M:%S").hour
                hour_count[cur_hour] += 1
    print(hour_count)


if __name__ == '__main__':
    # print(weekday("2008-05-17 00:32:44"), weekday("2008-06-10 00:32:44"))
    # weekday_yes_count("./data/trajs")  # [52894, 52185, 54102, 55406, 61225, 73183, 69741]
    # print(((73183 + 69741) / 2) / ((52894 + 52185 + 54102 + 55406 + 61225) / 5))  # 29.5%
    day_yes_count("./data/trajs")
    print("ok")
