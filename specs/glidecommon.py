##########################################################################
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
##########################################################################/

"""glide.h"""

#from .glidetypes import *
from .winapi import *


"""3dfx.h"""

from .stdapi import *

FxI8 = Alias("FxI8", Int8)
FxU8 = Alias("FxU8", UInt8)
FxI16 = Alias("FxI16", Int16)
FxU16 = Alias("FxU16", UInt16)
FxI32 = Alias("FxI32", Int32)
FxU32 = Alias("FxU32", UInt32)
FxI64 = Alias("FxI64", Int64)
FxU64 = Alias("FxU64", UInt64)
FxBool = Alias("FxBool", Bool)
FxFloat = Alias("FxFloat", Float)
FxDouble = Alias("FxDouble", Double)
FxColor_t = Alias("FxColor_t", UInt32)
FxColor4 = Struct("FxColor4", [
    (Float, "r"),
    (Float, "g"),
    (Float, "b"),
    (Float, "a"),
])

"""glide.h"""

GrColor_t = Alias("GrColor_t", FxU32)
GrAlpha_t = Alias("GrAlpha_t", FxU8)
GrMipMapId_t = Alias("GrMipMapId_t", FxU32)
GrFog_t = Alias("GrFog_t", FxU8)
GrFog = Array(Const(GrFog_t), 64) # GR_FOG_TABLE_SIZE

GrChipID_t = FakeEnum(FxI32, [
    "GR_TMU0",
    "GR_TMU1",
    "GR_TMU2",
    "GR_FBI",
])

GrCombineFunction_t = FakeEnum(FxI32, [
    "GR_COMBINE_FUNCTION_ZERO", # "GR_COMBINE_FUNCTION_NONE",
    "GR_COMBINE_FUNCTION_LOCAL",
    "GR_COMBINE_FUNCTION_LOCAL_ALPHA",
    "GR_COMBINE_FUNCTION_SCALE_OTHER", # "GR_COMBINE_FUNCTION_BLEND_OTHER",
    "GR_COMBINE_FUNCTION_SCALE_OTHER_ADD_LOCAL",
    "GR_COMBINE_FUNCTION_SCALE_OTHER_ADD_LOCAL_ALPHA",
    "GR_COMBINE_FUNCTION_SCALE_OTHER_MINUS_LOCAL",
    "GR_COMBINE_FUNCTION_SCALE_OTHER_MINUS_LOCAL_ADD_LOCAL", # "GR_COMBINE_FUNCTION_BLEND",
    "GR_COMBINE_FUNCTION_SCALE_OTHER_MINUS_LOCAL_ADD_LOCAL_ALPHA",
    "GR_COMBINE_FUNCTION_SCALE_MINUS_LOCAL_ADD_LOCAL", # "GR_COMBINE_FUNCTION_BLEND_LOCAL",
    "GR_COMBINE_FUNCTION_SCALE_MINUS_LOCAL_ADD_LOCAL_ALPHA",
])

GrCombineFactor_t = FakeEnum(FxI32, [
    "GR_COMBINE_FACTOR_ZERO", # "GR_COMBINE_FACTOR_NONE",
    "GR_COMBINE_FACTOR_LOCAL",
    "GR_COMBINE_FACTOR_OTHER_ALPHA",
    "GR_COMBINE_FACTOR_LOCAL_ALPHA",
    "GR_COMBINE_FACTOR_DETAIL_FACTOR", # "GR_COMBINE_FACTOR_TEXTURE_ALPHA",
    "GR_COMBINE_FACTOR_LOD_FRACTION", # "GR_COMBINE_FACTOR_TEXTURE_RGB", - RGB absent from 2.11
    "GR_COMBINE_FACTOR_ONE",
    "GR_COMBINE_FACTOR_ONE_MINUS_LOCAL",
    "GR_COMBINE_FACTOR_ONE_MINUS_OTHER_ALPHA",
    "GR_COMBINE_FACTOR_ONE_MINUS_LOCAL_ALPHA",
    "GR_COMBINE_FACTOR_ONE_MINUS_DETAIL_FACTOR", # "GR_COMBINE_FACTOR_ONE_MINUS_TEXTURE_ALPHA",
    "GR_COMBINE_FACTOR_ONE_MINUS_LOD_FRACTION",
])

GrCombineLocal_t = FakeEnum(FxI32, [
    "GR_COMBINE_LOCAL_ITERATED",
    "GR_COMBINE_LOCAL_CONSTANT", # "GR_COMBINE_LOCAL_NONE",
    "GR_COMBINE_LOCAL_DEPTH",
])

