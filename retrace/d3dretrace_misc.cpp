/**************************************************************************
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
#include <string.h>

#include <algorithm>
#include <iostream>
#include <list>

#include "retrace.hpp"
#include "retrace_swizzle.hpp"
#include "d3dretrace.hpp"
#include "d3dretrace_misc.hpp"

#include "d3dimports.hpp"

namespace d3dretrace {

typedef std::map<unsigned long long, HDC> HDCMap;
static HDCMap hdc_map;
static std::list<unsigned long long> enumSurfaces;

void
setHDC(unsigned long long hdc_id, HDC hDC) {
    if (hdc_id == 0) {
        return;
    }

    if (hDC) {
        hdc_map[hdc_id] = hDC;
    } else {
        hdc_map.erase(hdc_id);
    }
}

static HDC
getHDC(unsigned long long hdc_id) {
    if (hdc_id == 0) {
        return NULL;
    }

    HDCMap::const_iterator it;
    it = hdc_map.find(hdc_id);
    if (it == hdc_map.end()) {
        return NULL;
    }

    return it->second;
}

unsigned long long
getEnumSurface() {
    unsigned long long result = enumSurfaces.front();
    enumSurfaces.pop_front();

    return result;
}

void
clearEnumSurfaces() {
    enumSurfaces.clear();
}

static void
retrace_bitblt(trace::Call& call)
{
    HDC hDC = getHDC(call.arg(0).toUInt());
    if (!hDC) {
        os::log("bitblt: received unmapped HDC\n");
        return;
    }

    retrace::Range srcRange;
    retrace::toRange(call.arg(1), srcRange);

    size_t n = call.arg(2).toUInt();

    HBITMAP hBmpSrc = (HBITMAP)GetCurrentObject(hDC, OBJ_BITMAP);
    if (!hBmpSrc) {
        os::log("bitblt: failed to get source bitmap\n");
        return;
    }

    BITMAP bm;
    GetObject(hBmpSrc, sizeof(bm), &bm);

    BITMAPINFO bmi{ 0 };
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = bm.bmWidth;
    bmi.bmiHeader.biHeight = bm.bmHeight;
    bmi.bmiHeader.biPlanes = bm.bmPlanes;
    bmi.bmiHeader.biBitCount = bm.bmBitsPixel;
    bmi.bmiHeader.biCompression = BI_RGB;

    void* pBits = NULL;
    HDC mDC = CreateCompatibleDC(hDC);
    if (!mDC) {
        os::log("bitblt: failed to get compatible DC\n");
        return;
    }

    HBITMAP hBmp = CreateDIBSection(mDC, &bmi, DIB_RGB_COLORS, &pBits, NULL, 0);
    if (!hBmp) {
        os::log("bitblt: failed to get compatible bitmap\n");
        return;
    }

    SelectObject(mDC, hBmp);

    size_t bitsSize = bm.bmWidth * bm.bmHeight * (bm.bmBitsPixel / 8);
    if (n > bitsSize) {
        retrace::warning(call) << "bitblt: dest buffer overflow of " << n - bitsSize << " bytes\n";
    }

    if (n > srcRange.len) {
        retrace::warning(call) << "bitblt: src buffer overflow of " << n - srcRange.len << " bytes\n";
    }

    n = std::min(n, bitsSize);
    n = std::min(n, srcRange.len);

    memcpy(pBits, srcRange.ptr, n);

    BitBlt(hDC, 0, 0, bm.bmWidth, bm.bmHeight, mDC, 0, 0, SRCCOPY);

    DeleteObject(hBmp);
    DeleteDC(mDC);
}

static void
retrace_enumsurfacescallback(trace::Call& call)
{
    unsigned long long origSurface = call.arg(2).toUInt();
    if (origSurface) {
        enumSurfaces.push_back(origSurface);
    }
}

static void
retrace_executebufferdump(trace::Call& call)
{
}

const retrace::Entry ddraw_misc_callbacks[] = {
    { "bitblt", &retrace_bitblt },
    { "enumsurfacescallback", &retrace_enumsurfacescallback },
    { "executebufferdump", &retrace_executebufferdump },
    { NULL, NULL },
};

}