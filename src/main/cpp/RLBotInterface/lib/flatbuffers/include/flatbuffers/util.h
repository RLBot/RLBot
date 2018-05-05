/*
 * Copyright 2014 Google Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef FLATBUFFERS_UTIL_H_
#define FLATBUFFERS_UTIL_H_

#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#ifdef _WIN32
#  ifndef WIN32_LEAN_AND_MEAN
#    define WIN32_LEAN_AND_MEAN
#  endif
#  ifndef NOMINMAX
#    define NOMINMAX
#  endif
#  include <windows.h>  // Must be included before <direct.h>
#  include <direct.h>
#  include <winbase.h>
#  undef interface  // This is also important because of reasons
#else
#  include <limits.h>
#endif
#include <sys/stat.h>
#include <sys/types.h>

#include "flatbuffers/base.h"

namespace flatbuffers {

// Convert an integer or floating point value to a string.
// In contrast to std::stringstream, "char" values are
// converted to a string of digits, and we don't use scientific notation.
template<typename T> std::string NumToString(T t) {
  std::stringstream ss;
  ss << t;
  return ss.str();
}
// Avoid char types used as character data.
template<> inline std::string NumToString<signed char>(signed char t) {
  return NumToString(static_cast<int>(t));
}
template<> inline std::string NumToString<unsigned char>(unsigned char t) {
  return NumToString(static_cast<int>(t));
}
#if defined(FLATBUFFERS_CPP98_STL)
template<> inline std::string NumToString<long long>(long long t) {
  char buf[21];  // (log((1 << 63) - 1) / log(10)) + 2
  snprintf(buf, sizeof(buf), "%lld", t);
  return std::string(buf);
}

template<>
inline std::string NumToString<unsigned long long>(unsigned long long t) {
  char buf[22];  // (log((1 << 63) - 1) / log(10)) + 1
  snprintf(buf, sizeof(buf), "%llu", t);
  return std::string(buf);
}
#endif  // defined(FLATBUFFERS_CPP98_STL)

// Special versions for floats/doubles.
template<typename T> std::string FloatToString(T t, int precision) {
  // to_string() prints different numbers of digits for floats depending on
  // platform and isn't available on Android, so we use stringstream
  std::stringstream ss;
  // Use std::fixed to surpress scientific notation.
  ss << std::fixed;
  // Default precision is 6, we want that to be higher for doubles.
  ss << std::setprecision(precision);
  ss << t;
  auto s = ss.str();
  // Sadly, std::fixed turns "1" into "1.00000", so here we undo that.
  auto p = s.find_last_not_of('0');
  if (p != std::string::npos) {
    // Strip trailing zeroes. If it is a whole number, keep one zero.
    s.resize(p + (s[p] == '.' ? 2 : 1));
  }
  return s;
}

template<> inline std::string NumToString<double>(double t) {
  return FloatToString(t, 12);
}
template<> inline std::string NumToString<float>(float t) {
  return FloatToString(t, 6);
}

// Convert an integer value to a hexadecimal string.
// The returned string length is always xdigits long, prefixed by 0 digits.
// For example, IntToStringHex(0x23, 8) returns the string "00000023".
inline std::string IntToStringHex(int i, int xdigits) {
  std::stringstream ss;
  ss << std::setw(xdigits) << std::setfill('0') << std::hex << std::uppercase
     << i;
  return ss.str();
}

// Portable implementation of strtoll().
inline int64_t StringToInt(const char *str, char **endptr = nullptr,
                           int base = 10) {
  // clang-format off
  #ifdef _MSC_VER
    return _strtoi64(str, endptr, base);
  #else
    return strtoll(str, endptr, base);
  #endif
  // clang-format on
}

// Portable implementation of strtoull().
inline uint64_t StringToUInt(const char *str, char **endptr = nullptr,
                             int base = 10) {
  // clang-format off
  #ifdef _MSC_VER
    return _strtoui64(str, endptr, base);
  #else
    return strtoull(str, endptr, base);
  #endif
  // clang-format on
}

typedef bool (*LoadFileFunction)(const char *filename, bool binary,
                                 std::string *dest);
typedef bool (*FileExistsFunction)(const char *filename);

LoadFileFunction SetLoadFileFunction(LoadFileFunction load_file_function);

FileExistsFunction SetFileExistsFunction(
    FileExistsFunction file_exists_function);

// Check if file "name" exists.
bool FileExists(const char *name);

// Check if "name" exists and it is also a directory.
bool DirExists(const char *name);

// Load file "name" into "buf" returning true if successful
// false otherwise.  If "binary" is false data is read
// using ifstream's text mode, otherwise data is read with
// no transcoding.
bool LoadFile(const char *name, bool binary, std::string *buf);

// Save data "buf" of length "len" bytes into a file
// "name" returning true if successful, false otherwise.
// If "binary" is false data is written using ifstream's
// text mode, otherwise data is written with no
// transcoding.
inline bool SaveFile(const char *name, const char *buf, size_t len,
                     bool binary) {
  std::ofstream ofs(name, binary ? std::ofstream::binary : std::ofstream::out);
  if (!ofs.is_open()) return false;
  ofs.write(buf, len);
  return !ofs.bad();
}

// Save data "buf" into file "name" returning true if
// successful, false otherwise.  If "binary" is false
// data is written using ifstream's text mode, otherwise
// data is written with no transcoding.
inline bool SaveFile(const char *name, const std::string &buf, bool binary) {
  return SaveFile(name, buf.c_str(), buf.size(), binary);
}

// Functionality for minimalistic portable path handling.

// The functions below behave correctly regardless of whether posix ('/') or
// Windows ('/' or '\\') separators are used.

// Any new separators inserted are always posix.

// We internally store paths in posix format ('/'). Paths supplied
// by the user should go through PosixPath to ensure correct behavior
// on Windows when paths are string-compared.

static const char kPathSeparator = '/';
static const char kPathSeparatorWindows = '\\';
static const char *PathSeparatorSet = "\\/";  // Intentionally no ':'

// Returns the path with the extension, if any, removed.
inline std::string StripExtension(const std::string &filepath) {
  size_t i = filepath.find_last_of(".");
  return i != std::string::npos ? filepath.substr(0, i) : filepath;
}

// Returns the extension, if any.
inline std::string GetExtension(const std::string &filepath) {
  size_t i = filepath.find_last_of(".");
  return i != std::string::npos ? filepath.substr(i + 1) : "";
}

// Return the last component of the path, after the last separator.
inline std::string StripPath(const std::string &filepath) {
  size_t i = filepath.find_last_of(PathSeparatorSet);
  return i != std::string::npos ? filepath.substr(i + 1) : filepath;
}

// Strip the last component of the path + separator.
inline std::string StripFileName(const std::string &filepath) {
  size_t i = filepath.find_last_of(PathSeparatorSet);
  return i != std::string::npos ? filepath.substr(0, i) : "";
}

// Concatenates a path with a filename, regardless of wether the path
// ends in a separator or not.
inline std::string ConCatPathFileName(const std::string &path,
                                      const std::string &filename) {
  std::string filepath = path;
  if (filepath.length()) {
    char &filepath_last_character = string_back(filepath);
    if (filepath_last_character == kPathSeparatorWindows) {
      filepath_last_character = kPathSeparator;
    } else if (filepath_last_character != kPathSeparator) {
      filepath += kPathSeparator;
    }
  }
  filepath += filename;
  // Ignore './' at the start of filepath.
  if (filepath[0] == '.' && filepath[1] == kPathSeparator) {
    filepath.erase(0, 2);
  }
  return filepath;
}

// Replaces any '\\' separators with '/'
inline std::string PosixPath(const char *path) {
  std::string p = path;
  std::replace(p.begin(), p.end(), '\\', '/');
  return p;
}

// This function ensure a directory exists, by recursively
// creating dirs for any parts of the path that don't exist yet.
inline void EnsureDirExists(const std::string &filepath) {
  auto parent = StripFileName(filepath);
  if (parent.length()) EnsureDirExists(parent);
    // clang-format off
  #ifdef _WIN32
    (void)_mkdir(filepath.c_str());
  #else
    mkdir(filepath.c_str(), S_IRWXU|S_IRGRP|S_IXGRP);
  #endif
  // clang-format on
}

// Obtains the absolute path from any other path.
// Returns the input path if the absolute path couldn't be resolved.
inline std::string AbsolutePath(const std::string &filepath) {
  // clang-format off
  #ifdef FLATBUFFERS_NO_ABSOLUTE_PATH_RESOLUTION
    return filepath;
  #else
    #ifdef _WIN32
      char abs_path[MAX_PATH];
      return GetFullPathNameA(filepath.c_str(), MAX_PATH, abs_path, nullptr)
    #else
      char abs_path[PATH_MAX];
      return realpath(filepath.c_str(), abs_path)
    #endif
      ? abs_path
      : filepath;
  #endif // FLATBUFFERS_NO_ABSOLUTE_PATH_RESOLUTION
  // clang-format on
}

// To and from UTF-8 unicode conversion functions

// Convert a unicode code point into a UTF-8 representation by appending it
// to a string. Returns the number of bytes generated.
inline int ToUTF8(uint32_t ucc, std::string *out) {
  assert(!(ucc & 0x80000000));  // Top bit can't be set.
  // 6 possible encodings: http://en.wikipedia.org/wiki/UTF-8
  for (int i = 0; i < 6; i++) {
    // Max bits this encoding can represent.
    uint32_t max_bits = 6 + i * 5 + static_cast<int>(!i);
    if (ucc < (1u << max_bits)) {  // does it fit?
      // Remaining bits not encoded in the first byte, store 6 bits each
      uint32_t remain_bits = i * 6;
      // Store first byte:
      (*out) += static_cast<char>((0xFE << (max_bits - remain_bits)) |
                                  (ucc >> remain_bits));
      // Store remaining bytes:
      for (int j = i - 1; j >= 0; j--) {
        (*out) += static_cast<char>(((ucc >> (j * 6)) & 0x3F) | 0x80);
      }
      return i + 1;  // Return the number of bytes added.
    }
  }
  assert(0);  // Impossible to arrive here.
  return -1;
}

// Converts whatever prefix of the incoming string corresponds to a valid
// UTF-8 sequence into a unicode code. The incoming pointer will have been
// advanced past all bytes parsed.
// returns -1 upon corrupt UTF-8 encoding (ignore the incoming pointer in
// this case).
inline int FromUTF8(const char **in) {
  int len = 0;
  // Count leading 1 bits.
  for (int mask = 0x80; mask >= 0x04; mask >>= 1) {
    if (**in & mask) {
      len++;
    } else {
      break;
    }
  }
  if ((static_cast<const unsigned char>(**in) << len) & 0x80) return -1;  // Bit after leading 1's must be 0.
  if (!len) return *(*in)++;
  // UTF-8 encoded values with a length are between 2 and 4 bytes.
  if (len < 2 || len > 4) { return -1; }
  // Grab initial bits of the code.
  int ucc = *(*in)++ & ((1 << (7 - len)) - 1);
  for (int i = 0; i < len - 1; i++) {
    if ((**in & 0xC0) != 0x80) return -1;  // Upper bits must 1 0.
    ucc <<= 6;
    ucc |= *(*in)++ & 0x3F;  // Grab 6 more bits of the code.
  }
  // UTF-8 cannot encode values between 0xD800 and 0xDFFF (reserved for
  // UTF-16 surrogate pairs).
  if (ucc >= 0xD800 && ucc <= 0xDFFF) { return -1; }
  // UTF-8 must represent code points in their shortest possible encoding.
  switch (len) {
    case 2:
      // Two bytes of UTF-8 can represent code points from U+0080 to U+07FF.
      if (ucc < 0x0080 || ucc > 0x07FF) { return -1; }
      break;
    case 3:
      // Three bytes of UTF-8 can represent code points from U+0800 to U+FFFF.
      if (ucc < 0x0800 || ucc > 0xFFFF) { return -1; }
      break;
    case 4:
      // Four bytes of UTF-8 can represent code points from U+10000 to U+10FFFF.
      if (ucc < 0x10000 || ucc > 0x10FFFF) { return -1; }
      break;
  }
  return ucc;
}

// Wraps a string to a maximum length, inserting new lines where necessary. Any
// existing whitespace will be collapsed down to a single space. A prefix or
// suffix can be provided, which will be inserted before or after a wrapped
// line, respectively.
inline std::string WordWrap(const std::string in, size_t max_length,
                            const std::string wrapped_line_prefix,
                            const std::string wrapped_line_suffix) {
  std::istringstream in_stream(in);
  std::string wrapped, line, word;

  in_stream >> word;
  line = word;

  while (in_stream >> word) {
    if ((line.length() + 1 + word.length() + wrapped_line_suffix.length()) <
        max_length) {
      line += " " + word;
    } else {
      wrapped += line + wrapped_line_suffix + "\n";
      line = wrapped_line_prefix + word;
    }
  }
  wrapped += line;

  return wrapped;
}

inline bool EscapeString(const char *s, size_t length, std::string *_text,
                         bool allow_non_utf8) {
  std::string &text = *_text;
  text += "\"";
  for (uoffset_t i = 0; i < length; i++) {
    char c = s[i];
    switch (c) {
      case '\n': text += "\\n"; break;
      case '\t': text += "\\t"; break;
      case '\r': text += "\\r"; break;
      case '\b': text += "\\b"; break;
      case '\f': text += "\\f"; break;
      case '\"': text += "\\\""; break;
      case '\\': text += "\\\\"; break;
      default:
        if (c >= ' ' && c <= '~') {
          text += c;
        } else {
          // Not printable ASCII data. Let's see if it's valid UTF-8 first:
          const char *utf8 = s + i;
          int ucc = FromUTF8(&utf8);
          if (ucc < 0) {
            if (allow_non_utf8) {
              text += "\\x";
              text += IntToStringHex(static_cast<uint8_t>(c), 2);
            } else {
              // There are two cases here:
              //
              // 1) We reached here by parsing an IDL file. In that case,
              // we previously checked for non-UTF-8, so we shouldn't reach
              // here.
              //
              // 2) We reached here by someone calling GenerateText()
              // on a previously-serialized flatbuffer. The data might have
              // non-UTF-8 Strings, or might be corrupt.
              //
              // In both cases, we have to give up and inform the caller
              // they have no JSON.
              return false;
            }
          } else {
            if (ucc <= 0xFFFF) {
              // Parses as Unicode within JSON's \uXXXX range, so use that.
              text += "\\u";
              text += IntToStringHex(ucc, 4);
            } else if (ucc <= 0x10FFFF) {
              // Encode Unicode SMP values to a surrogate pair using two \u
              // escapes.
              uint32_t base = ucc - 0x10000;
              auto high_surrogate = (base >> 10) + 0xD800;
              auto low_surrogate = (base & 0x03FF) + 0xDC00;
              text += "\\u";
              text += IntToStringHex(high_surrogate, 4);
              text += "\\u";
              text += IntToStringHex(low_surrogate, 4);
            }
            // Skip past characters recognized.
            i = static_cast<uoffset_t>(utf8 - s - 1);
          }
        }
        break;
    }
  }
  text += "\"";
  return true;
}

}  // namespace flatbuffers

#endif  // FLATBUFFERS_UTIL_H_
