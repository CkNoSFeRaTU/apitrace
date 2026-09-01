/**************************************************************************
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sub license,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.  IN NO EVENT SHALL
 * AUTHORS,
 * AND/OR THEIR SUPPLIERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
 * OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 **************************************************************************/


/*
 * Auxiliary functions to compute the size of array/blob arguments.
 */

#pragma once

#include <string>
#include <fstream>
#include <vector>

enum GrIntFmt_t : FxU32 {
    GR_FMT_UNKNOWN = 0,
    GR_FMT_RGB_332,
    GR_FMT_RGB_555,
    GR_FMT_RGB_565,
    GR_FMT_RGB_888,
    GR_FMT_ARGB_1555,
    GR_FMT_ARGB_4444,
    GR_FMT_ARGB_8888,
    GR_FMT_ARGB_8332,
    GR_FMT_YIQ_422,
    GR_FMT_AYIQ_8422,
    GR_FMT_A_8,
    GR_FMT_I_8,
    GR_FMT_P_8,
    GR_FMT_P_8_6666,
    GR_FMT_AI_44,
    GR_FMT_AI_88,
    GR_FMT_AP_88,
    GR_FMT_ZA_16,
    GR_FMT_RLE16,
    GR_FMT_ARGB_CMP_FXT1,
    GR_FMT_YUYV_422,
    GR_FMT_UYVY_422,
    GR_FMT_AYUV_444,
    GR_FMT_ARGB_CMP_DXT1,
    GR_FMT_ARGB_CMP_DXT2,
    GR_FMT_ARGB_CMP_DXT3,
    GR_FMT_ARGB_CMP_DXT4,
    GR_FMT_ARGB_CMP_DXT5,

    // for LFB operations on depth
    GR_FMT_RGB_555_DEPTH,
    GR_FMT_RGB_565_DEPTH,
    GR_FMT_ARGB_1555_DEPTH,
};

struct GlideMipMapOffset {
    GrLOD_t smallLodLog2;
    GrLOD_t largeLodLog2;
    FxU32 offset;
    FxU32 size;
    FxU32 width;
    FxU32 height;
};

static std::string
IFormatToString(GrIntFmt_t format) {
    switch (format) {
        case GR_FMT_RGB_332:
            return "GR_FMT_RGB_332";
        case GR_FMT_RGB_555:
        case GR_FMT_RGB_555_DEPTH:
            return "GR_FMT_RGB_555";
        case GR_FMT_RGB_565:
        case GR_FMT_RGB_565_DEPTH:
            return "GR_FMT_RGB_565";
        case GR_FMT_RGB_888:
            return "GR_FMT_RGB_888";
        case GR_FMT_ARGB_1555:
        case GR_FMT_ARGB_1555_DEPTH:
            return "GR_FMT_ARGB_1555";
        case GR_FMT_ARGB_4444:
            return "GR_FMT_ARGB_4444";
        case GR_FMT_ARGB_8888:
            return "GR_FMT_ARGB_8888";
        case GR_FMT_ARGB_8332:
            return "GR_FMT_ARGB_8332";
        case GR_FMT_YIQ_422:
            return "GR_FMT_YIQ_442";
        case GR_FMT_AYIQ_8422:
            return "GR_FMT_AYIQ_8442";
        case GR_FMT_A_8:
            return "GR_FMT_A_8";
        case GR_FMT_I_8:
            return "GR_FMT_I_8";
        case GR_FMT_P_8:
            return "GR_FMT_P_8";
        case GR_FMT_AI_44:
            return "GR_FMT_AI_44";
        case GR_FMT_AP_88:
            return "GR_FMT_AP_88";
        case GR_FMT_ZA_16:
            return "GR_FMT_ZA_16";
        case GR_FMT_RLE16:
            return "GR_FMT_RLE16";
#ifdef GLIDE3X
        case GR_FMT_ARGB_CMP_FXT1:
            return "GR_FMT_ARGB_CMP_FXT1";
        case GR_FMT_YUYV_422:
            return "GR_FMT_YUYV_422";
        case GR_FMT_UYVY_422:
            return "GR_FMT_UYVY_422";
        case GR_FMT_AYUV_444:
            return "GR_FMT_AYUV_444";
        case GR_FMT_ARGB_CMP_DXT1:
            return "GR_FMT_ARGB_CMP_DXT1";
        case GR_FMT_ARGB_CMP_DXT2:
            return "GR_FMT_ARGB_CMP_DXT2";
        case GR_FMT_ARGB_CMP_DXT3:
            return "GR_FMT_ARGB_CMP_DXT3";
        case GR_FMT_ARGB_CMP_DXT4:
            return "GR_FMT_ARGB_CMP_DXT4";
        case GR_FMT_ARGB_CMP_DXT5:
            return "GR_FMT_ARGB_CMP_DXT5";
#endif
        default:
            return "Unknown";
    }
}

