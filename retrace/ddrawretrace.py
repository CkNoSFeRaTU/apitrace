##########################################################################
#
# Copyright 2011 Jose Fonseca
# All Rights Reserved.
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


"""D3D retracer generator."""


import sys
from dllretrace import DllRetracer as Retracer
from specs.stdapi import API
from specs.d3d import ddraw, HWND
from specs.ddraw import DDCREATE_LPGUID

class D3DRetracer(Retracer):
    def retraceApi(self, api):
        print('// Swizzling mapping for lock addresses')
        print('static std::map<void *, void *> _maps;')
        print()
        # FIXME: Properly handle multiple windows
        print('static HWND g_hWnd{0};')
        print('static int g_width = 0, g_height = 0;');
        print('static LPDIRECTDRAWCLIPPER g_clipper = nullptr;')
        print('static std::list<void *> g_enumSurfaces;')
        print()

        Retracer.retraceApi(self, api)

    def invokeInterfaceMethod(self, interface, method):
        # keep track of the last used device for state dumping
        if interface.name == 'IUnknown' and method.name == 'Release':
            print(r'    if (call.ret->toUInt() == 0) {')
            print(r'        if (_this == d3d3Dumper.pLastDevice) {')
            print(r'            d3d3Dumper.unbindDevice(static_cast<IDirect3DDevice*>(_this));')
            print(r'        }')
            print(r'        else if (_this == d3d5Dumper.pLastDevice) {')
            print(r'            d3d5Dumper.unbindDevice(static_cast<IDirect3DDevice2*>(_this));')
            print(r'        }')
            print(r'        else if (_this == d3d6Dumper.pLastDevice) {')
            print(r'            d3d6Dumper.unbindDevice(static_cast<IDirect3DDevice3*>(_this));')
            print(r'        }')
            print(r'        else if (_this == d3d7Dumper.pLastDevice) {')
            print(r'            d3d7Dumper.unbindDevice(static_cast<IDirect3DDevice7*>(_this));')
            print(r'        }')
            print(r'        else if (_this == ddrawDumper.pLastDevice) {')
            print(r'            ddrawDumper.unbindDevice(static_cast<IDirectDraw*>(_this));')
            print(r'        }')
            print(r'        else if (_this == ddraw2Dumper.pLastDevice) {')
            print(r'            ddraw2Dumper.unbindDevice(static_cast<IDirectDraw2*>(_this));')
            print(r'        }')
            print(r'        else if (_this == ddraw4Dumper.pLastDevice) {')
            print(r'            ddraw4Dumper.unbindDevice(static_cast<IDirectDraw4*>(_this));')
            print(r'        }')
            print(r'        else if (_this == ddraw7Dumper.pLastDevice) {')
            print(r'            ddraw7Dumper.unbindDevice(static_cast<IDirectDraw7*>(_this));')
            print(r'        }')
            print(r'        else {')
            print(r'             using S = std::decay_t<decltype(d3dstate::lastSetSurface)>;')
            print(r'             if constexpr(!std::is_same_v<S, std::monostate>) {')
            print(r'                  d3dstate::setSurface(std::monostate{});')
            print(r'             }')
