#pragma once
#include "wincompat.h"
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <signal.h>
#include <pwd.h>
typedef uint32_t DWORD;
typedef void* HANDLE;
typedef int BOOL;
#define INVALID_HANDLE_VALUE ((HANDLE)(intptr_t)-1)
#define MAX_COMPUTERNAME_LENGTH 255
#define UNLEN 256
#define FILE_ATTRIBUTE_DIRECTORY 0x10
struct FILETIME { DWORD dwLowDateTime; DWORD dwHighDateTime; };
union ULARGE_INTEGER { struct { DWORD LowPart; DWORD HighPart; }; uint64_t QuadPart; };
struct WIN32_FIND_DATA {
  DWORD dwFileAttributes;
  FILETIME ftLastWriteTime;
  DWORD nFileSizeLow;
  DWORD nFileSizeHigh;
  char cFileName[4096];
};
struct __FindState { DIR* dir; std::string base; };
inline bool __fillFind(__FindState* st, WIN32_FIND_DATA* d) {
  struct dirent* e = readdir(st->dir);
  if (!e) return false;
  std::strncpy(d->cFileName, e->d_name, sizeof(d->cFileName) - 1);
  d->cFileName[sizeof(d->cFileName) - 1] = 0;
  struct stat sb {};
  std::string full = st->base + "/" + e->d_name;
  stat(full.c_str(), &sb);
  d->dwFileAttributes = S_ISDIR(sb.st_mode) ? FILE_ATTRIBUTE_DIRECTORY : 0;
  ULARGE_INTEGER t; t.QuadPart = ((uint64_t)sb.st_mtime + 11644473600ULL) * 10000000ULL;
  d->ftLastWriteTime.dwLowDateTime = t.LowPart; d->ftLastWriteTime.dwHighDateTime = t.HighPart;
  ULARGE_INTEGER s; s.QuadPart = (uint64_t)sb.st_size;
  d->nFileSizeLow = s.LowPart; d->nFileSizeHigh = s.HighPart;
  return true;
}
inline HANDLE FindFirstFileA(const char* pattern, WIN32_FIND_DATA* d) {
  std::string p(pattern);
  for (auto& c : p) if (c == '\\') c = '/';
  if (p.size() >= 2 && p.substr(p.size() - 2) == "/*") p = p.substr(0, p.size() - 2);
  DIR* dir = opendir(p.c_str());
  if (!dir) return INVALID_HANDLE_VALUE;
  auto st = new __FindState { dir, p };
  if (!__fillFind(st, d)) { closedir(dir); delete st; return INVALID_HANDLE_VALUE; }
  return st;
}
inline BOOL FindNextFileA(HANDLE h, WIN32_FIND_DATA* d) { return __fillFind((__FindState*)h, d); }
inline BOOL FindClose(HANDLE h) { auto st = (__FindState*)h; closedir(st->dir); delete st; return 1; }
inline BOOL GetComputerNameA(char* buf, DWORD* len) { std::strcpy(buf, "linux"); *len = 5; return 1; }
inline BOOL GetUserNameA(char* buf, DWORD* len) { std::strcpy(buf, "user"); *len = 5; return 1; }
inline BOOL IsDebuggerPresent() { return 0; }
#define __debugbreak() raise(SIGTRAP)
