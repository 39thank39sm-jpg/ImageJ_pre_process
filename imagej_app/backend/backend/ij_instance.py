import imagej

_ij = None

def get_ij():
    global _ij
    if _ij is None:
        _ij = imagej.init("sc.fiji:fiji", mode="headless")
    return _ij
