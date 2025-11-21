/**************************************************************************
 *
 * Copyright 2015 VMware, Inc.
 * All Rights Reserved.
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

static inline size_t
_getVertexSize(DWORD dwFVF) {
    size_t size = 0;

    assert((dwFVF & D3DFVF_RESERVED0) == 0);

    switch (dwFVF & D3DFVF_POSITION_MASK) {
    case D3DFVF_XYZ:
        size += 3 * sizeof(FLOAT);
        break;
    case D3DFVF_XYZRHW:
        size += 4 * sizeof(FLOAT);
        break;
    case D3DFVF_XYZB1:
        size += (3 + 1) * sizeof(FLOAT);
        break;
    case D3DFVF_XYZB2:
        size += (3 + 2) * sizeof(FLOAT);
        break;
    case D3DFVF_XYZB3:
        size += (3 + 3) * sizeof(FLOAT);
        break;
    case D3DFVF_XYZB4:
        size += (3 + 4) * sizeof(FLOAT);
        break;
    case D3DFVF_XYZB5:
        size += (3 + 5) * sizeof(FLOAT);
        break;
#if DIRECT3D_VERSION >= 0x0900
    case D3DFVF_XYZW:
        size += 4 * sizeof(FLOAT);
        break;
#endif
    }

    if (dwFVF & D3DFVF_NORMAL) {
        size += 3 * sizeof(FLOAT);
    }
#if DIRECT3D_VERSION >= 0x0800
    if (dwFVF & D3DFVF_PSIZE) {
        size += sizeof(FLOAT);
    }
#else
    if (dwFVF & D3DFVF_RESERVED1) {
        // D3DLVERTEX
        size += sizeof(DWORD);
    }
#endif
    if (dwFVF & D3DFVF_DIFFUSE) {
        size += sizeof(D3DCOLOR);
    }
    if (dwFVF & D3DFVF_SPECULAR) {
        size += sizeof(D3DCOLOR);
    }

    DWORD dwNumTextures = (dwFVF & D3DFVF_TEXCOUNT_MASK) >> D3DFVF_TEXCOUNT_SHIFT;
    for (DWORD CoordIndex = 0; CoordIndex < dwNumTextures; ++CoordIndex) {
        // See D3DFVF_TEXCOORDSIZE*
        DWORD dwTexCoordSize = (dwFVF >> (CoordIndex*2 + 16)) & 3;
        switch (dwTexCoordSize) {
        case D3DFVF_TEXTUREFORMAT2:
            size += 2 * sizeof(FLOAT);
            break;
        case D3DFVF_TEXTUREFORMAT1:
            size += 1 * sizeof(FLOAT);
            break;
        case D3DFVF_TEXTUREFORMAT3:
            size += 3 * sizeof(FLOAT);
            break;
        case D3DFVF_TEXTUREFORMAT4:
            size += 4 * sizeof(FLOAT);
            break;
        }
    }

    assert((dwFVF & D3DFVF_RESERVED2) == 0);

    return size;
}

static inline void
_getFormatSize(LPDDPIXELFORMAT fmt, size_t & BlockSize, UINT & BlockWidth, UINT & BlockHeight) {
    BlockSize = 0;
    BlockWidth = 1;
    BlockHeight = 1;

    if (fmt->dwFlags & DDPF_RGB) {
        BlockSize = fmt->dwRGBBitCount;
    } else if ((fmt->dwFlags & DDPF_ZBUFFER)) {
        BlockSize = fmt->dwZBufferBitDepth;
    } else if ((fmt->dwFlags & DDPF_LUMINANCE)) {
        BlockSize = fmt->dwLuminanceBitCount;
    } else if ((fmt->dwFlags & DDPF_BUMPDUDV)) {
        BlockSize = fmt->dwBumpBitCount;
    } else if ((fmt->dwFlags & DDPF_FOURCC)) {
        switch (fmt->dwFourCC) {
            case MAKEFOURCC('D', 'X', 'T', '1'):
                BlockHeight = BlockWidth = 4;
                BlockSize = 64;
                break;
            case MAKEFOURCC('D', 'X', 'T', '2'):
            case MAKEFOURCC('D', 'X', 'T', '3'):
            case MAKEFOURCC('D', 'X', 'T', '4'):
            case MAKEFOURCC('D', 'X', 'T', '5'):
                BlockHeight = BlockWidth = 4;
                BlockSize = 128;
                break;
            default:
                os::log("apitrace: warning: %s: unknown FOURCC DDPIXELFORMAT %lu\n", __FUNCTION__, fmt->dwFlags);
                BlockSize = 0;
                break;
        }
    } else {
        os::log("apitrace: warning: %s: unknown DDPIXELFORMAT %lu\n", __FUNCTION__, fmt->dwFlags);
        BlockSize = 0;
    }
}

#define PACKED_PITCH 0x7ffffff

static inline size_t
_getLockSize(LPDDPIXELFORMAT Format, bool Partial, UINT Width, UINT Height, INT RowPitch = PACKED_PITCH, UINT Depth = 1, INT SlicePitch = 0) {
    if (Width == 0 || Height == 0 || Depth == 0) {
        return 0;
    }

    if (RowPitch < 0) {
        os::log("apitrace: warning: %s: negative row pitch %i\n", __FUNCTION__, RowPitch);
        return 0;
    }

    size_t size;
    {
        size_t BlockSize;
        UINT BlockWidth;
        UINT BlockHeight;
        _getFormatSize(Format, BlockSize, BlockWidth, BlockHeight);
        assert(BlockHeight);
        Height = (Height + BlockHeight - 1) / BlockHeight;

        if (RowPitch == PACKED_PITCH) {
            RowPitch = ((Width + BlockWidth  - 1) / BlockWidth * BlockSize + 7) / 8;
        }

        size = Height * RowPitch;

        if (Partial || Height == 1) {
            // Must take pixel size in consideration
            if (BlockWidth) {
                Width = (Width + BlockWidth  - 1) / BlockWidth;
                size = (Width * BlockSize + 7) / 8;
                if (Height > 1) {
                    size += (Height - 1) * RowPitch;
                }
            }
        }
    }

    if (Depth > 1) {
        if (SlicePitch < 0) {
            os::log("apitrace: warning: %s: negative slice pitch %i\n", __FUNCTION__, SlicePitch);
            return 0;
        }

        size += (Depth - 1) * SlicePitch;
    }

    return size;
}

// FIXME: remove ExtractComponent and SaveSurfaceToBMP debug functions eventually
static inline uint8_t ExtractComponent(DWORD pixel, DWORD mask)
{
    if (mask == 0) return 0;
    DWORD m = mask;

    int shift = 0;
    while ((m & 1) == 0) {
        m >>= 1;
        shift++;
    }

    // unshifted value
    DWORD raw = (pixel & mask) >> shift;
    // number of mask bits
    int bits = 0;

    while (m) {
        m >>= 1;
        bits++;
    }

    // scale to 8-bit
    if (bits == 0)
        return 0;

    return (uint8_t)((raw * 255) / ((1 << bits) - 1));
}

bool SaveSurfaceToBMP(std::string filename, IDirectDrawSurface7* pSurface, RECT* pRect)
{
#define BMP_32
#define BMP_BOTTOM_UP
#define SURFACE_IS_LOCKED
    //#define SURFACE_UNLOCK

    if (!pSurface)
        return false;

#ifdef SURFACE_IS_LOCKED
    if (FAILED(pSurface->Unlock(pRect)))
        return false;
#endif

    DDSURFACEDESC2 desc;
    desc.dwSize = sizeof(desc);
    HRESULT hr = pSurface->GetSurfaceDesc(&desc);
    if (FAILED(hr))
        return false;

    if (FAILED(pSurface->Lock(nullptr, &desc, DDLOCK_WAIT, nullptr)))
        return false;

    int width = desc.dwWidth;
    int height = desc.dwHeight;
    int left = 0;
    int right = width;
    int top = 0;
    int bottom = height;
    if (pRect) {
        left = pRect->left;
        right = pRect->right;
        top = pRect->top;
        bottom = pRect->bottom;
        width = pRect->right - pRect->left;
        height = pRect->bottom - pRect->top;
    }
    int pitch = desc.lPitch;
    BYTE* pixels = (BYTE*)desc.lpSurface;

    const DDPIXELFORMAT& pf = desc.ddpfPixelFormat;

    int bitsPerPixel = pf.dwRGBBitCount;

    DWORD rmask = pf.dwRBitMask;
    DWORD gmask = pf.dwGBitMask;
    DWORD bmask = pf.dwBBitMask;
    DWORD amask = pf.dwRGBAlphaBitMask;

    // prepare BMP headers
    BITMAPFILEHEADER bmf = { 0 };
    BITMAPINFOHEADER bih = { 0 };

    bih.biSize = sizeof(BITMAPINFOHEADER);
    bih.biWidth = width;
#ifdef BMP_BOTTOM_UP
    bih.biHeight = height;
#else
    bih.biHeight = -height;
#endif
    bih.biPlanes = 1;
#ifdef BMP_32
    bih.biBitCount = 32;
#else
    bih.biBitCount = 24;
#endif
    bih.biCompression = BI_RGB;

#ifdef BMP_32
    // BMP row stride for 32bit (4-byte aligned)
    int rowSize = ((width * 4 + 4) & ~4);
#else
    // BMP row stride for 24bit (4-byte aligned)
    int rowSize = ((width * 3 + 3) & ~3);
#endif
    int imageSize = rowSize * height;

    // "BM" magic bytes
    bmf.bfType = 0x4D42;
    bmf.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    bmf.bfSize = bmf.bfOffBits + imageSize;

    FILE* f = fopen(filename.c_str(), "wb");
    if (!f) {
#ifdef SURFACE_UNLOCK
        pSurface->Unlock(nullptr);
#endif
        return false;
    }

    // write BMP headers
    fwrite(&bmf, sizeof(bmf), 1, f);
    fwrite(&bih, sizeof(bih), 1, f);

    // convert surface's pixel data
    uint8_t* rowBuf = new uint8_t[rowSize];
    for (int y = top; y < height; y++)
    {
        uint8_t* dst = rowBuf;
#ifdef BMP_BOTTOM_UP
        uint8_t* src = pixels + (height - 1 - y) * pitch;
#else
        uint8_t* src = pixels + y * pitch;
#endif
        for (int x = left; x < width; x++)
        {
            DWORD pixel = 0;

            switch (bitsPerPixel)
            {
            case 8:
                pixel = src[x];
                break;

            case 16:
                pixel = ((uint16_t*)src)[x];
                break;

            case 24:
            {
                uint8_t* p = src + x * 3;
                pixel = p[0] | (p[1] << 8) | (p[2] << 16);
                break;
            }

            case 32:
                pixel = ((uint32_t*)src)[x];
                break;

            default:
                // unsupported surface format
#ifdef SURFACE_UNLOCK
                pSurface->Unlock(nullptr);
#endif
                delete[] rowBuf;
                fclose(f);
                return false;
            }

            // extract components from masks
            uint8_t r = ExtractComponent(pixel, rmask);
            uint8_t g = ExtractComponent(pixel, gmask);
            uint8_t b = ExtractComponent(pixel, bmask);
#ifdef BMP_32
            uint8_t a = ExtractComponent(pixel, amask);
#endif

            // BMP expects BGR(A)
            * dst++ = b;
            *dst++ = g;
            *dst++ = r;
#ifdef BMP_32
            * dst++ = a;
#endif
        }

        fwrite(rowBuf, rowSize, 1, f);
    }

    delete[] rowBuf;
    fclose(f);

#ifdef SURFACE_UNLOCK
    pSurface->Unlock(nullptr);
#endif

    return true;
}

static inline void
_getMapInfo(IDirectDrawSurface* surface, RECT * pRect, DDSURFACEDESC * pDesc,
             void * & pLockedData, size_t & MappedSize) {
    MappedSize = 0;
    pLockedData = nullptr;
    return;

    UINT Width;
    UINT Height;
    if (pRect) {
        Width  = pRect->right  - pRect->left;
        Height = pRect->bottom - pRect->top;
    } else {
        Width  = pDesc->dwWidth;
        Height = pDesc->dwHeight;
    }

    MappedSize = _getLockSize(&pDesc->ddpfPixelFormat, pRect, Width, Height, pDesc->lPitch);
}

static inline void
_getMapInfo(IDirectDrawSurface2* surface, RECT * pRect, DDSURFACEDESC * pDesc,
             void * & pLockedData, size_t & MappedSize) {
    MappedSize = 0;
    pLockedData = nullptr;
    return;

    UINT Width;
    UINT Height;
    if (pRect) {
        Width  = pRect->right  - pRect->left;
        Height = pRect->bottom - pRect->top;
    } else {
        Width  = pDesc->dwWidth;
        Height = pDesc->dwHeight;
    }

    MappedSize = _getLockSize(&pDesc->ddpfPixelFormat, pRect, Width, Height, pDesc->lPitch);
}

static inline void
_getMapInfo(IDirectDrawSurface3* surface, RECT * pRect, DDSURFACEDESC * pDesc,
             void * & pLockedData, size_t & MappedSize) {
    MappedSize = 0;
    pLockedData = nullptr;
    return;

    UINT Width;
    UINT Height;
    if (pRect) {
        Width  = pRect->right  - pRect->left;
        Height = pRect->bottom - pRect->top;
    } else {
        Width  = pDesc->dwWidth;
        Height = pDesc->dwHeight;
    }

    MappedSize = _getLockSize(&pDesc->ddpfPixelFormat, pRect, Width, Height, pDesc->lPitch);
}

static inline void
_getMapInfo(IDirectDrawSurface4* surface, RECT * pRect, DDSURFACEDESC2 * pDesc,
             void * & pLockedData, size_t & MappedSize) {
    MappedSize = 0;
    pLockedData = nullptr;
    return;

    UINT Width;
    UINT Height;
    if (pRect) {
        Width  = pRect->right  - pRect->left;
        Height = pRect->bottom - pRect->top;
    } else {
        Width  = pDesc->dwWidth;
        Height = pDesc->dwHeight;
    }

    MappedSize = _getLockSize(&pDesc->ddpfPixelFormat, pRect, Width, Height, pDesc->lPitch);
}

static inline void
_getMapInfo(IDirectDrawSurface7* pSurface, RECT * pRect, DDSURFACEDESC2 * pDesc,
             void * & pLockedData, size_t & MappedSize) {
    MappedSize = 0;
    pLockedData = nullptr;

    UINT Width;
    UINT Height;
    if (pRect) {
        Width  = pRect->right  - pRect->left;
        Height = pRect->bottom - pRect->top;
    } else {
        Width  = pDesc->dwWidth;
        Height = pDesc->dwHeight;
    }

    MappedSize = _getLockSize(&pDesc->ddpfPixelFormat, pRect, Width, Height, pDesc->lPitch);
    pLockedData = pDesc->lpSurface;

//#define DEBUG_SAVEBMP
#ifdef DEBUG_SAVEBMP
    static int picIndex = 0;
    picIndex++;
    size_t nZero = 4;
    std::string sNumber = std::to_string(picIndex);
    std::string filename = "image_" + std::string(nZero - std::min(nZero, sNumber.length()), '0') + sNumber + ".bmp";
    SaveSurfaceToBMP(filename, pSurface, pRect);
#endif
}

static inline void
_getMapInfo(IDirectDrawSurface7* pSurface, HDC* hDC,
    void*& pLockedData, size_t& MappedSize) {
    MappedSize = 0;

    DDSURFACEDESC2 desc;
    desc.dwSize = sizeof(desc);
    HRESULT hr = pSurface->GetSurfaceDesc(&desc);

    if (SUCCEEDED(hr))
        pLockedData = desc.lpSurface;
    else {
        pLockedData = nullptr;
        return;
    }

    UINT Width = desc.dwWidth;
    UINT Height = desc.dwHeight;

    MappedSize = _getLockSize(&desc.ddpfPixelFormat, false, Width, Height, desc.lPitch);
}

static inline void
_getMapInfo(IDirect3DVertexBuffer* pBuffer, void **ppbData, DWORD* lpdwSize,
            void * & pLockedData, size_t & MappedSize) {
    pLockedData = *ppbData;
    MappedSize = 0;

    D3DVERTEXBUFFERDESC Desc;
    HRESULT hr = pBuffer->GetVertexBufferDesc(&Desc);
    if (FAILED(hr)) {
        return;
    }
    MappedSize = _getVertexSize(Desc.dwFVF) * Desc.dwNumVertices;
}

static inline void
_getMapInfo(IDirect3DVertexBuffer7* pBuffer, void **ppbData, DWORD *lpdwSize,
             void * & pLockedData, size_t & MappedSize) {
    pLockedData = *ppbData;
    MappedSize = 0;

    D3DVERTEXBUFFERDESC Desc;
    HRESULT hr = pBuffer->GetVertexBufferDesc(&Desc);
    if (FAILED(hr)) {
        return;
    }
    MappedSize = _getVertexSize(Desc.dwFVF) * Desc.dwNumVertices;
}

static inline void
_getMapInfo(IDirect3DExecuteBuffer* pBuffer, D3DEXECUTEBUFFERDESC* pDesc,
    void*& pLockedData, size_t& MappedSize) {
    pLockedData = nullptr;
    MappedSize = pDesc->dwBufferSize;
}
