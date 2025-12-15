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
convertFormat(const DDPIXELFORMAT & ddpfPixelFormat)
{
    if (ddpfPixelFormat.dwSize != sizeof ddpfPixelFormat) {
        return D3DFMT_UNKNOWN;
    }

    switch (ddpfPixelFormat.dwFlags) {
    case DDPF_RGB:
        switch (ddpfPixelFormat.dwRGBBitCount) {
        case 8:
            return (ddpfPixelFormat.dwFlags & DDPF_PALETTEINDEXED8) ? D3DFMT_P8 : D3DFMT_R3G3B2;
        case 16:
            switch (ddpfPixelFormat.dwRBitMask) {
            case (0x0F << 8):
                return D3DFMT_A4R4G4B4;
            case (0x1F << 10):
                return (ddpfPixelFormat.dwRGBAlphaBitMask) ? D3DFMT_A1R5G5B5 : D3DFMT_X1R5G5B5;
            case (0x1F << 11):
                return D3DFMT_R5G6B5;
            break;
            }
        case 32:
            return (ddpfPixelFormat.dwRGBAlphaBitMask) ? D3DFMT_A8R8G8B8 : D3DFMT_X8R8G8B8;
        }
        break;
    case DDPF_ZBUFFER:
    case DDPF_ZBUFFER | DDPF_STENCILBUFFER:
        switch (ddpfPixelFormat.dwZBufferBitDepth) {
        case 16:
            if (ddpfPixelFormat.dwZBitMask == 0x0000ffff) {
                return D3DFMT_D16;
            }
            break;
        case 32:
            if (ddpfPixelFormat.dwZBitMask == 0x00ffffff) {
                return D3DFMT_D24X8;
            }
            switch (ddpfPixelFormat.dwStencilBitMask) {
            case 0:
                return D3DFMT_D24X8;
            case 0xFF:
                return D3DFMT_D24S8;
            case (DWORD(0xFF << 24)):
                return D3DFMT_D24S8;
            }
            break;
        }
        break;
    case DDPF_LUMINANCE:
        switch (ddpfPixelFormat.dwLuminanceBitCount) {
        case 8: {
            switch (ddpfPixelFormat.dwLuminanceBitMask) {
            case (0xF):
                return D3DFMT_L8;
            case (0x8):
                return D3DFMT_A4L4;
            }
        }
        case 16:
            return D3DFMT_A8L8;
        }
        break;
    case DDPF_BUMPDUDV:
        switch (ddpfPixelFormat.dwBumpBitCount) {
        case 16:
          return ddpfPixelFormat.dwBumpLuminanceBitMask ? D3DFMT_L6V5U5 : D3DFMT_V8U8;
        case 32:
          return D3DFMT_X8L8V8U8;
        }
        break;
    case DDPF_FOURCC:
        switch (ddpfPixelFormat.dwFourCC) {
        case D3DFMT_DXT1:
            return static_cast<D3DFORMAT>(D3DFMT_DXT1);
        case D3DFMT_DXT2:
            return static_cast<D3DFORMAT>(D3DFMT_DXT2);
        case D3DFMT_DXT3:
            return static_cast<D3DFORMAT>(D3DFMT_DXT3);
        case D3DFMT_DXT4:
            return static_cast<D3DFORMAT>(D3DFMT_DXT4);
        case D3DFMT_DXT5:
            return static_cast<D3DFORMAT>(D3DFMT_DXT5);
        case D3DFMT_YUY2:
            return static_cast<D3DFORMAT>(D3DFMT_YUY2);
        }
        break;
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
        std::cerr << "warning: unsupported DDPIXELFORMAT\n";
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
            writer.beginMember("RENDER_TARGET_0");
            StateWriter::ImageDesc imgDesc;
            imgDesc.depth = 1;
            imgDesc.format = image->formatName;
            writer.writeImage(image, imgDesc);
            writer.endMember(); // RENDER_TARGET_*
            delete image;
        }

        // Search for a depth-stencil attachment
        DDSCAPS2 ddsCaps;
        ZeroMemory(&ddsCaps, sizeof ddsCaps);
        ddsCaps.dwCaps = DDSCAPS_ZBUFFER;
        com_ptr<IDirectDrawSurface7> pDepthStencil;
        hr = pRenderTarget->GetAttachedSurface(&ddsCaps, &pDepthStencil);
        if (SUCCEEDED(hr) && pDepthStencil) {
            image = getSurfaceImage(pDevice, pDepthStencil);
            if (image) {
                writer.beginMember("DEPTH_STENCIL");
                StateWriter::ImageDesc imgDesc;
                imgDesc.depth = 1;
                imgDesc.format = image->formatName;
                writer.writeImage(image, imgDesc);
                writer.endMember(); // DEPTH_STENCIL
                delete image;
            }
        }

        ddsCaps.dwCaps = DDSCAPS_FRONTBUFFER;
        com_ptr<IDirectDrawSurface7> pFrontBuffer;
        hr = pRenderTarget->GetAttachedSurface(&ddsCaps, &pFrontBuffer);
        if (SUCCEEDED(hr) && pFrontBuffer) {
            image = getSurfaceImage(pDevice, pFrontBuffer);
            if (image) {
                writer.beginMember("FRONT_BUFFER");
                StateWriter::ImageDesc imgDesc;
                imgDesc.depth = 1;
                imgDesc.format = image->formatName;
                writer.writeImage(image, imgDesc);
                writer.endMember();
                delete image;
            }
        }

        ddsCaps.dwCaps = DDSCAPS_BACKBUFFER | DDSCAPS_FLIP;
        com_ptr<IDirectDrawSurface7> pBackBuffer;
        hr = pRenderTarget->GetAttachedSurface(&ddsCaps, &pBackBuffer);
        if (SUCCEEDED(hr) && pBackBuffer) {
            image = getSurfaceImage(pDevice, pBackBuffer);
            if (image) {
                writer.beginMember("BACK_BUFFER");
                StateWriter::ImageDesc imgDesc;
                imgDesc.depth = 1;
                imgDesc.format = image->formatName;
                writer.writeImage(image, imgDesc);
                writer.endMember();
                delete image;
            }
        }

        ddsCaps.dwCaps = DDSCAPS_PRIMARYSURFACE;
        com_ptr<IDirectDrawSurface7> pPrimarySurface;
        hr = pRenderTarget->GetAttachedSurface(&ddsCaps, &pPrimarySurface);
        if (SUCCEEDED(hr) && pPrimarySurface) {
            image = getSurfaceImage(pDevice, pPrimarySurface);
            if (image) {
                writer.beginMember("PRIMARY_SURFACE");
                StateWriter::ImageDesc imgDesc;
                imgDesc.depth = 1;
                imgDesc.format = image->formatName;
                writer.writeImage(image, imgDesc);
                writer.endMember();
                delete image;
            }
        }
    }

    writer.endObject();
    writer.endMember(); // framebuffer
}


} /* namespace d3dstate */
