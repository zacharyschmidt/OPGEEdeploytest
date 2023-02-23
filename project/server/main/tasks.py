# project/server/main/tasks.py

import os

import pandas as pd
import os
from datetime import date
from opgee.tool import Opgee
import warnings


def get_data():
    opg = Opgee.getInstance(loadPlugins=False)
    plugins = opg._plugins
    print(plugins)
    args = opg.parser.parse_args(args=["run", "-a", "example", "-p", "test_rmi.csv"])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        opg.run(args=args)
    result = pd.read_csv("test_rmi.csv")
    return result
    pass


if __name__ == '__main__':
    get_data()
