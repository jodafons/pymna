import pytest, os
import numpy as np
import pymna
from pymna.simulator import Simulator  # Adjust the import based on your project structure

module_path = pymna.__file__
module_directory = os.path.dirname(module_path)

def get_reference( path ):
    with open(path, 'r') as f:
        lines = f.readlines()
        keys = lines[0].strip().split()
        d={k:[] for k in keys}
        print(keys)
        for l in lines[1::]:
            ll=l.strip().split()
            for idx, key in enumerate(keys):
                d[key].append( float(ll[idx]) )
        return d




class TestTransient:


    def test_chua(self) -> bool:

        """Test the Chua circuit transient simulation."""
        testfile = module_directory + "/tests/data/netlists/Chua.net"
        reffile  = module_directory + "/tests/data/results/Chua.sim"
        simulator = Simulator()
        circuit, result = simulator.run_from_nl( testfile )
        ref = get_reference(reffile)
        for key in ref.keys():
            ref_values = np.array(ref[key])
            result_values = np.array(result[key])
            assert len(ref_values) == len(result_values), f"Length mismatch for key '{key}': {len(ref_values)} != {len(result_values)}"
            assert np.abs(ref_values-result_values).sum() < 0.1, f"Value mismatch for key '{key}'"
        return True



if __name__ == "__main__":

    test = TestTransient()
    test.test_chua()