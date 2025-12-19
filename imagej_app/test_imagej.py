import imagej

ij = imagej.init("sc.fiji:fiji", headless=True)
print("ImageJ OK:", ij.getVersion())
