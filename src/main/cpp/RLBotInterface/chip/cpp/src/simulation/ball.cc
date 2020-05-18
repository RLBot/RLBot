#include "simulation/ball.h"
#include "simulation/field.h"

#include "misc/json.h"

const float Ball::restitution = 0.6f;
const float Ball::drag = -0.0305f;
const float Ball::mu = 2.0f;

const float Ball::v_max = 4000.0f;
const float Ball::w_max = 6.0f;

const float Ball::m = 30.0f;
const float Ball::soccar_radius = 91.25f;
const float Ball::hoops_radius = 91.25f;
const float Ball::dropshot_radius = 100.45f;
const float Ball::soccar_collision_radius = 93.15f;
const float Ball::hoops_collision_radius = 93.15f;
const float Ball::dropshot_collision_radius = 103.6f;

float Ball::radius = Ball::soccar_radius;
float Ball::collision_radius = Ball::soccar_collision_radius;
float Ball::I = 0.4f * Ball::m * Ball::radius * Ball::radius;
vec3 Ball::gravity = vec3{ 0.0, 0.0, -650.0f };
bool Ball::heatseeker_mode = false;
vec3 Ball::orange_goal{ 0.f, 5280.f, 100.f };
vec3 Ball::blue_goal{ 0.f, -5280.f, 100.f };

Ball::Ball() {
	time = 0.0f;
	position = vec3{ 0.0f, 0.0f, 1.1f * collision_radius };
	velocity = vec3{ 0.0f, 0.0f, 0.0f };
	angular_velocity = vec3{ 0.0f, 0.0f, 0.0f };
}

sphere Ball::hitbox() {
	return sphere{ position, collision_radius };
}

void Ball::perform_collision(ray contact, float dt) {
	vec3 p = contact.start;
	vec3 n = contact.direction;

	vec3 L = p - position;

	float m_reduced = 1.0f / ((1.0f / m) + dot(L, L) / I);

	vec3 v_perp = fminf(dot(velocity, n), 0.0f) * n;
	vec3 v_para = velocity - v_perp - cross(L, angular_velocity);

	float ratio = norm(v_perp) / fmaxf(norm(v_para), 0.0001f);

	vec3 J_perp = -(1.0f + restitution) * m * v_perp;
	vec3 J_para = -fminf(1.0f, mu * ratio) * m_reduced * v_para;

	vec3 J = J_perp + J_para;

	angular_velocity += cross(L, J) / I;
	velocity += (J / m) + drag * velocity * dt;
	position += velocity * dt;

	float penetration = collision_radius - dot(position - p, n);
	if (penetration > 0.0f) {
		position += 1.001f * penetration * n;
	}
}

void Ball::step(float dt) {

	if (heatseeker_mode) {
		step_heatseeker(dt);
	}

	ray contact = Field::collide(hitbox());

	if (norm(contact.direction) > 0.0) {
		if (contact.direction[1] > .99) {
			heatseeker_target = orange_goal;
		}
		else if (contact.direction[1] < -.99) {
			heatseeker_target = blue_goal;
		}
		perform_collision(contact, dt);
	}
	else {
		velocity += (drag * velocity + gravity) * dt;
		position += velocity * dt;
	}

	angular_velocity *= fminf(1.0, w_max / norm(angular_velocity));
	if (!heatseeker_mode)
	{
		velocity *= fminf(1.0, v_max / norm(velocity));
	}
	
	time += dt;
}


void Ball::step_heatseeker(float dt) {
	// Logic provided by Recruit_main707#8518 and GodGamer029#4765
	// https://discordapp.com/channels/348658686962696195/423167304956903428/702534700190924800

	float speed = norm(velocity);
	// The ball speed can be 3000, 3080, 3160, ... 4600. Snap to the nearest one
	int currentState = (((int)speed) - 3000 + 40) / 80;
	if (currentState < 0) {
		currentState = 0;
	}
	else if (currentState > 20) {
		currentState = 20;
	}
	float target_speed = currentState * 80 + 3000;

	float horizVal = currentState / 40.f + 1;
	float zVal = 1 / 1.5f;
	vec3 delta = normalize(heatseeker_target - position) * (target_speed * dt);
	delta[0] *= horizVal;
	delta[1] *= horizVal;
	delta[2] *= zVal;

	velocity += delta;
	velocity *= std::min(1.f, target_speed / speed);
}

