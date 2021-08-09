import datetime

import icclim.icclim


def run():
    files = "netcdf_files/climpact.sampledata.gridded.1991-2010.nc"
    out_f = "netcdf_files/output/yolo.nc"
    # bp = [datetime.datetime(1991, 1, 1), datetime.datetime(2000, 12, 31)]
    # tr = [datetime.datetime(1991, 1, 1), datetime.datetime(2010, 12, 31)]
    # icclim.icclim_new.indice(
    #     indice_name="SU",
    #     in_files=files,
    #     time_range=tr,
    #     # base_period_time_range=bp,
    #     var_name="tmax",
    #     slice_mode="month",
    #     out_file=out_f,
    #     threshold=[20, 30]
    #     # save_percentile=True,
    # )

    icclim.icclim.indice(
        in_files=files,
        var_name="tmax",
        user_indice={
            "indice_name": "my_indice",
            "calc_operation": "nb_events",
            "logical_operation": "gt",
            "thresh": 0 + 273.15,
            "date_event": True,
        },
        slice_mode="month",
        out_file=out_f,
        # save_percentile=True,
    )


if __name__ == "__main__":
    run()
