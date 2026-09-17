
# MAIN FUNCTION TO CALL THE ISM MODULE

from ism.src.ism import ism

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\\Users\\Usuario\\Downloads\\SHARED-20260910T162811Z-1-001\\SHARED\\EODP_code\\auxiliary'
indir = r"C:\\Users\\Usuario\\Downloads\\SHARED-20260910T162811Z-1-001\\SHARED\\EODP_TER_2021\\EODP-TS-ISM\\input\\gradient_alt100_act150"
outdir = r"C:\\Users\\Usuario\\Downloads\\SHARED-20260910T162811Z-1-001\\SHARED\\EODP_TER_2021\\EODP-TS-ISM\\output_test"
# Initialise the ISM
myIsm = ism(auxdir, indir, outdir)
myIsm.processModule()
