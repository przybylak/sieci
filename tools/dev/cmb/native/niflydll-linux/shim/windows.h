// Stand-in for <windows.h> so PyNifly's NiflyDLL sources build on Linux (Commonwealth Motorbike asset tools).
// Only what NiflyDLL/framework.h users need: FindProjectRoot() in NiflyFunctions.cpp asks which file the
// library was loaded from (the skeletons folder is looked up beside it).
#pragma once
#include <dlfcn.h>
#include <climits>
#include <cstring>
#include <cstdint>

#ifndef MAX_PATH
#define MAX_PATH PATH_MAX
#endif
typedef void* HMODULE;
typedef const char* LPCSTR;
typedef char* LPSTR;
typedef int BOOL;
typedef unsigned long DWORD;
#define GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS 0x4
#define GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT 0x2

// The "module handle" is the address asked about; GetModuleFileNameA resolves it with dladdr.
static inline BOOL GetModuleHandleExA(DWORD, LPCSTR address, HMODULE* out) {
    *out = const_cast<void*>(static_cast<const void*>(address));
    return address != nullptr;
}
static inline DWORD GetModuleFileNameA(HMODULE h, LPSTR buf, DWORD len) {
    Dl_info info;
    if (!h || !dladdr(h, &info) || !info.dli_fname || len == 0) return 0;
    std::strncpy(buf, info.dli_fname, len - 1);
    buf[len - 1] = 0;
    return static_cast<DWORD>(std::strlen(buf));
}
