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
REFERENCE_DIR = ROOT / "output"
L1C_DIR = ROOT / "output_test"

PLOT_DIR = ROOT / "cross_validation_plots"

CONFIG = globalConfig()
BANDS = CONFIG.bands


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



def read_grids(band):
    lat_l1b, lon_l1b = readGeodetic(
        str(GM_DIR), CONFIG.gm_geoloc
    )

    toa_l1c, lat_l1c, lon_l1c = readL1c(
        str(L1C_DIR),
        f"{CONFIG.l1c_toa}{band}.nc"
    )

    return lat_l1b, lon_l1b, lat_l1c, lon_l1c


# 1. PLOT L1B GRID VS L1C GRID

def plot_l1b_vs_l1c(lat_l1b, lon_l1b, lat_l1c, lon_l1c, band):
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

    plt.title(f"Projection on ground - {band}")
    plt.xlabel("Longitude [deg]")
    plt.ylabel("Latitude [deg]")

    plt.grid(alpha=0.4)
    plt.legend()
    plt.tight_layout()

    output_file = PLOT_DIR / f"l1b_vs_l1c_grid_{band}.png"

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
    fig.suptitle("Spatial Sampling Distance - L1B geolocation")

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

def cross_validation():

        print("\nL1C CROSS-VALIDATION (VNIR-0 to VNIR-3)\n")

        all_identical = True

        for band in BANDS:
            filename = f"{CONFIG.l1c_toa}{band}.nc"

            professor_file = REFERENCE_DIR / filename
            our_file = L1C_DIR / filename

            print(f" {band} ")

            if not professor_file.is_file() or not our_file.is_file():
                missing = [
                    str(p)
                    for p in (professor_file, our_file)
                    if not p.is_file()
                ]
                print("MISSING:", ", ".join(missing))
                all_identical = False
                continue

            professor_toa, professor_lat, professor_lon = readL1c(
                str(REFERENCE_DIR), filename
            )

            our_toa, our_lat, our_lon = readL1c(
                str(L1C_DIR), filename
            )

            band_identical = True

            for field, reference, test in (
                    ("toa", professor_toa, our_toa),
                    ("lat", professor_lat, our_lat),
                    ("lon", professor_lon, our_lon),
            ):
                if reference.shape != test.shape:
                    print(
                        f"{field}: DIFFERENT SHAPE "
                        f"{reference.shape} != {test.shape}"
                    )
                    band_identical = False
                    continue

                difference = np.abs(
                    test.astype(np.float64)
                    - reference.astype(np.float64)
                )

                identical = np.array_equal(reference, test)

                print(
                    f"{field:<5} "
                    f"identical={str(identical):<5}  "
                    f"MAE={np.mean(difference):.3e}  "
                    f"max error={np.max(difference):.3e}"
                )

                if not identical:
                    band_identical = False

            print(f"{band}: {'PASS' if band_identical else 'FAIL'}\n")
            all_identical &= band_identical

        print(
            f"RESULT: {'PASS' if all_identical else 'FAIL'} "
            "- L1C VNIR cross-validation\n"
        )

        return all_identical



if __name__ == "__main__":
    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    passed = cross_validation()

    for band in BANDS:
        filename = L1C_DIR / f"{CONFIG.l1c_toa}{band}.nc"

        if not filename.is_file():
            print(f"Skipping grid plot for {band}: {filename} not found")
            continue

        lat_l1b, lon_l1b, lat_l1c, lon_l1c = read_grids(band)

        plot_l1b_vs_l1c(
            lat_l1b,
            lon_l1b,
            lat_l1c,
            lon_l1c,
            band
        )
    if any(
        (L1C_DIR / f"{CONFIG.l1c_toa}{band}.nc").is_file()
        for band in BANDS
    ):
        spatial_sampling_distance(lat_l1b, lon_l1b)

    if not passed:
        raise AssertionError(
            "L1C cross-validation failed: output and output_test differ."
        )
