from icclim.user_indice.user_indice import UserIndice
from xarray.core.dataarray import DataArray


def apply_coef(indice: UserIndice, da: DataArray) -> DataArray:
    if indice.coef is not None:
        return da * indice.coef
    return da


def filter_by_logical_op(indice: UserIndice, da: DataArray) -> DataArray:
    if indice.logical_operation is not None:
        return da.where(indice.logical_operation.compute(da, indice.thresh), drop=True)
    return da


def user_indice_max(indice: UserIndice, da: DataArray):
    da = apply_coef(indice, da)
    da = filter_by_logical_op(indice, da)
    return da.max(dim="time")


def user_indice_min(indice: UserIndice, da: DataArray):
    da = apply_coef(indice, da)
    da = filter_by_logical_op(indice, da)
    return da.min(dim="time")


def user_indice_sum(indice: UserIndice, da: DataArray):
    da = apply_coef(indice, da)
    da = filter_by_logical_op(indice, da)
    return da.sum(dim="time")


def user_indice_mean(indice: UserIndice, da: DataArray):
    da = apply_coef(indice, da)
    da = filter_by_logical_op(indice, da)
    return da.mean(dim="time")


def compute_user_indice(indice: UserIndice, da: DataArray) -> DataArray:
    return CALC_OPERATION_MAPPING[indice.calc_operation](indice, da)


CALC_OPERATION_MAPPING = {
    "max": user_indice_max,
    "min": user_indice_min,
    "sum": user_indice_sum,
    "mean": user_indice_mean,
    # TODO add others calc functions
}
