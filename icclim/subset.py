import xarray as xr
import numpy as np
import cftime
import pdb


def subset_time(ds, time_range):
    date_cf = cftime.date2num(
        [time_range], ds.time.units, calendar=ds.time.calendar)[0]
#    pdb.set_trace()
    return ds.sel(time=slice(date_cf[0], date_cf[1]))


def subset_spatial():
    # TODO
    print("TODO")


def subset_bbox(ds, time_range=None):

    # TODO spatial subset

    if time_range is not None:
        ds = subset_time(ds, time_range)

    return ds


def vectorize(encoded_ds: xr.Dataset, var_ds, indice_name, slice_mode=None):
    ds = xr.decode_cf(encoded_ds)

    time_value = ds.time.values
    year = ds.groupby(ds['time.year']).groups
    yearA = np.array([*year])

    i = 0
    season = ["MAM", "JJA", "SON"]
    centroid_time = []
    time_bnds = []

    if slice_mode in season:

        seasonA = ds.groupby(ds['time.season']).groups[slice_mode]
        for season_year in yearA:
            s_y = np.array(year[season_year])
            mask = np.isin(s_y, seasonA)
            interval_season = time_value[s_y[mask]]

            if i == 0:
                dataA = np.zeros((len(yearA), len(interval_season), len(
                    ds.coords['lat']), len(ds.coords['lon'])))
                time2compute = np.arange(len(interval_season))

            centroid_time.append(ds.time.sel(time=slice(
                interval_season[0], interval_season[-1])).mean())
            time_bnds.append([interval_season[0], interval_season[-1]])
            dataA[i, :] = ds[indice_name].sel(time=slice(
                interval_season[0], interval_season[-1])).values
            i += 1

    elif slice_mode == 'month':
        month_iteration = 0
        list_month = []
        time2compute = np.arange(31)
        for year_i in yearA:
            year_interval = [year[year_i][0], year[year_i][-1]]
            year_boundary = encoded_ds.time.values[year_interval]
            da_subset = encoded_ds.sel(time=slice(
                year_boundary[0], year_boundary[1]))
            ds_year = xr.decode_cf(da_subset)
            monthA = ds_year.groupby(ds_year['time.month']).groups

            for month in monthA:

                dat = np.zeros(
                    (31, len(ds.coords['lat']), len(ds.coords['lon'])))
                dat[:] = np.nan
                dat[np.arange(len(monthA[month])),
                    :] = ds_year[indice_name].values[monthA[month], :]
                list_month.append(dat)

                time_bnds.append([da_subset.time.values[monthA[month]]
                                  [0],
                                  da_subset.time.values[monthA[month]][-1]])
                centroid_time.append(np.mean(time_bnds[month_iteration]))

                month_iteration += 1

        dataA = np.asarray(list_month)

    lon = ds.lon.values
    lat = ds.lat.values

    data = xr.Dataset({indice_name: (['time', 'time2compute', 'lat', 'lon'], dataA),
                       'time_bnds': (['time', 'bnds'], time_bnds)},
                      coords={'time': centroid_time, 'time2compute': time2compute, 'lon': lon, 'lat': lat})

    return data
