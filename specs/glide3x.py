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

"""glide3x.h"""

from .glidecommon import *
from .winapi import *

GrAspectRatio_t = FakeEnum(FxI32, [
    "GR_ASPECT_LOG2_1x8",
    "GR_ASPECT_LOG2_1x4",
    "GR_ASPECT_LOG2_1x2",
    "GR_ASPECT_LOG2_1x1",
    "GR_ASPECT_LOG2_2x1",
    "GR_ASPECT_LOG2_4x1",
    "GR_ASPECT_LOG2_8x1",
])

GrCoordinateSpaceMode_t = FakeEnum(FxU32, [
    "GR_WINDOW_COORDS",
    "GR_CLIP_COORDS",
])

GrContext_t = Alias("GrContext_t", ULong)

GrControl_t = FakeEnum(FxU32, [
    "GR_CONTROL_ACTIVATE",
    "GR_CONTROL_DEACTIVATE",
    "GR_CONTROL_RESIZE",
    "GR_CONTROL_MOVE",
])

GrEnableMode_t = FakeEnum(FxU32, [
    "GR_MODE_DISABLE",
    "GR_AA_ORDERED", # GR_MODE_ENABLE
    "GR_ALLOW_MIPMAP_DITHER",
    "GR_PASSTHRU",
    "GR_SHAMELESS_PLUG",
    "GR_VIDEO_SMOOTHING",
])

GrFogMode_t = FakeEnum(FxI32, [
    "GR_FOG_DISABLE",
    "GR_FOG_WITH_TABLE_ON_FOGCOORD_EXT",
    "GR_FOG_WITH_TABLE_ON_Q", # GR_FOG_WITH_TABLE_ON_W
    "GR_FOG_WITH_ITERATED_Z",
    "GR_FOG_WITH_ITERATED_ALPHA_EXT",
    "GR_FOG_MULT2",
    "GR_FOG_ADD2",
])

GrHint_t = FakeEnum(FxU32, [
    "GR_HINT_STWHINT",
    "GR_HINT_FIFOCHECKHINT",
    "GR_HINT_FPUPRECISION",
    "GR_HINT_ALLOW_MIPMAP_DITHER",
    "GR_HINT_LFB_WRITE",
    "GR_HINT_LFB_PROTECT",
    "GR_HINT_LFB_RESET",
    "GR_HINT_H3DENABLE",
])

GrLfbSrcFmt_t = FakeEnum(FxU32, [
    "GR_LFB_SRC_FMT_565",
    "GR_LFB_SRC_FMT_555",
    "GR_LFB_SRC_FMT_1555",
    "GR_LFB_SRC_FMT_888",
    "GR_LFB_SRC_FMT_8888",
    "GR_LFB_SRC_FMT_565_DEPTH",
    "GR_LFB_SRC_FMT_555_DEPTH",
    "GR_LFB_SRC_FMT_1555_DEPTH",
    "GR_LFB_SRC_FMT_ZA16",
    "GR_LFB_SRC_FMT_RLE16",
])

GrLfbWriteMode_t = FakeEnum(FxI32, [
    "GR_LFBWRITEMODE_565",
    "GR_LFBWRITEMODE_555",
    "GR_LFBWRITEMODE_1555",
    "GR_LFBWRITEMODE_RESERVED1",
    "GR_LFBWRITEMODE_888",
    "GR_LFBWRITEMODE_8888",
    "GR_LFBWRITEMODE_RESERVED2",
    "GR_LFBWRITEMODE_RESERVED3",
    "GR_LFBWRITEMODE_RESERVED4",
    "GR_LFBWRITEMODE_RESERVED5",
    "GR_LFBWRITEMODE_RESERVED6",
    "GR_LFBWRITEMODE_RESERVED7",
    "GR_LFBWRITEMODE_565_DEPTH",
    "GR_LFBWRITEMODE_555_DEPTH",
    "GR_LFBWRITEMODE_1555_DEPTH",
    "GR_LFBWRITEMODE_ZA16",
    "GR_LFBWRITEMODE_ANY",
])

GrLfbInfo_t = Struct("GrLfbInfo_t", [
    (Int, "size"),
    (OpaquePointer(Void), "lfbPtr"),
    (FxU32, "strideInBytes"),
    (GrLfbWriteMode_t, "writeMode"),
    (GrOriginLocation_t, "origin"),
])

