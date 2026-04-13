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

    def deserializeArgs(self, interface, method):
        if interface != None and interface.name == 'IDirect3DLight' and method.name == 'SetLight':
            print(r'    DWORD dwSize = sizeof(D3DLIGHT);')
            print(r'    const trace::Array *_a = (call.arg(1)).toArray();')
            print(r'    if (_a) {')
            print(r'        const trace::Struct *_s = (*_a->values[0]).toStruct();')
            print(r'        dwSize = (*_s->members[0]).toUInt();')
            print(r'    }')

        Retracer.deserializeArgs(self, interface, method)

    def invokeInterfaceMethod(self, interface, method):
        # keep track of the last used device for state dumping
        if interface.name == 'IUnknown' and method.name == 'Release':
            print(r'    int releasedType = 0;')
            print(r'    if (_this == d3d3Dumper.pLastDevice) {')
            print(r'        releasedType = DEVICE_D3D3;')
            print(r'    } else if (_this == d3d5Dumper.pLastDevice) {')
            print(r'        releasedType = DEVICE_D3D5;')
            print(r'    } else if (_this == d3d6Dumper.pLastDevice) {')
            print(r'        releasedType = DEVICE_D3D6;')
            print(r'    } else if (_this == d3d7Dumper.pLastDevice) {')
            print(r'        releasedType = DEVICE_D3D7;')
            print(r'    } else if (_this == ddrawDumper.pLastDevice) {')
            print(r'        releasedType = DEVICE_DDRAW;')
            print(r'    } else if (_this == ddraw2Dumper.pLastDevice) {')
            print(r'        releasedType = DEVICE_DDRAW2;')
            print(r'    } else if (_this == ddraw4Dumper.pLastDevice) {')
            print(r'        releasedType = DEVICE_DDRAW4;')
            print(r'    } else if (_this == ddraw7Dumper.pLastDevice) {')
            print(r'        releasedType = DEVICE_DDRAW7;')
            print(r'    } else {')
            print(r'        std::visit([_this, &releasedType](auto &surface) {')
            print(r'            using T = std::decay_t<decltype(surface)>;')
            print(r'            if constexpr (!std::is_same_v<T, std::monostate>) {')
            print(r'                if (_this == surface) {')
            print(r'                    releasedType = SURFACE_DDRAW;')
            print(r'                }')
            print(r'            }')
            print(r'        }, d3dstate::lastSetSurface);')
            print(r'        std::visit([_this, &releasedType](auto &surface) {')
            print(r'            using T = std::decay_t<decltype(surface)>;')
            print(r'            if constexpr (!std::is_same_v<T, std::monostate>) {')
            print(r'                if (_this == surface) {')
            print(r'                    releasedType = SURFACE_RENDERTARGET;')
            print(r'                }')
            print(r'            }')
            print(r'        }, d3dstate::lastSetRenderTarget);')
            print(r'        for (auto lastSetTexture : d3dstate::lastSetTextures) {')
            print(r'            std::visit([_this, &releasedType](auto &texture) {')
            print(r'                using T = std::decay_t<decltype(texture)>;')
            print(r'                if constexpr (!std::is_same_v<T, std::monostate>) {')
            print(r'                    if (_this == texture) {')
            print(r'                        releasedType = TEXTURE_SET;')
            print(r'                        return;')
            print(r'                    }')
            print(r'                }')
            print(r'            }, lastSetTexture);')
            print(r'        }')
            print(r'    }')

        if interface.name == 'IDirect3DDevice' and method.name != 'Release':
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

        if interface.name == 'IDirect3DDevice' and method.name in ('DeleteMatrix', 'SetMatrix'):
            if method.name == 'DeleteMatrix':
                print(r'    DWORD hOriginal = %s;' % method.getArgByName('D3DMatHandle').name)
            print(r'    %s = d3dstate::getMatrixHandle(%s);' % (method.getArgByName('D3DMatHandle').name, method.getArgByName('D3DMatHandle').name))
            if method.name == 'DeleteMatrix':
                print(r'    d3dstate::setMatrixMap(hOriginal, 0);')

        if interface.name.startswith('IDirect3DDevice') and method.name == 'SwapTextureHandles':
            print(r'    d3dstate::swapTextures(%s, %s);' % (method.getArgByName('lpD3DTex1').name, method.getArgByName('lpD3DTex2').name))

        if interface.name == 'IDirect3DDevice' and method.name == 'Execute':
            print(r'    std::vector<uint8_t> buffer;');
            print(r'    if (%s != nullptr) {' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'        d3dstate::clearTextures();')
            print(r'        D3DEXECUTEDATA data;')
            print(r'        ZeroMemory(&data, sizeof(data));')
            print(r'        data.dwSize = sizeof(data);')
            print(r'        if (SUCCEEDED(%s->GetExecuteData(&data))) {' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'            D3DEXECUTEBUFFERDESC desc;')
            print(r'            ZeroMemory(&desc, sizeof(desc));')
            print(r'            desc.dwSize = sizeof(desc);')
            print(r'            if (SUCCEEDED(%s->Lock(&desc))) {' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'                uint8_t* buf = (uint8_t*)desc.lpData;')
            print(r'                if (buf != nullptr) {')
            print(r'                    buffer.resize(desc.dwBufferSize);')
            print(r'                    memcpy(buffer.data(), buf, desc.dwBufferSize);')
            print(r'                    uint8_t* ptr = buf + data.dwInstructionOffset;')
            # Sadly can't rely on data.dwInstructionLength as some games send garbage there
            print(r'                    while (true) {')
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
            print(r'                        case D3DOP_MATRIXLOAD: {')
            print(r'                            D3DMATRIXLOAD* matrixLoad = reinterpret_cast<D3DMATRIXLOAD*>(operation);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DMATRIXLOAD& ml = matrixLoad[i];')
            print(r'                                ml.hSrcMatrix = d3dstate::getMatrixHandle(ml.hSrcMatrix);')
            print(r'                                ml.hDestMatrix = d3dstate::getMatrixHandle(ml.hDestMatrix);')
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_MATRIXMULTIPLY: {')
            print(r'                            D3DMATRIXMULTIPLY* matrixLoad = reinterpret_cast<D3DMATRIXMULTIPLY*>(operation);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DMATRIXMULTIPLY& mm = matrixLoad[i];')
            print(r'                                mm.hSrcMatrix1 = d3dstate::getMatrixHandle(mm.hSrcMatrix1);')
            print(r'                                mm.hSrcMatrix2 = d3dstate::getMatrixHandle(mm.hSrcMatrix2);')
            print(r'                                mm.hDestMatrix = d3dstate::getMatrixHandle(mm.hDestMatrix);')
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
            print(r'                        case D3DOP_STATELIGHT: {')
            print(r'                            D3DSTATE* state = reinterpret_cast<D3DSTATE*>(operation);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DSTATE& s = state[i];')
            print(r'                                if (s.dlstLightStateType == D3DLIGHTSTATE_MATERIAL) {')
            print(r'                                    s.dwArg[0] = d3dstate::getMaterialHandle(s.dwArg[0]);')
            print(r'                                }')
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_STATERENDER: {')
            print(r'                            D3DSTATE* state = reinterpret_cast<D3DSTATE*>(operation);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DSTATE& s = state[i];')
            print(r'                                d3dstate::setRenderState(s.drstRenderStateType, s.dwArg[0]);')
            print(r'                                if (s.drstRenderStateType == D3DRENDERSTATE_TEXTUREHANDLE) {')
            print(r'                                    d3dstate::setTexture(s.dwArg[0]);')
            print(r'                                    s.dwArg[0] = d3dstate::getTextureHandle(s.dwArg[0]);')
            print(r'                                }')
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_STATETRANSFORM: {')
            print(r'                            D3DSTATE* state = reinterpret_cast<D3DSTATE*>(operation);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DSTATE& s = state[i];')
            print(r'                                s.dwArg[0] = d3dstate::getMatrixHandle(s.dwArg[0]);')
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_TEXTURELOAD: {')
            print(r'                            D3DTEXTURELOAD* textureLoad = reinterpret_cast<D3DTEXTURELOAD*>(operation);')
            print(r'                            for (uint16_t i = 0; i < instruction->wCount; i++) {')
            print(r'                                D3DTEXTURELOAD& tl = textureLoad[i];')
            print(r'                                tl.hDestTexture = d3dstate::getTextureHandle(tl.hDestTexture);')
            print(r'                                tl.hSrcTexture = d3dstate::getTextureHandle(tl.hSrcTexture);')
            print(r'                                ptr += instruction->bSize;')
            print(r'                            }')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        case D3DOP_LINE:')
            print(r'                        case D3DOP_POINT:')
            print(r'                        case D3DOP_PROCESSVERTICES:')
            print(r'                        case D3DOP_TRIANGLE:')
            print(r'                        case D3DOP_SPAN: {')
            print(r'                            ptr += instruction->bSize * instruction->wCount;')
            print(r'                            break;')
            print(r'                        }')
            print(r'                        default: {')
            print(r'                            retrace::warning(call) << "Unknown execute buffer opcode: " << static_cast<uint32_t>(instruction->bOpcode) << "\n";')
            print(r'                            ptr += instruction->bSize * instruction->wCount;')
            print(r'                            break;')
            print(r'                        }}')
            print(r'                    }')
            print(r'                }')
            print(r'                %s->Unlock();' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'            }')
            print(r'        }')
            print(r'    }')

        Retracer.invokeInterfaceMethod(self, interface, method)

        if interface.name == 'IDirect3DDevice' and method.name == 'Execute':
            print(r'    if (%s != nullptr && buffer.size() > 0) {' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'        D3DEXECUTEDATA data;')
            print(r'        ZeroMemory(&data, sizeof(data));')
            print(r'        data.dwSize = sizeof(data);')
            print(r'        if (SUCCEEDED(%s->GetExecuteData(&data))) {' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'            D3DEXECUTEBUFFERDESC desc;')
            print(r'            ZeroMemory(&desc, sizeof(desc));')
            print(r'            desc.dwSize = sizeof(desc);')
            print(r'            if (SUCCEEDED(%s->Lock(&desc))) {' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'                uint8_t* buf = (uint8_t*)desc.lpData;')
            print(r'                if (buf != nullptr) {')
            print(r'                    buffer.resize(desc.dwBufferSize);')
            print(r'                    memcpy(buf, buffer.data(), desc.dwBufferSize);')
            print(r'                }')
            print(r'                %s->Unlock();' % method.getArgByName('lpDirect3DExecuteBuffer').name)
            print(r'            }')
            print(r'        }')
            print(r'    }')

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
            print(r'            d3dstate::setRenderTarget(*lplpDDSurface);')
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
            print(r'        d3dstate::clearTextures();')
            print(r'        d3dstate::setTexture(%s);' % method.getArgByName('dwRenderState').name)
            print(r'    }')

        if interface.name.startswith('IDirectDrawSurface') and method != 'Release':
            print(r'    if (SUCCEEDED(_result)) {')
            print(r'          d3dstate::setSurface(_this);')
            print(r'    } else {')
            print(r'          d3dstate::setSurface(std::monostate{});')
            print(r'    }')

        if interface.name == 'IDirect3DDevice' and method.name == 'CreateMatrix':
            print(r'    if (SUCCEEDED(_result) && %s) {' % method.getArgByName('lpD3DMatHandle').name)
            print(r'        const trace::Array *_ar = (call.arg(1)).toArray();')
            print(r'        if (_ar) {')
            print(r'            DWORD hOriginal = static_cast<DWORD>((*_ar->values[0]).toUInt());')
            print(r'            d3dstate::setMatrixMap(hOriginal, *%s);' % method.getArgByName('lpD3DMatHandle').name)
            print(r'        }')
            print(r'    }')

        if interface.name == 'IUnknown' and method.name == 'Release':
#           Ignore refcounts for now as there can be instances where devices/surfaces could be Released indirectly.
#            print(r'    if (_orig_result == 0 || _result == 0) {')
            print(r'        if (releasedType == DEVICE_D3D3) {')
            print(r'            d3d3Dumper.unbindDevice(d3d3Dumper.pLastDevice);')
            print(r'        } else if (releasedType == DEVICE_D3D5) {')
            print(r'            d3d5Dumper.unbindDevice(d3d5Dumper.pLastDevice);')
            print(r'        } else if (releasedType == DEVICE_D3D6) {')
            print(r'            d3d6Dumper.unbindDevice(d3d6Dumper.pLastDevice);')
            print(r'        } else if (releasedType == DEVICE_D3D7) {')
            print(r'            d3d7Dumper.unbindDevice(d3d7Dumper.pLastDevice);')
            print(r'        } else if (releasedType == DEVICE_DDRAW) {')
            print(r'            ddrawDumper.unbindDevice(ddrawDumper.pLastDevice);')
            print(r'        } else if (releasedType == DEVICE_DDRAW2) {')
            print(r'            ddraw2Dumper.unbindDevice(ddraw2Dumper.pLastDevice);')
            print(r'        } else if (releasedType == DEVICE_DDRAW4) {')
            print(r'            ddraw4Dumper.unbindDevice(ddraw4Dumper.pLastDevice);')
            print(r'        } else if (releasedType == DEVICE_DDRAW7) {')
            print(r'            ddraw7Dumper.unbindDevice(ddraw7Dumper.pLastDevice);')
            print(r'        } else if (releasedType == SURFACE_DDRAW) {')
            print(r'            d3dstate::setSurface(std::monostate{});')
            print(r'        } else if (releasedType == SURFACE_RENDERTARGET) {')
            print(r'            d3dstate::setRenderTarget(std::monostate{});')
            print(r'        } else if (releasedType == TEXTURE_SET) {')
            print(r'            d3dstate::clearTextures();')
            print(r'        }')
#            print(r'    }')
        if interface.name == 'IUnknown' and method.name == 'QueryInterface':
            print(r'    if (SUCCEEDED(_result) && (riid == IID_IDirect3DDevice || riid == IID_IDirect3DHALDevice || riid == IID_IDirect3DRGBDevice || riid == IID_IDirect3DRampDevice || riid == IID_IDirect3DMMXDevice)) {')
            print(r'        if (!strcmp(call.name(), "IDirectDrawSurface::QueryInterface")) {')
            print(r'            d3dstate::setRenderTarget(static_cast<IDirectDrawSurface2*>(_this));')
            print(r'        } else if (!strcmp(call.name(), "IDirectDrawSurface2::QueryInterface")) {')
            print(r'            d3dstate::setRenderTarget(static_cast<IDirectDrawSurface2*>(_this));')
            print(r'        } else if (!strcmp(call.name(), "IDirectDrawSurface3::QueryInterface")) {')
            print(r'            d3dstate::setRenderTarget(static_cast<IDirectDrawSurface3*>(_this));')
            print(r'        } else if (!strcmp(call.name(), "IDirectDrawSurface4::QueryInterface")) {')
            print(r'            d3dstate::setRenderTarget(static_cast<IDirectDrawSurface4*>(_this));')
            print(r'        } else if (!strcmp(call.name(), "IDirectDrawSurface7::QueryInterface")) {')
            print(r'            d3dstate::setRenderTarget(static_cast<IDirectDrawSurface7*>(_this));')
            print(r'        }')
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

    print('enum {')
    print('   DEVICE_DDRAW = 1,')
    print('   DEVICE_DDRAW2,')
    print('   DEVICE_DDRAW4,')
    print('   DEVICE_DDRAW7,')
    print('   DEVICE_D3D3,')
    print('   DEVICE_D3D5,')
    print('   DEVICE_D3D6,')
    print('   DEVICE_D3D7,')
    print('   SURFACE_DDRAW,')
    print('   SURFACE_RENDERTARGET,')
    print('   TEXTURE_SET,')
    print('};')

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
