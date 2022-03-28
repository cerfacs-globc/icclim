from xarray import DataArray, Dataset


# FIXME To remove once minimal xarray version is v0.20.0 (use .chunksizes instead)
def _da_chunksizes(da: DataArray) -> dict:
    # Copied and adapted from xarray
    if hasattr(da.data, "chunks"):
        return {dim: c for dim, c in zip(da.dims, da.data.chunks)}
    else:
        return {}


# FIXME To remove once minimal xarray version is v0.20.0 (use .chunksizes instead)
def _get_chunksizes(ds: Dataset) -> dict:
    # Copied and adapted from xarray
    chunks = {}
    for v in ds.variables.values():
        if hasattr(v.data, "chunks"):
            for dim, c in _da_chunksizes(v).items():
                if dim in chunks and c != chunks[dim]:
                    raise ValueError(
                        f"Object has inconsistent chunks along dimension {dim}."
                        " This can be fixed by calling unify_chunks()."
                    )
                chunks[dim] = c
    return chunks