GrLOD_t = FakeEnum(FxI32, [
    "GR_LOD_LOG2_1",
    "GR_LOD_LOG2_2",
    "GR_LOD_LOG2_4",
    "GR_LOD_LOG2_8",
    "GR_LOD_LOG2_16",
    "GR_LOD_LOG2_32",
    "GR_LOD_LOG2_64",
    "GR_LOD_LOG2_128",
    "GR_LOD_LOG2_256",
    # Napalm
    "GR_LOD_LOG2_512",
    "GR_LOD_LOG2_1024",
    "GR_LOD_LOG2_2048",
])

GrOriginLocation_t = FakeEnum(FxI32, [
    "GR_ORIGIN_UPPER_LEFT",
    "GR_ORIGIN_LOWER_LEFT",
    "GR_ORIGIN_ANY",
])

GrProc = Alias("GrProc", Pointer(Opaque("int (*)()")))

GrScreenResolution_t = FakeEnum(FxI32, [
    "GR_RESOLUTION_320x200",
    "GR_RESOLUTION_320x240",
    "GR_RESOLUTION_400x256",
    "GR_RESOLUTION_512x384",
    "GR_RESOLUTION_640x200",
    "GR_RESOLUTION_640x350",
    "GR_RESOLUTION_640x400",
    "GR_RESOLUTION_640x480",
    "GR_RESOLUTION_800x600",
    "GR_RESOLUTION_960x720",
    "GR_RESOLUTION_856x480",
    "GR_RESOLUTION_512x256",
    "GR_RESOLUTION_1024x768",
    "GR_RESOLUTION_1280x1024",
    "GR_RESOLUTION_1600x1200",
    "GR_RESOLUTION_400x300",
])

GrResolution = Struct("GrResolution", [
    (GrScreenResolution_t, "resolution"),
    (GrScreenRefresh_t, "refresh"),
    (Int, "numColorBuffers"),
    (Int, "numAuxBuffers"),
])

GrStippleMode_t = FakeEnum(FxI32, [
    "GR_STIPPLE_DISABLE",
    "GR_STIPPLE_PATTERN",
    "GR_STIPPLE_ROTATE",
])

GrStipplePattern_t = Alias("GrStipplePattern_t", FxU32)

GrTexInfo = Struct("GrTexInfo", [
    (GrLOD_t, "smallLodLog2"),
    (GrLOD_t, "largeLodLog2"),
    (GrAspectRatio_t, "aspectRatioLog2"),
    (GrTextureFormat_t, "format"),
    (Blob(Void, "_getTexSize({self}.smallLodLog2, {self}.largeLodLog2, {self}.aspectRatioLog2, {self}.format, evenOdd)"), "data"),
])

GrVoodooConfig_St = Struct("GrVoodooConfig_St", [
    (Int, "fbRam"),
    (Int, "fbiRev"),
    (Int, "nTexelfx"),
    (FxBool, "sliDetect"),
    (Array(GrTMUConfig_t, 2), "tmuConfig"),
])

GrVoodooConfig_t = Alias("GrVoodooConfig_t", GrVoodooConfig_St)

GrSst96Config_St = Struct("GrSst96Config_St", [
    (Int, "fbRam"),
    (Int, "nTexelfx"),
    (GrTMUConfig_t, "tmuConfig"),
])

GrSst96Config_t = Alias("GrSst96Config_t", GrSst96Config_St)

GrVoodoo2Config_t = Alias("GrVoodoo2Config_t", GrVoodooConfig_t)

GrAT3DConfig_St = Struct("GrAT3DConfig_St", [
    (Int, "rev"),
])

GrAT3DConfig_t = Alias("GrAT3DConfig_t", GrAT3DConfig_St)

GrHardwareBoard = Struct("SstBoard_u", [
    (GrSstType, "type"),
    (Union("{self}.type", [
        ("GR_SSTTYPE_VOODOO", GrVoodooConfig_t, "VoodooConfig"),
        ("GR_SSTTYPE_SST96", GrSst96Config_t, "SST96Config"),
        ("GR_SSTTYPE_AT3D", GrAT3DConfig_t, "AT3DConfig"),
        ("GR_SSTTYPE_Voodoo2", GrVoodoo2Config_t, "Voodoo2Config"),
    ]), "sstBoard"),
])

