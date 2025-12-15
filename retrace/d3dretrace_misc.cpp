#include <assert.h>
#include <string.h>

#include <iostream>
#include <algorithm>

#include "retrace.hpp"
#include "retrace_swizzle.hpp"
#include "d3dretrace.hpp"
#include "d3dretrace_misc.hpp"

namespace d3dretrace {

typedef std::map<unsigned long long, HDC> HDCMap;
static HDCMap hdc_map;

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

const retrace::Entry ddraw_misc_callbacks[] = {
    { "bitblt", &retrace_bitblt },
    { NULL, NULL },
};

}