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

#include "image.hpp"
#include "state_writer.hpp"
#include "com_ptr.hpp"
#include "d3dimports.hpp"
#include "d3dstate.hpp"


typedef enum _D3DFORMAT
{
    D3DFMT_UNKNOWN              =  0,

    D3DFMT_R8G8B8               = 20,
    D3DFMT_A8R8G8B8             = 21,
    D3DFMT_X8R8G8B8             = 22,
    D3DFMT_R5G6B5               = 23,
    D3DFMT_X1R5G5B5             = 24,
    D3DFMT_A1R5G5B5             = 25,
    D3DFMT_A4R4G4B4             = 26,
    D3DFMT_R3G3B2               = 27,
    D3DFMT_A8                   = 28,
    D3DFMT_A8R3G3B2             = 29,
    D3DFMT_X4R4G4B4             = 30,
    D3DFMT_A2B10G10R10          = 31,

    D3DFMT_A8P8                 = 40,
    D3DFMT_P8                   = 41,

    D3DFMT_L8                   = 50,
    D3DFMT_A8L8                 = 51,
    D3DFMT_A4L4                 = 52,

    D3DFMT_V8U8                 = 60,
    D3DFMT_L6V5U5               = 61,
    D3DFMT_X8L8V8U8             = 62,

    D3DFMT_D16_LOCKABLE         = 70,
    D3DFMT_D32                  = 71,
    D3DFMT_D15S1                = 73,
    D3DFMT_D24S8                = 75,
    D3DFMT_D24X8                = 77,
    D3DFMT_D24X4S4              = 79,
    D3DFMT_D16                  = 80,

    D3DFMT_D32F_LOCKABLE        = 82,
    D3DFMT_D24FS8               = 83,

    D3DFMT_FORCE_DWORD          = 0x7fffffff
} D3DFORMAT;

