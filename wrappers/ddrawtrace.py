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
        afterCall = None
        callFlags = "trace::FLAG_NONE"

        hWndArg = method.getArgByType(HWND)
        if hWndArg is not None:
            if method.name == "SetCooperativeLevel":
                print(r'    if (!g_hWnd) {')
                print(r'        g_hWnd = hWnd;')
                print(r'    }')
                print(r'    g_windowed = !(dwFlags & (DDSCL_FULLSCREEN|DDSCL_EXCLUSIVE));')

        # Endframe flag
        if interface.name.startswith('IDirectDrawSurface') and method.name in ('Blt', 'BltFast', 'EndScene', 'Flip', 'Unlock', 'ReleaseDC'):
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
        if interface.name.startswith('IDirectDraw') and method.name in ('FLipToGDISurface'):
            print(r'    callFlags = static_cast<trace::Flags>(trace::FLAG_END_FRAME|trace::FLAG_SWAP_RENDERTARGET);')
            callFlags = "callFlags"

        # Clipper negation
        if interface.name.startswith('IDirectDrawSurface'):
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

        if interface.name == 'IDirect3DVertexBuffer7' and method.name == 'ProcessVerticesStrided':
            print('    DWORD dwVertexType = 0;')
            print('    D3DVERTEXBUFFERDESC desc;')
            print('    ZeroMemory(&desc, sizeof(desc));')
            print('    desc.dwSize = sizeof(desc);')
            print('    if (SUCCEEDED(this->GetVertexBufferDesc(&desc))) {')
            print('        dwVertexType = desc.dwFVF;')
            print('    }')

        if method.name == 'Unlock':
            print('    if (_MappedSize && m_pbData) {')
            self.emit_memcpy('(LPBYTE)m_pbData', '_MappedSize')
            print('    }')

        if method.name == 'Lock':
            # Reset _DONOTWAIT flags. Otherwise they may fail, and we have no
            # way to cope with it (other than retry).
            mapFlagsArg = method.getArgByName('dwFlags')
            if mapFlagsArg is not None:
                print(r'    dwFlags &= ~DDLOCK_DONOTWAIT;')
                print(r'    dwFlags |= DDLOCK_WAIT;')

        if interface.name.startswith('IDirectDrawSurface') and method.name == 'SetSurfaceDesc':
            print(r'    if (lpDDSD && (lpDDSD->dwFlags & (DDSD_LPSURFACE)) && lpDDSD->lpSurface) {')
            print(r'        _getMapInfo(_this, NULL, lpDDSD, m_pbData, _MappedSize);')
            print(r'        m_pbData = lpDDSD->lpSurface;')
            print(r'        if (_MappedSize && m_pbData) {')
            self.emit_malloc('(LPBYTE)m_pbData', '_MappedSize')
            self.emit_memcpy('(LPBYTE)m_pbData', '_MappedSize')
            print(r'        }')
            print(r'    }')

        if interface.name.startswith('IDirectDraw') and method.name in ('EnumAttachedSurfaces', 'EnumSurfaces'):
            resultOverride = "_result"
            print('    CBEnumContext context{lpContext, (void*)lpEnumSurfacesCallback, "%s::%s"};' % (interface.name, method.name))

            if method.name == 'EnumAttachedSurfaces':
                print('    _result = _this->EnumAttachedSurfaces(&context, &EnumAttachedSurfacesCB);')
            else:
                print('    _result = _this->EnumSurfaces(dwFlags, lpDDSurfaceDesc, &context, &EnumAttachedSurfacesCB);')


        DllTracer.implementWrapperInterfaceMethodBody(self, interface, base, method, resultOverride = resultOverride, callFlags = callFlags, afterCall = afterCall)

        if interface.name.startswith('IDirectDrawSurface'):
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
            if interface.name.startswith('IDirectDrawSurface'):
                print('    if (SUCCEEDED(_result) && !(dwFlags & DDLOCK_READONLY)) {')
            #elif interface.name.startswith('IDirect3DVertexBuffer'):
            #    print('    if (SUCCEEDED(_result) && !(dwFlags & DDLOCK_NOOVERWRITE)) {')
            else:
                print('    if (SUCCEEDED(_result)) {')
            if interface.name.startswith('IDirectDrawSurface') and method.name == 'Lock':
                print('        _getMapInfo(_this, %s, m_pbData, _MappedSize);' % ', '.join(method.argNames()[:-2]))
            elif interface.name.startswith('IDirect3DVertexBuffer'):
                print('        _getMapInfo(_this, %s, m_pbData, _MappedSize);' % ', '.join(method.argNames()[1:]))
                #print('        if (dwFlags & DDLOCK_DISCARDCONTENTS) {')
                #print('             memset(m_pbData, 0x00, _MappedSize);')
                #print('        }')
            else:
                print('        _getMapInfo(_this, %s, m_pbData, _MappedSize);' % ', '.join(method.argNames()))
            print('    } else {')
            print('        m_pbData = nullptr;')
            print('        _MappedSize = 0;')
            print('    }')

        if interface.name.startswith('IDirectDrawSurface') and method.name == 'SetSurfaceDesc':
            print(r'    if (lpDDSD && (lpDDSD->dwFlags & (DDSD_LPSURFACE)) && lpDDSD->lpSurface) {')
            print(r'        if (_MappedSize && m_pbData) {')
            self.emit_free('(LPBYTE)m_pbData')
            print(r'        }')
            print('        m_pbData = nullptr;')
            print('        _MappedSize = 0;')
            print(r'    }')

