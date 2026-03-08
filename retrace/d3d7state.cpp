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


#include <stdio.h>

#include <iostream>
#include <sstream>
#include <memory>

#include "state_writer.hpp"
#include "d3dimports.hpp"
#include "d3dcommon.hpp"
#include "d3dstate.hpp"


namespace d3dstate {

static void
dumpTextureStates(StateWriter &writer, IDirect3DDevice7 *pDevice)
{
#define _DUMP_TS(x) { \
    DWORD rsDword = 0; \
    pDevice->GetTextureStageState(i, x, &rsDword); \
    writeTextureRenderState(writer, #x, rsDword); \
}

    for (int i = 0; i < 8; i++)
    {
        std::ostringstream oss;
        oss << "TextureStageState" << i;
        writer.beginMember(oss.str());
        writer.beginObject();

        _DUMP_TS(D3DTSS_COLOROP);
        _DUMP_TS(D3DTSS_COLORARG1);
        _DUMP_TS(D3DTSS_COLORARG2);
        _DUMP_TS(D3DTSS_ALPHAOP);
        _DUMP_TS(D3DTSS_ALPHAARG1);
        _DUMP_TS(D3DTSS_ALPHAARG2);
        _DUMP_TS(D3DTSS_BUMPENVMAT00);
        _DUMP_TS(D3DTSS_BUMPENVMAT01);
        _DUMP_TS(D3DTSS_BUMPENVMAT10);
        _DUMP_TS(D3DTSS_BUMPENVMAT11);
        _DUMP_TS(D3DTSS_TEXCOORDINDEX);
        _DUMP_TS(D3DTSS_BUMPENVLSCALE);
        _DUMP_TS(D3DTSS_BUMPENVLOFFSET);
        _DUMP_TS(D3DTSS_TEXTURETRANSFORMFLAGS);

        _DUMP_TS(D3DTSS_ADDRESS);
        _DUMP_TS(D3DTSS_ADDRESSU);
        _DUMP_TS(D3DTSS_ADDRESSV);
        _DUMP_TS(D3DTSS_BORDERCOLOR);
        _DUMP_TS(D3DTSS_FORCE_DWORD);
        _DUMP_TS(D3DTSS_MAGFILTER);
        _DUMP_TS(D3DTSS_MAXANISOTROPY);
        _DUMP_TS(D3DTSS_MAXMIPLEVEL);
        _DUMP_TS(D3DTSS_MINFILTER);
        _DUMP_TS(D3DTSS_MIPFILTER);

        writer.endObject();
        writer.endMember();
    }

#undef _DUMP_TS
}

static void
dumpViewport(StateWriter &writer, IDirect3DDevice7 *pDevice)
{
    writer.beginMember("Viewport");
    writer.beginObject();

    D3DVIEWPORT7 vp;
    ZeroMemory(&vp, sizeof(vp));
    HRESULT hr = pDevice->GetViewport(&vp);
    if (SUCCEEDED(hr)) {
        writer.writeIntMember("X", vp.dwX);
        writer.writeIntMember("Y", vp.dwY);
        writer.writeIntMember("Width", vp.dwWidth);
        writer.writeIntMember("Height", vp.dwHeight);
        writer.writeFloatMember("MinZ", vp.dvMinZ);
        writer.writeFloatMember("MaxZ", vp.dvMaxZ);
    }

    writer.endObject();
    writer.endMember();
}

void
dumpRenderstate(StateWriter &writer, IDirect3DDevice7 *pDevice)
{
#define _DUMP_RS(x) { \
    DWORD rsDword = 0; \
    pDevice->GetRenderState(x, &rsDword); \
    writeRenderState(writer, #x, rsDword); \
}

    writer.beginMember("parameters");
    writer.beginObject();

    _DUMP_RS(D3DRENDERSTATE_ANTIALIAS);
    _DUMP_RS(D3DRENDERSTATE_TEXTUREPERSPECTIVE);
    _DUMP_RS(D3DRENDERSTATE_ZENABLE);
    _DUMP_RS(D3DRENDERSTATE_FILLMODE);
    _DUMP_RS(D3DRENDERSTATE_SHADEMODE);
    _DUMP_RS(D3DRENDERSTATE_LINEPATTERN);
    _DUMP_RS(D3DRENDERSTATE_ZWRITEENABLE);
    _DUMP_RS(D3DRENDERSTATE_ALPHATESTENABLE);
    _DUMP_RS(D3DRENDERSTATE_LASTPIXEL);
    _DUMP_RS(D3DRENDERSTATE_SRCBLEND);
    _DUMP_RS(D3DRENDERSTATE_DESTBLEND);
    _DUMP_RS(D3DRENDERSTATE_CULLMODE);
    _DUMP_RS(D3DRENDERSTATE_ZFUNC);
    _DUMP_RS(D3DRENDERSTATE_ALPHAREF);
    _DUMP_RS(D3DRENDERSTATE_ALPHAFUNC);
    _DUMP_RS(D3DRENDERSTATE_DITHERENABLE);
    _DUMP_RS(D3DRENDERSTATE_ALPHABLENDENABLE);
    _DUMP_RS(D3DRENDERSTATE_FOGENABLE);
    _DUMP_RS(D3DRENDERSTATE_SPECULARENABLE);
    _DUMP_RS(D3DRENDERSTATE_ZVISIBLE);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEDALPHA);
    _DUMP_RS(D3DRENDERSTATE_FOGCOLOR);
    _DUMP_RS(D3DRENDERSTATE_FOGTABLEMODE);
    _DUMP_RS(D3DRENDERSTATE_FOGSTART);
    _DUMP_RS(D3DRENDERSTATE_FOGEND);
    _DUMP_RS(D3DRENDERSTATE_FOGDENSITY);
    _DUMP_RS(D3DRENDERSTATE_EDGEANTIALIAS);
    _DUMP_RS(D3DRENDERSTATE_COLORKEYENABLE);
    _DUMP_RS(D3DRENDERSTATE_ZBIAS);
    _DUMP_RS(D3DRENDERSTATE_RANGEFOGENABLE);
    _DUMP_RS(D3DRENDERSTATE_STENCILENABLE);
    _DUMP_RS(D3DRENDERSTATE_STENCILFAIL);
    _DUMP_RS(D3DRENDERSTATE_STENCILZFAIL);
    _DUMP_RS(D3DRENDERSTATE_STENCILPASS);
    _DUMP_RS(D3DRENDERSTATE_STENCILFUNC);
    _DUMP_RS(D3DRENDERSTATE_STENCILREF);
    _DUMP_RS(D3DRENDERSTATE_STENCILMASK);
    _DUMP_RS(D3DRENDERSTATE_STENCILWRITEMASK);
    _DUMP_RS(D3DRENDERSTATE_TEXTUREFACTOR);
    _DUMP_RS(D3DRENDERSTATE_WRAP0);
    _DUMP_RS(D3DRENDERSTATE_WRAP1);
    _DUMP_RS(D3DRENDERSTATE_WRAP2);
    _DUMP_RS(D3DRENDERSTATE_WRAP3);
    _DUMP_RS(D3DRENDERSTATE_WRAP4);
    _DUMP_RS(D3DRENDERSTATE_WRAP5);
    _DUMP_RS(D3DRENDERSTATE_WRAP6);
    _DUMP_RS(D3DRENDERSTATE_WRAP7);
    _DUMP_RS(D3DRENDERSTATE_CLIPPING);
    _DUMP_RS(D3DRENDERSTATE_LIGHTING);
    _DUMP_RS(D3DRENDERSTATE_EXTENTS);
    _DUMP_RS(D3DRENDERSTATE_AMBIENT);
    _DUMP_RS(D3DRENDERSTATE_FOGVERTEXMODE);
    _DUMP_RS(D3DRENDERSTATE_COLORVERTEX);
    _DUMP_RS(D3DRENDERSTATE_LOCALVIEWER);
    _DUMP_RS(D3DRENDERSTATE_NORMALIZENORMALS);
    _DUMP_RS(D3DRENDERSTATE_COLORKEYBLENDENABLE);
    _DUMP_RS(D3DRENDERSTATE_DIFFUSEMATERIALSOURCE);
    _DUMP_RS(D3DRENDERSTATE_SPECULARMATERIALSOURCE);
    _DUMP_RS(D3DRENDERSTATE_AMBIENTMATERIALSOURCE);
    _DUMP_RS(D3DRENDERSTATE_EMISSIVEMATERIALSOURCE);
    _DUMP_RS(D3DRENDERSTATE_VERTEXBLEND);
    _DUMP_RS(D3DRENDERSTATE_CLIPPLANEENABLE);

#undef _DUMP_RS

    dumpViewport(writer, pDevice);

    dumpTextureStates(writer, pDevice);

    writer.endObject();
    writer.endMember(); // parameters
}

void
dumpDevice(StateWriter &writer, IDirect3DDevice7 *pDevice)
{
    dumpRenderstate(writer, pDevice);

    writer.beginMember("shaders");
    writer.beginObject();
    writer.endObject();
    writer.endMember(); // shaders

    dumpTextures(writer, pDevice);

    dumpFramebuffer(writer, pDevice);
}


} /* namespace d3dstate */
