import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from common.mbr import MBR
from common.grid import Grid

san_mbr = MBR(37.6988, -122.5173, 37.8089, -122.3784)  # 12km * 12km
san_grid = Grid(san_mbr, 120, 120)


def multi_files_heat_map(traj_dir):
    """ 画出轨迹热力图 """
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


def cal_grid(file_path):
    res = np.zeros((san_grid.row_num, san_grid.col_num), dtype=np.int32)
    start_pos = pd.read_csv(file_path)
    for i in range(len(start_pos)):
        lat = start_pos["lat"][i]
        lng = start_pos["lng"][i]
        try:
            row_idx, col_idx = san_grid.get_matrix_idx(lat, lng)
            res[row_idx, col_idx] += 1
        except IndexError:
            # print('({}, {}) is out of mbr, skip'.format(lat, lng))
            continue
    print("cal grid done")
    return res


def heat_map(data):
    sns.set()
    # data[data <= 0] = 1  # 防止log运算出错
    # sns.heatmap(np.log(data), square=True, vmin=0)
    sns.heatmap(data, square=True, vmin=0)
    # plt.savefig("./data/san_heat_map.pdf".format(san_grid.row_num, san_grid.col_num))
    plt.show()


if __name__ == '__main__':
    # multi_files_heat_map("./data/trajs")
    # heat_map(cal_grid("./data/start_pos.csv") - cal_grid("./data/end_pos.csv"))
    # heat_map(cal_grid("./data/end_pos.csv") - cal_grid("./data/start_pos.csv"))
    print("ok")
