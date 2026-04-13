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

#include <variant>
#include <vector>

#include "image.hpp"
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

template <typename D>
struct CBContext {
    D* pDevice;
    StateWriter* writer;
    struct {
        uint8_t backbuffer;
        uint8_t frontbuffer;
        uint8_t primarysurface;
        uint8_t primarysurfaceleft;
        uint8_t offscreenplain;
        uint8_t overlay;
        uint8_t zbuffer;
        uint8_t stencilbuffer;
        uint8_t complex;
        uint8_t unknown;
    } counters;

    CBContext(D* pDevice, StateWriter* writer) {
      this->pDevice = pDevice;
      this->writer = writer;
      this->counters = {0};
    };

    ~CBContext() {};
};
template struct CBContext<IDirect3DDevice2>;
template struct CBContext<IDirect3DDevice3>;
template struct CBContext<IDirect3DDevice7>;

template <typename S, typename D>
HRESULT CALLBACK
EnumAttachedSurfacesCB(S* pSurface, D* pDesc, void* pContext);
extern template HRESULT CALLBACK
EnumAttachedSurfacesCB<IDirectDrawSurface, DDSURFACEDESC>(IDirectDrawSurface*, DDSURFACEDESC*, void*);
extern template HRESULT CALLBACK
EnumAttachedSurfacesCB<IDirectDrawSurface4, DDSURFACEDESC2>(IDirectDrawSurface4*, DDSURFACEDESC2*, void*);
extern template HRESULT CALLBACK
EnumAttachedSurfacesCB<IDirectDrawSurface7, DDSURFACEDESC2>(IDirectDrawSurface7*, DDSURFACEDESC2*, void*);

template <typename S>
image::Image *
getSurfaceImage(S *pSurface);
extern template image::Image*
getSurfaceImage<IDirectDrawSurface>(IDirectDrawSurface*);
extern template image::Image*
getSurfaceImage<IDirectDrawSurface2>(IDirectDrawSurface2*);
extern template image::Image*
getSurfaceImage<IDirectDrawSurface3>(IDirectDrawSurface3*);
extern template image::Image*
getSurfaceImage<IDirectDrawSurface4>(IDirectDrawSurface4*);
extern template image::Image*
getSurfaceImage<IDirectDrawSurface7>(IDirectDrawSurface7*);

DWORD
getRenderState(DWORD state);
void
setRenderState(DWORD state, DWORD value);

using Surface = std::variant<IDirectDrawSurface*, IDirectDrawSurface2*, IDirectDrawSurface3*, IDirectDrawSurface4*, IDirectDrawSurface7*, std::monostate>;
extern Surface lastSetRenderTarget;
void
setRenderTarget(Surface pSurface);

extern Surface lastSetSurface;
void
setSurface(Surface pSurface);

void
setStateBlockMap(DWORD hOriginal, DWORD hStateBlock);
DWORD
getStateBlockHandle(DWORD hOriginal);

void
setMaterialMap(DWORD hOriginal, DWORD hMaterial);
DWORD
getMaterialHandle(DWORD hOriginal);

void
setMatrixMap(DWORD hOriginal, DWORD hMaterial);
DWORD
getMatrixHandle(DWORD hOriginal);

using Texture = std::variant<IDirect3DTexture*, IDirect3DTexture2*, std::monostate>;
extern std::vector<Texture> lastSetTextures;
void
setTextureMap(DWORD hOriginal, DWORD hTexture, Texture pTexture);
void
swapTextures(Texture pTex1, Texture pTex2);
DWORD
getTextureHandle(DWORD hOriginal);
void
setTexture(DWORD hOriginal);
void
clearTextures();

void
writeTextureRenderState(StateWriter &writer, std::string state, DWORD value);

void
writeRenderState(StateWriter &writer, std::string state, DWORD value);

} /* namespace d3dstate */