static GrIntFmt_t
TexFormatToIFormat(GrTextureFormat_t format) {
    switch (format) {
        case(GR_TEXFMT_RGB_332):
            return GR_FMT_RGB_332;
        case(GR_TEXFMT_YIQ_422):
            return GR_FMT_YIQ_422;
        case(GR_TEXFMT_ALPHA_8):
            return GR_FMT_A_8;
        case(GR_TEXFMT_INTENSITY_8):
            return GR_FMT_I_8;
        case(GR_TEXFMT_ALPHA_INTENSITY_44):
            return GR_FMT_AI_44;
        case(GR_TEXFMT_P_8):
            return GR_FMT_P_8;
        case(GR_TEXFMT_ARGB_8332):
            return GR_FMT_ARGB_8332;
        case(GR_TEXFMT_AYIQ_8422):
            return GR_FMT_AYIQ_8422;
        case(GR_TEXFMT_RGB_565):
            return GR_FMT_RGB_565;
        case(GR_TEXFMT_ARGB_1555):
            return GR_FMT_ARGB_1555;
        case(GR_TEXFMT_ARGB_4444):
            return GR_FMT_ARGB_4444;
        case(GR_TEXFMT_ALPHA_INTENSITY_88):
            return GR_FMT_AI_88;
        case(GR_TEXFMT_AP_88):
            return GR_FMT_AP_88;
#ifdef GLIDE3X
        case(GR_TEXFMT_ARGB_CMP_FXT1):
            return GR_FMT_ARGB_CMP_FXT1;
        case(GR_TEXFMT_ARGB_8888):
            return GR_FMT_ARGB_8888;
        case(GR_TEXFMT_YUYV_422):
            return GR_FMT_YUYV_422;
        case(GR_TEXFMT_UYVY_422):
            return GR_FMT_UYVY_422;
        case(GR_TEXFMT_AYUV_444):
            return GR_FMT_AYUV_444;
        case(GR_TEXFMT_ARGB_CMP_DXT1):
            return GR_FMT_ARGB_CMP_DXT1;
        case(GR_TEXFMT_ARGB_CMP_DXT2):
            return GR_FMT_ARGB_CMP_DXT2;
        case(GR_TEXFMT_ARGB_CMP_DXT3):
            return GR_FMT_ARGB_CMP_DXT3;
        case(GR_TEXFMT_ARGB_CMP_DXT4):
            return GR_FMT_ARGB_CMP_DXT4;
        case(GR_TEXFMT_ARGB_CMP_DXT5):
            return GR_FMT_ARGB_CMP_DXT5;
        case(GR_TEXFMT_RGB_888):
            return GR_FMT_RGB_888;
#endif
        default:
            break;
    }

    return GR_FMT_UNKNOWN;
}

static GrTextureFormat_t
IFormatToTexFormat(GrIntFmt_t format) {
    switch (format) {
        case(GR_FMT_RGB_332):
            return GR_TEXFMT_RGB_332;
        case(GR_FMT_YIQ_422):
            return GR_TEXFMT_YIQ_422;
        case(GR_FMT_A_8):
            return GR_TEXFMT_ALPHA_8;
        case(GR_FMT_I_8):
            return GR_TEXFMT_INTENSITY_8;
        case(GR_FMT_AI_44):
            return GR_TEXFMT_ALPHA_INTENSITY_44;
        case(GR_FMT_P_8):
            return GR_TEXFMT_P_8;
        case(GR_FMT_ARGB_8332):
            return GR_TEXFMT_ARGB_8332;
        case(GR_FMT_AYIQ_8422):
            return GR_TEXFMT_AYIQ_8422;
        case(GR_FMT_RGB_565):
            return GR_TEXFMT_RGB_565;
        case(GR_FMT_ARGB_1555):
            return GR_TEXFMT_ARGB_1555;
        case(GR_FMT_ARGB_4444):
            return GR_TEXFMT_ARGB_4444;
        case(GR_FMT_AI_88):
            return GR_TEXFMT_ALPHA_INTENSITY_88;
        case(GR_FMT_AP_88):
            return GR_TEXFMT_AP_88;
#ifdef GLIDE3X
        case(GR_FMT_ARGB_CMP_FXT1):
            return GR_TEXFMT_ARGB_CMP_FXT1;
        case(GR_FMT_ARGB_8888):
            return GR_TEXFMT_ARGB_8888;
        case(GR_FMT_YUYV_422):
            return GR_TEXFMT_YUYV_422;
        case(GR_FMT_UYVY_422):
            return GR_TEXFMT_UYVY_422;
        case(GR_FMT_AYUV_444):
            return GR_TEXFMT_AYUV_444;
        case(GR_FMT_ARGB_CMP_DXT1):
            return GR_TEXFMT_ARGB_CMP_DXT1;
        case(GR_FMT_ARGB_CMP_DXT2):
            return GR_TEXFMT_ARGB_CMP_DXT2;
        case(GR_FMT_ARGB_CMP_DXT3):
            return GR_TEXFMT_ARGB_CMP_DXT3;
        case(GR_FMT_ARGB_CMP_DXT4):
            return GR_TEXFMT_ARGB_CMP_DXT4;
        case(GR_FMT_ARGB_CMP_DXT5):
            return GR_TEXFMT_ARGB_CMP_DXT5;
        case(GR_FMT_RGB_888):
            return GR_TEXFMT_RGB_888;
#endif
        default:
            break;
    }

    return GR_TEXFMT_RGB_332;
}

