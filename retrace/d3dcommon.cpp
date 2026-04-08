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
#include <map>
#include <sstream>
#include <variant>

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
             UINT Width, UINT Height,
             PALETTEENTRY *palette);

D3DFORMAT
convertFormat(const DDPIXELFORMAT & ddpf)
{
    /*
     * TODO: For some reason at least WineD3D in some cases return dwSize=0 even when descriptor itself is not jank.
     * e.g. that happens in Sea Dogs which uses IClassFactory. Need investigation, so comment-out this check for now.
     */
    /*
    if (ddpf.dwSize != sizeof(ddpf)) {
        std::cerr << "warning: wrong format dwSize: " << ddpf.dwSize << "\n";
        return D3DFMT_UNKNOWN;
    }
    */

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

    if (ddpf.dwFlags & DDPF_FOURCC) {
        return static_cast<D3DFORMAT>(ddpf.dwFourCC);
    }

    return D3DFMT_UNKNOWN;
}

template <typename S>
image::Image *
getSurfaceImage(S *pSurface)
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
    if (Format != D3DFMT_UNKNOWN) {
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

        PALETTEENTRY *palette = nullptr;
        if (Format == D3DFMT_P8) {
            IDirectDrawPalette *pPalette = nullptr;
            hr = pSurface->GetPalette(&pPalette);
            if (SUCCEEDED(hr)) {
                palette = new PALETTEENTRY[256];
                hr = pPalette->GetEntries(0, 0, 256, palette);
                if (FAILED(hr)) {
                    pPalette->Release();
                }
            }

            // Palette can also come from primary surface
            if (FAILED(hr)) {
                std::visit([&hr, &palette](auto& surface) {
                using T = std::decay_t<decltype(surface)>;
                    if constexpr (!std::is_same_v<T, std::monostate>) {
                        IDirectDrawPalette *pPalette = nullptr;

                        hr = surface->GetPalette(&pPalette);
                        if (SUCCEEDED(hr)) {
                            palette = new PALETTEENTRY[256];
                            hr = pPalette->GetEntries(0, 0, 256, palette);
                            if (FAILED(hr)) {
                                pPalette->Release();
                            }
                        }
                    }
                }, lastSetRenderTarget);
            }
        }

        image = ConvertImage(Format, desc.lpSurface, pitch, desc.dwWidth, desc.dwHeight, palette);
        delete palette;
    }

    pSurface->Unlock(nullptr);

    return image;
}

template image::Image *
getSurfaceImage<IDirectDrawSurface>(IDirectDrawSurface *);
template image::Image *
getSurfaceImage<IDirectDrawSurface2>(IDirectDrawSurface2 *);
template image::Image *
getSurfaceImage<IDirectDrawSurface3>(IDirectDrawSurface3 *);
template image::Image *
getSurfaceImage<IDirectDrawSurface4>(IDirectDrawSurface4 *);
template image::Image *
getSurfaceImage<IDirectDrawSurface7>(IDirectDrawSurface7 *);

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

    image::Image* image = getSurfaceImage(pSurface);
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

Surface lastSetRenderTarget = std::monostate{};
Surface lastSetSurface = std::monostate{};
std::vector<Texture> lastSetTextures;
struct textureBind {
    DWORD hTexture;
    Texture pTexture;
};
static std::map<DWORD, DWORD> stateBlockMap;
static std::map<DWORD, DWORD> materialMap;
static std::map<DWORD, DWORD> matrixMap;
static std::map<DWORD, textureBind> textureMap;
static std::map<DWORD, DWORD> renderStates = {
    {D3DRENDERSTATE_ANTIALIAS, 0},
    {D3DRENDERSTATE_TEXTUREPERSPECTIVE, 0},
    {D3DRENDERSTATE_ZENABLE, 0},
    {D3DRENDERSTATE_FILLMODE, 0},
    {D3DRENDERSTATE_SHADEMODE, 0},
    {D3DRENDERSTATE_LINEPATTERN, 0},
    {D3DRENDERSTATE_ZWRITEENABLE, 0},
    {D3DRENDERSTATE_ALPHATESTENABLE, 0},
    {D3DRENDERSTATE_LASTPIXEL, 0},
    {D3DRENDERSTATE_SRCBLEND, 0},
    {D3DRENDERSTATE_DESTBLEND, 0},
    {D3DRENDERSTATE_CULLMODE, 0},
    {D3DRENDERSTATE_ZFUNC, 0},
    {D3DRENDERSTATE_ALPHAREF, 0},
    {D3DRENDERSTATE_ALPHAFUNC, 0},
    {D3DRENDERSTATE_DITHERENABLE, 0},
    {D3DRENDERSTATE_ALPHABLENDENABLE, 0},
    {D3DRENDERSTATE_FOGENABLE, 0},
    {D3DRENDERSTATE_SPECULARENABLE, 0},
    {D3DRENDERSTATE_ZVISIBLE, 0},
    {D3DRENDERSTATE_STIPPLEDALPHA, 0},
    {D3DRENDERSTATE_FOGCOLOR, 0},
    {D3DRENDERSTATE_FOGTABLEMODE, 0},
    {D3DRENDERSTATE_FOGSTART, 0},
    {D3DRENDERSTATE_FOGEND, 0},
    {D3DRENDERSTATE_FOGDENSITY, 0},
    {D3DRENDERSTATE_WRAP0, 0},
    {D3DRENDERSTATE_WRAP1, 0},
    {D3DRENDERSTATE_WRAP2, 0},
    {D3DRENDERSTATE_WRAP3, 0},
    {D3DRENDERSTATE_WRAP4, 0},
    {D3DRENDERSTATE_WRAP5, 0},
    {D3DRENDERSTATE_WRAP6, 0},
    {D3DRENDERSTATE_WRAP7, 0},
    {D3DRENDERSTATE_TEXTUREHANDLE, 0},
    {D3DRENDERSTATE_TEXTUREADDRESS, 0},
    {D3DRENDERSTATE_WRAPU, 0},
    {D3DRENDERSTATE_WRAPV, 0},
    {D3DRENDERSTATE_MONOENABLE, 0},
    {D3DRENDERSTATE_ROP2, 0},
    {D3DRENDERSTATE_PLANEMASK, 0},
    {D3DRENDERSTATE_TEXTUREMAG, 0},
    {D3DRENDERSTATE_TEXTUREMIN, 0},
    {D3DRENDERSTATE_TEXTUREMAPBLEND, 0},
    {D3DRENDERSTATE_SUBPIXEL, 0},
    {D3DRENDERSTATE_SUBPIXELX, 0},
    {D3DRENDERSTATE_STIPPLEENABLE, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN00, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN01, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN02, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN03, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN04, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN05, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN06, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN07, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN08, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN09, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN10, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN11, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN12, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN13, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN14, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN15, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN16, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN17, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN18, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN19, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN20, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN21, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN22, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN23, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN24, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN25, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN26, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN27, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN28, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN29, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN30, 0},
    {D3DRENDERSTATE_STIPPLEPATTERN31, 0},
};

