##########################################################################
#
# Copyright 2008-2015 VMware, Inc.
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


from dlltrace import DllTracer
from specs.stdapi import API
from specs.d3d import ddraw, interfaces, HWND


class DDrawTracer(DllTracer):
    # FIXME: emit fake memcpy calls for IDirectDrawSurface7::EnumAttachedSurfaces

    # FIXME: wrap objects passed to IDirectDrawSurface7::EnumAttachedSurfaces
    # callback -- we don't really care for tracing these calls, but we do want
    # to trace everything done inside the callback.

    # FIXME: GetDC & ReleaseDC is often used by applications with some interop like GDI's BitBlt.
    # We should save result on ReleaseDC in trace and then on retrace use Lock, copy/blit saved data and Unlock instead.
    # Heck, almost all samples in DX7SDK has been using and so encouraging this bad practice...
    def enumWrapperInterfaceVariables(self, interface):
        variables = DllTracer.enumWrapperInterfaceVariables(self, interface)

        # Add additional members to track locks
        if interface.getMethodByName('Lock') is not None:
            variables += [
                ('size_t', '_MappedSize', '0'),
                ('VOID *', 'm_pbData', '0'),
            ]

        return variables
    def implementWrapperInterfaceMethodBody(self, interface, base, method):
        beforeCall = None

        # Hack to cooperate with clipper.
        hWndArg = method.getArgByType(HWND)
        if hWndArg is not None:
            if method.name == "SetCooperativeLevel":
                print(r'    if (!g_hWnd) {')
                print(r'        g_hWnd = hWnd;')
                print(r'    }')
                print(r'    g_windowed = !(dwFlags & (DDSCL_FULLSCREEN|DDSCL_EXCLUSIVE));')

        def restoreState():
            print('    if (g_windowed && g_clipper && lpDestRect) {')
            print('        (*lpDestRect).left += cRect.left;')
            print('        (*lpDestRect).right += cRect.left;')
            print('        (*lpDestRect).top += cRect.top;')
            print('        (*lpDestRect).bottom += cRect.top;')
            print('    }')

        if interface.name.startswith("IDirectDrawSurface"):
            if method.name == 'Blt':
                print('    RECT cRect;')
                # We shouldn't save coordinates whose depend on window position to properly handle clipper on retrace
                print('    if (g_windowed && g_clipper && lpDestRect && GetWindowRect(g_hWnd, &cRect)) {')
                print('        (*lpDestRect).left -= cRect.left;')
                print('        (*lpDestRect).right -= cRect.left;')
                print('        (*lpDestRect).top -= cRect.top;')
                print('        (*lpDestRect).bottom -= cRect.top;')
                print('    }')
                # Restore to original state before the call
                beforeCall = restoreState
            elif method.name == 'SetClipper':
                if interface.name in ('IDirectDrawSurface4', 'IDirectDrawSurface7'):
                    print(r'    DDSCAPS2 ddsCaps;')
                else:
                    print(r'    DDSCAPS ddsCaps;')
                print(r'    if (SUCCEEDED(_this->GetCaps(&ddsCaps) && (ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE))) {')
                print(r'        g_clipper = true;')
                print(r'    }')

        if method.name == 'Unlock':
            print('    if (_MappedSize && m_pbData) {')
            if method.name == 'Unlock':
                self.emit_memcpy('(LPBYTE)m_pbData', '_MappedSize')
            print('    }')

        DllTracer.implementWrapperInterfaceMethodBody(self, interface, base, method, beforeCall = beforeCall)

        if method.name == 'Lock':
            # FIXME: handle recursive locks
            if interface.name.startswith("IDirectDrawSurface") and method.name == 'Lock':
                print('    if (SUCCEEDED(_result) && !(dwFlags & DDLOCK_READONLY)) {')
            else:
                print('    if (SUCCEEDED(_result)) {')
            if interface.name.startswith("IDirectDrawSurface") and method.name == 'Lock':
                print('        _getMapInfo(_this, %s, m_pbData, _MappedSize);' % ', '.join(method.argNames()[:-2]))
            elif interface.name.startswith("IDirect3DVertexBuffer"):
                print('        _getMapInfo(_this, %s, m_pbData, _MappedSize);' % ', '.join(method.argNames()[1:]))
            else:
                print('        _getMapInfo(_this, %s, m_pbData, _MappedSize);' % ', '.join(method.argNames()))
            print('    } else {')
            print('        m_pbData = nullptr;')
            print('        _MappedSize = 0;')
            print('    }')

if __name__ == '__main__':
    print('#define INITGUID')
    print('#include "d3dimports.hpp"')
    print('#include "trace_writer_local.hpp"')
    print('#include "d3d7size.hpp"')
    print('#include "os.hpp"')
    print()

    print('static HWND g_hWnd{0};')
    print('static bool g_clipper = false;')
    print('static bool g_windowed = false;')

    api = API()
    api.addModule(ddraw)

    fake_function_names = [
        'GetCurrentObject',
    ]

    # Declare helper functions to emit fake function calls into the trace
    for function in api.getAllFunctions():
        if function.name in fake_function_names:
            print(function.prototype('_fake_' + function.name) + ';')
        print()

    tracer = DDrawTracer()
    tracer.traceApi(api)