GrHwConfiguration = Struct("GrHwConfiguration", [
    (Int, "num_sst"),
    (Array(GrHardwareBoard, 4), "SSTs"), #MAX_NUM_SST
])

Gu3dfHeader = Struct("Gu3dfHeader", [
    (FxU32, "width"),
    (FxU32, "height"),
    (Int, "small_lod"),
    (Int, "large_lod"),
    (GrAspectRatio_t, "aspect_ratio"),
    (GrTextureFormat_t, "format"),
])

Gu3dfInfo = Struct("Gu3dfInfo", [
    (Gu3dfHeader, "header"),
    (GuTexTable, "table"),
    (OpaquePointer(Void), "data"),
    (FxU32, "mem_required"),
])

GrVertexLayoutParam_t = FakeEnum(FxU32, [
    "GR_PARAM_XY",
    "GR_PARAM_Z",
    "GR_PARAM_W",
    "GR_PARAM_Q",
    "GR_PARAM_FOG_EXT",
    "GR_PARAM_A",
    "GR_PARAM_RGB",
    "GR_PARAM_PARGB",
    "GR_PARAM_ST0",
    "GR_PARAM_ST1",
    "GR_PARAM_ST2",
    "GR_PARAM_Q0",
    "GR_PARAM_Q1",
    "GR_PARAM_Q2",
])

GrVertexLayoutOffset_t = FakeEnum(FxI32, [
    "GR_VERTEX_X_OFFSET",
    "GR_VERTEX_Y_OFFSET",
    "GR_VERTEX_OOZ_OFFSET",
    "GR_VERTEX_OOW_OFFSET",
    "GR_VERTEX_R_OFFSET",
    "GR_VERTEX_G_OFFSET",
    "GR_VERTEX_B_OFFSET",
    "GR_VERTEX_A_OFFSET",
    "GR_VERTEX_Z_OFFSET",
    "GR_VERTEX_SOW_TMU0_OFFSET",
    "GR_VERTEX_TOW_TMU0_OFFSET",
    "GR_VERTEX_OOW_TMU0_OFFSET",
    "GR_VERTEX_SOW_TMU1_OFFSET",
    "GR_VERTEX_TOW_TMU1_OFFSET",
    "GR_VERTEX_OOW_TMU1_OFFSET",
    "GR_VERTEX_SOW_TMU2_OFFSET",
    "GR_VERTEX_TOW_TMU2_OFFSET",
    "GR_VERTEX_OOW_TMU2_OFFSET",
])

GrVertexLayoutMode_t = FakeEnum(FxU32, [
    "GR_PARAM_DISABLE",
    "GR_PARAM_ENABLE",
])

GrDrawVertexArrayMode_t = FakeEnum(FxU32, [
    "GR_POINTS",
    "GR_LINE_STRIP",
    "GR_LINES",
    "GR_POLYGON",
    "GR_TRIANGLE_STRIP",
    "GR_TRIANGLE_FAN",
    "GR_TRIANGLES",
    "GR_TRIANGLE_STRIP_CONTINUE",
    "GR_TRIANGLE_FAN_CONTINUE",
])

