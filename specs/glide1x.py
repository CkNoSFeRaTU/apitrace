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

"""glide1x.h"""

from .glidecommon import *
from .winapi import *


GrAspectRatio_t = FakeEnum(FxI32, [
    "GR_ASPECT_8x1",
    "GR_ASPECT_4x1",
    "GR_ASPECT_2x1",
    "GR_ASPECT_1x1",
    "GR_ASPECT_1x2",
    "GR_ASPECT_1x4",
    "GR_ASPECT_1x8",
])

GrFogMode_t = FakeEnum(FxI32, [
    "GR_FOG_DISABLE",
    "GR_FOG_WITH_ITERATED_ALPHA",
    "GR_FOG_WITH_TABLE",
    "GR_FOG_MULT2",
    "GR_FOG_ADD2",
])

GrHint_t = FakeEnum(FxU32, [
    "GR_HINT_STWHINT",
    "GR_HINT_FIFOCHECKHINT",
    "GR_HINT_FPUPRECISION",
    "GR_HINT_ALLOW_MIPMAP_DITHER",
])

GrLfbBypassMode_t = FakeEnum(FxI32, [
    "GR_LFBBYPASS_DISABLE",
    "GR_LFBBYPASS_ENABLE",
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
    "GR_LFBWRITEMODE_DEPTH_DEPTH", # "GR_LFBWRITEMODE_ALPHA_ALPHA"
])

GrLOD_t = FakeEnum(FxI32, [
    "GR_LOD_256",
    "GR_LOD_128",
    "GR_LOD_64",
    "GR_LOD_32",
    "GR_LOD_16",
    "GR_LOD_8",
    "GR_LOD_4",
    "GR_LOD_2",
    "GR_LOD_1",
])

GrMipMapInfo = Struct("GrMipMapInfo", [
    (Int, "sst"),
    (FxBool, "valid"),
    (Int, "width"),
    (Int, "height"),
    (GrAspectRatio_t, "aspect_ratio"),
    (OpaquePointer(Void), "data"),
    (GrTextureFormat_t, "format"),
    (GrMipMapMode_t, "mipmap_mode"),
    (GrTextureFilterMode_t, "magfilter_mode"),
    (GrTextureFilterMode_t, "minfilter_mode"),
    (GrTextureClampMode_t, "s_clamp_mode"),
    (GrTextureClampMode_t, "t_clamp_mode"),
    (FxU32, "tLOD"),
    (FxU32, "tTextureMode"),
    (FxU32, "lod_bias"),
    (GrLOD_t, "lod_min"),
    (GrLOD_t, "lod_max"),
    (Int, "tmu"),
    (FxU32, "odd_even_mask"),
    (FxU32, "tmu_base_address"),
    (FxBool, "trilinear"),
    (GuNccTable, "ncc_table"),
])

GrOriginLocation_t = FakeEnum(FxI32, [
    "GR_ORIGIN_UPPER_LEFT",
    "GR_ORIGIN_LOWER_LEFT",
])

GrPassthruMode_t = FakeEnum(FxI32, [
    "GR_PASSTHRU_SHOW_VGA",
    "GR_PASSTHRU_SHOW_SST1",
])

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
])

GrResolution = Struct("GrResolution", [
    (GrScreenResolution_t, "resolution"),
    (GrScreenRefresh_t, "refresh"),
    (Int, "numColorBuffers"),
    (Int, "numAuxBuffers"),
])

GrSmoothingMode_t = FakeEnum(FxI32, [
    "GR_SMOOTHING_DISABLE",
    "GR_SMOOTHING_ENABLE",
])

GrTexInfo = Struct("GrTexInfo", [
    (GrLOD_t, "smallLod"),
    (GrLOD_t, "largeLod"),
    (GrAspectRatio_t, "aspectRatio"),
    (GrTextureFormat_t, "format"),
    (Blob(Void, "_getTexSizeAPI({self}.smallLod, {self}.largeLod, {self}.aspectRatio, {self}.format, evenOdd)"), "data"),
])

