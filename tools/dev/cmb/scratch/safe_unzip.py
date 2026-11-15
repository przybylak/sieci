import sys, zipfile, os
src, dst = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(src)
dst = os.path.realpath(dst)
n = 0
for i in z.infolist():
    p = os.path.realpath(os.path.join(dst, i.filename))
    if not (p == dst or p.startswith(dst + os.sep)):
        sys.exit("unsafe path: " + i.filename)
    if (i.external_attr >> 16) & 0o170000 == 0o120000:
        sys.exit("symlink: " + i.filename)
    if not i.is_dir():
        n += 1
z.extractall(dst)
print("files", n, "bad:", z.testzip())