namespace d3dstate {

image::Image *
ConvertImage(D3DFORMAT SrcFormat,
             void *SrcData,
             INT SrcPitch,
             UINT Width, UINT Height);

const char *
formatToString(D3DFORMAT fmt);

static D3DFORMAT
convertFormat(const DDPIXELFORMAT & ddpf)
{
    if (ddpf.dwSize != sizeof(ddpf)) {
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
                if (hasAlphaPixels && ddpf.dwAlphaBitDepth == 0x8000) {
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

static image::Image *
getSurfaceImage(IDirect3DDevice7 *pDevice, IDirectDrawSurface7 *pSurface)
{
    HRESULT hr;

    DDSURFACEDESC2 desc;
    ZeroMemory(&desc, sizeof(DDSURFACEDESC2));
    desc.dwSize = sizeof desc;

    hr = pSurface->Lock(NULL, &desc, DDLOCK_WAIT | DDLOCK_READONLY | DDLOCK_SURFACEMEMORYPTR | DDLOCK_NOSYSLOCK, NULL);
    if (FAILED(hr)) {
        std::cerr << "warning: IDirectDrawSurface7::Lock failed\n";
        return NULL;
    }

    image::Image *image = NULL;
    D3DFORMAT Format = convertFormat(desc.ddpfPixelFormat);
    if (Format == D3DFMT_UNKNOWN) {
        std::cerr << "warning: DDPIXELFORMAT is unsupported, image skipped\n";
    } else {
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
            }
        }

        image = ConvertImage(Format, desc.lpSurface, pitch, desc.dwWidth, desc.dwHeight);
    }

    pSurface->Unlock(NULL);

    return image;
}


image::Image *
getRenderTargetImage(IDirect3DDevice7 *pDevice) {
    HRESULT hr;

    com_ptr<IDirectDrawSurface7> pRenderTarget;
    hr = pDevice->GetRenderTarget(&pRenderTarget);
    if (FAILED(hr)) {
        return NULL;
    }
    assert(pRenderTarget);

    return getSurfaceImage(pDevice, pRenderTarget);
}


void
dumpTextures(StateWriter &writer, IDirect3DDevice7 *pDevice)
{
    HRESULT hr;

    writer.beginMember("textures");
    writer.beginObject();

    for (DWORD Stage = 0; Stage < 8; ++Stage) {
        com_ptr<IDirectDrawSurface7> pTexture = nullptr;
        hr = pDevice->GetTexture(Stage, &pTexture);
        if (FAILED(hr)) {
            continue;
        }

        if (!pTexture) {
            continue;
        }

        DDSURFACEDESC2 desc;
        ZeroMemory(&desc, sizeof(DDSURFACEDESC2));
        desc.dwSize = sizeof(desc);
        hr = pTexture->GetSurfaceDesc(&desc);
        if (FAILED(hr)) {
            continue;
        }

        bool isCube = desc.ddsCaps.dwCaps & DDSCAPS2_CUBEMAP;

        DWORD NumFaces = isCube ? 6 : 1;
        static const DWORD cubeFaceCaps[6] = {
            DDSCAPS2_CUBEMAP_POSITIVEX,
            DDSCAPS2_CUBEMAP_NEGATIVEX,
            DDSCAPS2_CUBEMAP_POSITIVEY,
            DDSCAPS2_CUBEMAP_NEGATIVEY,
            DDSCAPS2_CUBEMAP_POSITIVEZ,
            DDSCAPS2_CUBEMAP_NEGATIVEZ
        };

        // For each face (1 for normal textures)
        for (DWORD Face = 0; Face < NumFaces; ++Face) {

            // Start with base level of this face
            LPDIRECTDRAWSURFACE7 pLevel = nullptr;

            if (isCube) {
                DDSCAPS2 capsFace = {};
                capsFace.dwCaps = DDSCAPS_TEXTURE | DDSCAPS_COMPLEX;
                capsFace.dwCaps2 = cubeFaceCaps[Face];

                hr = pTexture->GetAttachedSurface(&capsFace, &pLevel);
                if (FAILED(hr) || !pLevel)
                    continue;
            } else {
                pLevel = pTexture;
                image::Image *image = getSurfaceImage(pDevice, pLevel);
                if (image) {
                    char label[128];
                    _snprintf(label, sizeof label,
                              "PS_RESOURCE_%lu_FACE_%lu",
                               Stage, Face);

                    writer.beginMember(label);
                    StateWriter::ImageDesc imgDesc;
                    imgDesc.depth = 1;
                    imgDesc.format = image->formatName;
                    writer.writeImage(image, imgDesc);
                    writer.endMember();
                    delete image;
                }
                pLevel->AddRef();
            }

            // Traverse mipmap chain
            DWORD Level = 0;
            while (pLevel) {
                image::Image *image = getSurfaceImage(pDevice, pLevel);
                if (image) {
                    char label[128];

                    if (isCube) {
                        _snprintf(label, sizeof label,
                                  "PS_RESOURCE_%lu_FACE_%lu_LEVEL_%lu",
                                   Stage, Face, Level);
                    } else {
                        _snprintf(label, sizeof label,
                                  "PS_RESOURCE_%lu_LEVEL_%lu",
                                   Stage, Level);
                    }

                    writer.beginMember(label);
                    StateWriter::ImageDesc imgDesc;
                    imgDesc.depth = 1;
                    imgDesc.format = image->formatName;
                    writer.writeImage(image, imgDesc);
                    writer.endMember();
                    delete image;
                }

                // Get next mip level
                DDSCAPS2 capsMips = {};
                capsMips.dwCaps  = DDSCAPS_TEXTURE | DDSCAPS_MIPMAP;
                capsMips.dwCaps2 = isCube ? cubeFaceCaps[Face] : 0;

                LPDIRECTDRAWSURFACE7 pNext = nullptr;
                hr = pLevel->GetAttachedSurface(&capsMips, &pNext);

                pLevel->Release();

                if (FAILED(hr) || !pNext)
                    break;

                pLevel = pNext;
                Level++;
            }
        }
    }

    writer.endObject();
    writer.endMember(); // textures
}

struct CBContext {
    IDirect3DDevice7* pDevice;
    StateWriter* writer;
    struct {
        uint8_t backbuffer;
        uint8_t frontbuffer;
        uint8_t primarysurface;
        uint8_t offscreenplain;
        uint8_t overlay;
        uint8_t zbuffer;
        uint8_t stencilbuffer;
        uint8_t unknown;
    } counters;
};

HRESULT CALLBACK
EnumAttachedSurfacesCB(IDirectDrawSurface7* pSurface, DDSURFACEDESC2* desc, void* lpContext)
{
    CBContext* context = static_cast<CBContext*>(lpContext);
    char label[128];

    if (!pSurface || !desc || desc->dwWidth == 0 || desc->dwHeight == 0)
        return DDENUMRET_OK;

    if (desc->ddsCaps.dwCaps & DDSCAPS_FRONTBUFFER) {
        _snprintf(label, sizeof label, "FRONTBUFFER_%u", context->counters.frontbuffer++);
    } else if (desc->ddsCaps.dwCaps & DDSCAPS_BACKBUFFER) {
        _snprintf(label, sizeof label, "BACKBUFFER_%u", context->counters.backbuffer++);
    } else if (desc->ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE) {
        _snprintf(label, sizeof label, "PRIMARYSURFACE_%u", context->counters.primarysurface++);
    } else if (desc->ddsCaps.dwCaps & DDSCAPS_OFFSCREENPLAIN) {
        _snprintf(label, sizeof label, "OFFSCREENPLAIN_%u", context->counters.offscreenplain++);
    } else if (desc->ddsCaps.dwCaps & DDSCAPS_OVERLAY) {
        _snprintf(label, sizeof label, "OVERLAY_%u", context->counters.overlay++);
    } else if (desc->ddsCaps.dwCaps & DDSCAPS_ZBUFFER) {
        if (desc->ddpfPixelFormat.dwFlags & DDPF_STENCILBUFFER)
            _snprintf(label, sizeof label, "STENCILBUFFER_%u", context->counters.stencilbuffer++);
        else
            _snprintf(label, sizeof label, "ZBUFFER_%u", context->counters.zbuffer++);
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
}

void
dumpFramebuffer(StateWriter &writer, IDirect3DDevice7 *pDevice)
{
    HRESULT hr;

    writer.beginMember("framebuffer");
    writer.beginObject();

    com_ptr<IDirectDrawSurface7> pRenderTarget;
    hr = pDevice->GetRenderTarget(&pRenderTarget);
    if (SUCCEEDED(hr) && pRenderTarget) {
        image::Image *image;
        image = getSurfaceImage(pDevice, pRenderTarget);
        if (image) {
            writer.beginMember("RENDER_TARGET");
            StateWriter::ImageDesc imgDesc;
            imgDesc.depth = 1;
            imgDesc.format = image->formatName;
            writer.writeImage(image, imgDesc);
            writer.endMember(); // RENDER_TARGET
            delete image;
        }

        struct CBContext context { pDevice, &writer, 0 };
        pRenderTarget->EnumAttachedSurfaces(&context, &EnumAttachedSurfacesCB);
    }

    writer.endObject();
    writer.endMember(); // framebuffer
}


} /* namespace d3dstate */
