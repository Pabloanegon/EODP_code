
# MAIN FUNCTION TO CALL THE L1B MODULE

from l1b.src.l1b import l1b

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\\Users\\Usuario\\Downloads\\SHARED-20260910T162811Z-1-001\\SHARED\\EODP_code\\auxiliary'
indir = r"C:\\Users\\Usuario\\Downloads\\SHARED-20260910T162811Z-1-001\\SHARED\\EODP_TER_2021\\EODP-TS-L1B\\input"
outdir = r"C:\\Users\\Usuario\\Downloads\\SHARED-20260910T162811Z-1-001\\SHARED\\EODP_TER_2021\\EODP-TS-L1B\\output_no_equalization"

# Initialise the ISM
myL1b = l1b(auxdir, indir, outdir)
myL1b.processModule()