DWORD
getRenderState(DWORD state) {
    return renderStates[state];
}

void
setRenderState(DWORD state, DWORD value) {
    renderStates[state] = value;
}

DWORD
getStateBlockHandle(DWORD hOriginal) {
    if (hOriginal == 0) {
        return 0;
    }

    auto it = stateBlockMap.find(hOriginal);
    if (it == stateBlockMap.end()) {
        return 0;
    }

    return it->second;
}

void
setStateBlockMap(DWORD hOriginal, DWORD hStateBlock) {
    if (!hOriginal) {
        return;
    }

    if (hStateBlock) {
        stateBlockMap[hOriginal] = hStateBlock;
    } else {
        stateBlockMap.erase(hOriginal);
    }
}

DWORD
getMaterialHandle(DWORD hOriginal) {
    if (hOriginal == 0) {
        return 0;
    }

    auto it = materialMap.find(hOriginal);
    if (it == materialMap.end()) {
        return 0;
    }

    return it->second;
}

void
setMaterialMap(DWORD hOriginal, DWORD hMaterial) {
    if (!hOriginal) {
        return;
    }

    if (hMaterial) {
        materialMap[hOriginal] = hMaterial;
    } else {
        materialMap.erase(hOriginal);
    }
}

DWORD
getMatrixHandle(DWORD hOriginal) {
    if (hOriginal == 0) {
        return 0;
    }

    auto it = matrixMap.find(hOriginal);
    if (it == matrixMap.end()) {
        return 0;
    }

    return it->second;
}

void
setMatrixMap(DWORD hOriginal, DWORD hMatrix) {
    if (!hOriginal) {
        return;
    }

    if (hMatrix) {
        matrixMap[hOriginal] = hMatrix;
    } else {
        matrixMap.erase(hOriginal);
    }
}

DWORD
getTextureHandle(DWORD hOriginal) {
    if (hOriginal == 0) {
        return 0;
    }

    auto it = textureMap.find(hOriginal);
    if (it == textureMap.end()) {
        return 0;
    }

    return it->second.hTexture;
}

void
swapTextures(Texture pTex1, Texture pTex2) {
    using T1 = std::decay_t<decltype(pTex1)>;
    using T2 = std::decay_t<decltype(pTex2)>;

    if (std::is_same_v<T1, std::monostate> || std::is_same_v<T2, std::monostate> || pTex1 == pTex2) {
        return;
    }

    textureBind *first = nullptr;
    textureBind *second = nullptr;

    for (auto it = textureMap.begin(); it != textureMap.end(); it++) {
        if (it->second.pTexture == pTex1) {
            first = &it->second;
        } else if (it->second.pTexture == pTex2) {
            second = &it->second;
        }

        if (first && second) {
            first->pTexture = pTex2;
            second->pTexture = pTex1;
            return;
        }
    }
}

void
setTextureMap(DWORD hOriginal, DWORD hTexture, Texture pTexture) {
    if (!hOriginal || !hTexture) {
        return;
    }

    if constexpr (!std::is_same_v<Texture, std::monostate>) {
        textureMap[hOriginal] = {hTexture, pTexture};
    } else {
        textureMap.erase(hOriginal);
    }
}

static Texture
getTextureFromMap(DWORD hTexture) {
    if (hTexture == 0) {
        return std::monostate{};
    }

    for (auto it = textureMap.begin(); it != textureMap.end(); it++) {
        if (it->second.hTexture == hTexture) {
            return it->second.pTexture;
        }
    }

    return std::monostate{};
}