GrCombineOther_t = FakeEnum(FxI32, [
    "GR_COMBINE_OTHER_ITERATED",
    "GR_COMBINE_OTHER_TEXTURE",
    "GR_COMBINE_OTHER_CONSTANT", # "GR_COMBINE_OTHER_NONE",
])

GrAlphaSource_t = FakeEnum(FxI32, [
    "GR_ALPHASOURCE_CC_ALPHA",
    "GR_ALPHASOURCE_ITERATED_ALPHA",
    "GR_ALPHASOURCE_TEXTURE_ALPHA",
    "GR_ALPHASOURCE_TEXTURE_ALPHA_TIMES_ITERATED_ALPHA",
])

GrColorCombineFnc_t = FakeEnum(FxI32, [
    "GR_COLORCOMBINE_ZERO",
    "GR_COLORCOMBINE_CCRGB",
    "GR_COLORCOMBINE_ITRGB",
    "GR_COLORCOMBINE_ITRGB_DELTA0",
    "GR_COLORCOMBINE_DECAL_TEXTURE",
    "GR_COLORCOMBINE_TEXTURE_TIMES_CCRGB",
    "GR_COLORCOMBINE_TEXTURE_TIMES_ITRGB",
    "GR_COLORCOMBINE_TEXTURE_TIMES_ITRGB_DELTA0",
    "GR_COLORCOMBINE_TEXTURE_TIMES_ITRGB_ADD_ALPHA",
    "GR_COLORCOMBINE_TEXTURE_TIMES_ALPHA",
    "GR_COLORCOMBINE_TEXTURE_TIMES_ALPHA_ADD_ITRGB",
    "GR_COLORCOMBINE_TEXTURE_ADD_ITRGB",
    "GR_COLORCOMBINE_TEXTURE_SUB_ITRGB",
    "GR_COLORCOMBINE_CCRGB_BLEND_ITRGB_ON_TEXALPHA",
    "GR_COLORCOMBINE_DIFF_SPEC_A",
    "GR_COLORCOMBINE_DIFF_SPEC_B",
    "GR_COLORCOMBINE_ONE",
])

GrAlphaBlendFnc_t = FakeEnum(FxI32, [
    "GR_BLEND_ZERO",
    "GR_BLEND_SRC_ALPHA",
    "GR_BLEND_SRC_COLOR", # "GR_BLEND_DST_COLOR",
    "GR_BLEND_DST_ALPHA",
    "GR_BLEND_ONE",
    "GR_BLEND_ONE_MINUS_SRC_ALPHA",
    "GR_BLEND_ONE_MINUS_SRC_COLOR", # "GR_BLEND_ONE_MINUS_DST_COLOR"
    "GR_BLEND_ONE_MINUS_DST_ALPHA",
    "GR_BLEND_RESERVED_8",
    "GR_BLEND_RESERVED_9",
    "GR_BLEND_RESERVED_A",
    "GR_BLEND_RESERVED_B",
    "GR_BLEND_RESERVED_C",
    "GR_BLEND_RESERVED_D",
    "GR_BLEND_RESERVED_E",
    "GR_BLEND_ALPHA_SATURATE", # "GR_BLEND_PREFOG_COLOR"
])

GrBuffer_t = FakeEnum(FxI32, [
    "GR_BUFFER_FRONTBUFFER",
    "GR_BUFFER_BACKBUFFER",
    "GR_BUFFER_AUXBUFFER",
    "GR_BUFFER_DEPTHBUFFER",
    "GR_BUFFER_ALPHABUFFER",
    "GR_BUFFER_TRIPLEBUFFER",
])

GrChromakeyMode_t = FakeEnum(FxI32, [
    "GR_CHROMAKEY_DISABLE",
    "GR_CHROMAKEY_ENABLE",
])

GrCmpFnc_t = FakeEnum(FxI32, [
    "GR_CMP_NEVER",
    "GR_CMP_LESS",
    "GR_CMP_EQUAL",
    "GR_CMP_LEQUAL",
    "GR_CMP_GREATER",
    "GR_CMP_NOTEQUAL",
    "GR_CMP_GEQUAL",
    "GR_CMP_ALWAYS",
])

GrColorFormat_t = FakeEnum(FxI32, [
    "GR_COLORFORMAT_ARGB",
    "GR_COLORFORMAT_ABGR",
    "GR_COLORFORMAT_RGBA",
    "GR_COLORFORMAT_BGRA",
])

GrCullMode_t = FakeEnum(FxI32, [
    "GR_CULL_DISABLE",
    "GR_CULL_NEGATIVE",
    "GR_CULL_POSITIVE",
])

