#pragma once
#include <fcntl.h>
#include <unistd.h>
#include <string>
#define _O_BINARY 0
#define _O_RDONLY O_RDONLY
#define _O_SEQUENTIAL 0
inline int _open(const char* p, int flags) { std::string s(p); for (auto& c : s) if (c == '\\') c = '/'; return open(s.c_str(), flags); }
#define _read read
#define _close close
inline int _eof(int fd) { off_t cur = lseek(fd, 0, SEEK_CUR); off_t end = lseek(fd, 0, SEEK_END); lseek(fd, cur, SEEK_SET); return cur >= end ? 1 : 0; }
