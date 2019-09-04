#include "simulation/mesh.h"

mesh::mesh(std::vector < int > ids_, std::vector < float > vertices_) {
	ids = ids_;
	vertices = vertices_;
}

mesh::mesh(std::initializer_list < mesh > other_meshes) {

	size_t id_offset = 0;
	ids = std::vector < int >();
	vertices = std::vector < float >();

	size_t nids = 0;
	size_t nvertices = 0;

	for (auto m : other_meshes) {
		nids += m.ids.size();
		nvertices += m.vertices.size();
	}

	ids.reserve(nids);
	vertices.reserve(nvertices);

	for (auto m : other_meshes) {

		for (int i = 0; i < m.ids.size(); i++) {
			ids.push_back(m.ids[i] + int(id_offset));
		}

		for (int i = 0; i < m.vertices.size(); i++) {
			vertices.push_back(m.vertices[i]);
		}

		id_offset += m.vertices.size() / 3;

	}

}

mesh mesh::transform(mat3 A) {

	mesh transformed(ids, vertices);

	size_t n = vertices.size() / 3;
	for (int i = 0; i < n; i++) {
		vec3 v{ vertices[i * 3 + 0], vertices[i * 3 + 1], vertices[i * 3 + 2] };
		v = dot(A, v);
		transformed.vertices[i * 3 + 0] = v[0];
		transformed.vertices[i * 3 + 1] = v[1];
		transformed.vertices[i * 3 + 2] = v[2];
	}

	// for transformations that flip things 
	// inside-out, change triangle winding
	if (det(A) < 0.0f) {
		n = ids.size() / 3;
		for (int i = 0; i < n; i++) {
			transformed.ids[i * 3 + 0] = ids[i * 3 + 1];
			transformed.ids[i * 3 + 1] = ids[i * 3 + 0];
			transformed.ids[i * 3 + 2] = ids[i * 3 + 2];
		}
	}

	return transformed;

}

mesh mesh::translate(vec3 p) {

	mesh translated(ids, vertices);

	size_t n = translated.vertices.size() / 3;
	for (int i = 0; i < n; i++) {
		translated.vertices[i * 3 + 0] += p[0];
		translated.vertices[i * 3 + 1] += p[1];
		translated.vertices[i * 3 + 2] += p[2];
	}

	return translated;

}

std::vector < tri > mesh::to_triangles() {

	std::vector < tri > triangles(ids.size() / 3);
	for (int i = 0; i < triangles.size(); i++) {
		for (int j = 0; j < 3; j++) {
			int id = ids[i * 3 + j];
			triangles[i].p[j] = vec3{ vertices[id * 3 + 0], vertices[id * 3 + 1], vertices[id * 3 + 2] };
		}
	}

	return triangles;

}