GRGETRESETTYPE, GRGETRESETVALUE = EnumPolymorphic("FxU32", "pname", [
    ("GR_BITS_DEPTH", FxI32),
    ("GR_BITS_RGBA", Array(FxU32, 4)),
    ("GR_FIFO_FULLNESS", FxI32),
    ("GR_FOG_TABLE_ENTRIES", FxI32),
    ("GR_GAMMA_TABLE_ENTRIES", FxI32),
    ("GR_GLIDE_STATE_SIZE", FxI32),
    ("GR_GLIDE_VERTEXLAYOUT_SIZE", FxI32),
    ("GR_IS_BUSY", FxI32),
    ("GR_LFB_PIXEL_PIPE", FxI32),
    ("GR_MAX_TEXTURE_SIZE", FxI32),
    ("GR_MAX_TEXTURE_ASPECT_RATIO", FxI32),
    ("GR_MEMORY_FB", FxI32),
    ("GR_MEMORY_TMU", FxI32),
    ("GR_MEMORY_UMA", FxI32),
    ("GR_NUM_BOARDS", FxI32),
    ("GR_NON_POWER_OF_TWO_TEXTURES", FxI32),
    ("GR_NUM_FB", FxI32),
    ("GR_NUM_SWAP_HISTORY_BUFFER", FxI32),
    ("GR_NUM_TMU", FxI32),
    ("GR_PENDING_BUFFERSWAPS", FxI32),
    ("GR_REVISION_FB", FxI32),
    ("GR_REVISION_TMU", FxI32),
    ("GR_STATS_LINES", FxI32),
    ("GR_STATS_PIXELS_AFUNC_FAIL", FxI32),
    ("GR_STATS_PIXELS_CHROMA_FAIL", FxI32),
    ("GR_STATS_PIXELS_DEPTHFUNC_FAIL", FxI32),
    ("GR_STATS_PIXELS_IN", FxI32),
    ("GR_STATS_PIXELS_OUT", FxI32),
    ("GR_STATS_PIXELS", FxI32),
    ("GR_STATS_POINTS", FxI32),
    ("GR_STATS_TRIANGLES_IN", FxI32),
    ("GR_STATS_TRIANGLES_OUT", FxI32),
    ("GR_STATS_TRIANGLES", FxI32),
    ("GR_SWAP_HISTORY", FxI32),
    ("GR_SUPPORTS_PASSTHRU", FxI32),
    ("GR_TEXTURE_ALIGN", FxI32),
    ("GR_VIDEO_POSITION", FxI32),
    ("GR_VIEWPORT", FxI32),
    ("GR_WDEPTH_MIN_MAX", FxI32),
    ("GR_ZDEPTH_MIN_MAX", FxI32),
    ("GR_VERTEX_PARAMETER", FxI32),
    ("GR_BITS_GAMMA", Array(FxU8, 4)),
    ("GR_GET_RESERVED_1", FxI32),
], FxI32)

GrGetParam_t = FakeEnum(FxU32, [
    "GR_EXTENSION",
    "GR_HARDWARE",
    "GR_RENDERER",
    "GR_VENDOR",
    "GR_VERSION",
])

GrTexTable_t = FakeEnum(FxU32, [
    "GR_TEXTABLE_NCC0",
    "GR_TEXTABLE_NCC1",
    "GR_TEXTABLE_PALETTE",
    "GR_TEXTABLE_PALETTE_6666_EXT",
])

# TODO: extensions via grGetProcAddress

