#include "..\inc\bvh.h"
#include "..\inc\timer.h"
#include "..\inc\morton.h"
#include "..\inc\bit_packing.h"

#include <algorithm>

std::vector < uint64_t > morton_sort(
    const std::vector < aabb > & boxes, 
    const aabb & global) {

  constexpr size_t dim = 3;

  uint32_t num_boxes = uint32_t(boxes.size());
  float x_offset = global.min_x;
  float y_offset = global.min_y;
  float z_offset = global.min_z;

  int b = bits_needed(num_boxes);
  int bits_per_dimension = (64 - b) / dim;
  int divisions_per_dimension = 1 << bits_per_dimension;

  float scale = float(divisions_per_dimension - 1);

  float x_scale = scale / (global.max_x - global.min_x);
  float y_scale = scale / (global.max_y - global.min_y);
  float z_scale = scale / (global.max_z - global.min_z);

  std::vector < uint64_t > code_ids(num_boxes);

  for (uint32_t i = 0; i < num_boxes; i++) {

    aabb box = boxes[i];

    // get the centroid of the ith bounding box
    float cx = 0.5f * (box.min_x + box.max_x);
    float cy = 0.5f * (box.min_y + box.max_y);
    float cz = 0.5f * (box.min_z + box.max_z);

    uint64_t ux = (uint64_t)((cx - x_offset) * x_scale);
    uint64_t uy = (uint64_t)((cy - y_offset) * y_scale);
    uint64_t uz = (uint64_t)((cz - z_offset) * z_scale);

    uint64_t code = morton::encode(ux, uy, uz); 

    code_ids[i] = (code << b) + uint64_t(i);

  }

  std::sort(code_ids.begin(), code_ids.end());

  return code_ids;

}

// convenience class for bounds checking morton codes,
// and computing the number of prefix bits common to two 
// 64-bit words
class PrefixComparator{

  public:

    const uint64_t   base;
    const uint64_t * codes;
    const int        n;

    PrefixComparator(const uint64_t   _base,
                     const uint64_t * _codes,
                     const int        _n) :
      base(_base), codes(_codes), n(_n){}

    inline int operator()(int i){
      return (i >= 0 && i < n) ? clz(base ^ codes[i]) : -1;
    }

};

template < typename T >
void bvh< T >::build_radix_tree() {

  parents[num_leaves] = num_leaves;

  for (int i = 0; i < num_leaves - 1; i++) {

    PrefixComparator shared_prefix(code_ids[i], &code_ids[0], num_leaves);

    // Choose search direction.
    int prefix_prev = shared_prefix(i-1);
    int prefix_next = shared_prefix(i+1);
    int prefix_min = std::min(prefix_prev, prefix_next);

    int d = (prefix_next > prefix_prev) ? 1 : -1;

    // Find upper bound for length.
    int lmax = 32;
    uint32_t probe;
    do{
      lmax <<= 2;
      probe = i + lmax * d;
    } while ((probe < num_leaves) && (shared_prefix(probe) > prefix_min));

    // Determine length.
    int l = 0;
    for(int t = lmax >> 1; t > 0; t >>= 1){
      probe = i + (l + t) * d;
      if (probe < num_leaves & shared_prefix(probe) > prefix_min) {
        l += t;
      }
    }
    int j = i + l * d;
    int prefix_node = shared_prefix(j);

    // Find split point.
    int s = 0;
    int t = l;
    do{
      t = (t + 1) >> 1;
      probe = i + (s + t) * d;
      if (probe < num_leaves && shared_prefix(probe) > prefix_node) {
        s += t;
      }
    } while (t > 1);
    int k = i + s * d + std::min(d, 0);

    // Output node.
    int32_t lo = std::min(i, j);
    int32_t hi = std::max(i, j);

    int32_t left  = (lo == k    ) ? k + 0 : (k + 0 + num_leaves);
    int32_t right = (hi == k + 1) ? k + 1 : (k + 1 + num_leaves);

    parents[left] = i + num_leaves;
    parents[right] = i + num_leaves;
    siblings[left] = right;
    siblings[right] = left;
    nodes[i + num_leaves].code = (uint64_t(left) << 32) + uint64_t(right);
    ranges[i + num_leaves] = int2{lo, hi};

  }

}

template < typename T >
void bvh< T >::fit_bounding_boxes() {

  for (int i = 0; i < ready.size(); i++) {
    ready[i] = 0;
  }

  for (int i = 0; i < num_leaves; i++) {

    // start with the bounds of the leaf nodes
    // and have each thread work its way up the tree
    int current = i;
    aabb box = nodes[i].box;
    int32_t parent = parents[i];
    int state = 0;

    while(true) {

      state = ready[parent]++;

      // only process a parent node if the other
      // sibling has visited the parent as well
      if (state != 1) break; 

      // compute the union of the two sibling boxes
      box = aabb(box, nodes[siblings[current]].box);

      // move up to the parent node
      current = parent;
      parent = parents[current];

      // and assign the new box to it
      nodes[current].box = box;

    }

  }

}

