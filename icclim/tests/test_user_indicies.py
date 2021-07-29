from icclim.user_indice.user_indice import LogicalOperation, UserIndiceConfig


class Test_UserIndice:
    def test_simple(self):
        dico = {
            "indice_name": "my_indice",
            "calc_operation": "min",
            "logical_operation": "gt",
            "thresh": 0 + 273.15,
            "date_event": True,
        }
        plop = UserIndiceConfig(**dico, freq="MS")
        assert plop.indice_name == "my_indice"
        assert plop.calc_operation == "min"
        assert plop.logical_operation == LogicalOperation.GREATER_THAN
        assert plop.thresh == 273.15
        assert plop.date_event
