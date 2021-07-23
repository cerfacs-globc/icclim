from icclim.user_indice.user_indice import LogicalOperation, UserIndice


class Test_UserIndice:
    def test_simple(self):
        dico = {
            "indice_name": "my_indice",
            "calc_operation": "min",
            "logical_operation": "gt",
            "thresh": 0 + 273.15,  ### input data in Kelvin ==> threshold in Kelvin!
            "date_event": True,
        }
        plop = UserIndice(**dico)
        assert plop.indice_name == "my_indice"
        assert plop.calc_operation == "min"
        assert plop.logical_operation == LogicalOperation.GT
        assert plop.thresh == 273.15
        assert plop.date_event == True