static GrIntFmt_t
LfbWriteModeToIFormat(GrLfbWriteMode_t writeMode) {
    switch (writeMode) {
        case GR_LFBWRITEMODE_555:
            return GR_FMT_RGB_555;
        case GR_LFBWRITEMODE_565:
            return GR_FMT_RGB_565;
        case GR_LFBWRITEMODE_1555:
            return GR_FMT_ARGB_1555;
        case GR_LFBWRITEMODE_888:
            return GR_FMT_RGB_888;
        case GR_LFBWRITEMODE_8888:
            return GR_FMT_ARGB_8888;
        case GR_LFBWRITEMODE_555_DEPTH:
            return GR_FMT_RGB_555_DEPTH;
        case GR_LFBWRITEMODE_565_DEPTH:
            return GR_FMT_RGB_565_DEPTH;
        case GR_LFBWRITEMODE_1555_DEPTH:
            return GR_FMT_ARGB_1555_DEPTH;
#ifdef GLIDE1X
        case GR_LFBWRITEMODE_DEPTH_DEPTH:
#else
        case GR_LFBWRITEMODE_ZA16:
#endif
            return GR_FMT_ZA_16;
        default:
            break;
    }

    return GR_FMT_UNKNOWN;
}

static inline size_t
_getTexTableSize(GrTexTable_t type) {
    switch (type) {
        case GR_TEXTABLE_NCC0:
        case GR_TEXTABLE_NCC1:
            return sizeof(GuNccTable);
        case GR_TEXTABLE_PALETTE:
            return sizeof(GuTexPalette);
    }

    return 0;
}

static inline void
_getTexDimensions(GrLOD_t smallLodLog2, GrLOD_t largeLodLog2
    , GrAspectRatio_t aspectRatioLog2, FxU32& width, FxU32& height) {
    if (aspectRatioLog2 >= 0) {
        width = 1U << largeLodLog2;
        height = width >> aspectRatioLog2;
    } else {
        height = 1U << largeLodLog2;
        width = height >> -aspectRatioLog2;
    }
}

static inline void
_getTexFormatSize(GrIntFmt_t format, FxU32* BlockSize, FxU32* BlockWidth = nullptr, FxU32* BlockHeight = nullptr) {
    if (BlockSize != nullptr)
        *BlockSize = 0;
    if (BlockWidth != nullptr)
        *BlockWidth = 1;
    if (BlockHeight != nullptr)
        *BlockHeight = 1;

    switch (format) {
    case GR_FMT_A_8:
    case GR_FMT_I_8:
    case GR_FMT_AI_44:
    case GR_FMT_P_8:
    case GR_FMT_RGB_332:
    case GR_FMT_YIQ_422:
#ifdef GLIDE3X
    case(GR_FMT_P_8_6666):
#endif
        if (BlockSize != nullptr)
            *BlockSize = 8;
        break;
//    case GR_FMT_RSVD1:
    case GR_FMT_AYIQ_8422:
    case GR_FMT_ARGB_1555:
    case GR_FMT_ARGB_4444:
    case GR_FMT_ARGB_8332:
    case GR_FMT_AI_88:
    case GR_FMT_AP_88:
    case GR_FMT_RGB_565:
    case GR_FMT_ZA_16:
        if (BlockSize != nullptr)
            *BlockSize = 16;
        break;
#ifdef GLIDE3X
    case GR_FMT_RGB_888:
        if (BlockSize != nullptr)
            *BlockSize = 24;
        break;
    case GR_FMT_RGB_555_DEPTH:
    case GR_FMT_RGB_565_DEPTH:
    case GR_FMT_ARGB_1555_DEPTH:
    case GR_FMT_ARGB_8888:
        if (BlockSize != nullptr)
            *BlockSize = 32;
        break;
    case GR_FMT_YUYV_422:
    case GR_FMT_UYVY_422:
    case GR_FMT_AYUV_444:
        if (BlockWidth != nullptr)
            *BlockWidth = 2;
        if (BlockSize != nullptr)
            *BlockSize = 32;
        break;
    case GR_FMT_ARGB_CMP_FXT1:
    case GR_FMT_ARGB_CMP_DXT1:
        if (BlockWidth != nullptr)
            *BlockWidth = 4;
        if (BlockHeight != nullptr)
            *BlockHeight = 4;
        if (BlockSize != nullptr)
            *BlockSize = 64;
        break;
    case GR_FMT_ARGB_CMP_DXT2:
    case GR_FMT_ARGB_CMP_DXT3:
    case GR_FMT_ARGB_CMP_DXT4:
    case GR_FMT_ARGB_CMP_DXT5:
        if (BlockWidth != nullptr)
            *BlockWidth = 4;
        if (BlockHeight != nullptr)
            *BlockHeight = 4;
        if (BlockSize != nullptr)
            *BlockSize = 128;
        break;
#endif
    }
}

