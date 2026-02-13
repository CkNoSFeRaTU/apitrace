/**************************************************************************
 *
 * Copyright 2015 VMware, Inc.
 * All Rights Reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 **************************************************************************/


#include <assert.h>
#include <stdint.h>

#include <list>

#include "image.hpp"
#include "state_writer.hpp"
#include "com_ptr.hpp"
#include "d3dcommon.hpp"
#include "d3dimports.hpp"
#include "d3dstate.hpp"

namespace d3dstate {

const char *
formatToString(D3DFORMAT);

image::Image *
ConvertImage(D3DFORMAT SrcFormat,
             void *SrcData,
             INT SrcPitch,
             UINT Width, UINT Height);

D3DFORMAT
convertFormat(const DDPIXELFORMAT & ddpf)
{
    if (ddpf.dwSize != sizeof(ddpf)) {
        std::cerr << "warning: wrong format dwSize: " << ddpf.dwSize << "\n";
        return D3DFMT_UNKNOWN;
    }

    bool hasAlphaPixels = ddpf.dwFlags & DDPF_ALPHAPIXELS;
    if (ddpf.dwFlags & DDPF_RGB) {
        switch (ddpf.dwRGBBitCount) {
        case 8:
            if (ddpf.dwFlags & DDPF_PALETTEINDEXED8) {
                return D3DFMT_P8;
            } else if (ddpf.dwRBitMask == 0xe0 && ddpf.dwGBitMask == 0x1c && ddpf.dwBBitMask == 0x03) {
                return D3DFMT_R3G3B2;
            }
            break;
        case 16:
            if (!hasAlphaPixels && ddpf.dwRBitMask == 0xf800 && ddpf.dwGBitMask == 0x07e0 && ddpf.dwBBitMask == 0x001f) {
                return D3DFMT_R5G6B5;
            } else if (ddpf.dwRBitMask == 0x7c00 && ddpf.dwGBitMask == 0x03e0 && ddpf.dwBBitMask == 0x001f) {
                if (hasAlphaPixels && ddpf.dwRGBAlphaBitMask == 0x8000) {
                    return D3DFMT_A1R5G5B5;
                } else if (!hasAlphaPixels) {
                    return D3DFMT_X1R5G5B5;
                }
            } else if (hasAlphaPixels && ddpf.dwRGBAlphaBitMask == 0xf000 && ddpf.dwGBitMask == 0x00f0 && ddpf.dwBBitMask == 0x000f) {
                return D3DFMT_A4R4G4B4;
            }
            break;
        case 32:
            if (ddpf.dwRBitMask == 0x00ff0000 && ddpf.dwGBitMask == 0x0000ff00 && ddpf.dwBBitMask == 0x000000ff) {
                if (hasAlphaPixels && ddpf.dwRGBAlphaBitMask == 0xff000000) {
                    return D3DFMT_A8R8G8B8;
                } else if (!hasAlphaPixels) {
                    return D3DFMT_X8R8G8B8;
                }
            }
            break;
        }
    }

    if (ddpf.dwFlags & DDPF_LUMINANCE) {
        switch (ddpf.dwLuminanceBitCount) {
        case 8:
            if (hasAlphaPixels && ddpf.dwLuminanceAlphaBitMask == 0xf0 && ddpf.dwLuminanceBitMask == 0x0f) {
                return D3DFMT_A4L4;
            } else if (!hasAlphaPixels && ddpf.dwLuminanceBitMask == 0xff) {
                return D3DFMT_L8;
            }
            break;
        case 16:
            if (hasAlphaPixels && ddpf.dwLuminanceAlphaBitMask == 0xff00 && ddpf.dwBumpLuminanceBitMask == 0x0f) {
                return D3DFMT_A8L8;
            }
            break;
        }
    }

    bool hasBumpLuminance = ddpf.dwFlags & DDPF_BUMPLUMINANCE;
    if (ddpf.dwFlags & DDPF_BUMPDUDV) {
        switch (ddpf.dwBumpBitCount) {
        case 16:
            if (!hasBumpLuminance && ddpf.dwBumpDuBitMask == 0x00ff && ddpf.dwBumpDvBitMask == 0xff00) {
                return D3DFMT_V8U8;
            } else if (hasBumpLuminance && ddpf.dwBumpLuminanceBitMask == 0xfc00 && ddpf.dwBumpDuBitMask == 0x001f && ddpf.dwBumpDvBitMask == 0x03e0) {
                return D3DFMT_L6V5U5;
            }
            break;
        case 32:
            if (hasBumpLuminance && ddpf.dwBumpLuminanceBitMask == 0x00ff0000 && ddpf.dwBumpDuBitMask == 0x000000ff && ddpf.dwBumpDvBitMask == 0x0000ff00) {
                return D3DFMT_X8L8V8U8;
            }
            break;
        case DDPF_FOURCC:
            return static_cast<D3DFORMAT>(ddpf.dwFourCC);
        }
    }

    bool hasStencil = ddpf.dwFlags & DDPF_STENCILBUFFER;
    if (ddpf.dwFlags & DDPF_ZBUFFER) {
        switch (ddpf.dwZBufferBitDepth) {
        case 16:
            if (hasStencil && ddpf.dwStencilBitMask == 0x8000 && ddpf.dwStencilBitDepth == 1 && ddpf.dwZBitMask == 0x7fff) {
                return D3DFMT_D15S1;
            } else if (!hasStencil && ddpf.dwZBitMask == 0xffff) {
                return D3DFMT_D16;
            }
            break;
        case 24:
        case 32:
            if (ddpf.dwZBitMask == 0x00ffffff) {
                if (hasStencil && ddpf.dwStencilBitMask == 0xf0000000) {
                    return D3DFMT_D24X4S4;
                } else if (hasStencil && ddpf.dwStencilBitMask == 0xff000000) {
                    return D3DFMT_D24S8;
                } else if (!hasStencil) {
                    return D3DFMT_D24X8;
                }
            } else if (!hasStencil && ddpf.dwZBitMask == 0xffffffff) {
                return D3DFMT_D32;
            }
            break;
        }
    }


    return D3DFMT_UNKNOWN;
}

template <typename D, typename S>
image::Image *
getSurfaceImage(D *pDevice, S *pSurface)
{
    HRESULT hr;

    using DT = std::conditional_t<std::is_same_v<S, IDirectDrawSurface7>, DDSURFACEDESC2,
        std::conditional_t<std::is_same_v<S, IDirectDrawSurface4>,
            DDSURFACEDESC2, DDSURFACEDESC
        >
    >;

    DT desc;
    ZeroMemory(&desc, sizeof(desc));
    desc.dwSize = sizeof(desc);

    hr = pSurface->Lock(nullptr, &desc, DDLOCK_WAIT | DDLOCK_READONLY | DDLOCK_SURFACEMEMORYPTR | DDLOCK_NOSYSLOCK, NULL);
    if (FAILED(hr)) {
        hr = pSurface->Unlock(nullptr);
        if (SUCCEEDED(hr)) {
            hr = pSurface->Lock(nullptr, &desc, DDLOCK_WAIT | DDLOCK_READONLY | DDLOCK_SURFACEMEMORYPTR | DDLOCK_NOSYSLOCK, NULL);
            if (FAILED(hr)) {
                std::cerr << "warning: IDirectDrawSurface::Lock failed\n";
                return nullptr;
            }
        } else {
            std::cerr << "warning: IDirectDrawSurface::Lock failed\n";
            return nullptr;
        }
    }

    image::Image *image = nullptr;
    D3DFORMAT Format = convertFormat(desc.ddpfPixelFormat);
    {
        INT pitch = 0;
        if (desc.dwFlags & DDSD_PITCH) {
            pitch = desc.lPitch;
        } else {
            switch (Format) {
            case(D3DFMT_DXT1):
                pitch = ((desc.dwWidth + 3) / 4) * (64 / 8);
                break;
            case(D3DFMT_DXT2):
            case(D3DFMT_DXT3):
            case(D3DFMT_DXT4):
            case(D3DFMT_DXT5):
                pitch = ((desc.dwWidth + 3) / 4) * (128 / 8);
                break;
            default:
                std::cerr << "warning: unsupported D3DFMT: " << formatToString(Format) << "\n";
                pSurface->Unlock(NULL);
                return nullptr;
            }
        }

        image = ConvertImage(Format, desc.lpSurface, pitch, desc.dwWidth, desc.dwHeight);
    }

    pSurface->Unlock(nullptr);

    return image;
}

template image::Image *
getSurfaceImage<IDirect3DDevice2, IDirectDrawSurface>(IDirect3DDevice2 *, IDirectDrawSurface *);
template image::Image *
getSurfaceImage<IDirect3DDevice3, IDirectDrawSurface4>(IDirect3DDevice3 *, IDirectDrawSurface4 *);
template image::Image *
getSurfaceImage<IDirect3DDevice7, IDirectDrawSurface7>(IDirect3DDevice7 *, IDirectDrawSurface7 *);

template <typename S, typename D>
HRESULT CALLBACK
EnumAttachedSurfacesCB(S* pSurface, D* pDesc, void* pContext)
{
    char label[128];
    CBContext<D>* context = static_cast<CBContext<D>*>(pContext);

    if (!context)
        return DDENUMRET_CANCEL;

    if (!pSurface || !pDesc || pDesc->dwWidth == 0 || pDesc->dwHeight == 0)
        return DDENUMRET_OK;

    if (pDesc->ddsCaps.dwCaps & DDSCAPS_FRONTBUFFER) {
        _snprintf(label, sizeof label, "FRONTBUFFER_%u", context->counters.frontbuffer++);
    } else if (pDesc->ddsCaps.dwCaps & DDSCAPS_BACKBUFFER) {
        _snprintf(label, sizeof label, "BACKBUFFER_%u", context->counters.backbuffer++);
    } else if (pDesc->ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE) {
        _snprintf(label, sizeof label, "PRIMARYSURFACE_%u", context->counters.primarysurface++);
    } else if (pDesc->ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACELEFT) {
        _snprintf(label, sizeof label, "PRIMARYSURFACELEFT_%u", context->counters.primarysurfaceleft++);
    } else if (pDesc->ddsCaps.dwCaps & DDSCAPS_OFFSCREENPLAIN) {
        _snprintf(label, sizeof label, "OFFSCREENPLAIN_%u", context->counters.offscreenplain++);
    } else if (pDesc->ddsCaps.dwCaps & DDSCAPS_OVERLAY) {
        _snprintf(label, sizeof label, "OVERLAY_%u", context->counters.overlay++);
    } else if (pDesc->ddsCaps.dwCaps & DDSCAPS_ZBUFFER) {
        if (pDesc->ddpfPixelFormat.dwFlags & DDPF_STENCILBUFFER)
            _snprintf(label, sizeof label, "STENCILBUFFER_%u", context->counters.stencilbuffer++);
        else
            _snprintf(label, sizeof label, "ZBUFFER_%u", context->counters.zbuffer++);
    } else if (pDesc->ddsCaps.dwCaps & DDSCAPS_COMPLEX) {
        _snprintf(label, sizeof label, "COMPLEX_%u", context->counters.complex++);
    } else {
        _snprintf(label, sizeof label, "UNKNOWN_%u", context->counters.unknown++);
    }

    image::Image* image = getSurfaceImage(context->pDevice, pSurface);
    if (image) {
        context->writer->beginMember(label);
        StateWriter::ImageDesc imgDesc;
        imgDesc.depth = 1;
        imgDesc.format = image->formatName;
        context->writer->writeImage(image, imgDesc);
        context->writer->endMember();
        delete image;
    }

    return DDENUMRET_OK;
}

template HRESULT CALLBACK
EnumAttachedSurfacesCB<IDirectDrawSurface, DDSURFACEDESC>(IDirectDrawSurface*, DDSURFACEDESC*, void*);
template HRESULT CALLBACK
EnumAttachedSurfacesCB<IDirectDrawSurface4, DDSURFACEDESC2>(IDirectDrawSurface4*, DDSURFACEDESC2*, void*);
template HRESULT CALLBACK
EnumAttachedSurfacesCB<IDirectDrawSurface7, DDSURFACEDESC2>(IDirectDrawSurface7*, DDSURFACEDESC2*, void*);

} /* namespace d3dstate */