GrTexTable_t = FakeEnum(FxU32, [
    "GR_TEXTABLE_NCC0",
    "GR_TEXTABLE_NCC1",
    "GR_TEXTABLE_PALETTE",
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

glide1x = Module("glide")
glide1x.addFunctions([
    StdDecoratedFunction("_ConvertAndDownloadRle@64", Void, "ConvertAndDownloadRle", [(GrChipID_t, "tmu"), (FxU32, "startAddress"), (GrLOD_t, "thisLod"), (GrLOD_t, "largeLod"), (GrAspectRatio_t, "aspectRatio"), (GrTextureFormat_t, "format"), (MipMapLevelMask_t, "evenOdd"), Out(Pointer(FxU8), "bm_data"), (Long, "bm_h"), (FxU32, "u0"), (FxU32, "v0"), (FxU32, "width"), (FxU32, "height"), (FxU32, "dest_width"), (FxU32, "dest_height"), Out(Pointer(FxU16), "tlut")]),
    StdDecoratedFunction("_grAADrawLine@8", Void, "grAADrawLine", [(Pointer(Const(GrVertex)), "v1"), (Pointer(Const(GrVertex)), "v2")]),
    StdDecoratedFunction("_grAADrawPoint@4", Void, "grAADrawPoint", [(Pointer(Const(GrVertex)), "pt")]),
    StdDecoratedFunction("_grAADrawPolygon@12", Void, "grAADrawPolygon", [(Const(Int), "nverts"), (Blob(Const(Int), "nverts * sizeof(FxI32)"), "ilist"), (Blob(Const(GrVertex), "nverts * sizeof(GrVertex)"), "vlist")]),
    StdDecoratedFunction("_grAADrawPolygonVertexList@8", Void, "grAADrawPolygonVertexList", [(Const(Int), "nverts"), (Blob(Const(GrVertex), "nverts * sizeof(GrVertex)"), "vlist")]),
    StdDecoratedFunction("_grAADrawTriangle@24", Void, "grAADrawTriangle", [(Pointer(Const(GrVertex)), "a"), (Pointer(Const(GrVertex)), "b"), (Pointer(Const(GrVertex)), "c"), (FxBool, "ab_antialias"), (FxBool, "bc_antialias"), (FxBool, "ca_antialias")]),
    StdDecoratedFunction("_grAlphaBlendFunction@16", Void, "grAlphaBlendFunction", [(GrAlphaBlendFnc_t, "rgb_sf"), (GrAlphaBlendFnc_t, "rgb_df"), (GrAlphaBlendFnc_t, "alpha_sf"), (GrAlphaBlendFnc_t, "alpha_df")]),
    StdDecoratedFunction("_grAlphaCombine@20", Void, "grAlphaCombine", [(GrCombineFunction_t, "function"), (GrCombineFactor_t, "factor"), (GrCombineLocal_t, "local"), (GrCombineOther_t, "other"), (FxBool, "invert")]),
    StdDecoratedFunction("_grAlphaControlsITRGBLighting@4", Void, "grAlphaControlsITRGBLighting", [(FxBool, "enable")]),
    StdDecoratedFunction("_grAlphaTestFunction@4", Void, "grAlphaTestFunction", [(GrCmpFnc_t, "function")]),
    StdDecoratedFunction("_grAlphaTestReferenceValue@4", Void, "grAlphaTestReferenceValue", [(GrAlpha_t, "value")]),
    StdDecoratedFunction("_grBufferClear@12", Void, "grBufferClear", [(GrColor_t, "color"), (GrAlpha_t, "alpha"), (FxU16, "depth")]),
    StdDecoratedFunction("_grBufferNumPending@0", Int, "grBufferNumPending", []),
    StdDecoratedFunction("_grBufferSwap@4", Void, "grBufferSwap", [(Int, "swap_interval")]),
    StdDecoratedFunction("_grCheckForRoom@4", Void, "grCheckForRoom", [(FxI32, "n")]),
    StdDecoratedFunction("_grChromakeyMode@4", Void, "grChromakeyMode", [(GrChromakeyMode_t, "mode")]),
    StdDecoratedFunction("_grChromakeyValue@4", Void, "grChromakeyValue", [(GrColor_t, "value")]),
    StdDecoratedFunction("_grClipWindow@16", Void, "grClipWindow", [(Int, "minx"), (Int, "miny"), (Int, "maxx"), (Int, "maxy")]),
    StdDecoratedFunction("_grColorCombine@20", Void, "grColorCombine", [(GrCombineFunction_t, "function"), (GrCombineFactor_t, "factor"), (GrCombineLocal_t, "local"), (GrCombineOther_t, "other"), (FxBool, "invert")]),
    StdDecoratedFunction("_grColorMask@8", Void, "grColorMask", [(FxBool, "rgb"), (FxBool, "a")]),
    StdDecoratedFunction("_grConstantColorValue4@16", Void, "grConstantColorValue4", [(Float, "a"), (Float, "r"), (Float, "g"), (Float, "b")]),
    StdDecoratedFunction("_grConstantColorValue@4", Void, "grConstantColorValue", [(GrColor_t, "value")]),
    StdDecoratedFunction("_grCullMode@4", Void, "grCullMode", [(GrCullMode_t, "mode")]),
    StdDecoratedFunction("_grDepthBiasLevel@4", Void, "grDepthBiasLevel", [(FxI16, "level")]),
    StdDecoratedFunction("_grDepthBufferFunction@4", Void, "grDepthBufferFunction", [(GrCmpFnc_t, "function")]),
    StdDecoratedFunction("_grDepthBufferMode@4", Void, "grDepthBufferMode", [(GrDepthBufferMode_t, "mode")]),
    StdDecoratedFunction("_grDepthMask@4", Void, "grDepthMask", [(FxBool, "mask")]),
    StdDecoratedFunction("_grDisableAllEffects@0", Void, "grDisableAllEffects", []),
    StdDecoratedFunction("_grDitherMode@4", Void, "grDitherMode", [(GrDitherMode_t, "mode")]),
    StdDecoratedFunction("_grDrawLine@8", Void, "grDrawLine", [(Pointer(Const(GrVertex)), "v1"), (Pointer(Const(GrVertex)), "v2")]),
    StdDecoratedFunction("_grDrawPlanarPolygon@12", Void, "grDrawPlanarPolygon", [(Int, "nverts"), (Blob(Const(Int), "nverts * sizeof(FxI32)"), "ilist"), (Blob(Const(GrVertex), "nverts * sizeof(GrVertex)"), "vlist")]),
    StdDecoratedFunction("_grDrawPlanarPolygonVertexList@8", Void, "grDrawPlanarPolygonVertexList", [(Int, "nverts"), (Blob(Const(GrVertex), "nverts * sizeof(GrVertex)"), "vlist")]),
    StdDecoratedFunction("_grDrawPoint@4", Void, "grDrawPoint", [(Pointer(Const(GrVertex)), "pt")]),
    StdDecoratedFunction("_grDrawPolygon@12", Void, "grDrawPolygon", [(Int, "nverts"), (Blob(Const(Int), "nverts * sizeof(FxI32)"), "ilist"), (Blob(Const(GrVertex), "nverts * sizeof(GrVertex)"), "vlist")]),
    StdDecoratedFunction("_grDrawPolygonVertexList@8", Void, "grDrawPolygonVertexList", [(Int, "nverts"), (Blob(Const(GrVertex), "nverts * sizeof(GrVertex)"), "vlist")]),
    StdDecoratedFunction("_grDrawTriangle@12", Void, "grDrawTriangle", [(Pointer(Const(GrVertex)), "a"), (Pointer(Const(GrVertex)), "b"), (Pointer(Const(GrVertex)), "c")]),
    StdDecoratedFunction("_grErrorSetCallback@4", Void, "grErrorSetCallback", [(GrErrorCallbackFnc_t, "fnc")], sideeffects=False),
    StdDecoratedFunction("_grFogColorValue@4", Void, "grFogColorValue", [(GrColor_t, "fogcolor")]),
    StdDecoratedFunction("_grFogMode@4", Void, "grFogMode", [(GrFogMode_t, "mode")]),
    StdDecoratedFunction("_grFogTable@4", Void, "grFogTable", [(Blob(Const(GrFog_t), "GR_FOG_TABLE_SIZE"), "ft")]),
    StdDecoratedFunction("_grGammaCorrectionValue@4", Void, "grGammaCorrectionValue", [(Float, "value")]),
    StdDecoratedFunction("_grGlideGetState@4", Void, "grGlideGetState", [Out(Pointer(GrState), "state")], sideeffects=False),
    StdDecoratedFunction("_grGlideGetVersion@4", Void, "grGlideGetVersion", [Out(Pointer(Char), "version")], sideeffects=False),
    StdDecoratedFunction("_grGlideInit@0", Void, "grGlideInit", []),
    StdDecoratedFunction("_grGlideSetState@4", Void, "grGlideSetState", [(Pointer(Const(GrState)), "state")]),
    StdDecoratedFunction("_grGlideShamelessPlug@4", Void, "grGlideShamelessPlug", [(Const(FxBool), "on")]),
    StdDecoratedFunction("_grGlideShutdown@0", Void, "grGlideShutdown", []),
    StdDecoratedFunction("_grHints@8", Void, "grHints", [(GrHint_t, "hintType"), (GrSTWHint_t, "hintMask")]),
    StdDecoratedFunction("_grLfbBegin@0", Void, "grLfbBegin", []),
    StdDecoratedFunction("_grLfbBypassMode@4", Void, "grLfbBypassMode", [(GrLfbBypassMode_t, "mode")]),
    StdDecoratedFunction("_grLfbConstantAlpha@4", Void, "grLfbConstantAlpha", [(GrAlpha_t, "alpha")]),
    StdDecoratedFunction("_grLfbConstantDepth@4", Void, "grLfbConstantDepth", [(FxU16, "depth")]),
    StdDecoratedFunction("_grLfbEnd@0", Void, "grLfbEnd", []),
    StdDecoratedFunction("_grLfbGetReadPtr@4", ConstPointer(FxU32), "grLfbGetReadPtr", [(GrBuffer_t, "buffer")], sideeffects=False),
#    StdDecoratedFunction("_grLfbGetWritePtr@4", LinearPointer(Void, "g_lock.size"), "grLfbGetWritePtr", [(GrBuffer_t, "buffer")]),
    StdDecoratedFunction("_grLfbGetWritePtr@4", OpaquePointer(Void), "grLfbGetWritePtr", [(GrBuffer_t, "buffer")]),
    StdDecoratedFunction("_grLfbOrigin@4", Void, "grLfbOrigin", [(GrOriginLocation_t, "origin")]),
    StdDecoratedFunction("_grLfbReadRegion@28", FxBool, "grLfbReadRegion", [(GrBuffer_t, "src_buffer"), (FxU32, "src_x"), (FxU32, "src_y"), (FxU32, "src_width"), (FxU32, "src_height"), (FxU32, "dst_stride"), Out(Blob(Void, "dst_stride * src_height"), "dst_data")], sideeffects=False),
    StdDecoratedFunction("_grLfbWriteColorFormat@4", Void, "grLfbWriteColorFormat", [(GrColorFormat_t, "colorFormat")]),
    StdDecoratedFunction("_grLfbWriteColorSwizzle@8", Void, "grLfbWriteColorSwizzle", [(FxBool, "swizzleBytes"), (FxBool, "swapWords")]),
    StdDecoratedFunction("_grLfbWriteMode@4", Void, "grLfbWriteMode", [(GrLfbWriteMode_t, "mode")]),
    StdDecoratedFunction("_grRenderBuffer@4", Void, "grRenderBuffer", [(GrBuffer_t, "buffer")]),
    StdDecoratedFunction("_grResetTriStats@0", Void, "grResetTriStats", []),
    StdDecoratedFunction("_grSplash@20", Void, "grSplash", []),
    StdDecoratedFunction("_grSstConfigPipeline@12", Void, "grSstConfigPipeline", [(GrChipID_t, "chip"), (GrSstRegister, "reg"), (FxU32, "value")]),
    StdDecoratedFunction("_grSstDetectResources@0", Void, "grSstDetectResources", []),
    StdDecoratedFunction("_grSstIdle@0", Void, "grSstIdle", []),
    StdDecoratedFunction("_grSstIsBusy@0", FxBool, "grSstIsBusy", []),
    StdDecoratedFunction("_grSstOpen@24", FxBool, "grSstOpen", [(GrScreenResolution_t, "screen_resolution"), (GrScreenRefresh_t, "refresh_rate"), (GrColorFormat_t, "color_format"), (GrOriginLocation_t, "origin_location"), (GrSmoothingMode_t, "smoothing_filter"), (Int, "num_buffers")]),
    StdDecoratedFunction("_grSstOrigin@4", Void, "grSstOrigin", [(GrOriginLocation_t, "origin")]),
    StdDecoratedFunction("_grSstPassthruMode@4", Void, "grSstPassthruMode", [(GrPassthruMode_t, "mode")]),
    StdDecoratedFunction("_grSstPerfStats@4", Void, "grSstPerfStats", [Out(Pointer(GrSstPerfStats_t), "pStats")]),
    StdDecoratedFunction("_grSstQueryBoards@4", FxBool, "grSstQueryBoards", [Out(Pointer(GrHwConfiguration), "hwconfig")]),
    StdDecoratedFunction("_grSstQueryHardware@4", FxBool, "grSstQueryHardware", [Out(Pointer(GrHwConfiguration), "hwconfig")]),
    StdDecoratedFunction("_grSstResetPerfStats@0", Void, "grSstResetPerfStats", []),
    StdDecoratedFunction("_grSstScreenHeight@0", Int, "grSstScreenHeight", []),
    StdDecoratedFunction("_grSstScreenWidth@0", Int, "grSstScreenWidth", []),
    StdDecoratedFunction("_grSstSelect@4", Void, "grSstSelect", [(Int, "which_sst")]),
    StdDecoratedFunction("_grSstStatus@0", FxU32, "grSstStatus", [], sideeffects=False),
    StdDecoratedFunction("_grSstVRetraceOn@0", FxBool, "grSstVRetraceOn", []),
    StdDecoratedFunction("_grSstVidMode@8", Void, "grSstVidMode", [(FxU32, "whichSst"), (Pointer(FxVideoTimingInfo), "vidTimings")]),
    StdDecoratedFunction("_grSstVideoLine@0", FxU32, "grSstVideoLine", []),
    StdDecoratedFunction("_grSstWinClose@0", Void, "grSstWinClose", []),
    StdDecoratedFunction("_grSstWinOpen@28", FxBool, "grSstWinOpen", [(FxU32, "hWnd"), (GrScreenResolution_t, "screen_resolution"), (GrScreenRefresh_t, "refresh_rate"), (GrColorFormat_t, "color_format"), (GrOriginLocation_t, "origin_location"), (Int, "nColBuffers"), (Int, "nAuxBuffers")]),
    StdDecoratedFunction("_grTexCalcMemRequired@16", FxU32, "grTexCalcMemRequired", [(GrLOD_t, "lodmin"), (GrLOD_t, "lodmax"), (GrAspectRatio_t, "aspect"), (GrTextureFormat_t, "fmt")], sideeffects=False),
    StdDecoratedFunction("_grTexClampMode@12", Void, "grTexClampMode", [(GrChipID_t, "tmu"), (GrTextureClampMode_t, "s_clampmode"), (GrTextureClampMode_t, "t_clampmode")]),
    StdDecoratedFunction("_grTexCombine@28", Void, "grTexCombine", [(GrChipID_t, "tmu"), (GrCombineFunction_t, "rgb_function"), (GrCombineFactor_t, "rgb_factor"), (GrCombineFunction_t, "alpha_function"), (GrCombineFactor_t, "alpha_factor"), (FxBool, "rgb_invert"), (FxBool, "alpha_invert")]),
    StdDecoratedFunction("_grTexCombineFunction@8", Void, "grTexCombineFunction", [(GrChipID_t, "tmu"), (GrTextureCombineFnc_t, "fnc")]),
    StdDecoratedFunction("_grTexDetailControl@16", Void, "grTexDetailControl", [(GrChipID_t, "tmu"), (Int, "lod_bias"), (FxU8, "detail_scale"), (Float, "detail_max")]),
    StdDecoratedFunction("_grTexDownloadMipMap@16", Void, "grTexDownloadMipMap", [(GrChipID_t, "tmu"), (FxU32, "startAddress"), (MipMapLevelMask_t, "evenOdd"), (Pointer(GrTexInfo), "info")]),
    StdDecoratedFunction("_grTexDownloadMipMapLevel@32", Void, "grTexDownloadMipMapLevel", [(GrChipID_t, "tmu"), (FxU32, "startAddress"), (GrLOD_t, "thisLod"), (GrLOD_t, "largeLod"), (GrAspectRatio_t, "aspectRatio"), (GrTextureFormat_t, "format"), (MipMapLevelMask_t, "evenOdd"), (Blob(Void, "_getTexSizeAPI(thisLod, largeLod, aspectRatio, format, evenOdd)"), "data")]),
    StdDecoratedFunction("_grTexDownloadMipMapLevelPartial@40", Void, "grTexDownloadMipMapLevelPartial", [(GrChipID_t, "tmu"), (FxU32, "startAddress"), (GrLOD_t, "thisLod"), (GrLOD_t, "largeLod"), (GrAspectRatio_t, "aspectRatio"), (GrTextureFormat_t, "format"), (MipMapLevelMask_t, "evenOdd"), (Blob(Void, "_getTexSizeAPI(thisLod, largeLod, aspectRatio, format, evenOdd)"), "data"), (Int, "start"), (Int, "end")]),
    StdDecoratedFunction("_grTexDownloadTable@12", Void, "grTexDownloadTable", [(GrChipID_t, "tmu"), (GrTexTable_t, "type"), (Blob(Void, "_getTexTableSize(type)"), "data")]),
    StdDecoratedFunction("_grTexDownloadTablePartial@20", Void, "grTexDownloadTablePartial", [(GrChipID_t, "tmu"), (GrTexTable_t, "type"), (Blob(Void, "_getTexTableSize(type)"), "data"), (Int, "start"), (Int, "end")]),
    StdDecoratedFunction("_grTexFilterMode@12", Void, "grTexFilterMode", [(GrChipID_t, "tmu"), (GrTextureFilterMode_t, "minfilter_mode"), (GrTextureFilterMode_t, "magfilter_mode")]),
    StdDecoratedFunction("_grTexLodBiasValue@8", Void, "grTexLodBiasValue", [(GrChipID_t, "tmu"), (Float, "bias")]),
    StdDecoratedFunction("_grTexMaxAddress@4", FxU32, "grTexMaxAddress", [(GrChipID_t, "tmu")], sideeffects=False),
    StdDecoratedFunction("_grTexMinAddress@4", FxU32, "grTexMinAddress", [(GrChipID_t, "tmu")], sideeffects=False),
    StdDecoratedFunction("_grTexMipMapMode@12", Void, "grTexMipMapMode", [(GrChipID_t, "tmu"), (GrMipMapMode_t, "mode"), (FxBool, "lodBlend")]),
    StdDecoratedFunction("_grTexMultibase@8", Void, "grTexMultibase", [(GrChipID_t, "tmu"), (FxBool, "enable")]),
    StdDecoratedFunction("_grTexMultibaseAddress@20", Void, "grTexMultibaseAddress", [(GrChipID_t, "tmu"), (GrTexBaseRange_t, "range"), (FxU32, "startAddress"), (MipMapLevelMask_t, "evenOdd"), Out(Pointer(GrTexInfo), "info")]),
    StdDecoratedFunction("_grTexNCCTable@8", Void, "grTexNCCTable", [(GrChipID_t, "tmu"), (GrNCCTable_t, "table")]),
    StdDecoratedFunction("_grTexSource@16", Void, "grTexSource", [(GrChipID_t, "tmu"), (FxU32, "startAddress"), (MipMapLevelMask_t, "evenOdd"), (Pointer(GrTexInfo), "info")]),
    StdDecoratedFunction("_grTexTextureMemRequired@8", FxU32, "grTexTextureMemRequired", [(MipMapLevelMask_t, "evenOdd"), (Pointer(GrTexInfo), "info")], sideeffects=False),
    StdDecoratedFunction("_grTriStats@8", Void, "grTriStats", [Out(Pointer(FxU32), "trisProcessed"), Out(Pointer(FxU32), "trisDrawn")]),
    # Some gu* functions are in glideutl.h and some are in glide.h
    StdDecoratedFunction("_gu3dfGetInfo@8", FxBool, "gu3dfGetInfo", [(Pointer(Const(Char)), "filename"), Out(Pointer(Gu3dfInfo), "info")], sideeffects=False),
    StdDecoratedFunction("_gu3dfLoad@8", FxBool, "gu3dfLoad", [(Pointer(Const(Char)), "filename"), Out(Pointer(Gu3dfInfo), "data")]),
    StdDecoratedFunction("_guAADrawTriangleWithClip@12", Void, "guAADrawTriangleWithClip", [(Pointer(Const(GrVertex)), "a"), (Pointer(Const(GrVertex)), "b"), (Pointer(Const(GrVertex)), "c")]),
    StdDecoratedFunction("_guAlphaSource@4", Void, "guAlphaSource", [(GrAlphaSource_t, "mode")]),
    StdDecoratedFunction("_guColorCombineFunction@4", Void, "guColorCombineFunction", [(GrColorCombineFnc_t, "fnc")]),
    StdDecoratedFunction("_guDrawPolygonVertexListWithClip@8", Void, "guDrawPolygonVertexListWithClip", [(Int, "nverts"), (Blob(Const(GrVertex), "nverts * sizeof(GrVertex)"), "vlist")]),
    StdDecoratedFunction("_guDrawTriangleWithClip@12", Void, "guDrawTriangleWithClip", [(Pointer(Const(GrVertex)), "a"), (Pointer(Const(GrVertex)), "b"), (Pointer(Const(GrVertex)), "c")]),
    StdDecoratedFunction("_guEncodeRLE16@16", Int, "guEncodeRLE16", [Out(OpaquePointer(Void), "dst"), Out(OpaquePointer(Void), "src"), (FxU32, "width"), (FxU32, "height")]),
    StdDecoratedFunction("_guEndianSwapBytes@4", FxU16, "guEndianSwapBytes", [(FxU16, "value")]),
    StdDecoratedFunction("_guEndianSwapWords@4", FxU32, "guEndianSwapWords", [(FxU32, "value")]),
    StdDecoratedFunction("_guFbReadRegion@24", Void, "guFbReadRegion", [(Const(Int), "srcX"), (Const(Int), "srcY"), (Const(Int), "w"), (Const(Int), "h"), Out(Blob(Const(Void), "strideInBytes"), "dst"), (Const(Int), "strideInBytes")], sideeffects=False),
    StdDecoratedFunction("_guFbWriteRegion@24", Void, "guFbWriteRegion", [(Const(Int), "dstX"), (Const(Int), "dstY"), (Const(Int), "w"), (Const(Int), "h"), (Blob(Const(Void), "strideInBytes"), "src"), (Const(Int), "strideInBytes")]),
    StdDecoratedFunction("_guFogGenerateExp2@8", Void, "guFogGenerateExp2", [Out(Pointer(GrFog_t), "fogtable"), (Float, "density")], sideeffects=False),
    StdDecoratedFunction("_guFogGenerateExp@8", Void, "guFogGenerateExp", [Out(Pointer(GrFog_t), "fogtable"), (Float, "density")], sideeffects=False),
    StdDecoratedFunction("_guFogGenerateLinear@12", Void, "guFogGenerateLinear", [Out(Pointer(GrFog_t), "fogtable"), (Float, "nearZ"), (Float, "farZ")], sideeffects=False),
    StdDecoratedFunction("_guFogTableIndexToW@4", Float, "guFogTableIndexToW", [(Int, "i")]),
    # guMP* are in gump.h
    StdDecoratedFunction("_guMPDrawTriangle@12", Void, "guMPDrawTriangle", [(Pointer(Const(GrVertex)), "a"), (Pointer(Const(GrVertex)), "b"), (Pointer(Const(GrVertex)), "c")]),
    StdDecoratedFunction("_guMPInit@0", Void, "guMPInit", []),
    StdDecoratedFunction("_guMPTexCombineFunction@4", Void, "guMPTexCombineFunction", [(GrMPTextureCombineFnc_t, "tc")]),
    StdDecoratedFunction("_guMPTexSource@8", Void, "guMPTexSource", [(GrChipID_t, "virtual_tmu"), (GrMipMapId_t, "mmid")]),
    StdDecoratedFunction("_guMovieSetName@4", Void, "guMovieSetName", [(Pointer(Const(Char)), "name")]),
    StdDecoratedFunction("_guMovieStart@0", Void, "guMovieStart", []),
    StdDecoratedFunction("_guMovieStop@0", Void, "guMovieStop", []),
    StdDecoratedFunction("_guTexAllocateMemory@60", GrMipMapId_t, "guTexAllocateMemory", [(GrChipID_t, "tmu"), (FxU8, "odd_even_mask"), (Int, "width"), (Int, "height"), (GrTextureFormat_t, "fmt"), (GrMipMapMode_t, "mm_mode"), (GrLOD_t, "smallest_lod"), (GrLOD_t, "largest_lod"), (GrAspectRatio_t, "aspect"), (GrTextureClampMode_t, "s_clamp_mode"), (GrTextureClampMode_t, "t_clamp_mode"), (GrTextureFilterMode_t, "minfilter_mode"), (GrTextureFilterMode_t, "magfilter_mode"), (Float, "lod_bias"), (FxBool, "trilinear")]),
    StdDecoratedFunction("_guTexChangeAttributes@48", FxBool, "guTexChangeAttributes", [(GrMipMapId_t, "mmid"), (Int, "width"), (Int, "height"), (GrTextureFormat_t, "fmt"), (GrMipMapMode_t, "mm_mode"), (GrLOD_t, "smallest_lod"), (GrLOD_t, "largest_lod"), (GrAspectRatio_t, "aspect"), (GrTextureClampMode_t, "s_clamp_mode"), (GrTextureClampMode_t, "t_clamp_mode"), (GrTextureFilterMode_t, "minFilterMode"), (GrTextureFilterMode_t, "magFilterMode")]),
    StdDecoratedFunction("_guTexCombineFunction@8", Void, "guTexCombineFunction", [(GrChipID_t, "tmu"), (GrTextureCombineFnc_t, "fnc")]),
    StdDecoratedFunction("_guTexCreateColorMipMap", Pointer(FxU16), "guTexCreateColorMipMap", []),
    StdDecoratedFunction("_guTexDownloadMipMap@12", Void, "guTexDownloadMipMap", [(GrMipMapId_t, "mmid"), (Blob(Const(Void), "_getTexSizeGU(mmid)"), "src"), (Pointer(Const(GuNccTable)), "table")]),
    StdDecoratedFunction("_guTexDownloadMipMapLevel@12", Void, "guTexDownloadMipMapLevel", [(GrMipMapId_t, "mmid"), (GrLOD_t, "lod"), (Pointer(LinearPointer(Void, "_MappedSize")), "src")]),
    StdDecoratedFunction("_guTexGetCurrentMipMap@4", GrMipMapId_t, "guTexGetCurrentMipMap", [(GrChipID_t, "tmu")], sideeffects=False),
    StdDecoratedFunction("_guTexGetMipMapInfo@4", Pointer(GrMipMapInfo), "guTexGetMipMapInfo", [(GrMipMapId_t, "mmid")], sideeffects=False),
    StdDecoratedFunction("_guTexMemQueryAvail@4", FxU32, "guTexMemQueryAvail", [(GrChipID_t, "tmu")], sideeffects=False),
    StdDecoratedFunction("_guTexMemReset@0", Void, "guTexMemReset", []),
    StdDecoratedFunction("_guTexSource@4", Void, "guTexSource", [(GrMipMapId_t, "id")]),
])

