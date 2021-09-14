import encodings
import os


def disable(control):
    control.configure(state="disabled")
    control.configure(cursor="")


def enable(control, cursor="hand2"):
    control.configure(state="normal")
    control.configure(cursor=cursor)


def get_encodings():
    result = []
    first = []

    for encoding in os.listdir(os.path.dirname(encodings.__file__)):
        if encoding.startswith("__"):
            continue

        if encoding.endswith(".pyc"):
            encoding = encoding[:-4]
        elif encoding.endswith(".py"):
            encoding = encoding[:-3]

        encoding = encoding.replace("_", "-").replace("cp", "CP").replace("euc", "EUC").replace("utf", "UTF")\
            .replace("iso", "ISO").replace("jp", "JP")

        encoding = encoding[0].upper() + encoding[1:]
        cid = 0
        nm = encoding.find("-", cid)
        while nm != -1:
            cid = nm + 1
            encoding = encoding[:cid] + encoding[cid].upper() + encoding[nm + 2:]
            nm = encoding.find("-", cid)

        if encoding in ["UTF-8", "CP932", "EUC-JP", "UTF-16", "ASCII"]:
            first.append(encoding)
        else:
            result.append(encoding)

    return first + result
