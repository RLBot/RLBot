#pragma once

#include <intrin.h>

inline uint64_t pack64(uint64_t a, uint64_t b, uint32_t shift = 32) {
	return ((uint64_t(a) << shift) | uint64_t(b));
}

inline uint64_t unpack64_msb(uint64_t ab, uint64_t shift = 32) {
	uint64_t mask = (uint64_t(1) << shift) - 1;
	return ((ab >> shift) & mask);
}

inline uint64_t unpack64_lsb(uint64_t ab, uint32_t shift = 32) {
	uint64_t mask = (uint64_t(1) << shift) - 1;
	return (ab & mask);
}

inline uint32_t pack32(uint16_t a, uint16_t b, uint32_t shift = 16) {
	return ((uint64_t(a) << shift) | uint64_t(b));
}

inline uint32_t unpack32_msb(uint32_t ab, uint32_t shift = 16) {
	uint32_t mask = (uint32_t(1) << shift) - 1;
	return ((ab >> shift) & mask);
}

inline uint32_t unpack32_lsb(uint32_t ab, uint32_t shift = 16) {
	uint32_t mask = (uint32_t(1) << shift) - 1;
	return (ab & mask);
}

inline uint32_t clz(uint32_t n) {
	unsigned long index;
	unsigned char isNonzero = _BitScanReverse(&index, n);
	return uint32_t(isNonzero ? 31 - index : 32);
}

inline uint32_t clz(uint64_t n) {

#if 0
	return uint32_t(__lzcnt64(n));
#else
	uint32_t llz = clz(uint32_t(unpack64_msb(n)));
	uint32_t rlz = clz(uint32_t(unpack64_lsb(n)));

	return llz + (llz == 32) * rlz;
#endif

}

inline uint32_t bits_needed(uint32_t n) {
	return 32 - clz(n);
}
