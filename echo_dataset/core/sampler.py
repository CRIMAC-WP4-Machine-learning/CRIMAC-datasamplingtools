__all__ = ["ISampler", "RandomSampler"]


class ISampler:
    def __call__(self, *args, **kwargs) -> dict[str, any]:
        raise NotImplementedError


class RandomSampler(ISampler):
    pass
