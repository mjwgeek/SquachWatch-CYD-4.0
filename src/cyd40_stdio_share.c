// CYD40 flash budget: newlib links parallel integer-only and full
// stdio engines. The full engines implement the integer conversion
// subset too. Preserve all public stdio entry points and route only
// the three internal integer-only engines seen in the linked ELF audit.
// GNU ld --wrap redirects external references; it does not edit libc.
// Test both OTA images, formatting, scan parsing and hardware before release.
#if defined(CYD40)
#include <stdio.h>
#include <stdarg.h>
#include <reent.h>

extern int _vfprintf_r(struct _reent *, FILE *, const char *, va_list);
extern int _svfprintf_r(struct _reent *, FILE *, const char *, va_list);
extern int __ssvfscanf_r(struct _reent *, FILE *, const char *, va_list);

int __wrap__vfiprintf_r(struct _reent *r, FILE *f, const char *fmt, va_list ap) {
    return _vfprintf_r(r, f, fmt, ap);
}
int __wrap__svfiprintf_r(struct _reent *r, FILE *f, const char *fmt, va_list ap) {
    return _svfprintf_r(r, f, fmt, ap);
}
int __wrap___ssvfiscanf_r(struct _reent *r, FILE *f, const char *fmt, va_list ap) {
    return __ssvfscanf_r(r, f, fmt, ap);
}
#endif
