from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from config.globalConfig import globalConfig
from common.io.readGeodetic import readGeodetic
from common.io.l1cProduct import readL1c

ROOT = Path(
    r"C:\Users\Usuario\Downloads\SHARED-20260910T162811Z-1-001"
    r"\SHARED\EODP_TER_2021\EODP-TS-L1C"
)

INPUT_DIR = ROOT / "input"
GM_DIR = INPUT_DIR / "gm_alt100_act_150"
L1C_DIR = ROOT / "output_test"

PLOT_DIR = ROOT / "cross_validation_plots"

CONFIG = globalConfig()
BAND = "VNIR-0"


def haversine(lat1, lon1, lat2, lon2):
    R = 6378137  # Earth radius [m]

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )

    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def read_grids():
    # L1B
    lat_l1b, lon_l1b = readGeodetic(
        str(GM_DIR), CONFIG.gm_geoloc
    )

    # L1C
    toa_l1c, lat_l1c, lon_l1c = readL1c(
        str(L1C_DIR),
        f"{CONFIG.l1c_toa}{BAND}.nc"
    )

    return lat_l1b, lon_l1b, lat_l1c, lon_l1c

# 1. PLOT L1B GRID VS L1C GRID

def plot_l1b_vs_l1c(lat_l1b, lon_l1b, lat_l1c, lon_l1c):
    plt.figure(figsize=(11, 7))

    # L1B
    plt.scatter(
        lon_l1b,
        lat_l1b,
        color="red",
        s=4,
        label="L1B",
        alpha=0.7
    )

    # L1C
    plt.scatter(
        lon_l1c,
        lat_l1c,
        color="blue",
        s=4,
        label="L1C MGRS",
        alpha=0.7
    )

    plt.title("Projection on ground")
    plt.xlabel("Longitude [deg]")
    plt.ylabel("Latitude [deg]")

    plt.grid(alpha=0.4)
    plt.legend()
    plt.tight_layout()

    output_file = PLOT_DIR / "l1b_vs_l1c_grid.png"

    plt.savefig(output_file, dpi=150)
    plt.show()
    plt.close()

    print(f"Plot saved: {output_file.name}")

# 2. SPATIAL SAMPLING DISTANCE (HAVERSINE)

def spatial_sampling_distance(lat_l1b, lon_l1b):
    nlines, ncols = lat_l1b.shape

    control_row = nlines // 2      # 50
    control_col = ncols // 2       # 75

    ssd_act = []

    for j in range(ncols - 1):
        distance = haversine(
            lat_l1b[control_row, j],
            lon_l1b[control_row, j],
            lat_l1b[control_row, j + 1],
            lon_l1b[control_row, j + 1]
        )
        ssd_act.append(distance)

    ssd_act = np.array(ssd_act)

    ssd_alt = []

    for i in range(nlines - 1):
        distance = haversine(
            lat_l1b[i, control_col],
            lon_l1b[i, control_col],
            lat_l1b[i + 1, control_col],
            lon_l1b[i + 1, control_col]
        )
        ssd_alt.append(distance)

    ssd_alt = np.array(ssd_alt)

    x_act = np.arange(len(ssd_act))
    x_alt = np.arange(len(ssd_alt))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f"Spatial Sampling Distance - {BAND}")

    axes[0].plot(x_act, ssd_act, color="indianred", linewidth=2)
    axes[0].set_title(f"L1B - Control row {control_row}")
    axes[0].set_xlabel("ACT pixel")
    axes[0].set_ylabel("Spatial Sampling Distance [m]")
    axes[0].grid(alpha=0.4)
    axes[0].ticklabel_format(
        axis="y",
        style="plain",
        useOffset=False
    )

    axes[0].yaxis.set_major_formatter(
        plt.FormatStrFormatter("%.5f")
    )

    axes[1].plot(x_alt, ssd_alt, color="royalblue", linewidth=2)
    axes[1].set_title(f"L1B - Control column {control_col}")
    axes[1].set_xlabel("ALT pixel")
    axes[1].set_ylabel("Spatial Sampling Distance [m]")
    axes[1].grid(alpha=0.4)
    axes[1].ticklabel_format(
        axis="y",
        style="plain",
        useOffset=False
    )

    axes[1].yaxis.set_major_formatter(
        plt.FormatStrFormatter("%.5f")
    )

    plt.tight_layout()

    output_file = PLOT_DIR / "spatial_sampling_distance.png"

    plt.savefig(output_file, dpi=150)
    plt.show()
    plt.close()

    print(f"Plot saved: {output_file.name}")

    print()
    print("SPATIAL SAMPLING DISTANCE")
    print(f"L1B control row {control_row} mean SSD: {np.mean(ssd_act):.2f} m")
    print(f"L1B control column {control_col} mean SSD: {np.mean(ssd_alt):.2f} m")


if __name__ == "__main__":
    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    lat_l1b, lon_l1b, lat_l1c, lon_l1c = read_grids()

    plot_l1b_vs_l1c(
        lat_l1b,
        lon_l1b,
        lat_l1c,
        lon_l1c
    )

    spatial_sampling_distance(
        lat_l1b,
        lon_l1b
    )