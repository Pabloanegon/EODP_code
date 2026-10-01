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

    reference_files = {
        file.name: file
        for file in REFERENCE_DIR.glob("*.nc")
    }

    test_files = {
        file.name: file
        for file in TEST_DIR.glob("*.nc")
    }

    missing_test = reference_files.keys() - test_files.keys()
    missing_reference = test_files.keys() - reference_files.keys()

    if missing_test:
        print()
        print("Files present in professor output but missing in output_test:")
        for filename in sorted(missing_test):
            print("   ", filename)

    if missing_reference:
        print()
        print("Files present in output_test but missing in professor output:")
        for filename in sorted(missing_reference):
            print("   ", filename)

    common_files = reference_files.keys() & test_files.keys()

    if not common_files:
        print("No common NetCDF files found.")
        return False

    print()
    print("ISM CROSS-VALIDATION")
    print()

    all_identical = True

    for filename in sorted(common_files):

        reference = read_toa(reference_files[filename])
        test = read_toa(test_files[filename])

        if reference.shape != test.shape:
            print(
                f"{filename:<35} "
                f"DIFFERENT SHAPE "
                f"{reference.shape} != {test.shape}"
            )
            all_identical = False
            continue

        difference = (
            test.astype(np.float64)
            - reference.astype(np.float64)
        )

        abs_difference = np.abs(difference)

        mae = np.mean(abs_difference)
        max_error = np.max(abs_difference)

        identical = np.array_equal(reference, test)

        print(
            f"{filename:<35} "
            f"identical={str(identical):<5}  "
            f"MAE={mae:.3e}  "
            f"max error={max_error:.3e}"
        )

        if not identical:
            all_identical = False

    print()

    if all_identical:
        print(
            "RESULT: PASS - All comparable ISM outputs are identical."
        )
    else:
        print(
            "RESULT: FAIL - Differences were found in comparable outputs."
        )

    print()

    return all_identical


if __name__ == "__main__":

    passed = cross_validation()


    if not passed:
        raise AssertionError(
            "ISM cross-validation failed: "
            "output and output_test differ."
        )