void
setTexture(DWORD hTexture) {
    if (!hTexture) {
        return;
    }

    lastSetTextures.push_back(getTextureFromMap(hTexture));
}

void
clearTextures() {
    lastSetTextures.clear();
}

void
setRenderTarget(Surface pSurface) {
    lastSetRenderTarget = pSurface;
}

void
setSurface(Surface pSurface) {
    lastSetSurface = pSurface;
}

void
writeTextureRenderState(StateWriter &writer, std::string state, DWORD value)
{
    if (state == "D3DTSS_MAXMIPLEVEL"
        || state == "D3DTSS_MAXANISOTROPY") {
        writer.writeIntMember(state.c_str(), value);
    } else if (state == "D3DTSS_BUMPENVMAT00"
        || state == "D3DTSS_BUMPENVMAT01"
        || state == "D3DTSS_BUMPENVMAT10"
        || state == "D3DTSS_BUMPENVMAT11"
        || state == "D3DTSS_MIPMAPLODBIAS"
        || state == "D3DTSS_BUMPENVLSCALE"
        || state == "D3DTSS_BUMPENVLOFFSET") {
        writer.writeFloatMember(state.c_str(), static_cast<float>(value));

    } else if (state == "D3DTSS_COLORARG1"
        || state == "D3DTSS_COLORARG2"
        || state == "D3DTSS_ALPHAARG1"
        || state == "D3DTSS_ALPHAARG2") {
        switch (value) {
            case(D3DTA_DIFFUSE):
                writer.writeStringMember(state.c_str(), "D3DTA_DIFFUSE");
                break;
            case(D3DTA_CURRENT):
                writer.writeStringMember(state.c_str(), "D3DTA_CURRENT");
                break;
            case(D3DTA_TEXTURE):
                writer.writeStringMember(state.c_str(), "D3DTA_TEXTURE");
                break;
            case(D3DTA_TFACTOR):
                writer.writeStringMember(state.c_str(), "D3DTA_TFACTOR");
                break;
            case(D3DTA_SPECULAR):
                writer.writeStringMember(state.c_str(), "D3DTA_SPECULAR");
                break;
            case(D3DTA_COMPLEMENT):
                writer.writeStringMember(state.c_str(), "D3DTA_COMLEMENT");
                break;
            case(D3DTA_ALPHAREPLICATE):
                writer.writeStringMember(state.c_str(), "D3DTA_ALPHAREPLICATE");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DTSS_COLOROP"
        || state == "D3DTSS_ALPHAOP") {
        switch (value) {
            case(D3DTOP_DISABLE):
                writer.writeStringMember(state.c_str(), "D3DTOP_DISABLE");
                break;
            case(D3DTOP_SELECTARG1):
                writer.writeStringMember(state.c_str(), "D3DTOP_SELECTARG1");
                break;
            case(D3DTOP_SELECTARG2):
                writer.writeStringMember(state.c_str(), "D3DTOP_SELECTARG2");
                break;
            case(D3DTOP_MODULATE):
                writer.writeStringMember(state.c_str(), "D3DTOP_MODULATE");
                break;
            case(D3DTOP_MODULATE2X):
                writer.writeStringMember(state.c_str(), "D3DTOP_MODULATE2X");
                break;
            case(D3DTOP_MODULATE4X):
                writer.writeStringMember(state.c_str(), "D3DTOP_MODULATE4X");
                break;
            case(D3DTOP_ADD):
                writer.writeStringMember(state.c_str(), "D3DTOP_ADD");
                break;
            case(D3DTOP_ADDSIGNED):
                writer.writeStringMember(state.c_str(), "D3DTOP_ADDSIGNED");
                break;
            case(D3DTOP_ADDSIGNED2X):
                writer.writeStringMember(state.c_str(), "D3DTOP_ADDSIGNED2X");
                break;
            case(D3DTOP_SUBTRACT):
                writer.writeStringMember(state.c_str(), "D3DTOP_SUBTRACT");
                break;
            case(D3DTOP_ADDSMOOTH):
                writer.writeStringMember(state.c_str(), "D3DTOP_ADDSMOOTH");
                break;
            case(D3DTOP_BLENDDIFFUSEALPHA):
                writer.writeStringMember(state.c_str(), "D3DTOP_BLENDDIFFUSEALPHA");
                break;
            case(D3DTOP_BLENDTEXTUREALPHA):
                writer.writeStringMember(state.c_str(), "D3DTOP_BLENDTEXTUREALPHA");
                break;
            case(D3DTOP_BLENDFACTORALPHA):
                writer.writeStringMember(state.c_str(), "D3DTOP_BLENDFACTORALPHA");
                break;
            case(D3DTOP_BLENDTEXTUREALPHAPM):
                writer.writeStringMember(state.c_str(), "D3DTOP_BLENDTEXTUREALPHAPM");
                break;
            case(D3DTOP_BLENDCURRENTALPHA):
                writer.writeStringMember(state.c_str(), "D3DTOP_BLENDCURRENTALPHA");
                break;
            case(D3DTOP_PREMODULATE):
                writer.writeStringMember(state.c_str(), "D3DTOP_PREMODULATE");
                break;
            case(D3DTOP_MODULATEALPHA_ADDCOLOR):
                writer.writeStringMember(state.c_str(), "D3DTOP_MODULATEALPHA_ADDCOLOR");
                break;
            case(D3DTOP_MODULATECOLOR_ADDALPHA):
                writer.writeStringMember(state.c_str(), "D3DTOP_MODULATECOLOR_ADDALPHA");
                break;
            case(D3DTOP_MODULATEINVALPHA_ADDCOLOR):
                writer.writeStringMember(state.c_str(), "D3DTOP_MODULATEINVALPHA_ADDCOLOR");
                break;
            case(D3DTOP_MODULATEINVCOLOR_ADDALPHA):
                writer.writeStringMember(state.c_str(), "D3DTOP_MODULATEINVCOLOR_ADDALPHA");
                break;
            case(D3DTOP_BUMPENVMAP):
                writer.writeStringMember(state.c_str(), "D3DTOP_BUMPENVMAP");
                break;
            case(D3DTOP_BUMPENVMAPLUMINANCE):
                writer.writeStringMember(state.c_str(), "D3DTOP_BUMPENVMAPLUMINANCE");
                break;
            case(D3DTOP_DOTPRODUCT3):
                writer.writeStringMember(state.c_str(), "D3DTOP_DOTPRODUCT3");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }

    } else if (state == "D3DTSS_ADDRESS"
        || state == "D3DTSS_ADDRESSV"
        || state == "D3DTSS_ADDRESSU") {
        switch (value) {
            case(D3DTADDRESS_WRAP):
                writer.writeStringMember(state.c_str(), "D3DTADDRESS_WRAP");
                break;
            case(D3DTADDRESS_MIRROR):
                writer.writeStringMember(state.c_str(), "D3DTADDRESS_MIRROR");
                break;
            case(D3DTADDRESS_CLAMP):
                writer.writeStringMember(state.c_str(), "D3DTADDRESS_CLAMP");
                break;
            case(D3DTADDRESS_BORDER):
                writer.writeStringMember(state.c_str(), "D3DTADDRESS_BORDER");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DTSS_MAGFILTER") {
        switch (value) {
            case(D3DTFG_POINT):
                writer.writeStringMember(state.c_str(), "D3DTFG_POINT");
                break;
            case(D3DTFG_LINEAR):
                writer.writeStringMember(state.c_str(), "D3DTFG_LINEAR");
                break;
            case(D3DTFG_FLATCUBIC):
                writer.writeStringMember(state.c_str(), "D3DTFG_FLATCUBIC");
                break;
            case(D3DTFG_GAUSSIANCUBIC):
                writer.writeStringMember(state.c_str(), "D3DTFG_GAUSSIANCUBIC");
                break;
            case(D3DTFG_ANISOTROPIC):
                writer.writeStringMember(state.c_str(), "D3DTFG_ANISOTROPIC");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DTSS_MINFILTER") {
        switch (value) {
            case(D3DTFN_POINT):
                writer.writeStringMember(state.c_str(), "D3DTFN_POINT");
                break;
            case(D3DTFN_LINEAR):
                writer.writeStringMember(state.c_str(), "D3DTFN_LINEAR");
                break;
            case(D3DTFN_ANISOTROPIC):
                writer.writeStringMember(state.c_str(), "D3DTFN_ANISOTROPIC");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DTSS_MIPFILTER") {
        switch (value) {
            case(D3DTFP_NONE):
                writer.writeStringMember(state.c_str(), "D3DTFP_NONE");
                break;
            case(D3DTFP_POINT):
                writer.writeStringMember(state.c_str(), "D3DTFP_POINT");
                break;
            case(D3DTFP_LINEAR):
                writer.writeStringMember(state.c_str(), "D3DTFP_LINEAR");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DTSS_TEXCOORDINDEX") {
        switch (value) {
            case(D3DTSS_TCI_PASSTHRU):
                writer.writeStringMember(state.c_str(), "D3DTSS_TCI_PASSTHRU");
                break;
            case(D3DTSS_TCI_CAMERASPACENORMAL):
                writer.writeStringMember(state.c_str(), "D3DTSS_TCI_CAMERASPACENORMAL");
                break;
            case(D3DTSS_TCI_CAMERASPACEPOSITION):
                writer.writeStringMember(state.c_str(), "D3DTSS_TCI_CAMERASPACEPOSITION");
                break;
            case(D3DTSS_TCI_CAMERASPACEREFLECTIONVECTOR):
                writer.writeStringMember(state.c_str(), "D3DTSS_TCI_CAMERASPACEREFLECTIONVECTOR");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DTSS_TEXTURETRANSFORMFLAGS") {
        switch (value) {
            case(D3DTTFF_DISABLE):
                writer.writeStringMember(state.c_str(), "D3DTTFF_DISABLE");
                break;
            case(D3DTTFF_COUNT1):
                writer.writeStringMember(state.c_str(), "D3DTTFF_COUNT1");
                break;
            case(D3DTTFF_COUNT2):
                writer.writeStringMember(state.c_str(), "D3DTTFF_COUNT2");
                break;
            case(D3DTTFF_COUNT3):
                writer.writeStringMember(state.c_str(), "D3DTTFF_COUNT3");
                break;
            case(D3DTTFF_COUNT4):
                writer.writeStringMember(state.c_str(), "D3DTTFF_COUNT4");
                break;
            case(D3DTTFF_PROJECTED):
                writer.writeStringMember(state.c_str(), "D3DTTFF_PROJECTED");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DTSS_BORDERCOLOR") {
        writer.writeIntMember(state.c_str(), value);
    } else {
        writer.writeStringMember(state.c_str(), "NOT IMPLEMENTED");
    }
}

void
writeRenderState(StateWriter &writer, std::string state, DWORD value)
{
    if (state == "D3DRENDERSTATE_TEXTUREPERSPECTIVE"
        || state == "D3DRENDERSTATE_ZENABLE"
        || state == "D3DRENDERSTATE_ZWRITEENABLE"
        || state == "D3DRENDERSTATE_ALPHATESTENABLE"
        || state == "D3DRENDERSTATE_LASTPIXEL"
        || state == "D3DRENDERSTATE_DITHERENABLE"
        || state == "D3DRENDERSTATE_ALPHABLENDENABLE"
        || state == "D3DRENDERSTATE_FOGENABLE"
        || state == "D3DRENDERSTATE_SPECULARENABLE"
        || state == "D3DRENDERSTATE_ZVISIBLE"
        || state == "D3DRENDERSTATE_STIPPLEDALPHA"
        || state == "D3DRENDERSTATE_EDGEANTIALIAS"
        || state == "D3DRENDERSTATE_COLORKEYENABLE"
        || state == "D3DRENDERSTATE_RANGEFOGENABLE"
        || state == "D3DRENDERSTATE_STENCILENABLE"
        || state == "D3DRENDERSTATE_CLIPPING"
        || state == "D3DRENDERSTATE_LIGHTING"
        || state == "D3DRENDERSTATE_EXTENTS"
        || state == "D3DRENDERSTATE_COLORVERTEX"
        || state == "D3DRENDERSTATE_LOCALVIEWER"
        || state == "D3DRENDERSTATE_NORMALIZENORMALS"
        || state == "D3DRENDERSTATE_COLORKEYBLENDENABLE"
        || state == "D3DRENDERSTATE_CLIPPLANEENABLE"
        || state == "D3DRENDERSTATE_WRAPU"
        || state == "D3DRENDERSTATE_WRAPV"
        || state == "D3DRENDERSTATE_MONOENABLE"
        || state == "D3DRENDERSTATE_SUBPIXEL"
        || state == "D3DRENDERSTATE_SUBPIXELX"
        || state == "D3DRENDERSTATE_STIPPLEENABLE"
        || state == "D3DRENDERSTATE_OLDALPHABLENDENABLE"
        || state == "D3DRENDERSTATE_ANISOTROPY"
        || state == "D3DRENDERSTATE_FLUSHBATCH"
        || state == "D3DRENDERSTATE_TRANSLUCENTSORTINDEPENDENT") {
        writer.writeBoolMember(state.c_str(), value);
    } else if (state == "D3DRENDERSTATE_ALPHAREF"
        || state == "D3DRENDERSTATE_STENCILREF"
        || state == "D3DRENDERSTATE_STENCILMASK"
        || state == "D3DRENDERSTATE_STENCILWRITEMASK"
        || state == "D3DRENDERSTATE_TEXTUREHANDLE"
        || state == "D3DRENDERSTATE_PLANEMASK"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN00"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN01"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN02"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN03"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN04"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN05"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN06"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN07"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN08"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN09"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN10"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN11"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN12"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN13"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN14"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN15"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN16"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN17"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN18"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN19"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN20"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN21"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN22"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN23"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN24"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN25"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN26"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN27"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN28"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN29"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN30"
        || state == "D3DRENDERSTATE_STIPPLEPATTERN31") {
        writer.writeIntMember(state.c_str(), value);
    } else if (state == "D3DRENDERSTATE_FOGSTART"
        || state == "D3DRENDERSTATE_FOGEND"
        || state == "D3DRENDERSTATE_FOGDENSITY"
        || state == "D3DRENDERSTATE_MIPMAPLODBIAS"
        || state == "D3DRENDERSTATE_ZBIAS") {
        writer.writeFloatMember(state.c_str(), static_cast<float>(value));
    } else if (state == "D3DRENDERSTATE_ANTIALIAS") {
        switch (value) {
            case(D3DANTIALIAS_NONE):
                writer.writeStringMember(state.c_str(), "D3DANTIALIAS_NONE");
                break;
            case(D3DANTIALIAS_SORTDEPENDENT):
                writer.writeStringMember(state.c_str(), "D3DANTIALIAS_SORTDEPENDENT");
                break;
            case(D3DANTIALIAS_SORTINDEPENDENT):
                writer.writeStringMember(state.c_str(), "D3DANTIALIAS_SORTINDEPENDENT");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_WRAP0"
        || state == "D3DRENDERSTATE_WRAP1"
        || state == "D3DRENDERSTATE_WRAP2"
        || state == "D3DRENDERSTATE_WRAP3"
        || state == "D3DRENDERSTATE_WRAP4"
        || state == "D3DRENDERSTATE_WRAP5"
        || state == "D3DRENDERSTATE_WRAP6"
        || state == "D3DRENDERSTATE_WRAP7") {
        std::string buf{};
        if (value & D3DWRAPCOORD_0) {
            buf.append(buf.length() > 0 ? " | " : "").append("D3DWRAPCOORD_0");
        }
        if (value & D3DWRAPCOORD_1) {
            buf.append(buf.length() > 0 ? " | " : "").append("D3DWRAPCOORD_1");
        }
        if (value & D3DWRAPCOORD_2) {
            buf.append(buf.length() > 0 ? " | " : "").append("D3DWRAPCOORD_2");
        }
        if (value & D3DWRAPCOORD_3) {
            buf.append(buf.length() > 0 ? " | " : "").append("D3DWRAPCOORD_3");
        }
        if (buf.length() > 0) {
            writer.writeStringMember(state.c_str(), buf.c_str());
        } else {
            writer.writeIntMember(state.c_str(), value);
        }
    } else if (state == "D3DRENDERSTATE_SRCBLEND"
        || state == "D3DRENDERSTATE_DESTBLEND") {
        switch (value) {
            case(D3DBLEND_ZERO):
                writer.writeStringMember(state.c_str(), "D3DBLEND_ZERO");
                break;
            case(D3DBLEND_ONE):
                writer.writeStringMember(state.c_str(), "D3DBLEND_ONE");
                break;
            case(D3DBLEND_SRCCOLOR):
                writer.writeStringMember(state.c_str(), "D3DBLEND_SRCCOLOR");
                break;
            case(D3DBLEND_INVSRCCOLOR):
                writer.writeStringMember(state.c_str(), "D3DBLEND_INVSRCCOLOR");
                break;
            case(D3DBLEND_SRCALPHA):
                writer.writeStringMember(state.c_str(), "D3DBLEND_SRCALPHA");
                break;
            case(D3DBLEND_INVSRCALPHA):
                writer.writeStringMember(state.c_str(), "D3DBLEND_INVSRCALPHA");
                break;
            case(D3DBLEND_DESTALPHA):
                writer.writeStringMember(state.c_str(), "D3DBLEND_DESTALPHA");
                break;
            case(D3DBLEND_INVDESTALPHA):
                writer.writeStringMember(state.c_str(), "D3DBLEND_INVDESTALPHA");
                break;
            case(D3DBLEND_DESTCOLOR):
                writer.writeStringMember(state.c_str(), "D3DBLEND_DESTCOLOR");
                break;
            case(D3DBLEND_INVDESTCOLOR):
                writer.writeStringMember(state.c_str(), "D3DBLEND_INVDESTCOLOR");
                break;
            case(D3DBLEND_SRCALPHASAT):
                writer.writeStringMember(state.c_str(), "D3DBLEND_SRCALPHASAT");
                break;
            case(D3DBLEND_BOTHSRCALPHA):
                writer.writeStringMember(state.c_str(), "D3DBLEND_BOTHSRCALPHA");
                break;
            case(D3DBLEND_BOTHINVSRCALPHA):
                writer.writeStringMember(state.c_str(), "D3DBLEND_BOTHINVSRCALPHA");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_STENCILFAIL"
        || state == "D3DRENDERSTATE_STENCILZFAIL"
        || state == "D3DRENDERSTATE_STENCILPASS") {
        switch (value) {
            case(D3DSTENCILOP_KEEP):
                writer.writeStringMember(state.c_str(), "D3DSTENCILOP_KEEP");
                break;
            case(D3DSTENCILOP_ZERO):
                writer.writeStringMember(state.c_str(), "D3DSTENCILOP_ZERO");
                break;
            case(D3DSTENCILOP_REPLACE):
                writer.writeStringMember(state.c_str(), "D3DSTENCILOP_REPLACE");
                break;
            case(D3DSTENCILOP_INCRSAT):
                writer.writeStringMember(state.c_str(), "D3DSTENCILOP_INCRSAT");
                break;
            case(D3DSTENCILOP_DECRSAT):
                writer.writeStringMember(state.c_str(), "D3DSTENCILOP_DECRSAT");
                break;
            case(D3DSTENCILOP_INVERT):
                writer.writeStringMember(state.c_str(), "D3DSTENCILOP_INVERT");
                break;
            case(D3DSTENCILOP_INCR):
                writer.writeStringMember(state.c_str(), "D3DSTENCILOP_INCR");
                break;
            case(D3DSTENCILOP_DECR):
                writer.writeStringMember(state.c_str(), "D3DSTENCILOP_DECR");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_ZFUNC"
        || state == "D3DRENDERSTATE_ALPHAFUNC"
        || state == "D3DRENDERSTATE_STENCILFUNC") {
        switch (value) {
            case(D3DCMP_NEVER):
                writer.writeStringMember(state.c_str(), "D3DCMP_NEVER");
                break;
            case(D3DCMP_LESS):
                writer.writeStringMember(state.c_str(), "D3DCMP_LESS");
                break;
            case(D3DCMP_EQUAL):
                writer.writeStringMember(state.c_str(), "D3DCMP_EQUAL");
                break;
            case(D3DCMP_LESSEQUAL):
                writer.writeStringMember(state.c_str(), "D3DCMP_LESSEQUAL");
                break;
            case(D3DCMP_GREATER):
                writer.writeStringMember(state.c_str(), "D3DCMP_GREATER");
                break;
            case(D3DCMP_NOTEQUAL):
                writer.writeStringMember(state.c_str(), "D3DCMP_NOTEQUAL");
                break;
            case(D3DCMP_GREATEREQUAL):
                writer.writeStringMember(state.c_str(), "D3DCMP_GREATEREQUAL");
                break;
            case(D3DCMP_ALWAYS):
                writer.writeStringMember(state.c_str(), "D3DCMP_ALWAYS");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_FILLMODE") {
        std::string buf{};
        if (value & D3DFILL_POINT) {
            buf.append(buf.length() > 0 ? " | " : "").append("D3DFILL_POINT");
        }
        if (value & D3DFILL_WIREFRAME) {
            buf.append(buf.length() > 0 ? " | " : "").append("D3DFILL_WIREFRAME");
        }
        if (value & D3DFILL_SOLID) {
            buf.append(buf.length() > 0 ? " | " : "").append("D3DFILL_SOLID");
        }
        if (buf.length() > 0) {
            writer.writeStringMember(state.c_str(), buf.c_str());
        } else {
            writer.writeIntMember(state.c_str(), value);
        }
    } else if (state == "D3DRENDERSTATE_SHADEMODE") {
        std::string buf{};
        if (value & D3DSHADE_FLAT) {
            buf.append(buf.length() > 0 ? " | " : "").append("D3DSHADE_FLAT");
        }
        if (value & D3DSHADE_GOURAUD) {
            buf.append(buf.length() > 0 ? " | " : "").append("D3DSHADE_GOURAUD");
        }
        if (value & D3DSHADE_PHONG) {
            buf.append(buf.length() > 0 ? " | " : "").append("D3DSHADE_PHONG");
        }
        if (buf.length() > 0) {
            writer.writeStringMember(state.c_str(), buf.c_str());
        } else {
            writer.writeIntMember(state.c_str(), value);
        }
    } else if (state == "D3DRENDERSTATE_CULLMODE") {
        switch (value) {
            case(D3DCULL_NONE):
                writer.writeStringMember(state.c_str(), "D3DCULL_NONE");
                break;
            case(D3DCULL_CW):
                writer.writeStringMember(state.c_str(), "D3DCULL_CW");
                break;
            case(D3DCULL_CCW):
                writer.writeStringMember(state.c_str(), "D3DCULL_CCW");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_LINEPATTERN") {
        D3DLINEPATTERN *val = (D3DLINEPATTERN*)&value;
        std::ostringstream buf{};
        buf << "wRepeatFactor = " << val->wRepeatFactor << ", wLinePattern = " << val->wLinePattern;
        writer.writeStringMember(state.c_str(), buf.str().c_str());
    } else if (state == "D3DRENDERSTATE_FOGCOLOR"
        || state == "D3DRENDERSTATE_TEXTUREFACTOR"
        || state == "D3DRENDERSTATE_AMBIENT"
        || state == "D3DRENDERSTATE_BORDERCOLOR") {
        writer.writeIntMember(state.c_str(), value);
    } else if (state == "D3DRENDERSTATE_FOGTABLEMODE"
        || state == "D3DRENDERSTATE_FOGVERTEXMODE") {
        switch (value) {
            case(D3DFOG_NONE):
                writer.writeStringMember(state.c_str(), "D3DFOG_NONE");
                break;
            case(D3DFOG_EXP):
                writer.writeStringMember(state.c_str(), "D3DFOG_EXP");
                break;
            case(D3DFOG_EXP2):
                writer.writeStringMember(state.c_str(), "D3DFOG_EXP2");
                break;
            case(D3DFOG_LINEAR):
                writer.writeStringMember(state.c_str(), "D3DFOG_LINEAR");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_DIFFUSEMATERIALSOURCE"
        || state == "D3DRENDERSTATE_SPECULARMATERIALSOURCE"
        || state == "D3DRENDERSTATE_AMBIENTMATERIALSOURCE"
        || state == "D3DRENDERSTATE_EMISSIVEMATERIALSOURCE") {
        switch (value) {
            case(D3DMCS_MATERIAL):
                writer.writeStringMember(state.c_str(), "D3DMCS_MATERIAL");
                break;
            case(D3DMCS_COLOR1):
                writer.writeStringMember(state.c_str(), "D3DMCS_COLOR1");
                break;
            case(D3DMCS_COLOR2):
                writer.writeStringMember(state.c_str(), "D3DMCS_COLOR2");
                break;
            case(D3DMCS_FORCE_DWORD):
                writer.writeStringMember(state.c_str(), "D3DMCS_FORCE_DWORD");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_TEXTUREADDRESS"
        || state == "D3DRENDERSTATE_TEXTUREADDRESSU"
        || state == "D3DRENDERSTATE_TEXTUREADDRESSV") {
        switch (value) {
            case(D3DTADDRESS_WRAP):
                writer.writeStringMember(state.c_str(), "D3DTADDRESS_WRAP");
                break;
            case(D3DTADDRESS_MIRROR):
                writer.writeStringMember(state.c_str(), "D3DTADDRESS_MIRROR");
                break;
            case(D3DTADDRESS_CLAMP):
                writer.writeStringMember(state.c_str(), "D3DTADDRESS_CLAMP");
                break;
            case(D3DTADDRESS_BORDER):
                writer.writeStringMember(state.c_str(), "D3DTADDRESS_BORDER");
                break;
            case(D3DTADDRESS_FORCE_DWORD):
                writer.writeStringMember(state.c_str(), "D3DTADDRESS_FORCE_DWORD");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_TEXTUREMAG"
        || state == "D3DRENDERSTATE_TEXTUREMIN") {
        switch (value) {
            case(D3DFILTER_NEAREST):
                writer.writeStringMember(state.c_str(), "D3DFILTER_NEAREST");
                break;
            case(D3DFILTER_LINEAR):
                writer.writeStringMember(state.c_str(), "D3DFILTER_LINEAR");
                break;
            case(D3DFILTER_MIPNEAREST):
                writer.writeStringMember(state.c_str(), "D3DFILTER_MIPNEAREST");
                break;
            case(D3DFILTER_MIPLINEAR):
                writer.writeStringMember(state.c_str(), "D3DFILTER_MIPLINEAR");
                break;
            case(D3DFILTER_LINEARMIPNEAREST):
                writer.writeStringMember(state.c_str(), "D3DFILTER_LINEARMIPNEAREST");
                break;
            case(D3DFILTER_LINEARMIPLINEAR):
                writer.writeStringMember(state.c_str(), "D3DFILTER_LINEARMIPLINEAR");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_ROP2") {
        switch (value) {
            case(R2_BLACK):
                writer.writeStringMember(state.c_str(), "R2_BLACK");
                break;
            case(R2_NOTMERGEPEN):
                writer.writeStringMember(state.c_str(), "R2_NOTMERGEPEN");
                break;
            case(R2_MASKNOTPEN):
                writer.writeStringMember(state.c_str(), "R2_MASKNOTPEN");
                break;
            case(R2_NOTCOPYPEN):
                writer.writeStringMember(state.c_str(), "R2_NOTCOPYPEN");
                break;
            case(R2_MASKPENNOT):
                writer.writeStringMember(state.c_str(), "R2_MASKPENNOT");
                break;
            case(R2_NOT):
                writer.writeStringMember(state.c_str(), "R2_NOT");
                break;
            case(R2_XORPEN):
                writer.writeStringMember(state.c_str(), "R2_XORPEN");
                break;
            case(R2_NOTMASKPEN):
                writer.writeStringMember(state.c_str(), "R2_NOTMASKPEN");
                break;
            case(R2_MASKPEN):
                writer.writeStringMember(state.c_str(), "R2_MASKPEN");
                break;
            case(R2_NOTXORPEN):
                writer.writeStringMember(state.c_str(), "R2_NOTXORPEN");
                break;
            case(R2_NOP):
                writer.writeStringMember(state.c_str(), "R2_NOP");
                break;
            case(R2_MERGENOTPEN):
                writer.writeStringMember(state.c_str(), "R2_MERGENOTPEN");
                break;
            case(R2_COPYPEN):
                writer.writeStringMember(state.c_str(), "R2_COPYPEN");
                break;
            case(R2_MERGEPENNOT):
                writer.writeStringMember(state.c_str(), "R2_MERGEPENNOT");
                break;
            case(R2_MERGEPEN):
                writer.writeStringMember(state.c_str(), "R2_MERGEPEN");
                break;
            case(R2_WHITE):
                writer.writeStringMember(state.c_str(), "R2_WHITE");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_TEXTUREMAPBLEND") {
        switch (value) {
            case(D3DTBLEND_DECAL):
                writer.writeStringMember(state.c_str(), "D3DTBLEND_DECAL");
                break;
            case(D3DTBLEND_MODULATE):
                writer.writeStringMember(state.c_str(), "D3DTBLEND_MODULATE");
                break;
            case(D3DTBLEND_DECALALPHA):
                writer.writeStringMember(state.c_str(), "D3DTBLEND_DECALALPHA");
                break;
            case(D3DTBLEND_MODULATEALPHA):
                writer.writeStringMember(state.c_str(), "D3DTBLEND_MODULATEALPHA");
                break;
            case(D3DTBLEND_DECALMASK):
                writer.writeStringMember(state.c_str(), "D3DTBLEND_DECALMASK");
                break;
            case(D3DTBLEND_MODULATEMASK):
                writer.writeStringMember(state.c_str(), "D3DTBLEND_MODULATEMASK");
                break;
            case(D3DTBLEND_COPY):
                writer.writeStringMember(state.c_str(), "D3DTBLEND_COPY");
                break;
            case(D3DTBLEND_ADD):
                writer.writeStringMember(state.c_str(), "D3DTBLEND_ADD");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else if (state == "D3DRENDERSTATE_VERTEXBLEND") {
        switch (value) {
            case(D3DVBLEND_DISABLE):
                writer.writeStringMember(state.c_str(), "D3DVBLEND_DISABLE");
                break;
            case(D3DVBLEND_1WEIGHT):
                writer.writeStringMember(state.c_str(), "D3DVBLEND_1WEIGHT");
                break;
            case(D3DVBLEND_2WEIGHTS):
                writer.writeStringMember(state.c_str(), "D3DVBLEND_2WEIGHTS");
                break;
            case(D3DVBLEND_3WEIGHTS):
                writer.writeStringMember(state.c_str(), "D3DVBLEND_3WEIGHTS");
                break;
            default:
                writer.writeIntMember(state.c_str(), value);
                break;
        }
    } else {
        writer.writeStringMember(state.c_str(), "NOT IMPLEMENTED");
    }
}

} /* namespace d3dstate */