glide3x = Module("glide3x")
glide3x.addFunctions([
    StdDecoratedFunction("_grAADrawTriangle@24", Void, "grAADrawTriangle", [(Blob(Const(Void), "_getVertexSize()"), "a"), (Blob(Const(Void), "_getVertexSize()"), "b"), (Blob(Const(Void), "_getVertexSize()"), "c"), (FxBool, "ab_antialias"), (FxBool, "bc_antialias"), (FxBool, "ca_antialias")]),
    StdDecoratedFunction("_grAlphaBlendFunction@16", Void, "grAlphaBlendFunction", [(GrAlphaBlendFnc_t, "rgb_sf"), (GrAlphaBlendFnc_t, "rgb_df"), (GrAlphaBlendFnc_t, "alpha_sf"), (GrAlphaBlendFnc_t, "alpha_df")]),
    StdDecoratedFunction("_grAlphaCombine@20", Void, "grAlphaCombine", [(GrCombineFunction_t, "function"), (GrCombineFactor_t, "factor"), (GrCombineLocal_t, "local"), (GrCombineOther_t, "other"), (FxBool, "invert")]),
    StdDecoratedFunction("_grAlphaControlsITRGBLighting@4", Void, "grAlphaControlsITRGBLighting", [(FxBool, "enable")]),
    StdDecoratedFunction("_grAlphaTestFunction@4", Void, "grAlphaTestFunction", [(GrCmpFnc_t, "function")]),
    StdDecoratedFunction("_grAlphaTestReferenceValue@4", Void, "grAlphaTestReferenceValue", [(GrAlpha_t, "value")]),
    StdDecoratedFunction("_grBufferClear@12", Void, "grBufferClear", [(GrColor_t, "color"), (GrAlpha_t, "alpha"), (FxU32, "depth")]),
    StdDecoratedFunction("_grBufferSwap@4", Void, "grBufferSwap", [(FxU32, "swap_interval")]),
    StdDecoratedFunction("_grCheckForRoom@4", Void, "grCheckForRoom", [(FxI32, "n")]),
    StdDecoratedFunction("_grChromakeyMode@4", Void, "grChromakeyMode", [(GrChromakeyMode_t, "mode")]),
    StdDecoratedFunction("_grChromakeyValue@4", Void, "grChromakeyValue", [(GrColor_t, "value")]),
    StdDecoratedFunction("_grClipWindow@16", Void, "grClipWindow", [(FxU32, "minx"), (FxU32, "miny"), (FxU32, "maxx"), (FxU32, "maxy")]),
    StdDecoratedFunction("_grColorCombine@20", Void, "grColorCombine", [(GrCombineFunction_t, "function"), (GrCombineFactor_t, "factor"), (GrCombineLocal_t, "local"), (GrCombineOther_t, "other"), (FxBool, "invert")]),
    StdDecoratedFunction("_grColorMask@8", Void, "grColorMask", [(FxBool, "rgb"), (FxBool, "a")]),
    StdDecoratedFunction("_grConstantColorValue@4", Void, "grConstantColorValue", [(GrColor_t, "value")]),
    StdDecoratedFunction("_grCoordinateSpace@4", Void, "grCoordinateSpace", [(GrCoordinateSpaceMode_t, "mode")]),
    StdDecoratedFunction("_grCullMode@4", Void, "grCullMode", [(GrCullMode_t, "mode")]),
    StdDecoratedFunction("_grDepthBiasLevel@4", Void, "grDepthBiasLevel", [(FxI32, "level")]),
    StdDecoratedFunction("_grDepthBufferFunction@4", Void, "grDepthBufferFunction", [(GrCmpFnc_t, "function")]),
    StdDecoratedFunction("_grDepthBufferMode@4", Void, "grDepthBufferMode", [(GrDepthBufferMode_t, "mode")]),
    StdDecoratedFunction("_grDepthMask@4", Void, "grDepthMask", [(FxBool, "mask")]),
    StdDecoratedFunction("_grDepthRange@8", Void, "grDepthRange", [(FxFloat, "n"), (FxFloat, "f")]),
    StdDecoratedFunction("_grDisable@4", Void, "grDisable", [(GrEnableMode_t, "mode")]),
    StdDecoratedFunction("_grDisableAllEffects@0", Void, "grDisableAllEffects", []),
    StdDecoratedFunction("_grDitherMode@4", Void, "grDitherMode", [(GrDitherMode_t, "mode")]),
    StdDecoratedFunction("_grDrawLine@8", Void, "grDrawLine", [(Blob(Const(Void), "_getVertexSize()"), "v1"), (Blob(Const(Void), "_getVertexSize()"), "v2")]),
    StdDecoratedFunction("_grDrawPoint@4", Void, "grDrawPoint", [(Blob(Const(Void), "_getVertexSize()"), "pt")]),
    StdDecoratedFunction("_grDrawTriangle@12", Void, "grDrawTriangle", [(Blob(Const(Void), "_getVertexSize()"), "a"), (Blob(Const(Void), "_getVertexSize()"), "b"), (Blob(Const(Void), "_getVertexSize()"), "c")]),
    StdDecoratedFunction("_grDrawVertexArray@12", Void, "grDrawVertexArray", [(GrDrawVertexArrayMode_t, "mode"), (FxU32, "count"), (PointersArray(Blob(Void, "_getVertexSize()"), "count"), "pointers")]),
    StdDecoratedFunction("_grDrawVertexArrayContiguous@16", Void, "grDrawVertexArrayContiguous", [(GrDrawVertexArrayMode_t, "mode"), (FxU32, "count"), (Blob(Void, "stride * count"), "pointers"), (FxU32, "stride")]),
    StdDecoratedFunction("_grEnable@4", Void, "grEnable", [(GrEnableMode_t, "mode")]),
    StdDecoratedFunction("_grErrorSetCallback@4", Void, "grErrorSetCallback", [(GrErrorCallbackFnc_t, "fnc")], sideeffects=False),
    StdDecoratedFunction("_grFinish@0", Void, "grFinish", []),
    StdDecoratedFunction("_grFlush@0", Void, "grFlush", []),
    StdDecoratedFunction("_grFogColorValue@4", Void, "grFogColorValue", [(GrColor_t, "fogcolor")]),
    StdDecoratedFunction("_grFogMode@4", Void, "grFogMode", [(GrFogMode_t, "mode")]),
    StdDecoratedFunction("_grFogTable@4", Void, "grFogTable", [(Blob(Const(GrFog_t), "GR_FOG_TABLE_SIZE"), "ft")]),
    StdDecoratedFunction("_grGet@12", FxU32, "grGet", [(GRGETRESETTYPE, "pname"), (FxU32, "plength"), Out(Pointer(GRGETRESETVALUE), "params")], sideeffects=False),
    StdDecoratedFunction("_grGetProcAddress@4", GrProc, "grGetProcAddress", [(Pointer(Char), "procName")]),
    StdDecoratedFunction("_grGetString@4", ConstPointer(Char), "grGetString", [(GrGetParam_t, "pname")], sideeffects=False),
    StdDecoratedFunction("_grGlideGetState@4", Void, "grGlideGetState", [Out(Pointer(Void), "state")], sideeffects=False),
    StdDecoratedFunction("_grGlideGetVertexLayout@4", Void, "grGlideGetVertexLayout", [Out(Pointer(Void), "layout")], sideeffects=False),
    StdDecoratedFunction("_grGlideInit@0", Void, "grGlideInit", []),
    StdDecoratedFunction("_grGlideSetState@4", Void, "grGlideSetState", [(OpaquePointer(Const(Void)), "state")]),
    StdDecoratedFunction("_grGlideSetVertexLayout@4", Void, "grGlideSetVertexLayout", [(OpaquePointer(Const(Void)), "layout")]),
    StdDecoratedFunction("_grGlideShutdown@0", Void, "grGlideShutdown", []),
    StdDecoratedFunction("_grLfbConstantAlpha@4", Void, "grLfbConstantAlpha", [(GrAlpha_t, "alpha")]),
    StdDecoratedFunction("_grLfbConstantDepth@4", Void, "grLfbConstantDepth", [(FxU32, "depth")]),
    StdDecoratedFunction("_grLfbLock@24", FxBool, "grLfbLock", [(GrLock_t, "type"), (GrBuffer_t, "buffer"), (GrLfbWriteMode_t, "writeMode"), (GrOriginLocation_t, "origin"), (FxBool, "pixelPipeline"), InOut(Pointer(GrLfbInfo_t), "info")]),
    StdDecoratedFunction("_grLfbReadRegion@28", FxBool, "grLfbReadRegion", [(GrBuffer_t, "src_buffer"), (FxU32, "src_x"), (FxU32, "src_y"), (FxU32, "src_width"), (FxU32, "src_height"), (FxU32, "dst_stride"), Out(Blob(Void, "dst_stride * src_height"), "dst_data")], sideeffects=False),
    StdDecoratedFunction("_grLfbUnlock@8", FxBool, "grLfbUnlock", [(GrLock_t, "type"), (GrBuffer_t, "buffer")]),
    StdDecoratedFunction("_grLfbWriteColorFormat@4", Void, "grLfbWriteColorFormat", [(GrColorFormat_t, "colorFormat")]),
    StdDecoratedFunction("_grLfbWriteColorSwizzle@8", Void, "grLfbWriteColorSwizzle", [(FxBool, "swizzleBytes"), (FxBool, "swapWords")]),
    StdDecoratedFunction("_grLfbWriteRegion@36", FxBool, "grLfbWriteRegion", [(GrBuffer_t, "dst_buffer"), (FxU32, "dst_x"), (FxU32, "dst_y"), (GrLfbSrcFmt_t, "src_format"), (FxU32, "src_width"), (FxU32, "src_height"), (FxBool, "pixelPipeline"), (FxI32, "src_stride"), In(Blob(Void, "src_stride * src_height"), "src_data")]),
    StdDecoratedFunction("_grLoadGammaTable@16", Void, "grLoadGammaTable", [(FxU32, "nentries"), Out(Pointer(FxU32), "red"), Out(Pointer(FxU32), "green"), Out(Pointer(FxU32), "blue")]),
    # if output == null this function returns the size required to request resolution list, if output != null then it copies to output ptr resolution array, just save first returned in the trace
    StdDecoratedFunction("_grQueryResolutions@8", FxI32, "grQueryResolutions", [(ConstPointer(GrResolution), "resTemplate"), Out(Pointer(GrResolution), "output")], sideeffects=False),
    StdDecoratedFunction("_grRenderBuffer@4", Void, "grRenderBuffer", [(GrBuffer_t, "buffer")]),
    StdDecoratedFunction("_grReset@4", FxBool, "grReset", [(GRGETRESETTYPE  , "what")]),
    StdDecoratedFunction("_grSelectContext@4", FxBool, "grSelectContext", [(GrContext_t, "context")]),
    StdDecoratedFunction("_grSetNumPendingBuffers@4", Void, "grSetNumPendingBuffers", [(FxI32, "NumPendingBuffers")]),
    StdDecoratedFunction("_grSplash@20", Void, "grSplash", [(Float, "x"), (Float, "y"), (Float, "width"), (Float, "height"), (FxU32, "frame")]),
    StdDecoratedFunction("_grSstOrigin@4", Void, "grSstOrigin", [(GrOriginLocation_t, "origin")]),
    StdDecoratedFunction("_grSstSelect@4", Void, "grSstSelect", [(Int, "which_sst")]),
    StdDecoratedFunction("_grSstWinClose@4", FxBool, "grSstWinClose", [(GrContext_t, "context")]),
    StdDecoratedFunction("_grSstWinOpen@28", GrContext_t, "grSstWinOpen", [(FxU32, "hWnd"), (GrScreenResolution_t, "screen_resolution"), (GrScreenRefresh_t, "refresh_rate"), (GrColorFormat_t, "color_format"), (GrOriginLocation_t, "origin_location"), (Int, "nColBuffers"), (Int, "nAuxBuffers")]),
    StdDecoratedFunction("_grStippleMode@4", Void, "grStippleMode", [(GrStippleMode_t, "mode")]),
    StdDecoratedFunction("_grStipplePattern@4", Void, "grStipplePattern", [(GrStipplePattern_t, "mode")]),
    StdDecoratedFunction("_grTexCalcMemRequired@16", FxU32, "grTexCalcMemRequired", [(GrLOD_t, "lodmin"), (GrLOD_t, "lodmax"), (GrAspectRatio_t, "aspect"), (GrTextureFormat_t, "fmt")], sideeffects=False),
    StdDecoratedFunction("_grTexClampMode@12", Void, "grTexClampMode", [(GrChipID_t, "tmu"), (GrTextureClampMode_t, "s_clampmode"), (GrTextureClampMode_t, "t_clampmode")]),
    StdDecoratedFunction("_grTexCombine@28", Void, "grTexCombine", [(GrChipID_t, "tmu"), (GrCombineFunction_t, "rgb_function"), (GrCombineFactor_t, "rgb_factor"), (GrCombineFunction_t, "alpha_function"), (GrCombineFactor_t, "alpha_factor"), (FxBool, "rgb_invert"), (FxBool, "alpha_invert")]),
    StdDecoratedFunction("_grTexDetailControl@16", Void, "grTexDetailControl", [(GrChipID_t, "tmu"), (Int, "lod_bias"), (FxU8, "detail_scale"), (Float, "detail_max")]),
    StdDecoratedFunction("_grTexDownloadMipMap@16", Void, "grTexDownloadMipMap", [(GrChipID_t, "tmu"), (FxU32, "startAddress"), (MipMapLevelMask_t, "evenOdd"), (Pointer(GrTexInfo), "info")]),
    StdDecoratedFunction("_grTexDownloadMipMapLevel@32", Void, "grTexDownloadMipMapLevel", [(GrChipID_t, "tmu"), (FxU32, "startAddress"), (GrLOD_t, "thisLod"), (GrLOD_t, "largeLod"), (GrAspectRatio_t, "aspectRatio"), (GrTextureFormat_t, "format"), (MipMapLevelMask_t, "evenOdd"), (Blob(Void, "_getTexSize(thisLod, largeLod, aspectRatio, format, evenOdd)"), "data")]),
    StdDecoratedFunction("_grTexDownloadMipMapLevelPartial@40", FxBool, "grTexDownloadMipMapLevelPartial", [(GrChipID_t, "tmu"), (FxU32, "startAddress"), (GrLOD_t, "thisLod"), (GrLOD_t, "largeLod"), (GrAspectRatio_t, "aspectRatio"), (GrTextureFormat_t, "format"), (MipMapLevelMask_t, "evenOdd"), (Blob(Void, "_getTexSize(thisLod, largeLod, aspectRatio, format, evenOdd)"), "data"), (Int, "start"), (Int, "end")]),
    StdDecoratedFunction("_grTexDownloadTable@8", Void, "grTexDownloadTable", [(GrTexTable_t, "type"), (Blob(Void, "_getTexTableSize(type)"), "data")]),
    StdDecoratedFunction("_grTexDownloadTablePartial@16", Void, "grTexDownloadTablePartial", [(GrTexTable_t, "type"), (Blob(Void, "_getTexTableSize(type)"), "data"), (Int, "start"), (Int, "end")]),
    StdDecoratedFunction("_grTexFilterMode@12", Void, "grTexFilterMode", [(GrChipID_t, "tmu"), (GrTextureFilterMode_t, "minfilter_mode"), (GrTextureFilterMode_t, "magfilter_mode")]),
    StdDecoratedFunction("_grTexLodBiasValue@8", Void, "grTexLodBiasValue", [(GrChipID_t, "tmu"), (Float, "bias")]),
    StdDecoratedFunction("_grTexMaxAddress@4", FxU32, "grTexMaxAddress", [(GrChipID_t, "tmu")], sideeffects=False),
    StdDecoratedFunction("_grTexMinAddress@4", FxU32, "grTexMinAddress", [(GrChipID_t, "tmu")], sideeffects=False),
    StdDecoratedFunction("_grTexMipMapMode@12", Void, "grTexMipMapMode", [(GrChipID_t, "tmu"), (GrMipMapMode_t, "mode"), (FxBool, "lodBlend")]),
    StdDecoratedFunction("_grTexMultibase@8", Void, "grTexMultibase", [(GrChipID_t, "tmu"), (FxBool, "enable")]),
    StdDecoratedFunction("_grTexMultibaseAddress@20", Void, "grTexMultibaseAddress", [(GrChipID_t, "tmu"), (GrTexBaseRange_t, "range"), (FxU32, "startAddress"), (MipMapLevelMask_t, "evenOdd"), Out(Pointer(GrTexInfo), "info")]),
    StdDecoratedFunction("_grTexNCCTable@4", Void, "grTexNCCTable", [(GrNCCTable_t, "table")]),
    StdDecoratedFunction("_grTexSource@16", Void, "grTexSource", [(GrChipID_t, "tmu"), (FxU32, "startAddress"), (MipMapLevelMask_t, "evenOdd"), (Pointer(GrTexInfo), "info")]),
    StdDecoratedFunction("_grTexTextureMemRequired@8", FxU32, "grTexTextureMemRequired", [(MipMapLevelMask_t, "evenOdd"), (Pointer(GrTexInfo), "info")]),
    StdDecoratedFunction("_grVertexLayout@12", Void, "grVertexLayout", [(GrVertexLayoutParam_t, "param"), (GrVertexLayoutOffset_t, "offset"), (GrVertexLayoutMode_t, "mode")]),
    StdDecoratedFunction("_grViewport@16", Void, "grViewport", [(FxI32, "x"), (FxI32, "y"), (FxI32, "width"), (FxI32, "height")]),
    StdDecoratedFunction("_gu3dfGetInfo@8", FxBool, "gu3dfGetInfo", [(ConstPointer(Char), "filename"), Out(Pointer(Gu3dfInfo), "info")], sideeffects=False),
    StdDecoratedFunction("_gu3dfLoad@8", FxBool, "gu3dfLoad", [(ConstPointer(Char), "filename"), Out(Pointer(Gu3dfInfo), "data")]),
    StdDecoratedFunction("_guFogGenerateExp@8", Void, "guFogGenerateExp", [Out(Pointer(GrFog_t), "fogtable"), (Float, "density")]),
    StdDecoratedFunction("_guFogGenerateExp2@8", Void, "guFogGenerateExp2", [Out(Pointer(GrFog_t), "fogtable"), (Float, "density")]),
    StdDecoratedFunction("_guFogGenerateLinear@12", Void, "guFogGenerateLinear", [Out(Pointer(GrFog_t), "fogtable"), (Float, "nearZ"), (Float, "farZ")]),
    StdDecoratedFunction("_guFogTableIndexToW@4", Float, "guFogTableIndexToW", [(Int, "i")]),
    StdDecoratedFunction("_guGammaCorrectionRGB@12", Void, "guGammaCorrectionRGB", [(FxFloat, "red"), (FxFloat, "green"), (FxFloat, "blue")]),
])