GrDepthBufferMode_t = FakeEnum(FxI32, [
    "GR_DEPTHBUFFER_DISABLE",
    "GR_DEPTHBUFFER_ZBUFFER",
    "GR_DEPTHBUFFER_WBUFFER",
    "GR_DEPTHBUFFER_ZBUFFER_COMPARE_TO_BIAS",
    "GR_DEPTHBUFFER_WBUFFER_COMPARE_TO_BIAS",
])

GrDitherMode_t = FakeEnum(FxI32, [
    "GR_DITHER_DISABLE",
    "GR_DITHER_2x2",
    "GR_DITHER_4x4",
])

GrLock_t = Flags(FxU32, [
    "GR_LFB_READ_ONLY", # GR_LFB_IDLE
    "GR_LFB_WRITE_ONLY",
#    "GR_LFB_WRITE_ONLY_EXPLICIT_EXT",
    "GR_LFB_NOIDLE",
])

GrLfbBypassMode_t = FakeEnum(FxI32, [
    "GR_LFBBYPASS_DISABLE",
    "GR_LFBBYPASS_ENABLE",
])

GrOriginLocation_t = FakeEnum(FxI32, [
    "GR_ORIGIN_UPPER_LEFT",
    "GR_ORIGIN_LOWER_LEFT",
    "GR_ORIGIN_ANY",
])

GrMipMapMode_t = FakeEnum(FxI32, [
    "GR_MIPMAP_DISABLE",
    "GR_MIPMAP_NEAREST",
    "GR_MIPMAP_NEAREST_DITHER",
])

MipMapLevelMask_t = Flags(FxU32, [
    "GR_MIPMAPLEVELMASK_EVEN",
    "GR_MIPMAPLEVELMASK_ODD"
])

GrSmoothingMode_t = FakeEnum(FxI32, [
    "GR_SMOOTHING_DISABLE",
    "GR_SMOOTHING_ENABLE",
])

GrTextureClampMode_t = FakeEnum(FxI32, [
    "GR_TEXTURECLAMP_WRAP",
    "GR_TEXTURECLAMP_CLAMP",
])

GrTextureCombineFnc_t = FakeEnum(FxI32, [
    "GR_TEXTURECOMBINE_ZERO",
    "GR_TEXTURECOMBINE_DECAL",
    "GR_TEXTURECOMBINE_OTHER",
    "GR_TEXTURECOMBINE_ADD",
    "GR_TEXTURECOMBINE_MULTIPLY",
    "GR_TEXTURECOMBINE_SUBTRACT",
    "GR_TEXTURECOMBINE_DETAIL",
    "GR_TEXTURECOMBINE_DETAIL_OTHER",
    "GR_TEXTURECOMBINE_TRILINEAR_ODD",
    "GR_TEXTURECOMBINE_TRILINEAR_EVEN",
    "GR_TEXTURECOMBINE_ONE",
])

GrTextureFilterMode_t = FakeEnum(FxI32, [
    "GR_TEXTUREFILTER_POINT_SAMPLED",
    "GR_TEXTUREFILTER_BILINEAR",
])

GrTextureFormat_t = FakeEnum(FxI32, [
    "GR_TEXFMT_RGB_332", # GR_TEXFMT_8BIT
    "GR_TEXFMT_YIQ_422",
    "GR_TEXFMT_ALPHA_8",
    "GR_TEXFMT_INTENSITY_8",
    "GR_TEXFMT_ALPHA_INTENSITY_44",
    "GR_TEXFMT_P_8",
    "GR_TEXFMT_RSVD0",
    "GR_TEXFMT_RSVD1",
    "GR_TEXFMT_ARGB_8332", # GR_TEXFMT_16BIT
    "GR_TEXFMT_AYIQ_8422",
    "GR_TEXFMT_RGB_565",
    "GR_TEXFMT_ARGB_1555",
    "GR_TEXFMT_ARGB_4444",
    "GR_TEXFMT_ALPHA_INTENSITY_88",
    "GR_TEXFMT_AP_88",
    "GR_TEXFMT_RSVD2", # glide3 only, GR_TEXFMT_RSVD4
])

GrNCCTable_t = FakeEnum(FxU32, [
    "GR_NCCTABLE_NCC0",
    "GR_NCCTABLE_NCC1",
])

GrTexBaseRange_t = FakeEnum(FxU32, [
    "GR_TEXBASE_256",
    "GR_TEXBASE_128",
    "GR_TEXBASE_64",
    "GR_TEXBASE_32_TO_1",
])

_GrState_s = Struct("_GrState_s", [
    (Array(Char, 312), "pad"), # 312 - GLIDE_STATE_PAD_SIZE
])

