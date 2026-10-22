from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset

from config.globalConfig import globalConfig

ROOT = Path(
    r"C:\Users\Usuario\Downloads\SHARED-20260910T162811Z-1-001"
    r"\SHARED\EODP_TER_2021\EODP-TS-L1B"
)

REFERENCE_DIR = ROOT / "output"
TEST_DIR = ROOT / "output_test"
NO_EQ_DIR = ROOT / "output_no_equalization"
INPUT_DIR = ROOT / "input"

PLOT_DIR = ROOT / "cross_validation_plots"

CONFIG = globalConfig()


def read_toa(path):
    with Dataset(path, "r") as dataset:
        return np.asarray(dataset.variables["toa"][:])


def cross_validation():

    reference_files = {
        file.name: file
        for file in REFERENCE_DIR.glob("*.nc")
    }

    test_files = {
        file.name: file
        for file in TEST_DIR.glob("*.nc")
    }

    if reference_files.keys() != test_files.keys():
        missing_test = reference_files.keys() - test_files.keys()
        missing_reference = test_files.keys() - reference_files.keys()

        if missing_test:
            print("Missing in output_test:", sorted(missing_test))

        if missing_reference:
            print("Missing in output:", sorted(missing_reference))

        return False

    print()
    print("L1B CROSS-VALIDATION")

    all_identical = True

    for filename in sorted(reference_files):

        reference = read_toa(reference_files[filename])
        test = read_toa(test_files[filename])

        if reference.shape != test.shape:
            print(f"{filename:<30} DIFFERENT SHAPE")
            all_identical = False
            continue

        difference = (
            test.astype(np.float64)
            - reference.astype(np.float64)
        )

        mae = np.mean(np.abs(difference))
        max_error = np.max(np.abs(difference))

        identical = np.array_equal(reference, test)

        print(
            f"{filename:<30} "
            f"identical={str(identical):<5}  "
            f"MAE={mae:.3e}  "
            f"max error={max_error:.3e}"
        )

        if not identical:
            all_identical = False

    if all_identical:
        print("RESULT: PASS - All NetCDF outputs are identical.")
    else:
        print("RESULT: FAIL - Differences were found.")

    print()

    return all_identical

def cross_validation():

    bands = CONFIG.bands  # VNIR-0, VNIR-1, VNIR-2, VNIR-3

    reference_files = {
        f.name: f for f in REFERENCE_DIR.glob("*.nc")
    }
    test_files = {
        f.name: f for f in TEST_DIR.glob("*.nc")
    }

    print("\nL1B CROSS-VALIDATION (VNIR-0 to VNIR-3)\n")

    all_identical = True

    for band in bands:
        filenames = sorted(
            filename
            for filename in reference_files.keys() | test_files.keys()
            if filename.endswith(f"{band}.nc")
        )

        print(f" {band} ")

        if not filenames:
            print(f"Missing files for {band} in both folders")
            all_identical = False
            continue

        band_identical = True

        for filename in filenames:
            if filename not in reference_files or filename not in test_files:
                missing_in = (
                    "output"
                    if filename not in reference_files
                    else "output_test"
                )
                print(f"{filename}: MISSING in {missing_in}")
                band_identical = False
                continue

            reference = read_toa(reference_files[filename])
            test = read_toa(test_files[filename])

            if reference.shape != test.shape:
                print(
                    f"{filename}: DIFFERENT SHAPE "
                    f"{reference.shape} != {test.shape}"
                )
                band_identical = False
                continue

            difference = np.abs(
                test.astype(np.float64)
                - reference.astype(np.float64)
            )

            mae = np.mean(difference)
            max_error = np.max(difference)
            identical = np.array_equal(reference, test)

            print(
                f"{filename:<35} "
                f"identical={str(identical):<5}  "
                f"MAE={mae:.3e}  "
                f"max error={max_error:.3e}"
            )

            if not identical:
                band_identical = False

        print(f"{band}: {'PASS' if band_identical else 'FAIL'}\n")
        all_identical &= band_identical

    print(
        f"RESULT: {'PASS' if all_identical else 'FAIL'} "
        "- L1B VNIR cross-validation\n"
    )

    return all_identical


def plot_equalization_effect(band):

    # Output resultados
    professor_file = (
        REFERENCE_DIR
        / f"{CONFIG.l1b_toa}{band}.nc"
    )

    # output_test resultado
    our_file = (
        TEST_DIR
        / f"{CONFIG.l1b_toa}{band}.nc"
    )

    # L1B sin equalization
    no_eq_file = (
        NO_EQ_DIR
        / f"{CONFIG.l1b_toa}{band}.nc"
    )

    # Señal de referencia después ISRF
    isrf_file = (
        INPUT_DIR
        / f"{CONFIG.ism_toa_isrf}{band}.nc"
    )

    professor = read_toa(professor_file)
    ours = read_toa(our_file)
    no_eq = read_toa(no_eq_file)
    isrf = read_toa(isrf_file)

    # Revisar que todo tiene las mismas dimensiones
    if not (
        professor.shape
        == ours.shape
        == no_eq.shape
        == isrf.shape
    ):
        raise ValueError(
            f"Different matrix dimensions for {band}"
        )

    alt = professor.shape[0] // 2
    act = np.arange(professor.shape[1])

    plt.figure(figsize=(11, 6))

    # Referencia después de ISRF
    plt.plot(
        act,
        isrf[alt, :],
        color="blue",
        linewidth=2,
        label="TOA after the ISRF",
        zorder=1
    )

    # Sin equalization
    plt.plot(
        act,
        no_eq[alt, :],
        color="red",
        linewidth=1.4,
        label="TOA L1B no eq",
        zorder=2
    )

    # Output resultados
    plt.plot(
        act,
        professor[alt, :],
        color="black",
        linewidth=2.5,
        label="L1B with eq-output",
        zorder=3
    )

    # output_test resultados
    plt.plot(
        act,
        ours[alt, :],
        color="green",
        linestyle="--",
        linewidth=1.3,
        marker="o",
        markersize=3,
        markevery=10,
        label="L1B with eq-output_test",
        zorder=4
    )

    plt.title(f"Effect of the Equalization for {band}")
    plt.xlabel("ACT pixel [-]")
    plt.ylabel("TOA [mW/m2/sr]")

    plt.grid(alpha=0.4)
    plt.legend()
    plt.tight_layout()

    output_file = (
        PLOT_DIR
        / f"equalization_effect_{band}.png"
    )

    plt.savefig(output_file, dpi=150)
    plt.close()

    print(f"Plot saved: {output_file.name}")


def plot_all_bands():

    PLOT_DIR.mkdir(exist_ok=True)

    print("Generating equalization plots:")

    for band in CONFIG.bands:
        plot_equalization_effect(band)

    print()

if __name__ == "__main__":

    passed = cross_validation()

    plot_all_bands()

    if not passed:
        raise AssertionError(
            "Cross-validation failed: output and output_test differ."
        )