#pragma once

#include "primitives.h"

#include <vector>

template < typename T >
class bvh {

	struct bvh_node {
		aabb box;
		uint64_t code;
		int32_t left() const { return int32_t(code >> 32); }
		int32_t right() const { return int32_t(code & 0xFFFFFFFF); }
	};

public:

	aabb global;
	uint64_t mask;
	size_t num_leaves;

	std::vector < bvh_node > nodes;

	std::vector < int2 > ranges;
	std::vector < int32_t > ready;
	std::vector < int32_t > parents;
	std::vector < int32_t > siblings;
	std::vector < uint64_t > code_ids;
	std::vector < T > primitives;

	bvh() {};
	bvh(const std::vector < T > &);

	template < typename S >
	std::vector < int > intersect(const S &) const;

private:

	void build_radix_tree();
	void fit_bounding_boxes();

};
