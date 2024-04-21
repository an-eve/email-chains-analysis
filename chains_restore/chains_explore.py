import pandas as pd
import numpy as np
from collections import Counter
import json
import re
import paths



if __name__ == "__main__":
    with open('../'+paths.CHAINS_1, 'r') as file:
        chains_1 = json.load(file)
    with open('../'+paths.CHAINS_2, 'r') as file:
        chains_2 = json.load(file)