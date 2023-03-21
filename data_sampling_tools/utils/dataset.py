from ..core import IStatelessSampler, IStatefulSampler

from typing import Union, Optional


def eval_dataset_length(
    sampler: Union[IStatelessSampler, IStatefulSampler],
    pseudo_length: Optional[int] = None,
) -> int:
    if issubclass(type(sampler), IStatelessSampler):
        length = int(pseudo_length) if pseudo_length is not None else 1
    elif issubclass(type(sampler), IStatefulSampler):
        length = len(sampler)
    else:
        raise TypeError("Wrong sampler type")
    return length


__all__ = ["eval_dataset_length"]