GrState = Alias("GrState", _GrState_s)

GuNccTable = Struct("GuNccTable", [
    (Array(FxU8, 16), "yRGB"),
    (Array(Array(FxI16, 3), 4), "iRGB"),
    (Array(Array(FxI16, 3), 4), "qRGB"),
    (Array(FxU32, 12), "packed_data"),
])

GuTexPalette = Struct("GuTexPalette", [
    (Array(FxU32, 256), "data"),
])

GuTexTable = Struct("GuTexTable", [
    (GuNccTable, "nccTable"),
    (GuTexPalette, "palette"),
])

GrSstType = Alias("GrSstType", Int)

GrTMUConfig_St = Struct("GrTMUConfig_St", [
    (Int, "tmuRev"),
    (Int, "tmuRam"),
])

GrTMUConfig_t = Alias("GrTMUConfig_t", GrTMUConfig_St)

GrSstPerfStats_s = Struct("GrSstPerfStats_s", [
    (FxU32, "pixelsIn"),
    (FxU32, "chromaFail"),
    (FxU32, "zFuncFail"),
    (FxU32, "aFuncFail"),
    (FxU32, "pixelsOut"),
])

GrSstPerfStats_t = Alias("GrSstPerfStats_t", GrSstPerfStats_s)

GrTmuVertex = Struct("GrTmuVertex", [
    (Float, "sow"),
    (Float, "tow"),
    (Float, "oow"),
])

GrVertex = Struct("GrVertex", [
    (Float, "x"),
    (Float, "y"),
    (Float, "z"),
    (Float, "r"),
    (Float, "g"),
    (Float, "b"),
    (Float, "ooz"),
    (Float, "a"),
    (Float, "oow"),
    (Array(GrTmuVertex, 2), "tmuvtx"),
])

GrPassthruMode_t = FakeEnum(FxI32, [
    "GR_PASSTHRU_SHOW_VGA",
    "GR_PASSTHRU_SHOW_SST1",
])

GrSTWHint_t = Flags(FxU32, [
    "GR_STWHINT_W_DIFF_FBI",
    "GR_STWHINT_W_DIFF_TMU0",
    "GR_STWHINT_ST_DIFF_TMU0",
    "GR_STWHINT_W_DIFF_TMU1",
    "GR_STWHINT_ST_DIFF_TMU1",
    "GR_STWHINT_W_DIFF_TMU2",
    "GR_STWHINT_ST_DIFF_TMU2",
])

GrErrorCallbackFnc_t = Alias("GrErrorCallbackFnc_t", Opaque("void (*)( char const *,::FxBool )"))

"""fxglide.h"""

FxVideoTimingInfo = Struct("FxVideoTimingInfo", [
    (FxU32, "hSyncOn"),
    (FxU32, "hSyncOff"),
    (FxU32, "vSyncOn"),
    (FxU32, "vSyncOff"),
    (FxU32, "hBackPorch"),
    (FxU32, "vBackPorch"),
    (FxU32, "xDimension"),
    (FxU32, "yDimension"),
    (FxU32, "memOffset"),
    (FxU32, "memFifoEntries_1MB"),
    (FxU32, "memFifoEntries_2MB"),
    (FxU32, "memFifoEntries_4MB"),
    (FxU32, "tilesInX_Over2"),
    (FxU32, "vFifoThreshold"),
    (FxBool, "video16BPPIsOK"),
    (FxBool, "video24BPPIsOK"),
    (Float, "clkFreq16bpp"),
    (Float, "clkFreq24bpp"),
])

"""gsstdef.h"""

