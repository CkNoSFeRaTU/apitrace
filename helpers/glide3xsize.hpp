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

#define TRANSLATE_ASPECT(_aspect) (_aspect)
#define TRANSLATE_LOD(_lod) (_lod)
#include "glidecommonsize.hpp"
#undef ASPECT_TRANSLATE

#include <unordered_map>

typedef FxU32 (__stdcall * PFN_GRGET)(FxU32 pname, FxU32 plength, FxI32 * params);
extern PFN_GRGET _grGet;
typedef FxU32 (__stdcall * PFN_GRTEXTEXTUREMEMREQUIRED)(FxU32 evenOdd, GrTexInfo* info);
extern PFN_GRTEXTEXTUREMEMREQUIRED _grTexTextureMemRequired;

static std::unordered_map<FxU32, FxU32> _vLayout = {};

static inline size_t
_getFogTableSize() {
    FxI32 size = 0;
    if (_grGet(GR_FOG_TABLE_ENTRIES, sizeof(size), &size) == sizeof(size))
      return size;

    return 0;
}

static inline size_t
_getStateSize() {
    FxI32 size = 0;
    if (_grGet(GR_GLIDE_STATE_SIZE, sizeof(size), &size) == sizeof(size))
      return size;

    return 0;
}

static inline size_t
_getTexSizeAPI(GrLOD_t smallLodLog2, GrLOD_t largeLodLog2, GrAspectRatio_t aspectRatioLog2, GrTextureFormat_t format, FxU32 evenOdd = GR_MIPMAPLEVELMASK_BOTH) {
    GrTexInfo texInfo;
    texInfo.smallLodLog2 = smallLodLog2;
    texInfo.largeLodLog2 = largeLodLog2;
    texInfo.aspectRatioLog2 = aspectRatioLog2;
    texInfo.format = format;
    texInfo.data = nullptr;

    return _grTexTextureMemRequired(evenOdd, &texInfo);;
}

static inline size_t
_getVertexLayoutSize() {
    FxI32 size = 0;
    if (_grGet(GR_GLIDE_VERTEXLAYOUT_SIZE, sizeof(size), &size) == sizeof(size))
      return size;

    return 0;
}

static inline size_t
_getVertexSize() {
    FxU32 maxOffset = 0, maxParam = GR_PARAM_XY;
    for (auto& [param, offset] : _vLayout) {
        if (maxOffset < offset) {
            maxOffset = offset;
            maxParam = param;
        }
    }

    FxU32 size = 0;
    switch (maxParam) {
        case GR_PARAM_Z:
        case GR_PARAM_W:
        case GR_PARAM_A:
        case GR_PARAM_PARGB:
        case GR_PARAM_Q:
        case GR_PARAM_Q0:
        case GR_PARAM_Q1:
        case GR_PARAM_Q2:
            size = 4;
            break;
        case GR_PARAM_XY:
            size = 8;
            break;
        case GR_PARAM_RGB:
        case GR_PARAM_ST0:
        case GR_PARAM_ST1:
        case GR_PARAM_ST2:
            size = 12;
            break;
        default:
            assert(0);
    }

    return maxOffset + size;
}

static inline void
_setVertexSize(FxU32 param, FxU32 offset, FxU32 mode) {
    if (mode == GR_PARAM_ENABLE) {
        _vLayout[param] = offset;
    } else {
        _vLayout[param] = 0;
    }
}
