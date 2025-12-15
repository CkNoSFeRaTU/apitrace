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
        #print('static bool g_clipper = nullptr;')
        print('static LPDIRECTDRAWSURFACE7 g_primary = nullptr;')
        print()

        Retracer.retraceApi(self, api)

    def invokeInterfaceMethod(self, interface, method):
        # keep track of the last used device for state dumping
        if interface.name in ('IDirect3DDevice7',):
            if method.name == 'Release':
                print(r'    if (call.ret->toUInt() == 0) {')
                print(r'        d3d7Dumper.unbindDevice(_this);')
                print(r'    }')
            else:
                print(r'    d3d7Dumper.bindDevice(_this);')

        # notify frame has been completed
        # process events after presents
        if interface.name.startswith('IDirectDrawSurface') and method.name in ('Blt', 'EndScene', 'Flip', 'Unlock', 'ReleaseDC'):
            if interface.name in ('IDirectDrawSurface4', 'IDirectDrawSurface7'):
                print(r'    DDSCAPS2 ddsCaps;')
            else:
                print(r'    DDSCAPS ddsCaps;')
            print(r'    if (SUCCEEDED(_this->GetCaps(&ddsCaps)) &&')
            print(r'        (ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE)) {')
            print(r'        retrace::frameComplete(call);')
            print(r'        d3dretrace::processEvents();')
            print(r'    }')
        if interface.name in ('IDirectDrawColorControl', 'IDirectDrawPalette') and method.name in ('SetColorControls', 'SetEntries'):
            print(r'    retrace::frameComplete(call);')
            print(r'    d3dretrace::processEvents();')

        # handle windows
        hWndArg = method.getArgByType(HWND)
        if hWndArg is not None:
            if method.name == "SetCooperativeLevel":
                print(r'    g_hWnd = d3dretrace::createWindow(g_hWnd, g_width ? g_width : 640, g_height ? g_height : 480, \
                        dwFlags & DDSCL_FULLSCREEN ? WS_POPUP | WS_VISIBLE : 0, dwFlags & DDSCL_FULLSCREEN ? WS_EX_APPWINDOW : 0);')
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
                print(r'    if ((ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE) && lpDestRect) {')
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

        Retracer.invokeInterfaceMethod(self, interface, method)

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

        if method.name in ('Lock'):
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

    def extractArg(self, function, arg, arg_type, lvalue, rvalue):
        # Handle DDCREATE_* flags
        if arg.type is DDCREATE_LPGUID:
            print('    if (%s.toArray()) {' % rvalue)
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
    print(r'#include "d3d7size.hpp"')
    api.addModule(ddraw)
    print()
    print('''static d3dretrace::D3DDumper<IDirect3DDevice7> d3d7Dumper;''')
    print()

    retracer = D3DRetracer()
    retracer.table_name = 'd3dretrace::ddraw_callbacks'
    retracer.retraceApi(api)


if __name__ == '__main__':
    main()