#            print(r'             using T = std::decay_t<decltype(d3dstate::lastSetTexture)>;')
#            print(r'             if constexpr(!std::is_same_v<S, std::monostate>) {')
#            print(r'                  d3dstate::deleteTexture(std::monostate{});')
#            print(r'             }')
            print(r'        }')
            print(r'    }')
        elif interface.name == 'IDirect3DDevice' and method.name != 'Release':
            print(r'    d3d3Dumper.bindDevice(_this);')
        elif interface.name == 'IDirect3DDevice2' and method.name != 'Release':
            print(r'    d3d5Dumper.bindDevice(_this);')
        elif interface.name == 'IDirect3DDevice3' and method.name != 'Release':
            print(r'    d3d6Dumper.bindDevice(_this);')
        elif interface.name == 'IDirect3DDevice7' and method.name != 'Release':
            print(r'    d3d7Dumper.bindDevice(_this);')
        elif interface.name == 'IDirectDraw' and method.name != 'Release':
            print(r'    if (!d3d3Dumper.pLastDevice && !d3d5Dumper.pLastDevice && !d3d6Dumper.pLastDevice && !d3d7Dumper.pLastDevice) {')
            print(r'        ddrawDumper.bindDevice(_this);')
            print(r'    }')
        elif interface.name == 'IDirectDraw2' and method.name != 'Release':
            print(r'    if (!d3d3Dumper.pLastDevice && !d3d5Dumper.pLastDevice && !d3d6Dumper.pLastDevice && !d3d7Dumper.pLastDevice) {')
            print(r'        ddraw2Dumper.bindDevice(_this);')
            print(r'    }')
        elif interface.name == 'IDirectDraw4' and method.name != 'Release':
            print(r'    if (!d3d3Dumper.pLastDevice && !d3d5Dumper.pLastDevice && !d3d6Dumper.pLastDevice && !d3d7Dumper.pLastDevice) {')
            print(r'        ddraw4Dumper.bindDevice(_this);')
            print(r'    }')
        elif interface.name == 'IDirectDraw7' and method.name != 'Release':
            print(r'    if (!d3d3Dumper.pLastDevice && !d3d5Dumper.pLastDevice && !d3d6Dumper.pLastDevice && !d3d7Dumper.pLastDevice) {')
            print(r'        ddraw7Dumper.bindDevice(_this);')
            print(r'    }')

        # notify frame has been completed
        # process events after presents
        if interface.name.startswith('IDirectDraw') and method.name in ('Blt', 'BltFast', 'EndScene', 'Flip', 'Unlock', 'ReleaseDC'):
            if interface.name in ('IDirectDrawSurface4', 'IDirectDrawSurface7'):
                print(r'    DDSCAPS2 ddsCaps;')
            else:
                print(r'    DDSCAPS ddsCaps;')
            print(r'    HRESULT hr = _this->GetCaps(&ddsCaps);')
            print(r'    if (SUCCEEDED(hr) && (ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE)) {')
            print(r'        retrace::frameComplete(call);')
            print(r'        d3dretrace::processEvents();')
            print(r'    }')
        if interface.name.startswith('IDirectDraw') and method.name in ('SetColorControls', 'SetEntries', 'FlipToGDISurface'):
            print(r'    retrace::frameComplete(call);')
            print(r'    d3dretrace::processEvents();')

        # handle windows
        hWndArg = method.getArgByType(HWND)
        if hWndArg is not None:
            if method.name == "SetCooperativeLevel":
                print(r'    g_hWnd = d3dretrace::createWindow(g_hWnd, g_width ? g_width : 640, g_height ? g_height : 480,')
                print(r'        dwFlags & DDSCL_FULLSCREEN ? WS_POPUP | WS_VISIBLE : 0, dwFlags & DDSCL_FULLSCREEN ? WS_EX_APPWINDOW : 0);')
                print(r'    %s = g_hWnd;' % hWndArg.name)
                print(r'    _HWND_map[static_cast<HWND>((call.arg(1)).toPointer())] = g_hWnd;')
            else:
                print(r'    %s = g_hWnd;' % hWndArg.name)

        if method.name == 'Lock':
            # Reset _DONOTWAIT flags. Otherwise they may fail, and we have no
            # way to cope with it (other than retry).
            mapFlagsArg = method.getArgByName('dwFlags')
            if mapFlagsArg is not None:
                print(r'    dwFlags &= ~DDLOCK_DONOTWAIT;')
                print(r'    dwFlags |= DDLOCK_WAIT;')

        if method.name == 'ReleaseDC':
            print('    d3dretrace::setHDC((call.arg(1)).toUInt(), nullptr);')

        if interface.name.startswith('IDirectDrawSurface'):
            # Clipper adjustments
            if method.name == 'Blt':
                print(r'    if (SUCCEEDED(hr) && (ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE) && lpDestRect) {')
                print(r'        size_t n_width = (*lpDestRect).right - (*lpDestRect).left;')
                print(r'        size_t n_height = (*lpDestRect).bottom - (*lpDestRect).top;')
                print(r'        if (g_clipper && (n_width != g_width || n_height != g_height)) {')
                print(r'            g_width = n_width;')
                print(r'            g_height = n_height;')
                print(r'            d3dretrace::resizeWindow(g_hWnd, g_width, g_height);')
                print(r'        }')
                print(r'    }')
                print(r'    POINT cPt{0, 0};')
                print(r'    if (g_clipper && lpDestRect && ClientToScreen(g_hWnd, &cPt)) {')
                print(r'        (*lpDestRect).left += cPt.x;')
                print(r'        (*lpDestRect).right += cPt.x;')
                print(r'        (*lpDestRect).top += cPt.y;')
                print(r'        (*lpDestRect).bottom += cPt.y;')
                print(r'    }')

            if method.name == 'SetClipper':
                if interface.name in ('IDirectDrawSurface4', 'IDirectDrawSurface7'):
                    print(r'    DDSCAPS2 ddsCaps;')
                else:
                    print(r'    DDSCAPS ddsCaps;')
                print(r'    if (SUCCEEDED(_this->GetCaps(&ddsCaps) && (ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE))) {')
                print(r'        g_clipper = lpDDClipper;')
                print(r'    }')
        if interface.name.startswith('IDirectDraw'):
            if method.name == 'SetDisplayMode':
                print(r'    g_width = dwWidth;')
                print(r'    g_height = dwHeight;')
                print(r'    if (g_hWnd && g_clipper)')
                print(r'        d3dretrace::resizeWindow(g_hWnd, g_width, g_height);')

        if interface.name.startswith('IDirectDraw') and method.name in ('EnumSurfaces', 'EnumAttachedSurfaces'):
            print(r'    CBEnumContext context{call};')
            print(r'    lpContext = &context;')
            print(r'    lpEnumSurfacesCallback = &EnumAttachedSurfacesCB;')

        if interface.name == 'IDirect3DDevice7' and method.name in ('ApplyStateBlock', 'CaptureStateBlock', 'DeleteStateBlock'):
            print(r'    %s = d3dstate::getStateBlockHandle(%s);' % (method.getArgByName('dwBlockHandle').name, method.getArgByName('dwBlockHandle').name))

        if interface.name.startswith('IDirect3DDevice') and method.name == 'SetLightState':
            print(r'    if (%s == D3DLIGHTSTATE_MATERIAL) {' % method.getArgByName('dwLightStateType').name)
            print(r'        %s = d3dstate::getMaterialHandle(%s);' % (method.getArgByName('dwLightState').name, method.getArgByName('dwLightState').name))
            print(r'    }')

        if interface.name.startswith('IDirect3DDevice') and method.name == 'SetRenderState':
            print(r'    if (%s == D3DRENDERSTATE_TEXTUREHANDLE) {' % method.getArgByName('dwRenderStateType').name)
            print(r'        %s = d3dstate::getTextureHandle(%s);' % (method.getArgByName('dwRenderState').name, method.getArgByName('dwRenderState').name))
            print(r'    }')

        if interface.name.startswith('IDirect3DMaterial') and method.name == 'SetMaterial':
            print(r'    %s->hTexture = d3dstate::getTextureHandle(%s->hTexture);' % (method.getArgByName('lpMat').name, method.getArgByName('lpMat').name))

        if interface.name.startswith('IDirect3DViewport') and method.name == 'SetBackground':
            print(r'    %s = d3dstate::getMaterialHandle(%s);' % (method.getArgByName('hMat').name, method.getArgByName('hMat').name))

        Retracer.invokeInterfaceMethod(self, interface, method)

        if interface.name == 'IDirect3D2' and method.name == 'CreateDevice':
            print(r'    if (call.ret->toUInt() == 0) {')
            print(r'        d3d5Dumper.bindDevice(*lplpD3DDevice2);')
            print(r'    }')
        elif interface.name == 'IDirect3D3' and method.name == 'CreateDevice':
            print(r'    if (call.ret->toUInt() == 0) {')
            print(r'        d3d6Dumper.bindDevice(*lplpD3DDevice3);')
            print(r'    }')
        elif interface.name == 'IDirect3D7' and method.name == 'CreateDevice':
            print(r'    if (call.ret->toUInt() == 0) {')
            print(r'        d3d7Dumper.bindDevice(*lplpD3DDevice);')
            print(r'    }')

        if interface.name.startswith('IDirectDraw') and method.name in ('EnumSurfaces', 'EnumAttachedSurfaces'):
            print(r'    d3dretrace::clearEnumSurfaces();')

        if method.name == 'CreateDevice':
            print(r'    if (FAILED(_result)) {')
            print(r'        exit(1);')
            print(r'    }')

        # Hack to set window size according to primary surfaces sizes.
        if interface.name.startswith('IDirectDraw') and method.name == 'CreateSurface':
            print(r'    if (lpDDSurfaceDesc) {')
            print(r'        if ((*lpDDSurfaceDesc).ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE) {')
            print(r'            if ((*lpDDSurfaceDesc).dwHeight > 0 && (*lpDDSurfaceDesc).dwWidth > 0) {')
            print(r'                g_height = (*lpDDSurfaceDesc).dwHeight;')
            print(r'                g_width = (*lpDDSurfaceDesc).dwWidth;')
            print(r'                if (g_clipper) {')
            print(r'                    d3dretrace::resizeWindow(g_hWnd, g_width, g_height);')
            print(r'                }')
            print(r'            }')
            print(r'        }')
            print(r'    }')

        if method.name == 'Lock' and interface.name != "IDirect3DExecuteBuffer":
            print('    VOID *_pbData = nullptr;')
            print('    size_t _MappedSize = 0;')

            if interface.name.startswith("IDirectDrawSurface") and method.name == 'Lock':
                print('    if (!(dwFlags & DDLOCK_READONLY)) {')
            else:
                print('    if (true) {')
            if interface.name.startswith("IDirectDrawSurface") and method.name == 'Lock':
                print('        _getMapInfo(_this, %s, _pbData, _MappedSize);' % ', '.join(method.argNames()[:-2]))
            elif interface.name.startswith("IDirect3DVertexBuffer"):
                print('        _getMapInfo(_this, %s, _pbData, _MappedSize);' % ', '.join(method.argNames()[1:]))
            else:
                print('        _getMapInfo(_this, %s, _pbData, _MappedSize);' % ', '.join(method.argNames()))
            print('    }')
            print('    if (_MappedSize) {')
            print('        _maps[_this] = _pbData;')
            self.checkPitchMismatch(method);
            print('    } else {')
            print('        return;')
            print('    }')
        elif interface.name == 'IDirect3DExecuteBuffer' and method.name in ('Initialize', 'Lock'):
            print('    VOID *_pbData = nullptr;')
            print('    size_t _MappedSize = 0;')
            if method.name == 'Lock':
                print('    _getMapInfo(_this, %s, _pbData, _MappedSize);' % ', '.join(method.argNames()))
                print('    if (_MappedSize) {')
                print('        _maps[_this] = _pbData;')
                self.checkPitchMismatch(method);
                print('    } else {')
                print('        return;')
                print('    }')
                print('    const trace::Array *_a_desc = (call.arg(1)).toArray();')
                print('    const trace::Struct *_s_desc = (*_a_desc->values[0]).toStruct();')
                print('    retrace::addRegion(call, (*_s_desc->members[4]).toUIntPtr(), (lpDesc)->lpData, _MappedSize);')

        if method.name in ('Unlock'):
            print('    VOID *_pbData = 0;')
            print('    _pbData = _maps[_this];')
            print('    if (_pbData) {')
            print('        retrace::delRegionByPointer(_pbData);')
            print('        _maps[_this] = 0;')
            print('    }')

        if method.name == 'GetDC':
            print('    const trace::Array *_ar = (call.arg(1)).toArray();')
            print('    if (_ar) {')
            print('        d3dretrace::setHDC((*_ar->values[0]).toUInt(), phDC[0]);')
            print('    }')

        if interface.name == 'IDirect3DDevice7' and method.name in ('CreateStateBlock', 'EndStateBlock'):
            print(r'    if (SUCCEEDED(_result) && %s) {' % method.getArgByName('lpdwBlockHandle').name)
            if method.name == 'CreateStateBlock':
                print(r'        const trace::Array *_ar = (call.arg(2)).toArray();')
            elif method.name == 'EndStateBlock':
                print(r'        const trace::Array *_ar = (call.arg(1)).toArray();')
            print(r'        if (_ar) {')
            print(r'            DWORD hOriginal = static_cast<DWORD>((*_ar->values[0]).toUInt());')
            print(r'            d3dstate::setStateBlockMap(hOriginal, *%s);' % method.getArgByName('lpdwBlockHandle').name)
            print(r'        }')
            print(r'    }')

        if interface.name.startswith('IDirect3DMaterial') and method.name == 'GetHandle':
            print(r'    if (SUCCEEDED(_result) && %s) {' % method.getArgByName('lpHandle').name)
            print(r'        const trace::Array *_ar = (call.arg(2)).toArray();')
            print(r'        if (_ar) {')
            print(r'            DWORD hOriginal = static_cast<DWORD>((*_ar->values[0]).toUInt());')
            print(r'            d3dstate::setMaterialMap(hOriginal, *%s);' % method.getArgByName('lpHandle').name)
            print(r'        }')
            print(r'    }')

        if interface.name.startswith('IDirect3DTexture') and method.name == 'GetHandle':
            print(r'    if (SUCCEEDED(_result) && %s) {' % method.getArgByName('lpHandle').name)
            print(r'        const trace::Array *_ar = (call.arg(2)).toArray();')
            print(r'        if (_ar) {')
            print(r'            DWORD hOriginal = static_cast<DWORD>((*_ar->values[0]).toUInt());')
            print(r'            d3dstate::setTextureMap(hOriginal, *%s, _this);' % method.getArgByName('lpHandle').name)
            print(r'        }')
            print(r'    }')

        if interface.name.startswith('IDirect3DDevice') and method.name == 'SetRenderState':
            print(r'    if (SUCCEEDED(_result) && %s == D3DRENDERSTATE_TEXTUREHANDLE) {' % method.getArgByName('dwRenderStateType').name)
            print(r'        d3dstate::setTexture(%s);' % method.getArgByName('dwRenderState').name)
            print(r'    }')

        if interface.name.startswith('IDirectDrawSurface'):
            print(r'    if (SUCCEEDED(_result)) {')
            print(r'          d3dstate::setSurface(_this);')
            print(r'    } else {')
            print(r'          d3dstate::setSurface(std::monostate{});')
            print(r'    }')

    def extractArg(self, function, arg, arg_type, lvalue, rvalue):
        # Handle DDCREATE_* flags
        if arg.type is DDCREATE_LPGUID:
            print('    if (%s.toArray()) {' % rvalue)
            # We need to clear lpGUID as it can be GUID of GPU adapter and so trace from another machine/os could fail
            if arg.name == 'lpGUID' and function.name in ('DirectDrawCreate', 'DirectDrawCreateEx'):
                print('    %s = nullptr;' % lvalue)