static inline size_t
_getITexSize(GrLOD_t smallLodLog2, GrLOD_t largeLodLog2
    , GrAspectRatio_t aspectRatioLog2, GrIntFmt_t format
    , FxU32 evenOdd = GR_MIPMAPLEVELMASK_BOTH, FxBool round = FXFALSE
    , std::vector<GlideMipMapOffset>* offsets = nullptr) {
    size_t memSize = 0;

    if (smallLodLog2 > largeLodLog2)
        return memSize;

    if (evenOdd > GR_MIPMAPLEVELMASK_BOTH || evenOdd == GR_MIPMAPLEVELMASK_NONE)
        return memSize;

    GrLOD_t thisSmallLodLog2 = smallLodLog2;
    GrLOD_t thisLargeLodLog2 = largeLodLog2;
    while (thisLargeLodLog2 >= smallLodLog2) {
        FxU32 currentParity = (thisLargeLodLog2 % GR_MIPMAPLEVELMASK_ODD == 0) ? GR_MIPMAPLEVELMASK_EVEN : GR_MIPMAPLEVELMASK_ODD;
        FxU32 currentSize = 0;
        if ((evenOdd & currentParity) != 0) {
            FxU32 width, height, blockSize, blockWidth, blockHeight;
            _getTexDimensions(thisSmallLodLog2, thisLargeLodLog2, aspectRatioLog2, width, height);
            _getTexFormatSize(format, &blockSize, &blockWidth, &blockHeight);
            FxU32 currentSize = 0;
            if (blockSize > 0 && height > 0 && width > 0) {
                if (blockWidth > 1 || blockHeight > 1)
                    currentSize = std::min(height * width, ((height + blockHeight - 1) / blockHeight) * ((width + blockWidth - 1) / blockWidth) * (blockSize / (blockWidth + blockHeight)));
                else
                    currentSize = height * width * blockSize;
            }

            if (offsets != nullptr) {
              GlideMipMapOffset offset;
              offset.smallLodLog2 = thisSmallLodLog2;
              offset.largeLodLog2 = thisLargeLodLog2;
              offset.size = currentSize;
              offset.offset = memSize;
              offset.width = width;
              offset.height = height;
              offsets->push_back(std::move(offset));
            }

            memSize += currentSize;
        }
        thisSmallLodLog2--;
        thisLargeLodLog2--;
    }

    // bits to bytes
    memSize >>= 3;

    // round up to SST1 boundary
    if (round) {
        memSize += SST1_TEXTURE_ALIGN_MASK;
        memSize &= ~SST1_TEXTURE_ALIGN_MASK;
    }

    return memSize;
}

static inline size_t
_getTexSize(GrLOD_t smallLod, GrLOD_t largeLod
    , GrAspectRatio_t aspectRatio, GrTextureFormat_t format
    , FxU32 evenOdd = GR_MIPMAPLEVELMASK_BOTH, FxBool round = FXFALSE) {

    GrLOD_t smallLodLog2 = TRANSLATE_LOD(smallLod);
    GrLOD_t largeLodLog2 = TRANSLATE_LOD(largeLod);
    GrAspectRatio_t aspectRatioLog2 = TRANSLATE_ASPECT(aspectRatio);
    GrIntFmt_t iformat = TexFormatToIFormat(format);

    return _getITexSize(smallLodLog2, largeLodLog2, aspectRatioLog2, iformat, evenOdd, round);
}
