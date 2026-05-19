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
from specs.d3d import ddraw, interfaces, HWND
from specs.d3dtypes import D3DINSTRUCTION, D3DOPCODE, D3DBRANCH, D3DLINE, D3DMATRIXLOAD, D3DMATRIXMULTIPLY, D3DPOINT, D3DPROCESSVERTICES, D3DSPAN, D3DSTATE, D3DSTATUS, D3DTEXTURELOAD, D3DTRIANGLE
from specs.d3dtypes import D3DPROCESSVERTICESFlags, D3DTRIFLAG, D3DTRANSFORMSTATEVALUE
from specs.ddraw import DDSURFACEDESC, DDSURFACEDESC2
from trace import ComplexValueSerializer


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

        if interface.name == "IDirect3DDevice2":
            variables += [
                ('D3DVERTEXTYPE', '_LastVertexType', 'D3DVT_VERTEX'),
            ]

        if interface.name == "IDirect3DDevice3":
            variables += [
                ('DWORD', '_LastVertexType', '0'),
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
            print(r'        if (_MappedSize && m_pbData) {')
            self.emit_malloc('(LPBYTE)m_pbData', '_MappedSize')
            self.emit_memcpy('(LPBYTE)m_pbData', '_MappedSize')
            print(r'        }')
            print(r'    }')

        if interface.name.startswith('IDirectDraw') and method.name in ('EnumAttachedSurfaces', 'EnumSurfaces'):
            resultOverride = "_result"
            print('    CBTEnumContext context{lpContext, (void*)lpEnumSurfacesCallback, "%s::%s"};' % (interface.name, method.name))

            if method.name == 'EnumAttachedSurfaces':
                print('    _result = _this->EnumAttachedSurfaces(&context, &EnumAttachedSurfacesCBT);')
            else:
                print('    _result = _this->EnumSurfaces(dwFlags, lpDDSurfaceDesc, &context, &EnumAttachedSurfacesCBT);')


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
            print(r'                    while (true) {')
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
            print(r'                    const trace::FunctionSig executebufferdump_sig = { %u, "executebufferdump", 2, executebufferdump_args };' % self.getFunctionSigId())
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
            print(r'                            ptr += instruction->bSize * instruction->wCount;')
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

    print('struct CBTEnumContext {')
    print('    void *pContext;')
    print('    void *pCallback;')
    print('    std::string name;')
    print('};')

    print('template <typename S, typename D>')
    print('HRESULT CALLBACK')
    print('EnumAttachedSurfacesCBT(S* pSurface, D* pDesc, void* pContext);')

    print('template HRESULT CALLBACK')
    print('EnumAttachedSurfacesCBT<IDirectDrawSurface, DDSURFACEDESC>(IDirectDrawSurface*, DDSURFACEDESC*, void*);')
    print('template HRESULT CALLBACK')
    print('EnumAttachedSurfacesCBT<IDirectDrawSurface4, DDSURFACEDESC2>(IDirectDrawSurface4*, DDSURFACEDESC2*, void*);')
    print('template HRESULT CALLBACK')
    print('EnumAttachedSurfacesCBT<IDirectDrawSurface7, DDSURFACEDESC2>(IDirectDrawSurface7*, DDSURFACEDESC2*, void*);')

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

    print('template <typename S, typename D>')
    print('using EnumAttachedSurfaces = HRESULT(CALLBACK *)(S *, D *, void *);')

    print('template <typename S, typename D>')
    print('HRESULT CALLBACK')
    print('EnumAttachedSurfacesCBT(S* pSurface, D* pDesc, void *pContext) {')
    print('    CBTEnumContext* context = static_cast<CBTEnumContext*>(pContext);')
    print('    HRESULT hr = DDENUMRET_CANCEL;')

    print('    const char* enumsurfaces_args[4] = { "lpContext", "lpEnumSurfacesCallback", "lpDDSurface", "lpDDSurfaceDesc" };')
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
    print('        if constexpr (std::is_same_v<D, DDSURFACEDESC2>) {')
    tracer.serializeValue(Pointer(DDSURFACEDESC2), "pDesc");
    print('        } else {')
    tracer.serializeValue(Pointer(DDSURFACEDESC), "pDesc");
    print('        }')
    print('        trace::localWriter.endStruct();')
    print('        trace::localWriter.endArg();')
    print('    }')
    print('    trace::localWriter.endEnter();')
    print('    trace::localWriter.beginLeave(_callcallback);')
    print('    trace::localWriter.beginReturn();')
    print('    trace::localWriter.writeUInt(hr);')
    print('    trace::localWriter.endReturn();')
    print('    trace::localWriter.endLeave();')

    print('    #ifdef _MSC_VER')
    print('    EnumAttachedSurfaces<S, D> callback = static_cast<EnumAttachedSurfaces<S, D>>(context->pCallback);')
    print('    #else')
    print('    EnumAttachedSurfaces<S, D> callback = reinterpret_cast<EnumAttachedSurfaces<S, D>>(context->pCallback);')
    print('    #endif')
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
