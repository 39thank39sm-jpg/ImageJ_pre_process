import os
from .ij_instance import get_ij


def run_pipeline(input_dir: str, out_gif: str, speed: int = 20):
    ij = get_ij()

    input_dir = os.path.abspath(input_dir).replace("\\", "/")
    out_gif   = os.path.abspath(out_gif).replace("\\", "/")

    macro = f"""
    run("Image Sequence...", "open={input_dir} sort");
    run("Enhance Contrast", "saturated=0.35");
    run("Invert");
    run("Animation Options...", "speed={int(speed)}");
    saveAs("GIF", "{out_gif}");
    """

    ij.py.run_macro(macro)
