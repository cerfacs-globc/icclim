import datetime

import icclim.main
import eca_indices


def run():
    files = ["/Users/aoun/workspace/icclim/netcdf_files/climpact.full.nc"]
    # files = [
    #     "/Users/aoun/workspace/icclim/netcdf_files/climpact.sampledata.gridded.1991-2010.nc"]

    bp = [datetime.datetime(1991, 1, 1), datetime.datetime(2000, 12, 31)]
    tr = [datetime.datetime(1991, 1, 1), datetime.datetime(2010, 12, 31)]

    tas = filter(lambda x: eca_indices.TAS in x.variables, eca_indices.Indice)
    pr = filter(lambda x: eca_indices.PR in x.variables, eca_indices.Indice)
    for ind in [eca_indices.Indice.GD4]:
    # for ind in eca_indices.Indice:
    # for ind in pr:
        out_f = f"netcdf_files/output/{ind.name}_ANN_icclimv4_climpSampleData_1991_2010.nc"
        out_unit = "days"
        save_percentile = False
        if ind.name.find("p") != -1 or ind in [eca_indices.Indice.WSDI, eca_indices.Indice.CSDI] :
            out_unit = "%"
            save_percentile=True
            # continue
        if len(ind.variables) > 1:
            files = [
                "climpact.sampledata.gridded.1991-2010.nc",
                "climpact.sampledata.gridded.1991-2010.nc",
            ]
        print(ind)
        icclim.main.indice(
            indice_name=ind.name,
            in_files=files,
            slice_mode="year",
            var_name=ind.variables,
            base_period_time_range=bp,
            time_range=tr,
            out_file=out_f,
            # transfer_limit_Mbytes=200,
            out_unit=out_unit,
            save_percentile=save_percentile,
            interpolation="hyndman_fan"
        )


if __name__ == "__main__":
    run()
