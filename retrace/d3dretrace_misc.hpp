#pragma once

namespace d3dretrace {

void
setHDC(unsigned long long hdc_id, HDC hDC);

void
clearEnumSurfaces();

unsigned long long
getEnumSurface();

} // namespace d3dretrace