#                print('    %s = static_cast<%s>(0);' % (lvalue, arg_type))
            else:
                Retracer.extractArg(self, function, arg, arg_type, lvalue, rvalue)
            print('    } else {')
            print('        %s = static_cast<%s>(%s.toPointer());' % (lvalue, arg_type, rvalue))
            print('    }')
            return

        Retracer.extractArg(self, function, arg, arg_type, lvalue, rvalue)


def main():
    print(r'#include <string.h>')
    print()
    print(r'#include <iostream>')
    print()
    print(r'#include "d3dretrace.hpp"')
    print()

    api = API()

    print(r'#include "d3dimports.hpp"')
    print(r'#include "d3dcommon.hpp"')
    print(r'#include "d3d7size.hpp"')
    api.addModule(ddraw)
    print()
    print('''static d3dretrace::D3DDumper<IDirectDraw> ddrawDumper;''')
    print('''static d3dretrace::D3DDumper<IDirectDraw2> ddraw2Dumper;''')
    print('''static d3dretrace::D3DDumper<IDirectDraw4> ddraw4Dumper;''')
    print('''static d3dretrace::D3DDumper<IDirectDraw7> ddraw7Dumper;''')
    print('''static d3dretrace::D3DDumper<IDirect3DDevice> d3d3Dumper;''')
    print('''static d3dretrace::D3DDumper<IDirect3DDevice2> d3d5Dumper;''')
    print('''static d3dretrace::D3DDumper<IDirect3DDevice3> d3d6Dumper;''')
    print('''static d3dretrace::D3DDumper<IDirect3DDevice7> d3d7Dumper;''')
    print()

    print('struct CBEnumContext {')
    print('    trace::Call &call;')
    print('};')

    print('template <typename S, typename D>')
    print('HRESULT CALLBACK')
    print('EnumAttachedSurfacesCB(S* pSurface, D* pDesc, void* pContext);')

    print('template HRESULT CALLBACK')
    print('EnumAttachedSurfacesCB<IDirectDrawSurface, DDSURFACEDESC>(IDirectDrawSurface*, DDSURFACEDESC*, void*);')
    print('template HRESULT CALLBACK')
    print('EnumAttachedSurfacesCB<IDirectDrawSurface4, DDSURFACEDESC2>(IDirectDrawSurface4*, DDSURFACEDESC2*, void*);')
    print('template HRESULT CALLBACK')
    print('EnumAttachedSurfacesCB<IDirectDrawSurface7, DDSURFACEDESC2>(IDirectDrawSurface7*, DDSURFACEDESC2*, void*);')

    retracer = D3DRetracer()
    retracer.table_name = 'd3dretrace::ddraw_callbacks'
    retracer.retraceApi(api)

    print('template <typename S, typename D>')
    print('using EnumAttachedSurfaces = HRESULT(*)(S *, D *, void *);')

    print('template <typename S, typename D>')
    print('HRESULT CALLBACK')
    print('EnumAttachedSurfacesCB(S* pSurface, D* pDesc, void *pContext) {')
    print('    CBEnumContext* context = static_cast<CBEnumContext*>(pContext);')
    print('    unsigned long long addr = d3dretrace::getEnumSurface();')
    print('    if (addr && pSurface) {')
    print('        trace::Value &val = *new trace::Pointer(static_cast<uintptr_t>(addr));')
    print('        retrace::addObj(context->call, val, pSurface);')
    print('        return DDENUMRET_OK;')
    print('    }')
    print('    return DDENUMRET_CANCEL;')
    print('}')



if __name__ == '__main__':
    main()