if __name__ == '__main__':
    print('#define INITGUID')
    print('#include "d3dimports.hpp"')
    print('#include "trace_writer_local.hpp"')
    print('#include "d3d7size.hpp"')
    print('#include "os.hpp"')
    print()
    print('#include <list>')
    print()

    print('static HWND g_hWnd{0};')
    print('static LPDIRECTDRAWCLIPPER g_clipper = nullptr;')
    print('static bool g_windowed = false;')

    api = API()
    api.addModule(ddraw)

    print('struct CBEnumContext {')
    print('    void *pContext;')
    print('    void *pCallback;')
    print('    std::string name;')
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

    tracer = DDrawTracer()
    tracer.traceApi(api)

    print('template <typename S, typename D>')
    print('using EnumAttachedSurfaces = HRESULT(*)(S *, D *, void *);')

    print('template <typename S, typename D>')
    print('HRESULT CALLBACK')
    print('EnumAttachedSurfacesCB(S* pSurface, D* pDesc, void *pContext) {')
    print('    CBEnumContext* context = static_cast<CBEnumContext*>(pContext);')
    print('    HRESULT hr = DDENUMRET_CANCEL;')

    print('    const char* enumsurfaces_args[4] = { "lpContext", "lpEnumSurfacesCallback", "lpDDSurface", "lpDDSurfaceDescCaps" };')
    print('    const trace::FunctionSig enumsurfaces_sig = { %u, "enumsurfacescallback", 4, enumsurfaces_args };' % tracer.getFunctionSigId())
    print('    unsigned _callcallback = trace::localWriter.beginEnter(&enumsurfaces_sig, trace::FLAG_FAKE);')

    # TODO: serialize surface descriptor as well
    print('    trace::localWriter.beginArg(0);')
    print('    trace::localWriter.writePointer((uintptr_t)context->pContext);')
    print('    trace::localWriter.endArg();')
    print('    trace::localWriter.beginArg(1);')
    print('    trace::localWriter.writePointer((uintptr_t)context->pCallback);')
    print('    trace::localWriter.endArg();')
    print('    trace::localWriter.beginArg(2);')
    print('    trace::localWriter.writePointer((uintptr_t)pSurface);')
    print('    trace::localWriter.endArg();')
    print('    if (pDesc) {')
    print('        trace::localWriter.beginArg(3);')
    print('        trace::localWriter.beginStruct(&_structDDSCAPS_sig);')
    print('        trace::localWriter.writeBitmask(&_bitmaskDWORD31_sig, pDesc->ddsCaps.dwCaps);')
    print('        trace::localWriter.endStruct();')
    print('        trace::localWriter.endArg();')
    print('    }')
    print('    trace::localWriter.endEnter();')
    print('    trace::localWriter.beginLeave(_callcallback);')
    print('    trace::localWriter.beginReturn();')
    print('    trace::localWriter.writeUInt(hr);')
    print('    trace::localWriter.endReturn();')
    print('    trace::localWriter.endLeave();')

    print('    EnumAttachedSurfaces<S, D> callback = reinterpret_cast<EnumAttachedSurfaces<S, D>>(context->pCallback);')
    print('    if (callback) {')
    print('        if constexpr (std::is_same_v<S, IDirectDrawSurface>) {')
    print('            WrapIDirectDrawSurface::_wrap(context->name.c_str(), &pSurface);')
    print('            return callback(pSurface, pDesc, context->pContext);')
    print('        }')
    print('        else if constexpr (std::is_same_v<S, IDirectDrawSurface4>) {')
    print('            WrapIDirectDrawSurface4::_wrap(context->name.c_str(), &pSurface);')
    print('            return callback(pSurface, pDesc, context->pContext);')
    print('        }')
    print('        else if constexpr (std::is_same_v<S, IDirectDrawSurface7>) {')
    print('            WrapIDirectDrawSurface7::_wrap(context->name.c_str(), &pSurface);')
    print('            return callback(pSurface, pDesc, context->pContext);')
    print('        }')
    print('    }')
    print('    return hr;')
    print('}')