aabb global_aabb(const std::vector < aabb > & boxes) {

  aabb global_box = boxes[0];
  for (int i = 1; i < boxes.size(); i++) {
    global_box = aabb(global_box, boxes[i]);
  }
  return global_box;

}

template < typename T >
bvh< T >::bvh(const std::vector < T > & _primitives) {

  timer stopwatch;

  num_leaves = int(_primitives.size());

  primitives.resize(num_leaves);

  nodes.resize(2 * num_leaves - 1);
  ranges.resize(2 * num_leaves - 1);
  ready.resize(2 * num_leaves - 1);
  parents.resize(2 * num_leaves - 1);
  siblings.resize(2 * num_leaves - 1);

  mask = (uint64_t(1) << bits_needed(num_leaves)) - 1;

  std::vector < aabb > boxes(num_leaves);
  for (int i = 0; i < num_leaves; i++) {
    boxes[i] = aabb(_primitives[i]);
  }

  global = global_aabb(boxes);

  code_ids = morton_sort(boxes, global);

  for (int i = 0; i < num_leaves; i++) {
    uint32_t id = uint32_t(code_ids[i] & mask);
    primitives[i] = _primitives[id];
    nodes[i] = bvh_node{boxes[id], code_ids[i]};
  }

  build_radix_tree();
  fit_bounding_boxes();

}

template bvh< aabb >::bvh(const std::vector < aabb > &);
template bvh< tri >::bvh(const std::vector < tri > &);

template < typename T >
template < typename S >
std::vector < int > bvh< T >::intersect(const S & query_object) const {

  aabb query_box(query_object);

  std::vector < int > hits(0);

  // Allocate traversal stack from thread-local memory,
  // and push NULL to indicate that there are no postponed nodes.
  int   stack[32];
  int * stack_ptr = stack;
  *stack_ptr++ = -1;
  
  // Traverse nodes starting from the root.
  int n = num_leaves;
  do {

    // Check each child node for overlap.
    int left  = nodes[n].left();
    int right = nodes[n].right();

    bool overlap_left = ::intersect(nodes[left].box, query_box);
    if (overlap_left && (left < num_leaves)) {
      int left_id = int(nodes[left].code & mask);
      if (::intersect(primitives[left], query_object)) {
        hits.push_back(left_id);
      }
    }

    bool overlap_right = ::intersect(nodes[right].box, query_box);
    if (overlap_right && (right < num_leaves)) {
      int right_id = int(nodes[right].code & mask);
      if (::intersect(primitives[right], query_object)) {
        hits.push_back(right_id);
      }
    }

    // traverse when a query overlaps with an internal node
    bool traverse_left  = (overlap_left  && (left  >= num_leaves));
    bool traverse_right = (overlap_right && (right >= num_leaves));

    if (!traverse_left && !traverse_right) {
      n = *--stack_ptr; // pop
    } else {
      n = (traverse_left) ? left : right;
      if (traverse_left && traverse_right) {
        *stack_ptr++ = right; // push
      } 
    } 
  } while (n != -1);

  return hits;

}

template std::vector < int > bvh< tri >::intersect(const aabb &) const;
template std::vector < int > bvh< tri >::intersect(const obb &) const;
template std::vector < int > bvh< tri >::intersect(const sphere &) const;

template <>
template < typename S >
std::vector < int > bvh< aabb >::intersect(const S & query_object) const {

  std::vector < int > hits(0);

  // Allocate traversal stack from thread-local memory,
  // and push NULL to indicate that there are no postponed nodes.
  int   stack[32];
  int * stack_ptr = stack;
  *stack_ptr++ = -1;
  
  // Traverse nodes starting from the root.
  int n = num_leaves;
  do {

    // Check each child node for overlap.
    int left  = nodes[n].left();
    int right = nodes[n].right();

    bool overlap_left = ::intersect(nodes[left].box, query_object);
    if (overlap_left && (left < num_leaves)) {
      int left_id = int(nodes[left].code & mask);
      hits.push_back(left_id);
    }

    bool overlap_right = ::intersect(nodes[right].box, query_object);
    if (overlap_right && (right < num_leaves)) {
      int right_id = int(nodes[right].code & mask);
      hits.push_back(right_id);
    }

    // traverse when a query overlaps with an internal node
    bool traverse_left  = (overlap_left  && (left  >= num_leaves));
    bool traverse_right = (overlap_right && (right >= num_leaves));

    if (!traverse_left && !traverse_right) {
      n = *--stack_ptr; // pop
    } else {
      n = (traverse_left) ? left : right;
      if (traverse_left && traverse_right) {
        *stack_ptr++ = right; // push
      } 
    }
  } while (n != -1);

  return hits;

}

template std::vector < int > bvh< aabb >::intersect(const aabb &) const;
template std::vector < int > bvh< aabb >::intersect(const obb &) const;
template std::vector < int > bvh< aabb >::intersect(const sphere &) const;