vec3 closest_point_on_obb(const vec3 & v, const obb & hitbox) {
	vec3 v_local = dot(v - hitbox.center, hitbox.orientation);
	v_local[0] = clip(v_local[0], -hitbox.half_width[0], hitbox.half_width[0]);
	v_local[1] = clip(v_local[1], -hitbox.half_width[1], hitbox.half_width[1]);
	v_local[2] = clip(v_local[2], -hitbox.half_width[2], hitbox.half_width[2]);
	return dot(hitbox.orientation, v_local) + hitbox.center;
}

float scale(float dv) {
	const int n = 6;
	float values[n][2] = { {   0.0f, 0.65f},
						  { 500.0f, 0.65f},
						  {2300.0f, 0.55f},
						  {4600.0f, 0.30f} };

	float input = clip(dv, 0.0f, 4600.0f);

	for (int i = 0; i < (n - 1); i++) {
		if (values[i][0] <= input && input < values[i + 1][0]) {
			float u = (input - values[i][0]) / (values[i + 1][0] - values[i][0]);
			return lerp(values[i][1], values[i + 1][1], u);
		}
	}

	return -1.0f;
}

#if 0 // We don't want to compile more source files than we need to. This prevents us from compiling car.cc and files required by car.cc.
void Ball::step(float dt, const Car & c) {

	vec3 p = closest_point_on_obb(position, c.hitbox());

	if (norm(p - position) < collision_radius) {

    vec3 cx = c.position;
    vec3 cv = c.velocity;
    vec3 cw = c.angular_velocity;
    mat3 co = c.orientation;

		vec3 n1 = normalize(p - position);

		mat3 L_b = antisym(p - position);
		mat3 L_c = antisym(p - c.position);

		mat3 invI_c = dot(co, dot(c.invI, transpose(co)));

		mat3 M = inv(((1.0f / m) + (1.0f / c.m)) * eye<3>() - (dot(L_b, L_b) / I) - dot(L_c, dot(invI_c, L_c)));

		vec3 Delta_V = (cv - dot(L_c, cw)) - (velocity - dot(L_b, angular_velocity));

		// compute the impulse that is consistent with an inelastic collision
		vec3 J1 = dot(M, Delta_V);

		vec3 J1_perp = fminf(dot(J1, n1), -1.0) * n1;
		vec3 J1_para = J1 - J1_perp;

		float ratio = norm(J1_perp) / fmaxf(norm(J1_para), 0.001f);

		// scale the parallel component of J1 such that the
		// Coulomb friction model is satisfied
		J1 = J1_perp + fminf(1.0f, mu * ratio) * J1_para;


		vec3 f = c.forward();
		vec3 n2 = position - cx;
		n2[2] *= 0.35f;
		n2 = normalize(n2 - 0.35f * dot(n2, f) * f);

		float dv = fminf(norm(velocity - cv), 4600.0f);
		vec3 J2 = m * dv * scale(dv) * n2;

		angular_velocity += dot(L_b, J1) / I;
		velocity += (J1 + J2) / m;

	}

	step(dt);

}
#endif

std::string Ball::to_json() {
  return nlohmann::json{
    {"x", {position[0], position[1], position[2]}},
    {"v", {velocity[0], velocity[1], velocity[2]}},
    {"w", {angular_velocity[0], angular_velocity[1], angular_velocity[2]}}
  }.dump();
}

#ifdef GENERATE_PYTHON_BINDINGS
#include <pybind11/pybind11.h>
void init_ball(pybind11::module & m) {
	pybind11::class_<Ball>(m, "Ball")
		.def(pybind11::init<>())
		.def(pybind11::init<const Ball &>())
		.def_readwrite("location", &Ball::x)
		.def_readwrite("velocity", &Ball::v)
		.def_readwrite("angular_velocity", &Ball::w)
		.def_readwrite("time", &Ball::time)
		.def_readonly_static("restitution", &Ball::restitution)
		.def_readonly_static("drag", &Ball::drag)
		.def_readonly_static("friction", &Ball::mu)
		.def_readonly_static("mass", &Ball::m)
		.def_readonly_static("moment_of_inertia", &Ball::I)
		.def_readonly_static("max_speed", &Ball::v_max)
		.def_readonly_static("max_omega", &Ball::w_max)
		.def_readonly_static("radius", &Ball::radius)
		.def_readonly_static("collision_radius", &Ball::collision_radius)
		.def("hitbox", &Ball::hitbox)
		.def("to_json", &Ball::to_json)
		.def("step", static_cast<void (Ball::*)(float)>(&Ball::step))
		.def("step", static_cast<void (Ball::*)(float, const Car &)>(&Ball::step));
}
#endif
