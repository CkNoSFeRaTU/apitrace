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
from specs.stdapi import API, Pointer, Collector, Struct
from specs.winapi import GUID, CLSID, REFCLSID, HMONITOR
from specs.d3d import ddraw, interfaces, HWND, D3DDEVICEDESC2, D3DDEVICEDESC5, D3DDEVICEDESC6, D3DDEVICEDESC7
from specs.d3dtypes import D3DINSTRUCTION, D3DOPCODE, D3DBRANCH, D3DLINE, D3DMATRIXLOAD, D3DMATRIXMULTIPLY, D3DPOINT, D3DPROCESSVERTICES, D3DSPAN, D3DSTATE, D3DSTATUS, D3DTEXTURELOAD, D3DTRIANGLE
from specs.d3dtypes import D3DPROCESSVERTICESFlags, D3DTRIFLAG, D3DTRANSFORMSTATEVALUE
from specs.ddraw import DDSURFACEDESC, DDSURFACEDESC2, DDPIXELFORMAT, DirectDrawEnumSurfacesFlags, DirectDrawEnumDisplayModesFlags
from trace import ComplexValueSerializer


class DDrawTracer(DllTracer):
    def enumWrapperInterfaceVariables(self, interface):
        variables = DllTracer.enumWrapperInterfaceVariables(self, interface)

        # Add additional members to track locks
        if interface.getMethodByName('Lock') is not None:
            variables += [
                ('size_t', '_MappedSize', '0'),
                ('VOID *', 'm_pbData', '0'),
            ]

        if interface.name == "IDirect3DDevice2":
            variables += [
                ('D3DVERTEXTYPE', '_LastVertexType', 'D3DVT_VERTEX'),
            ]

        if interface.name == "IDirect3DDevice3":
            variables += [
                ('DWORD', '_LastVertexType', '0'),
            ]

        return variables

    def traceFunctionImplBody(self, function):
        callFlags = "trace::FLAG_NONE"
        resultOverride = None

        if function.name.startswith('DirectDrawEnumerate'):
            print('    if (lpCallback == nullptr)')
            print('        return DDERR_INVALIDPARAMS;')
            if function.name == 'DirectDrawEnumerateA':
                print('    EnumDirectDrawContextA context;')
                print('    LPDDENUMCALLBACKA callback = (LPDDENUMCALLBACKA)&EnumDirectDrawACallback;')
                print('    _result = _DirectDrawEnumerateA(callback, &context);')
            if function.name == 'DirectDrawEnumerateW':
                print('    EnumDirectDrawContextW context;')
                print('    LPDDENUMCALLBACKW callback = (LPDDENUMCALLBACKW)&EnumDirectDrawWCallback;')
                print('    _result = _DirectDrawEnumerateW(callback, &context);')
            if function.name == 'DirectDrawEnumerateExA':
                print('    EnumDirectDrawContextA context;')
                print('    LPDDENUMCALLBACKEXA callback = (LPDDENUMCALLBACKEXA)&EnumDirectDrawExACallback;')
                print('    _result = _DirectDrawEnumerateExA(callback, &context, dwFlags);')
            if function.name == 'DirectDrawEnumerateExW':
                print('    EnumDirectDrawContextW context;')
                print('    LPDDENUMCALLBACKEXW callback = (LPDDENUMCALLBACKEXW)&EnumDirectDrawExWCallback;')
                print('    _result = _DirectDrawEnumerateExW(callback, &context, dwFlags);')
            resultOverride = "_result"

        DllTracer.traceFunctionImplBody(self, function, resultOverride = resultOverride, callFlags = callFlags)

        if function.name.startswith('DirectDrawEnumerate'):
            print('    if (_result != DD_OK)')
            print('        return _result;')
            print('')
            print('    for (const auto& result : context.result) {')
            if function.name.startswith('DirectDrawEnumerateEx'):
                print('        if (lpCallback(result.guid, result.deviceName, result.deviceDesc, lpContext, (HMONITOR)result.monitor) != D3DENUMRET_OK)')
                print('            break;')
            else:
                print('        if (lpCallback(result.guid, result.deviceName, result.deviceDesc, lpContext) != D3DENUMRET_OK)')
                print('            break;')
            print('    }')
            print('')
            print('    const char* enum_args[6] = { "origin", "originName", "resultCount", "result", "lpCallback", "lpContext" };')
            print('    const trace::FunctionSig enum_sig = { %u, "DirectDrawEnumerateCallbacks", 6, enum_args };' % self.getFunctionSigId())
            if function.name.startswith('DirectDrawEnumerateEx'):
                print('    const char* enum_result_members[4] = { "guid", "deviceName", "deviceDesc", "monitor" };')
                print('    const trace::StructSig enum_result_sig = { %u, "enumResult", 4, enum_result_members };' % self.getFunctionSigId())
            else:
                print('    const char* enum_result_members[3] = { "guid", "deviceName", "deviceDesc" };')
                print('    const trace::StructSig enum_result_sig = { %u, "enumResult", 3, enum_result_members };' % self.getFunctionSigId())
            print('    unsigned _callcallback = trace::localWriter.beginEnter(&enum_sig, trace::FLAG_FAKE);')
            print('')
            print('    int count = 0;')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeNull();')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeString("%s");' % (function.name))
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeSInt(context.result.size());')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.beginArray(context.result.size());')
            print('    for (const auto& result : context.result) {')
            print('        trace::localWriter.beginStruct(&enum_result_sig);')
            tracer.serializeValue(Pointer(CLSID), "result.guid");
            if function.name == 'DirectDrawEnumerateW' or function.name == 'DirectDrawEnumerateExW':
                print('        trace::localWriter.writeWString(result.deviceDesc);')
                print('        trace::localWriter.writeWString(result.deviceName);')
            else:
                print('        trace::localWriter.writeString(result.deviceDesc);')
                print('        trace::localWriter.writeString(result.deviceName);')
            if function.name.startswith('DirectDrawEnumerateEx'):
                tracer.serializeValue(HMONITOR, "result.monitor");
            print('        trace::localWriter.endStruct();')
            print('        delete []result.deviceDesc;')
            print('        delete []result.deviceName;')
            print('    }')
            print('    trace::localWriter.endArray();')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpContext);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpCallback);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.endEnter();')
            print('    trace::localWriter.beginLeave(_callcallback);')
            print('    trace::localWriter.endLeave();')

    def implementWrapperInterfaceMethod(self, interface, base, method):
        beforeUnwrap = None

        # (sic!) Half-Life WON does ProcessVerticies before unlocking source buffer
        if interface.name == 'IDirect3DVertexBuffer' and method.name == 'ProcessVertices':
            def bunwrap():
                print('    if (lpSrcBuffer != nullptr && !disableCopies) {')
                print('        WrapIDirect3DVertexBuffer* buffer = reinterpret_cast<WrapIDirect3DVertexBuffer*>(lpSrcBuffer);')
                print('        if (buffer->_MappedSize > 0 && buffer->m_pbData)')
                self.emit_memcpy('(LPBYTE)buffer->m_pbData', 'buffer->_MappedSize')
                print('    }')

            beforeUnwrap = bunwrap

        DllTracer.implementWrapperInterfaceMethod(self, interface, base, method, beforeUnwrap = beforeUnwrap)

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
            print('            const trace::FunctionSig bitblt_sig = { %u, "BitBlt", 3, bitblt_args };' % (self.getFunctionSigId()))

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
            print('    if (!disableCopies && _MappedSize > 0 && m_pbData) {')
            self.emit_memcpy('(LPBYTE)m_pbData', '_MappedSize')
            print('    }')

        if interface.name == "IDirect3DExecuteBuffer" and method.name == 'Lock':
            print('    _result = _this->Lock(%s);' % ', '.join(method.argNames()))
            resultOverride = "_result"
        elif method.name == 'Lock':
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
            print(r'        if (!disableCopies && _MappedSize > 0 && m_pbData) {')
            self.emit_malloc('(LPBYTE)m_pbData', '_MappedSize')
            self.emit_memcpy('(LPBYTE)m_pbData', '_MappedSize')
            print(r'        }')
            print(r'    }')

        # As application can do operations on received object inside of callbacks which we need to wrap but
        # localWriter don't support interleaving we have to finish writing this call information so these objects
        # not appear out of thin air. And only after that generate fake callback functions with what happened in callbacks.
        # So we have no choice but assume these calls are always succeed and write DD_OK return code in the trace.
        if interface.name.startswith('IDirectDraw') and method.name in ('EnumAttachedSurfaces', 'EnumSurfaces'):
            print('    if (lpEnumSurfacesCallback == nullptr)')
            print('        return DDERR_INVALIDPARAMS;')
            print('    _result = DD_OK;')
            resultOverride = "_result"

        if interface.name.startswith('IDirectDraw') and method.name == 'EnumDisplayModes':
            print('    if (lpEnumModesCallback == nullptr)')
            print('        return DDERR_INVALIDPARAMS;')
            if interface.name in ('IDirectDraw4', 'IDirectDraw7'):
                print('    EnumDisplayModesContext<DDSURFACEDESC2> context;')
                print('    LPDDENUMMODESCALLBACK2 callback = (LPDDENUMMODESCALLBACK2)&EnumDisplayModesCallback<DDSURFACEDESC2>;')
            else:
                print('    EnumDisplayModesContext<DDSURFACEDESC> context;')
                print('    LPDDENUMMODESCALLBACK callback = (LPDDENUMMODESCALLBACK)&EnumDisplayModesCallback<DDSURFACEDESC>;')
            print('    _result = _this->EnumDisplayModes(dwFlags, lpDDSurfaceDesc, &context, callback);')
            resultOverride = "_result"

        if interface.name.startswith('IDirect3D') and method.name == 'EnumDevices':
            print('    if (lpEnumDevicesCallback == nullptr)')
            print('        return DDERR_INVALIDPARAMS;')
            if interface.name == 'IDirect3D':
                print('    EnumDevicesContext<D3DDEVICEDESC2> context;')
                print('    LPD3DENUMDEVICESCALLBACK callback = (LPD3DENUMDEVICESCALLBACK)&EnumDevicesCallback<D3DDEVICEDESC2>;')
            elif interface.name == 'IDirect3D2':
                print('    EnumDevicesContext<D3DDEVICEDESC5> context;')
                print('    LPD3DENUMDEVICESCALLBACK callback = (LPD3DENUMDEVICESCALLBACK)&EnumDevicesCallback<D3DDEVICEDESC5>;')
            elif interface.name == 'IDirect3D3':
                print('    EnumDevicesContext<D3DDEVICEDESC6> context;')
                print('    LPD3DENUMDEVICESCALLBACK callback = (LPD3DENUMDEVICESCALLBACK)&EnumDevicesCallback<D3DDEVICEDESC6>;')
            elif interface.name == 'IDirect3D7':
                print('    EnumDevicesContext<D3DDEVICEDESC7> context;')
                print('    LPD3DENUMDEVICESCALLBACK7 callback = (LPD3DENUMDEVICESCALLBACK7)&EnumDevicesCallback7;')
            print('    _result = _this->EnumDevices(callback, &context);')
            resultOverride = "_result"

        if interface.name.startswith('IDirect3DDevice') and method.name == 'EnumTextureFormats':
            if interface.name == 'IDirect3DDevice' or interface.name == 'IDirect3DDevice2':
                print('    if (lpD3DEnumTextureProc == nullptr)')
                print('        return DDERR_INVALIDPARAMS;')
                print('    EnumTextureFormatsContext context;')
                print('    LPD3DENUMTEXTUREFORMATSCALLBACK callback = (LPD3DENUMTEXTUREFORMATSCALLBACK)&EnumTextureFormatsCallback;')
            else:
                print('    if (lpD3DEnumPixelProc == nullptr)')
                print('        return DDERR_INVALIDPARAMS;')
                print('    EnumPixelFormatsContext context;')
                print('    LPD3DENUMPIXELFORMATSCALLBACK callback = (LPD3DENUMPIXELFORMATSCALLBACK)&EnumPixelFormatsCallback;')
            print('    _result = _this->EnumTextureFormats(callback, &context);')
            resultOverride = "_result"

        if interface.name.startswith('IDirect3D') and method.name == 'EnumZBufferFormats':
            print('    if (lpEnumCallback == nullptr)')
            print('        return DDERR_INVALIDPARAMS;')
            print('    EnumZBufferFormatsContext context;')
            print('    LPD3DENUMPIXELFORMATSCALLBACK callback = (LPD3DENUMPIXELFORMATSCALLBACK)&EnumZBufferFormatsCallback;')
            print('    _result = _this->EnumZBufferFormats(riidDevice, callback, &context);')
            resultOverride = "_result"

        if interface.name == 'IDirect3DDevice2' and method.name == 'Begin':
            print('    _LastVertexType = d3dvtVertexType;')

        if interface.name == 'IDirect3DDevice3' and method.name == 'Begin':
            print('    _LastVertexType = dwVertexTypeDesc;')

        if interface.name == 'IDirect3DDevice' and method.name == 'Execute':
            print(r'    size_t instructionCount = 0;');
            print(r'    if (%s != nullptr) {' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'        D3DEXECUTEDATA data;')
            print(r'        ZeroMemory(&data, sizeof(data));')
            print(r'        data.dwSize = sizeof(data);')
            print(r'        if (SUCCEEDED(%s->GetExecuteData(&data))) {' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'            D3DEXECUTEBUFFERDESC desc;')
            print(r'            ZeroMemory(&desc, sizeof(desc));')
            print(r'            desc.dwSize = sizeof(desc);')
            print(r'            if (SUCCEEDED(%s->Lock(&desc))) {' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'                uint8_t* buf = (uint8_t*)desc.lpData;')
            print(r'                D3DSTATUS status = data.dsStatus;')
            print(r'                if (buf != nullptr) {')
            print(r'                    uint8_t* ptr = buf + data.dwInstructionOffset;')
            # Sadly can't rely on data.dwInstructionLength as some games send garbage there
            print(r'                    bool doParsing = true;')
            print(r'                    while (doParsing) {')
            print(r'                        instructionCount++;')
            print(r'                        D3DINSTRUCTION* instruction = reinterpret_cast<D3DINSTRUCTION*>(ptr);')
            print(r'                        ptr += sizeof(D3DINSTRUCTION);')
            print(r'                        uint8_t* operation = ptr;')
            print(r'                        if (instruction->bOpcode == D3DOP_EXIT)')
            print(r'                            break;')
            print(r'                        switch (instruction->bOpcode) {')
            print(r'                        case D3DOP_BRANCHFORWARD: {')
            print(r'                            D3DBRANCH* branch = reinterpret_cast<D3DBRANCH*>(operation);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DBRANCH& b = branch[i];')
            print(r'                                bool masked = (data.dsStatus.dwStatus & b.dwMask) == b.dwValue;')
            print(r'                                if (b.bNegate)')
            print(r'                                    masked = !masked;')
            print(r'                                if (masked && b.dwOffset) {')
            print(r'                                    ptr = reinterpret_cast<uint8_t*>(instruction) + branch->dwOffset;')
            print(r'                                    break;')
            print(r'                                }')
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_SETSTATUS: {')
            print(r'                            D3DSTATUS* status = reinterpret_cast<D3DSTATUS*>(operation);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                data.dsStatus = status[i];')
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        default: {')
            print(r'                            ptr += instruction->bSize * instruction->wCount;')
            print(r'                            break;')
            print(r'                        }}')
            print(r'                    }')
            print(r'                    data.dsStatus = status;')

            print(r'                    const char* executebufferdump_args[2] = { "instructionsCount", "instructions" };')
            print(r'                    const trace::FunctionSig executebufferdump_sig = { %u, "ExecuteBufferDump", 2, executebufferdump_args };' % self.getFunctionSigId())
            print(r'                    const char* instruction_members[2] = { "instruction", "operations" };')
            print(r'                    const trace::StructSig instruction_sig = { %u, "instruction", 2, instruction_members };' % self.getFunctionSigId())
            print(r'                    unsigned _executebuffer = trace::localWriter.beginEnter(&executebufferdump_sig, trace::FLAG_FAKE);')
            print(r'                    trace::localWriter.beginArg(0);')
            print(r'                    trace::localWriter.writeUInt(instructionCount);')
            print(r'                    trace::localWriter.endArg();')
            print(r'                    trace::localWriter.beginArg(1);')
            print(r'                    trace::localWriter.beginArray(instructionCount);')

            print(r'                    ptr = buf + data.dwInstructionOffset;')
            print(r'                    while (true) {')
            print(r'                        D3DINSTRUCTION* instruction = reinterpret_cast<D3DINSTRUCTION*>(ptr);')
            print(r'                        ptr += sizeof(D3DINSTRUCTION);')
            print(r'                        uint8_t* operation = ptr;')

            print(r'                        trace::localWriter.beginStruct(&instruction_sig);')
            tracer.serializeValue(Pointer(D3DINSTRUCTION), "instruction");

            print(r'                        if (instruction->bOpcode == D3DOP_EXIT) {')
            print(r'                            trace::localWriter.beginArray(0);')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            trace::localWriter.endStruct();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        switch (instruction->bOpcode) {')
            print(r'                        case D3DOP_BRANCHFORWARD: {')
            print(r'                            D3DBRANCH* branch = reinterpret_cast<D3DBRANCH*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DBRANCH& b = branch[i];')
            tracer.serializeValue(Pointer(D3DBRANCH), "&b");
            print(r'                                bool masked = (data.dsStatus.dwStatus & b.dwMask) == b.dwValue;')
            print(r'                                if (b.bNegate)')
            print(r'                                    masked = !masked;')
            print(r'                                if (masked && b.dwOffset) {')
            print(r'                                    ptr = reinterpret_cast<uint8_t*>(instruction) + branch->dwOffset;')
            print(r'                                    break;')
            print(r'                                }')
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_LINE: {')
            print(r'                            D3DLINE* line = reinterpret_cast<D3DLINE*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DLINE& l = line[i];')
            tracer.serializeValue(Pointer(D3DLINE), "&l");
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_MATRIXLOAD: {')
            print(r'                            D3DMATRIXLOAD* matrixLoad = reinterpret_cast<D3DMATRIXLOAD*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DMATRIXLOAD& ml = matrixLoad[i];')
            tracer.serializeValue(Pointer(D3DMATRIXLOAD), "&ml");
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_MATRIXMULTIPLY: {')
            print(r'                            D3DMATRIXMULTIPLY* matrixLoad = reinterpret_cast<D3DMATRIXMULTIPLY*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DMATRIXMULTIPLY& mm = matrixLoad[i];')
            tracer.serializeValue(Pointer(D3DMATRIXMULTIPLY), "&mm");
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_POINT: {')
            print(r'                            D3DPOINT* point = reinterpret_cast<D3DPOINT*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DPOINT& p = point[i];')
            tracer.serializeValue(Pointer(D3DPOINT), "&p");
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_PROCESSVERTICES: {')
            print(r'                            D3DPROCESSVERTICES* processvertices = reinterpret_cast<D3DPROCESSVERTICES*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DPROCESSVERTICES& pv = processvertices[i];')
            tracer.serializeValue(Pointer(D3DPROCESSVERTICES), "&pv");
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_SETSTATUS: {')
            print(r'                            D3DSTATUS* status = reinterpret_cast<D3DSTATUS*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DSTATUS& s = status[i];')
            tracer.serializeValue(Pointer(D3DSTATUS), "&s");
            print(r'                                data.dsStatus = s;')
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_SPAN: {')
            print(r'                            D3DSPAN* span = reinterpret_cast<D3DSPAN*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DSPAN& s = span[i];')
            tracer.serializeValue(Pointer(D3DSPAN), "&s");
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_STATELIGHT:')
            print(r'                        case D3DOP_STATERENDER:')
            print(r'                        case D3DOP_STATETRANSFORM: {')
            print(r'                            D3DSTATE* state = reinterpret_cast<D3DSTATE*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DSTATE& s = state[i];')
            print(r'                                DWORD dwLightStateType = s.dlstLightStateType;')
            print(r'                                DWORD dwRenderStateType = s.drstRenderStateType;')
            print(r'                                DWORD dwTransformStateType = s.dtstTransformStateType;')
            tracer.serializeValue(Pointer(D3DSTATE), "&s");
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_TEXTURELOAD: {')
            print(r'                            D3DTEXTURELOAD* textureLoad = reinterpret_cast<D3DTEXTURELOAD*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DTEXTURELOAD& tl = textureLoad[i];')
            tracer.serializeValue(Pointer(D3DTEXTURELOAD), "&tl");
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_TRIANGLE: {')
            print(r'                            D3DTRIANGLE* triangle = reinterpret_cast<D3DTRIANGLE*>(operation);')
            print(r'                            trace::localWriter.beginArray(instruction->wCount);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DTRIANGLE& t = triangle[i];')
            tracer.serializeValue(Pointer(D3DTRIANGLE), "&t");
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        default: {')
            print(r'                            os::log("apitrace: warning: Unknown execute buffer opcode: ''%d''\\n", instruction->bOpcode);')
            print(r'                            trace::localWriter.beginArray(0);')
            print(r'                            trace::localWriter.endArray();')
            print(r'                            doParsing = false;')
            print(r'                            break;')
            print(r'                        }}')
            print(r'                        trace::localWriter.endStruct();')
            print(r'                    }')
            print(r'                    trace::localWriter.endArray();')
            print(r'                    trace::localWriter.endArg();')
            print(r'                    trace::localWriter.endEnter();')
            print(r'                    trace::localWriter.beginLeave(_executebuffer);')
            print(r'                    trace::localWriter.endLeave();')
            print(r'                }')
            print(r'                %s->Unlock();' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'            }')
            print(r'        }')
            print(r'    }')

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
            elif interface.name.startswith('IDirect3DVertexBuffer'):
                print('    if (SUCCEEDED(_result) && !(dwFlags & DDLOCK_READONLY)) {')
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
            print('    if (lpDDSD && (lpDDSD->dwFlags & (DDSD_LPSURFACE)) && lpDDSD->lpSurface) {')
            print('        if (!disableCopies && _MappedSize && m_pbData) {')
            self.emit_free('(LPBYTE)m_pbData')
            print('        }')
            print('        m_pbData = nullptr;')
            print('        _MappedSize = 0;')
            print('    }')

        if interface.name.startswith('IDirectDraw') and method.name in ('EnumAttachedSurfaces', 'EnumSurfaces'):
            print('    if (_result != D3D_OK)')
            print('        return _result;')
            if interface.name == 'IDirectDraw4' or interface.name == 'IDirectDrawSurface4':
                print('    EnumSurfacesContext<IDirectDrawSurface4, DDSURFACEDESC2> context;')
            elif interface.name == 'IDirectDraw7' or interface.name == 'IDirectDrawSurface7':
                print('    EnumSurfacesContext<IDirectDrawSurface7, DDSURFACEDESC2> context;')
            else:
                print('    EnumSurfacesContext<IDirectDrawSurface, DDSURFACEDESC> context;')

            if interface.name == 'IDirectDraw4' or interface.name == 'IDirectDrawSurface4':
                print('    LPDDENUMSURFACESCALLBACK2 callback = (LPDDENUMSURFACESCALLBACK2)&EnumSurfacesCallback<IDirectDrawSurface4, DDSURFACEDESC2>;')
            elif interface.name == 'IDirectDraw7' or interface.name == 'IDirectDrawSurface7':
                print('    LPDDENUMSURFACESCALLBACK7 callback = (LPDDENUMSURFACESCALLBACK7)&EnumSurfacesCallback<IDirectDrawSurface7, DDSURFACEDESC2>;')
            else:
                print('    LPDDENUMSURFACESCALLBACK callback = (LPDDENUMSURFACESCALLBACK)&EnumSurfacesCallback<IDirectDrawSurface, DDSURFACEDESC>;')
            if method.name == 'EnumAttachedSurfaces':
                print('    _result = _this->EnumAttachedSurfaces(&context, callback);')
            else:
                print('    _result = _this->EnumSurfaces(dwFlags, lpDDSurfaceDesc, &context, callback);')
            print('    if (_result != DD_OK)')
            print('        return _result;')
            print('')
            if interface.name == 'IDirectDraw' or interface.name == 'IDirectDraw4' or interface.name == 'IDirectDraw7':
                print('    const char* enum_args[8] = { "origin", "originName", "resultCount", "result", "dwFlags", "lpDDSurfaceDesc", "lpContext", "lpEnumSurfacesCallback" };')
                print('    const trace::FunctionSig enum_sig = { %u, "EnumSurfacesCallbacks", 8, enum_args };' % self.getFunctionSigId())
            else:
                print('    const char* enum_args[6] = { "origin", "originName", "resultCount", "result", "lpContext", "lpEnumSurfacesCallback" };')
                print('    const trace::FunctionSig enum_sig = { %u, "EnumSurfacesCallbacks", 6, enum_args };' % self.getFunctionSigId())
            print('    const char* enum_result_members[2] = { "lpDDSurface", "lpDDSurfaceDesc" };')
            print('    const trace::StructSig enum_result_sig = { %u, "enumResult", 2, enum_result_members };' % self.getFunctionSigId())
            print('    unsigned _callcallback = trace::localWriter.beginEnter(&enum_sig, trace::FLAG_FAKE);')
            print('')
            print('    int count = 0;')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)_this);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeString("%s::%s");' % (interface.name, method.name))
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeSInt(context.result.size());')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.beginArray(context.result.size());')
            print('    for (const auto& result : context.result) {')
            print('        trace::localWriter.beginStruct(&enum_result_sig);')
            print('        trace::localWriter.writePointer((uintptr_t)result.surface);')
            if interface.name in ('IDirectDraw4', 'IDirectDrawSurface4', 'IDirectDraw7', 'IDirectDrawSurface7'):
                tracer.serializeValue(Pointer(DDSURFACEDESC2), "result.desc");
            else:
                tracer.serializeValue(Pointer(DDSURFACEDESC), "result.desc");
            print('        trace::localWriter.endStruct();')
            print('    }')
            print('    trace::localWriter.endArray();')
            print('    trace::localWriter.endArg();')
            if interface.name == 'IDirectDraw' or interface.name == 'IDirectDraw4' or interface.name == 'IDirectDraw7':
                print('    trace::localWriter.beginArg(count++);')
                tracer.serializeValue(DirectDrawEnumSurfacesFlags, "dwFlags");
                print('    trace::localWriter.endArg();')
                print('    trace::localWriter.beginArg(count++);')
                if interface.name == 'IDirectDraw':
                    tracer.serializeValue(Pointer(DDSURFACEDESC), "lpDDSurfaceDesc");
                else:
                    tracer.serializeValue(Pointer(DDSURFACEDESC2), "lpDDSurfaceDesc");
                print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpContext);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpEnumSurfacesCallback);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.endEnter();')
            print('    trace::localWriter.beginLeave(_callcallback);')
            print('    trace::localWriter.endLeave();')
            print('')
            print('    bool clean = false;')
            print('    for (const auto& result : context.result) {')
            print('        if (clean) {')
            print('            if (result.surface != nullptr)')
            print('                 result.surface->Release();')
            print('            delete result.desc;')
            print('            continue;')
            print('        }')
            if interface.name == 'IDirectDraw4' or interface.name == 'IDirectDrawSurface4':
                print('        IDirectDrawSurface4 *pSurface = result.surface;')
                print('        WrapIDirectDrawSurface4::_wrap(__FUNCTION__, &pSurface);')
            elif interface.name == 'IDirectDraw7' or interface.name == 'IDirectDrawSurface7':
                print('        IDirectDrawSurface7 *pSurface = result.surface;')
                print('        WrapIDirectDrawSurface7::_wrap(__FUNCTION__, &pSurface);')
            else:
                print('        IDirectDrawSurface *pSurface = result.surface;')
                print('        WrapIDirectDrawSurface::_wrap(__FUNCTION__, &pSurface);')
            print('        if (lpEnumSurfacesCallback(pSurface, result.desc, lpContext) != DDENUMRET_OK)')
            print('            clean = true;')
            print('        delete result.desc;')
            print('    }')
            print('')

        if interface.name.startswith('IDirectDraw') and method.name == 'EnumDisplayModes':
            print('    if (_result != DD_OK)')
            print('        return _result;')
            print('')
            print('    for (const auto& result : context.result) {')
            print('        if (lpEnumModesCallback(result.desc, lpContext) != DDENUMRET_OK)')
            print('            break;')
            print('    }')
            print('')
            print('    const char* enum_args[8] = { "origin", "originName", "resultCount", "result", "dwFlags", "lpDDSurfaceDesc", "lpContext", "lpEnumModesCallback" };')
            print('    const trace::FunctionSig enum_sig = { %u, "EnumDisplayModesCallbacks", 8, enum_args };' % self.getFunctionSigId())
            print('    const char* enum_result_members[1] = { "lpDDSurfaceDesc" };')
            print('    const trace::StructSig enum_result_sig = { %u, "enumResult", 1, enum_result_members };' % self.getFunctionSigId())
            print('    unsigned _callcallback = trace::localWriter.beginEnter(&enum_sig, trace::FLAG_FAKE);')
            print('')
            print('    int count = 0;')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)_this);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeString("%s::%s");' % (interface.name, method.name))
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeSInt(context.result.size());')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.beginArray(context.result.size());')
            print('    for (const auto& result : context.result) {')
            print('        trace::localWriter.beginStruct(&enum_result_sig);')
            if interface.name in ('IDirectDraw4', 'IDirectDraw7'):
                tracer.serializeValue(Pointer(DDSURFACEDESC2), "result.desc");
            else:
                tracer.serializeValue(Pointer(DDSURFACEDESC), "result.desc");
            print('        trace::localWriter.endStruct();')
            print('        delete result.desc;')
            print('    }')
            print('    trace::localWriter.endArray();')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            tracer.serializeValue(DirectDrawEnumDisplayModesFlags, "dwFlags");
            print('    trace::localWriter.beginArg(count++);')
            if interface.name in ('IDirectDraw4', 'IDirectDraw7'):
                tracer.serializeValue(Pointer(DDSURFACEDESC2), "lpDDSurfaceDesc");
            else:
                tracer.serializeValue(Pointer(DDSURFACEDESC), "lpDDSurfaceDesc");
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpContext);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpEnumModesCallback);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.endEnter();')
            print('    trace::localWriter.beginLeave(_callcallback);')
            print('    trace::localWriter.endLeave();')

        if interface.name.startswith('IDirect3D') and method.name == 'EnumDevices':
            print('    if (_result != D3D_OK)')
            print('        return _result;')
            print('')
            print('    for (const auto& result : context.result) {')
            if interface.name == 'IDirect3D7':
                print('        HRESULT hr = lpEnumDevicesCallback(result.deviceDesc, result.deviceName, result.hal, lpUserArg);')
            else:
                print('        HRESULT hr = lpEnumDevicesCallback(result.guid, result.deviceDesc, result.deviceName, (LPD3DDEVICEDESC)result.hal, (LPD3DDEVICEDESC)result.hel, lpUserArg);')
            print('            if (hr != D3DENUMRET_OK)')
            print('                break;')
            print('    }')
            print('')

            print('    const char* enum_args[6] = { "origin", "originName", "resultCount", "result", "lpUserArg", "lpEnumDevicesCallback" };')
            print('    const trace::FunctionSig enum_sig = { %u, "EnumDevicesCallbacks", 6, enum_args };' % self.getFunctionSigId())
            if interface.name == 'IDirect3D7':
                print('    const char* enum_result_members[3] = { "deviceDesc", "deviceName", "desc" };')
                print('    const trace::StructSig enum_result_sig = { %u, "enumResult", 3, enum_result_members };' % self.getFunctionSigId())
            else:
                print('    const char* enum_result_members[5] = { "guid", "deviceDesc", "deviceName", "hal", "hel" };')
                print('    const trace::StructSig enum_result_sig = { %u, "enumResult", 5, enum_result_members };' % self.getFunctionSigId())
            print('    unsigned _callcallback = trace::localWriter.beginEnter(&enum_sig, trace::FLAG_FAKE);')
            print('')
            print('    int count = 0;')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)_this);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeString("%s::%s");' % (interface.name, method.name))
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeSInt(context.result.size());')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.beginArray(context.result.size());')
            print('    for (const auto& result : context.result) {')
            print('        trace::localWriter.beginStruct(&enum_result_sig);')
            if interface.name != 'IDirect3D7':
                tracer.serializeValue(Pointer(CLSID), "result.guid");
            print('        trace::localWriter.writeString(result.deviceDesc);')
            print('        trace::localWriter.writeString(result.deviceName);')
            if interface.name == 'IDirect3D':
                tracer.serializeValue(Pointer(D3DDEVICEDESC2), "result.hal");
                tracer.serializeValue(Pointer(D3DDEVICEDESC2), "result.hel");
            elif interface.name == 'IDirect3D2':
                tracer.serializeValue(Pointer(D3DDEVICEDESC5), "result.hal");
                tracer.serializeValue(Pointer(D3DDEVICEDESC5), "result.hel");
            elif interface.name == 'IDirect3D3':
                tracer.serializeValue(Pointer(D3DDEVICEDESC6), "result.hal");
                tracer.serializeValue(Pointer(D3DDEVICEDESC6), "result.hel");
            else:
                tracer.serializeValue(Pointer(D3DDEVICEDESC7), "result.hal");
            print('        trace::localWriter.endStruct();')
            print('        delete []result.deviceDesc;')
            print('        delete []result.deviceName;')
            print('        delete result.hal;')
            print('        delete result.hel;')
            print('    }')
            print('    trace::localWriter.endArray();')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpUserArg);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpEnumDevicesCallback);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.endEnter();')
            print('    trace::localWriter.beginLeave(_callcallback);')
            print('    trace::localWriter.endLeave();')

        if interface.name.startswith('IDirect3DDevice') and method.name == 'EnumTextureFormats':
            print('    if (_result != D3D_OK)')
            print('        return _result;')
            print('')
            print('    for (const auto& result : context.result) {')
            if interface.name == 'IDirect3DDevice' or interface.name == 'IDirect3DDevice2':
                print('        if (lpD3DEnumTextureProc(result.ddsd, lpArg) != D3DENUMRET_OK)')
                print('            break;')
            else:
                print('        if (lpD3DEnumPixelProc(result.ddPixelFormat, lpArg) != D3DENUMRET_OK)')
                print('            break;')
            print('    }')
            print('')
            if interface.name == 'IDirect3DDevice' or interface.name == 'IDirect3DDevice2':
                print('    const char* enum_args[6] = { "origin", "originName", "resultCount", "result", "lpArg", "lpD3DEnumTextureProc" };')
            else:
                print('    const char* enum_args[6] = { "origin", "originName", "resultCount", "result", "lpArg", "lpD3DEnumPixelProc" };')
            print('    const trace::FunctionSig enum_sig = { %u, "EnumTexturesFormatsCallbacks", 6, enum_args };' % self.getFunctionSigId())
            print('    const char* enum_result_members[1] = { "lpDDPixFmt" };')
            print('    const trace::StructSig enum_result_sig = { %u, "enumResult", 1, enum_result_members };' % self.getFunctionSigId())
            print('    unsigned _callcallback = trace::localWriter.beginEnter(&enum_sig, trace::FLAG_FAKE);')
            print('')
            print('    int count = 0;')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)_this);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeString("%s::%s");' % (interface.name, method.name))
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeSInt(context.result.size());')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.beginArray(context.result.size());')
            print('    for (const auto& result : context.result) {')
            print('        trace::localWriter.beginStruct(&enum_result_sig);')
            if interface.name == 'IDirect3DDevice' or interface.name == 'IDirect3DDevice2':
                tracer.serializeValue(Pointer(DDSURFACEDESC), "result.ddsd");
                print('        delete result.ddsd;')
            else:
                tracer.serializeValue(Pointer(DDPIXELFORMAT), "result.ddPixelFormat");
                print('        delete result.ddPixelFormat;')
            print('        trace::localWriter.endStruct();')
            print('    }')
            print('    trace::localWriter.endArray();')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpArg);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            if interface.name == 'IDirect3DDevice' or interface.name == 'IDirect3DDevice2':
                print('    trace::localWriter.writePointer((uintptr_t)lpD3DEnumTextureProc);')
            else:
                print('    trace::localWriter.writePointer((uintptr_t)lpD3DEnumPixelProc);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.endEnter();')
            print('    trace::localWriter.beginLeave(_callcallback);')
            print('    trace::localWriter.endLeave();')

        if interface.name.startswith('IDirect3D') and method.name == 'EnumZBufferFormats':
            print('    if (_result != D3D_OK)')
            print('        return _result;')
            print('')
            print('    for (const auto& result : context.result) {')
            print('        if (lpEnumCallback(result.ddPixelFormat, lpContext) != D3DENUMRET_OK)')
            print('            break;')
            print('    }')
            print('')
            print('    const char* enum_args[7] = { "origin", "originName", "resultCount", "result", "riidDevice", "lpContext", "lpEnumCallback" };')
            print('    const trace::FunctionSig enum_sig = { %u, "EnumZBufferFormatsCallbacks", 7, enum_args };' % self.getFunctionSigId())
            print('    const char* enum_result_members[1] = { "lpDDPixFmt" };')
            print('    const trace::StructSig enum_result_sig = { %u, "enumResult", 1, enum_result_members };' % self.getFunctionSigId())
            print('    unsigned _callcallback = trace::localWriter.beginEnter(&enum_sig, trace::FLAG_FAKE);')
            print('')
            print('    int count = 0;')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)_this);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeString("%s::%s");' % (interface.name, method.name))
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writeSInt(context.result.size());')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.beginArray(context.result.size());')
            print('    for (const auto& result : context.result) {')
            print('        trace::localWriter.beginStruct(&enum_result_sig);')
            tracer.serializeValue(Pointer(DDPIXELFORMAT), "result.ddPixelFormat");
            print('        trace::localWriter.endStruct();')
            print('        delete result.ddPixelFormat;')
            print('    }')
            print('    trace::localWriter.endArray();')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            tracer.serializeValue(REFCLSID, "riidDevice");
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpContext);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.beginArg(count++);')
            print('    trace::localWriter.writePointer((uintptr_t)lpEnumCallback);')
            print('    trace::localWriter.endArg();')
            print('    trace::localWriter.endEnter();')
            print('    trace::localWriter.beginLeave(_callcallback);')
            print('    trace::localWriter.endLeave();')



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

    print('struct EnumDirectDrawResultA {')
    print('    CLSID* guid;')
    print('    char* deviceDesc = nullptr;')
    print('    char* deviceName = nullptr;')
    print('    HMONITOR monitor;')
    print('};')
    print('struct EnumDirectDrawContextA {')
    print('    std::vector<EnumDirectDrawResultA> result;')
    print('};')

    print('struct EnumDirectDrawResultW {')
    print('    CLSID* guid;')
    print('    wchar_t* deviceDesc = nullptr;')
    print('    wchar_t* deviceName = nullptr;')
    print('    HMONITOR monitor;')
    print('};')
    print('struct EnumDirectDrawContextW {')
    print('    std::vector<EnumDirectDrawResultW> result;')
    print('};')

    print('BOOL EnumDirectDrawACallback(GUID *guid, char* deviceName, char* deviceDesc, EnumDirectDrawContextA *pContext);')
    print('BOOL EnumDirectDrawWCallback(GUID *guid, wchar_t* deviceName, wchar_t* deviceDesc, EnumDirectDrawContextW *pContext);')
    print('BOOL EnumDirectDrawExACallback(GUID *guid, char* deviceName, char* deviceDesc, EnumDirectDrawContextA *pContext, HMONITOR monitor);')
    print('BOOL EnumDirectDrawExWCallback(GUID *guid, wchar_t* deviceName, wchar_t* deviceDesc, EnumDirectDrawContextW *pContext, HMONITOR monitor);')

    print('template <typename S, typename D> struct EnumSurfacesResult {')
    print('    S *surface = nullptr;')
    print('    D *desc = nullptr;')
    print('};')
    print('template <typename S, typename D> struct EnumSurfacesContext {')
    print('    std::vector<EnumSurfacesResult<S, D>> result;')
    print('};')
    print('template <typename S, typename D> HRESULT CALLBACK EnumSurfacesCallback(S* pSurface, D* pDesc, EnumSurfacesContext<S, D>* pContext);')
    print('template HRESULT CALLBACK EnumSurfacesCallback<IDirectDrawSurface, DDSURFACEDESC>(IDirectDrawSurface*, DDSURFACEDESC*, EnumSurfacesContext<IDirectDrawSurface, DDSURFACEDESC>*);')
    print('template HRESULT CALLBACK EnumSurfacesCallback<IDirectDrawSurface4, DDSURFACEDESC2>(IDirectDrawSurface4*, DDSURFACEDESC2*, EnumSurfacesContext<IDirectDrawSurface4, DDSURFACEDESC2>*);')
    print('template HRESULT CALLBACK EnumSurfacesCallback<IDirectDrawSurface7, DDSURFACEDESC2>(IDirectDrawSurface7*, DDSURFACEDESC2*, EnumSurfacesContext<IDirectDrawSurface7, DDSURFACEDESC2>*);')

    print('struct EnumPixelFormatsResult {')
    print('    DDPIXELFORMAT* ddPixelFormat = nullptr;')
    print('};')
    print('struct EnumPixelFormatsContext {')
    print('    std::vector<EnumPixelFormatsResult> result;')
    print('};')
    print('HRESULT CALLBACK')
    print('EnumPixelFormatsCallback(LPDDPIXELFORMAT lpDDPixFmt, EnumPixelFormatsContext *pContext);')

    print('struct EnumTextureFormatsResult {')
    print('    DDSURFACEDESC* ddsd = nullptr;')
    print('};')
    print('struct EnumTextureFormatsContext {')
    print('    std::vector<EnumTextureFormatsResult> result;')
    print('};')
    print('HRESULT CALLBACK')
    print('EnumTextureFormatsCallback(LPDDSURFACEDESC lpDdsd, EnumTextureFormatsContext *pContext);')

    print('struct EnumZBufferFormatsResult {')
    print('    DDPIXELFORMAT* ddPixelFormat = nullptr;')
    print('};')
    print('struct EnumZBufferFormatsContext {')
    print('    std::vector<EnumZBufferFormatsResult> result;')
    print('};')
    print('HRESULT CALLBACK')
    print('EnumZBufferFormatsCallback(LPDDPIXELFORMAT lpDDPixFmt, EnumZBufferFormatsContext *pContext);')

    print('template <typename D> struct EnumDisplayModesResult {')
    print('    D* desc = nullptr;')
    print('};')
    print('template <typename D> struct EnumDisplayModesContext {')
    print('    std::vector<EnumDisplayModesResult<D>> result;')
    print('};')
    print('template <typename D> HRESULT CALLBACK EnumDisplayModesCallback(D* pDesc, EnumDisplayModesContext<D> *pContext);')
    print('template HRESULT CALLBACK EnumDisplayModesCallback<DDSURFACEDESC>(DDSURFACEDESC* pDesc, EnumDisplayModesContext<DDSURFACEDESC> *pContext);')
    print('template HRESULT CALLBACK EnumDisplayModesCallback<DDSURFACEDESC2>(DDSURFACEDESC2* pDesc, EnumDisplayModesContext<DDSURFACEDESC2> *pContext);')

    print('template <typename D> struct EnumDevicesResult {')
    print('    CLSID* guid;')
    print('    char* deviceDesc = nullptr;')
    print('    char* deviceName = nullptr;')
    print('    D* hal = nullptr;')
    print('    D* hel = nullptr;')
    print('};')
    print('template <typename D> struct EnumDevicesContext {')
    print('    std::vector<EnumDevicesResult<D>> result;')
    print('};')
    print('template <typename D> HRESULT CALLBACK EnumDevicesCallback(CLSID* guid, char *deviceDesc, char *deviceName, D* hal, D* hel, EnumDevicesContext<D> *pContext);')
    print('template HRESULT CALLBACK EnumDevicesCallback<D3DDEVICEDESC2>(CLSID* guid, char *deviceDesc, char *deviceName, D3DDEVICEDESC2* hal, D3DDEVICEDESC2* hel, EnumDevicesContext<D3DDEVICEDESC2> *pContext);')
    print('template HRESULT CALLBACK EnumDevicesCallback<D3DDEVICEDESC5>(CLSID* guid, char *deviceDesc, char *deviceName, D3DDEVICEDESC5* hal, D3DDEVICEDESC5* hel, EnumDevicesContext<D3DDEVICEDESC5> *pContext);')
    print('template HRESULT CALLBACK EnumDevicesCallback<D3DDEVICEDESC6>(CLSID* guid, char *deviceDesc, char *deviceName, D3DDEVICEDESC6* hal, D3DDEVICEDESC6* hel, EnumDevicesContext<D3DDEVICEDESC6> *pContext);')
    print('HRESULT CALLBACK EnumDevicesCallback7(char *deviceDesc, char *deviceName, D3DDEVICEDESC7* pDesc, EnumDevicesContext<D3DDEVICEDESC7> *pContext);')

    tracer = DDrawTracer()
    visitor = ComplexValueSerializer(tracer.serializerFactory())

    # TODO: investigate why union signatures aren't generated on usual visit
    collector = Collector()
    collector.visit(D3DSTATE)
    for t in collector.types:
        if type(t) == Struct:
            visitor.visit(t)

    visitor.visit(D3DTRANSFORMSTATEVALUE)
    visitor.visit(D3DPROCESSVERTICESFlags)
    visitor.visit(D3DTRIFLAG)
    visitor.visit(D3DINSTRUCTION)
    visitor.visit(D3DBRANCH)
    visitor.visit(D3DLINE)
    visitor.visit(D3DMATRIXLOAD)
    visitor.visit(D3DMATRIXMULTIPLY)
    visitor.visit(D3DPOINT)
    visitor.visit(D3DPROCESSVERTICES)
    visitor.visit(D3DSPAN)
    visitor.visit(D3DTEXTURELOAD)
    visitor.visit(D3DTRIANGLE)
    tracer.traceApi(api)

    print('BOOL EnumDirectDrawACallback(GUID *guid, char* deviceName, char* deviceDesc, EnumDirectDrawContextA *pContext) {')
    print('    EnumDirectDrawResultA& result = pContext->result.emplace_back(EnumDirectDrawResultA{});')
    print('    if (guid != nullptr) {')
    print('        result.guid = new CLSID;')
    print('        memcpy(result.guid, guid, sizeof(CLSID));')
    print('    }')
    print('    if (deviceDesc != nullptr) {')
    print('        const size_t size = strlen(deviceDesc) + 1;')
    print('        result.deviceDesc = new char[size];')
    print('        strncpy(result.deviceDesc, deviceDesc, size);')
    print('    }')
    print('    if (deviceName != nullptr) {')
    print('        const size_t size = strlen(deviceName) + 1;')
    print('        result.deviceName = new char[size];')
    print('        strncpy(result.deviceName, deviceName, size);')
    print('    }')
    print('    return DDENUMRET_OK;')
    print('}')

    print('BOOL EnumDirectDrawWCallback(GUID *guid, wchar_t* deviceName, wchar_t* deviceDesc, EnumDirectDrawContextW *pContext) {')
    print('    EnumDirectDrawResultW& result = pContext->result.emplace_back(EnumDirectDrawResultW{});')
    print('    if (guid != nullptr) {')
    print('        result.guid = new CLSID;')
    print('        memcpy(result.guid, guid, sizeof(CLSID));')
    print('    }')
    print('    if (deviceDesc != nullptr) {')
    print('        const size_t size = wcslen(deviceDesc) + 1;')
    print('        result.deviceDesc = new wchar_t[size];')
    print('        wcsncpy(result.deviceDesc, deviceDesc, size);')
    print('    }')
    print('    if (deviceName != nullptr) {')
    print('        const size_t size = wcslen(deviceName) + 1;')
    print('        result.deviceName = new wchar_t[size];')
    print('        wcsncpy(result.deviceName, deviceName, size);')
    print('    }')
    print('    return DDENUMRET_OK;')
    print('}')

    print('BOOL EnumDirectDrawExACallback(GUID *guid, char* deviceName, char* deviceDesc, EnumDirectDrawContextA *pContext, HMONITOR monitor) {')
    print('    EnumDirectDrawResultA& result = pContext->result.emplace_back(EnumDirectDrawResultA{});')
    print('    if (guid != nullptr) {')
    print('        result.guid = new CLSID;')
    print('        memcpy(result.guid, guid, sizeof(CLSID));')
    print('    }')
    print('    if (deviceDesc != nullptr) {')
    print('        const size_t size = strlen(deviceDesc) + 1;')
    print('        result.deviceDesc = new char[size];')
    print('        strncpy(result.deviceDesc, deviceDesc, size);')
    print('    }')
    print('    if (deviceName != nullptr) {')
    print('        const size_t size = strlen(deviceName) + 1;')
    print('        result.deviceName = new char[size];')
    print('        strncpy(result.deviceName, deviceName, size);')
    print('    }')
    print('    result.monitor = monitor;')
    print('    return DDENUMRET_OK;')
    print('}')

    print('BOOL EnumDirectDrawExWCallback(GUID *guid, wchar_t* deviceName, wchar_t* deviceDesc, EnumDirectDrawContextW *pContext, HMONITOR monitor) {')
    print('    EnumDirectDrawResultW& result = pContext->result.emplace_back(EnumDirectDrawResultW{});')
    print('    if (guid != nullptr) {')
    print('        result.guid = new CLSID;')
    print('        memcpy(result.guid, guid, sizeof(CLSID));')
    print('    }')
    print('    if (deviceDesc != nullptr) {')
    print('        const size_t size = wcslen(deviceDesc) + 1;')
    print('        result.deviceDesc = new wchar_t[size];')
    print('        wcsncpy(result.deviceDesc, deviceDesc, size);')
    print('    }')
    print('    if (deviceName != nullptr) {')
    print('        const size_t size = wcslen(deviceName) + 1;')
    print('        result.deviceName = new wchar_t[size];')
    print('        wcsncpy(result.deviceName, deviceName, size);')
    print('    }')
    print('    result.monitor = monitor;')
    print('    return DDENUMRET_OK;')
    print('}')

    print('template <typename S, typename D> HRESULT CALLBACK EnumSurfacesCallback(S* pSurface, D* pDesc, EnumSurfacesContext<S, D> *pContext) {')
    print('    EnumSurfacesResult<S, D>& result = pContext->result.emplace_back(EnumSurfacesResult<S, D>{});')
    print('    result.surface = pSurface;')
    print('    if (pDesc != nullptr) {')
    print('        result.desc = new D;')
    print('        memcpy(result.desc, pDesc, sizeof(D));')
    print('    }')
    print('    return DDENUMRET_OK;')
    print('}')

    print('template <typename D> HRESULT CALLBACK EnumDisplayModesCallback(D* pDesc, EnumDisplayModesContext<D> *pContext) {')
    print('    EnumDisplayModesResult<D>& result = pContext->result.emplace_back(EnumDisplayModesResult<D>{});')
    print('    if (pDesc != nullptr) {')
    print('        result.desc = new D;')
    print('        memcpy(result.desc, pDesc, sizeof(D));')
    print('    }')
    print('    return DDENUMRET_OK;')
    print('}')

    print('template <typename D> HRESULT CALLBACK EnumDevicesCallback(CLSID* guid, char *deviceDesc, char *deviceName, D* hal, D* hel, EnumDevicesContext<D> *pContext) {')
    print('    EnumDevicesResult<D>& result = pContext->result.emplace_back(EnumDevicesResult<D>{});')
    print('    if (guid != nullptr) {')
    print('        result.guid = new CLSID;')
    print('        memcpy(result.guid, guid, sizeof(CLSID));')
    print('    }')
    print('    if (deviceDesc != nullptr) {')
    print('        const size_t size = strlen(deviceDesc) + 1;')
    print('        result.deviceDesc = new char[size];')
    print('        strncpy(result.deviceDesc, deviceDesc, size);')
    print('    }')
    print('    if (deviceName != nullptr) {')
    print('        const size_t size = strlen(deviceName) + 1;')
    print('        result.deviceName = new char[size];')
    print('        strncpy(result.deviceName, deviceName, size);')
    print('    }')
    print('    if (hal != nullptr) {')
    print('        result.hal = new D;')
    print('        memcpy(result.hal, hal, sizeof(D));')
    print('    }')
    print('    if (hel != nullptr) {')
    print('        result.hel = new D;')
    print('        memcpy(result.hel, hel, sizeof(D));')
    print('    }')
    print('    return D3DENUMRET_OK;')
    print('}')

    print('HRESULT CALLBACK EnumDevicesCallback7(char *deviceDesc, char *deviceName, D3DDEVICEDESC7* pDesc, EnumDevicesContext<D3DDEVICEDESC7> *pContext) {')
    print('    EnumDevicesResult<D3DDEVICEDESC7>& result = pContext->result.emplace_back(EnumDevicesResult<D3DDEVICEDESC7>{});')
    print('    if (deviceDesc != nullptr) {')
    print('        const size_t size = strlen(deviceDesc) + 1;')
    print('        result.deviceDesc = new char[size];')
    print('        strncpy(result.deviceDesc, deviceDesc, size);')
    print('    }')
    print('    if (deviceName != nullptr) {')
    print('        const size_t size = strlen(deviceName) + 1;')
    print('        result.deviceName = new char[size];')
    print('        strncpy(result.deviceName, deviceName, size);')
    print('    }')
    print('    if (pDesc != nullptr) {')
    print('        result.hal = new D3DDEVICEDESC7;')
    print('        memcpy(result.hal, pDesc, sizeof(D3DDEVICEDESC7));')
    print('    }')
    print('    return D3DENUMRET_OK;')
    print('}')

    print('HRESULT CALLBACK EnumPixelFormatsCallback(DDPIXELFORMAT* lpDDPixFmt, EnumPixelFormatsContext *pContext) {')
    print('    EnumPixelFormatsResult& result = pContext->result.emplace_back(EnumPixelFormatsResult{});')
    print('    if (lpDDPixFmt != nullptr) {')
    print('        result.ddPixelFormat = new DDPIXELFORMAT;')
    print('        memcpy(result.ddPixelFormat, lpDDPixFmt, sizeof(DDPIXELFORMAT));')
    print('    }')
    print('    return D3DENUMRET_OK;')
    print('}')

    print('HRESULT CALLBACK EnumTextureFormatsCallback(DDSURFACEDESC* lpDdsd, EnumTextureFormatsContext *pContext) {')
    print('    EnumTextureFormatsResult& result = pContext->result.emplace_back(EnumTextureFormatsResult{});')
    print('    if (lpDdsd != nullptr) {')
    print('        result.ddsd = new DDSURFACEDESC;')
    print('        memcpy(result.ddsd, lpDdsd, sizeof(DDSURFACEDESC));')
    print('    }')
    print('    return D3DENUMRET_OK;')
    print('}')

    print('HRESULT CALLBACK EnumZBufferFormatsCallback(DDPIXELFORMAT* lpDDPixFmt, EnumZBufferFormatsContext *pContext) {')
    print('    EnumZBufferFormatsResult& result = pContext->result.emplace_back(EnumZBufferFormatsResult{});')
    print('    if (lpDDPixFmt != nullptr) {')
    print('        result.ddPixelFormat = new DDPIXELFORMAT;')
    print('        memcpy(result.ddPixelFormat, lpDDPixFmt, sizeof(DDPIXELFORMAT));')
    print('    }')
    print('    return D3DENUMRET_OK;')
    print('}')
