from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from config.globalConfig import globalConfig


ROOT = Path(
    r"C:\Users\Usuario\Downloads\SHARED-20260910T162811Z-1-001"
    r"\SHARED\EODP_TER_2021\EODP-TS-ISM"
)

REFERENCE_DIR = ROOT / "output"
TEST_DIR = ROOT / "output_test"

PLOT_DIR = ROOT / "cross_validation_plots"

CONFIG = globalConfig()


def read_toa(path):

    with Dataset(path, "r") as dataset:
        return np.asarray(dataset.variables["toa"][:])



def cross_validation():

    bands = CONFIG.bands  # VNIR-0, VNIR-1, VNIR-2, VNIR-3

    reference_files = {
        f.name: f for f in REFERENCE_DIR.glob("*.nc")
    }
    test_files = {
        f.name: f for f in TEST_DIR.glob("*.nc")
    }

    print("\nISM CROSS-VALIDATION (VNIR-0 to VNIR-3)\n")

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
        "- ISM VNIR cross-validation\n"
    )

    return all_identical



if __name__ == "__main__":

    passed = cross_validation()


    if not passed:
        raise AssertionError(
            "ISM cross-validation failed: "
            "output and output_test differ."
        )