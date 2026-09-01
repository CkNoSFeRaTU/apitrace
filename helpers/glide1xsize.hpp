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

#define TRANSLATE_ASPECT(_aspect) (0x03 - _aspect)
#define TRANSLATE_LOD(_lod) (0x08 - _lod)
#include "glidecommonsize.hpp"
#undef ASPECT_TRANSLATE

#include <string>
#include <iostream>
#include <fstream>

typedef FxU32 (__stdcall * PFN_GRTEXTEXTUREMEMREQUIRED)(FxU32 evenOdd, GrTexInfo* info);
extern PFN_GRTEXTEXTUREMEMREQUIRED _grTexTextureMemRequired;

static inline size_t
_getTexSizeAPI(GrLOD_t smallLod, GrLOD_t largeLod
    , GrAspectRatio_t aspectRatio, GrTextureFormat_t format
    , FxU32 evenOdd = GR_MIPMAPLEVELMASK_BOTH, FxBool round = FXTRUE) {
    GrTexInfo texInfo;
    texInfo.smallLod = smallLod;
    texInfo.largeLod = largeLod;
    texInfo.aspectRatio = aspectRatio;
    texInfo.format = format;
    texInfo.data = nullptr;
    return _grTexTextureMemRequired(evenOdd, &texInfo);
}

static inline size_t
_getTexSizeGU(GrMipMapId_t mmid) {
    GrMipMapInfo* mminfo = guTexGetMipMapInfo(mmid);
    if (mminfo != nullptr)
        return _getTexSize(mminfo->lod_min, mminfo->lod_max, mminfo->aspect_ratio, mminfo->format, mminfo->odd_even_mask);

    return 0;
}
