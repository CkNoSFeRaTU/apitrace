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
        resultOverride = None
        callFlags = "trace::FLAG_NONE"

        hWndArg = method.getArgByType(HWND)
        if hWndArg is not None:
            if method.name == "SetCooperativeLevel":
                print(r'    if (!g_hWnd) {')
                print(r'        g_hWnd = hWnd;')
                print(r'    }')
                print(r'    g_windowed = !(dwFlags & (DDSCL_FULLSCREEN|DDSCL_EXCLUSIVE));')

        # Endframe flag
        if interface.name.startswith('IDirectDrawSurface') and method.name in ('Blt', 'EndScene', 'Flip', 'Unlock', 'ReleaseDC'):
            if interface.name in ('IDirectDrawSurface4', 'IDirectDrawSurface7'):
                print(r'    DDSCAPS2 ddsCaps;')
            else:
                print(r'    DDSCAPS ddsCaps;')
            print(r'    trace::Flags callFlags = trace::FLAG_NONE;')
            print(r'    if (SUCCEEDED(_this->GetCaps(&ddsCaps)) && (ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE)) {')
            if method.name == 'Flip':
                print(r'        callFlags = static_cast<trace::Flags>(trace::FLAG_END_FRAME|trace::FLAG_SWAP_RENDERTARGET);')
            else:
                print(r'        callFlags = trace::FLAG_END_FRAME;')
            print(r'    }')
            callFlags = "callFlags"
        if interface.name in ('IDirectDrawColorControl', 'IDirectDrawPalette') and method.name in ('SetColorControls', 'SetEntries'):
            print(r'    trace::Flags callFlags = trace::FLAG_END_FRAME;')
            callFlags = "callFlags"

        # Clipper negation
        if interface.name.startswith("IDirectDrawSurface"):
            if method.name == 'Blt':
                # We shouldn't save coordinates whose depend on current window position to properly handle clipper on retrace
                # So we invoke method earlier to decouple it from data saving in the trace
                print('    _result = _this->Blt(%s);' % ', '.join(method.argNames()))
                resultOverride = "_result"
                # And negate destination rect coordinates by current window position if we are in windowed mode and have attached clipper
                print('    POINT cPt{0, 0};')
                print('    RECT cRect{0, 0, 0, 0};')
                print('    if (g_windowed && g_clipper && lpDestRect && ClientToScreen(g_hWnd, &cPt)) {')
                print('        (*lpDestRect).left -= cPt.x;')
                print('        (*lpDestRect).right -= cPt.x;')
                print('        (*lpDestRect).top -= cPt.y;')
                print('        (*lpDestRect).bottom -= cPt.y;')
                print('    }')
            elif method.name == 'SetClipper':
                if interface.name in ('IDirectDrawSurface4', 'IDirectDrawSurface7'):
                    print(r'    DDSCAPS2 ddsCaps;')
                else:
                    print(r'    DDSCAPS ddsCaps;')
                print(r'    if (SUCCEEDED(_this->GetCaps(&ddsCaps) && (ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE))) {')
                print(r'        g_clipper = %s;' % ', '.join(method.argNames()))
                print(r'    }')

        if method.name == 'Unlock':
            print('    if (_MappedSize && m_pbData) {')
            self.emit_memcpy('(LPBYTE)m_pbData', '_MappedSize')
            print('    }')

        if method.name == 'ReleaseDC':
            print('    HBITMAP hBmpSrc = (HBITMAP)GetCurrentObject(hDC, OBJ_BITMAP);')
            print('    if (hBmpSrc) {')
            print('        BITMAP bm;')
            print('        GetObject(hBmpSrc, sizeof(bm), &bm);')

            print('        BITMAPINFO bmi{ 0 };')
            print('        bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);')
            print('        bmi.bmiHeader.biWidth = bm.bmWidth;')
            print('        bmi.bmiHeader.biHeight = bm.bmHeight;')
            print('        bmi.bmiHeader.biPlanes = bm.bmPlanes;')
            print('        bmi.bmiHeader.biBitCount = bm.bmBitsPixel;')
            print('        bmi.bmiHeader.biCompression = BI_RGB;')

            print('        void* pBits = NULL;')
            print('        HDC mDC = CreateCompatibleDC(hDC);')
            print('        HBITMAP hBmp = CreateDIBSection(mDC, &bmi, DIB_RGB_COLORS, &pBits, NULL, 0);')
            print('        if (mDC && hBmp) {')
            print('            SelectObject(mDC, hBmp);')

            print('            BitBlt(mDC, 0, 0, bm.bmWidth, bm.bmHeight, hDC, 0, 0, SRCCOPY);')

            print('            size_t bitsSize = bm.bmWidth * bm.bmHeight * (bm.bmBitsPixel / 8);')

            print('            const char* bitblt_args[3] = { "dest", "src", "n" };')
            print('            const trace::FunctionSig bitblt_sig = { %u, "bitblt", 3, bitblt_args };' % (self.getFunctionSigId()))

            print('            unsigned _call = trace::localWriter.beginEnter(&bitblt_sig, trace::FLAG_FAKE);')
            print('            trace::localWriter.beginArg(0);')
            print('            trace::localWriter.writePointer((uintptr_t)hDC);')
            print('            trace::localWriter.endArg();')
            print('            trace::localWriter.beginArg(1);')
            print('            trace::localWriter.writeBlob(pBits, bitsSize);')
            print('            trace::localWriter.endArg();')
            print('            trace::localWriter.beginArg(2);')
            print('            trace::localWriter.writeUInt(bitsSize);')
            print('            trace::localWriter.endArg();')
            print('            trace::localWriter.endEnter();')
            print('            trace::localWriter.beginLeave(_call);')
            print('            trace::localWriter.endLeave();')

            print('            DeleteObject(hBmp);')
            print('            DeleteDC(mDC);')
            print('        }')
            print('    }')

        DllTracer.implementWrapperInterfaceMethodBody(self, interface, base, method, resultOverride = resultOverride, callFlags = callFlags)

        if interface.name.startswith("IDirectDrawSurface"):
            if method.name == 'Blt':
                # We need to restore destination rect to original state if we messed with it so application don't become confused on subsequent calls
                print('    if (g_windowed && g_clipper && lpDestRect && (cPt.x || cPt.y)) {')
                print('        (*lpDestRect).left += cPt.x;')
                print('        (*lpDestRect).right += cPt.x;')
                print('        (*lpDestRect).top += cPt.y;')
                print('        (*lpDestRect).bottom += cPt.y;')
                print('    }')

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
    print('static LPDIRECTDRAWCLIPPER g_clipper = nullptr;')
    print('static bool g_windowed = false;')

    api = API()
    api.addModule(ddraw)

    tracer = DDrawTracer()
    tracer.traceApi(api)
