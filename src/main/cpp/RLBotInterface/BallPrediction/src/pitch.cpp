#include "..\inc\pitch.h"

#include <sstream>
#include <fstream>
#include <iostream>
#include <Windows.h>
#include <filesystem>


Pitch::Pitch() {

	std::string tempDir = std::experimental::filesystem::temp_directory_path().string();
	std::string filename = tempDir.append("rlbot-pitch.dat");

	printf("Looking for: %s\n", filename.c_str());

	std::ifstream infile(filename);

	tri t;
	std::string line;

	while (std::getline(infile, line)) {       
  
		std::stringstream ss(line); 

		ss >> t.p[0][0]; 
		ss >> t.p[0][1]; 
		ss >> t.p[0][2];
  
		ss >> t.p[1][0];
		ss >> t.p[1][1];
		ss >> t.p[1][2];
  
		ss >> t.p[2][0];
		ss >> t.p[2][1];
		ss >> t.p[2][2];
  
		triangles.push_back(t);
  
	}


	std::cout << "successfully read " << triangles.size() << " triangles" << std::endl;

	mesh = bvh < tri >(triangles); 

	std::cout << "successfully constructed bvh" << std::endl;

}

bool Pitch::in_contact_with(const sphere & s) {

  hits = mesh.intersect(s);
  return hits.size() > 0;

}

bool Pitch::in_contact_with(const obb & o) {

  hits = mesh.intersect(o);
  return hits.size() > 0;

}

ray Pitch::last_contact_info() {

	float count = 0;
	vec3 pos{0.0f, 0.0f, 0.0f};
	vec3 normal{0.0f, 0.0f, 0.0f};

	for (int i = 0; i < hits.size(); i++) {
		normal += triangles[hits[i]].unit_normal();
		pos += triangles[hits[i]].center();
		count++;
	}

	return ray{pos / count, normalize(normal)};

}
