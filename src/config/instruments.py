from enum import StrEnum


class Instruments(StrEnum):
    ARCS = "arcs"
    CG2 = "cg2"
    CNCs = "cncs"
    CORELLI = "corelli"
    EQSANS = "eqsans"
    HB2A = "hb2a"
    HB2B = "hb2b"
    HB2C = "hb2c"
    HB3A = "hb3a"
    HYS = "hys"
    MANDI = "mandi"
    NOM = "nom"
    PG3 = "pg3"
    REF_L = "ref_l"
    REF_M = "ref_m"
    SEQ = "seq"
    SNAP = "snap"
    TOPAZ = "topaz"
    USANS = "usans"
    VULCAN = "vulcan"
    # instruments that haven't published to livedata yet
    BL0 = "bl0"
    BSS = "bss"
    CG1D = "cg1d"
    CG3 = "cg3"
    FNPB = "fnpb"
    HB3 = "hb3"
    NOWB = "nowb"
    NOWD = "nowd"
    NOWG = "nowg"
    NOWV = "nowv"
    NOWX = "nowx"
    NSE = "nse"
    VENUS = "venus"
    VIS = "vis"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)
