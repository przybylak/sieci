#pragma once
// Minimal Linux shim so Caprica (MSVC-only upstream) can be built for syntax checking.
#include <cstring>
#include <strings.h>
#include <cstdint>
#include <string>
#include <x86intrin.h>
#define _stricmp strcasecmp
#define _strnicmp strncasecmp
#define _byteswap_ushort __builtin_bswap16
#define _byteswap_ulong __builtin_bswap32
#define _byteswap_uint64 __builtin_bswap64
#define __declspec(x)
#define __forceinline inline __attribute__((always_inline))