GrSstRegister = Enum("GrSstRegister", [
   "SSTR_STATUS",
   "SSTR_RESERVED0",
   "SSTR_VAX",
   "SSTR_VAY",
   "SSTR_VBX",
   "SSTR_VBY",
   "SSTR_VCX",
   "SSTR_VCY",
   "SSTR_R",
   "SSTR_G",
   "SSTR_B",
   "SSTR_Z",
   "SSTR_A",
   "SSTR_S",
   "SSTR_T",
   "SSTR_W",
   "SSTR_DRDX",
   "SSTR_DGDX",
   "SSTR_DBDX",
   "SSTR_DZDX",
   "SSTR_DADX",
   "SSTR_DSDX",
   "SSTR_DTDX",
   "SSTR_DWDX",
   "SSTR_DRDY",
   "SSTR_DGDY",
   "SSTR_DBDY",
   "SSTR_DZDY",
   "SSTR_DADY",
   "SSTR_DSDY",
   "SSTR_DTDY",
   "SSTR_DWDY",
   "SSTR_TRIANGLECMD",
   "SSTR_RESERVED1",
   "SSTR_FVAX",
   "SSTR_FVAY",
   "SSTR_FVBX",
   "SSTR_FVBY",
   "SSTR_FVCX",
   "SSTR_FVCY",
   "SSTR_FR",
   "SSTR_FG",
   "SSTR_FB",
   "SSTR_FZ",
   "SSTR_FA",
   "SSTR_FS",
   "SSTR_FT",
   "SSTR_FW",
   "SSTR_FDRDX",
   "SSTR_FDGDX",
   "SSTR_FDBDX",
   "SSTR_FDZDX",
   "SSTR_FDADX",
   "SSTR_FDSDX",
   "SSTR_FDTDX",
   "SSTR_FDWDX",
   "SSTR_FDRDY",
   "SSTR_FDGDY",
   "SSTR_FDBDY",
   "SSTR_FDZDY",
   "SSTR_FDADY",
   "SSTR_FDSDY",
   "SSTR_FDTDY",
   "SSTR_FDWDY",
   "SSTR_FTRIANGLECMD",
   "SSTR_FBZCOLORPATH",
   "SSTR_FOGMODE",
   "SSTR_ALPHAMODE",
   "SSTR_FBZMODE",
   "SSTR_LFBMODE",
   "SSTR_CLIPLEFTRIGHT",
   "SSTR_CLIPBOTTOMTOP",
   "SSTR_NOPCMD",
   "SSTR_FASTFILLCMD",
   "SSTR_SWAPBUFFERCMD",
   "SSTR_FOGCOLOR",
   "SSTR_ZACOLOR",
   "SSTR_CHROMAKEY",
   "SSTR_RESERVED2",
   "SSTR_RESERVED3",
   "SSTR_STIPPLE",
   "SSTR_C0",
   "SSTR_C1",
   "SSTR_FBIPIXELSIN",
   "SSTR_FBICHROMAFAIL",
   "SSTR_FBIZFUNCFAIL",
   "SSTR_FBIAFUNCFAIL",
   "SSTR_FBIPIXELSOUT",
   "SSTR_FOGTABLE",
   "SSTR_RESERVED8",
   "SSTR_FBIINIT4",
   "SSTR_VRETRACE",
   "SSTR_BACKPORCH",
   "SSTR_VIDEODIMENSIONS",
   "SSTR_FBIINIT0",
   "SSTR_FBIINIT1",
   "SSTR_FBIINIT2",
   "SSTR_FBIINIT3",
   "SSTR_HSYNC",
   "SSTR_VSYNC",
   "SSTR_CLUTDATA",
   "SSTR_DACDATA",
   "SSTR_MAX_RGB_DELTA",
   "SSTR_RESERVED51",
   "SSTR_TEXTUREMODE",
   "SSTR_TLOD",
   "SSTR_TDETAIL",
   "SSTR_TEXBASEADDR",
   "SSTR_TEXBASEADDR1",
   "SSTR_TEXBASEADDR2",
   "SSTR_TEXBASEADDR38",
   "SSTR_TEXINIT0",
   "SSTR_TEXINIT1",
   "SSTR_NCCTABLE0",
   "SSTR_NCCTABLE1",
   "SSTR_END_OF_REGISTER_SET",
])

"""gump.h"""
GrMPTextureCombineFnc_t = FakeEnum(FxU32, [
    "GR_MPTEXTURECOMBINE_ADD",
    "GR_MPTEXTURECOMBINE_MULTIPLY",
    "GR_MPTEXTURECOMBINE_DETAIL0",
    "GR_MPTEXTURECOMBINE_DETAIL1",
    "GR_MPTEXTURECOMBINE_TRILINEAR0",
    "GR_MPTEXTURECOMBINE_TRILINEAR1",
    "GR_MPTEXTURECOMBINE_SUBTRACT",
])

GrMPState = Struct("GrMPState", [
  (Array(GrMipMapId_t, 2), "mmid"), # 2 - GLIDE_NUM_VIRTUAL_TMU
  (GrMPTextureCombineFnc_t, "tc_fnc"),
])

"""sst1vid.h"""

GrScreenRefresh_t = FakeEnum(FxI32, [
    "GR_REFRESH_60Hz",
    "GR_REFRESH_70Hz",
    "GR_REFRESH_72Hz",
    "GR_REFRESH_75Hz",
    "GR_REFRESH_80Hz",
    "GR_REFRESH_90Hz",
    "GR_REFRESH_100Hz",
    "GR_REFRESH_85Hz",
    "GR_REFRESH_120Hz",
    "GR_REFRESH_NONE",
])
