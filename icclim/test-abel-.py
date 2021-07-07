import datetime

import icclim_new


def run():
    files = "climpact.sampledata.gridded.1991-2010.nc"
    out_f = "icclim.v5.nc"
    bp = [datetime.datetime(1991, 1, 1), datetime.datetime(2000, 12, 31)]
    tr = [datetime.datetime(2001, 1, 1), datetime.datetime(2010, 12, 31)]
    icclim_new.indice(
        indice_name="TX90p",
        in_files=files,
        time_range=tr,
        base_period_time_range=bp,
        var_name="tmax",
        slice_mode="month",
        out_file=out_f,
        # save_percentile=True,
    )


if __name__ == "__main__":
    run()

