import numpy as np
import pdb
class simple():

    def __init__(self):

        self.param = {}

    def _get_param(self):
        self.param = {"indice_type":"simple"}
        print(self.param)
        print('youhou')


coco = simple()
pdb.set_trace()