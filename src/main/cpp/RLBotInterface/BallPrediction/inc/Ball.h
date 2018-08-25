#pragma once

#include "DynamicState.h"

#include "pitch.h"

class Ball {

	static constexpr float ball_radius = 91.25f;

public:

	int count;
	Pitch p;
	vec3 x, v, w;

	Ball() {

		x = vec3{ 0.0f, 0.0f, 1.1f * ball_radius };
		v = vec3{ 0.0f, 0.0f, 0.0f };
		w = vec3{ 0.0f, 0.0f, 0.0f };

		count = 0;

	}

	inline sphere collider() {
		return sphere{ x, ball_radius };
	}

	inline void step(float dt) {

		const float R = ball_radius;
		const float G = -650.0f;
		const float A = 0.0003f;
		const float Y = 2.0f;
		const float mu = 0.280f;
		const float C_R = 0.6f;
		const float drag = -0.0305f;
		const float w_max = 6.0f;

		vec3 a = drag * v + vec3{ 0, 0, G };
		vec3 v_pred = v + a * dt;
		vec3 x_pred = x + v_pred * dt;
		vec3 w_pred = w;

		if (p.in_contact_with(sphere{ x_pred, ball_radius })) {

			ray r = p.last_contact_info();

			vec3 n = r.direction;

			vec3 v_perp = dot(v_pred, n) * n;
			vec3 v_para = v_pred - v_perp;
			vec3 v_spin = R * cross(n, w_pred);
			vec3 s = v_para + v_spin;

			float ratio = norm(v_perp) / norm(s);

			vec3 delta_v_perp = -(1.0f + C_R) * v_perp;
			vec3 delta_v_para = -fminf(1.0f, Y * ratio) * mu * s;

			w = w_pred + A * R * cross(delta_v_para, n);
			v = v_pred + delta_v_perp + delta_v_para;

			// TODO
			// TODO
			x = x + 0.5 * (v + v_pred) * dt;
			// TODO
			// TODO

			count++;

		}
		else {

			w = w_pred;
			v = v_pred;
			x = x_pred;

		}

		w *= fminf(1.0, w_max / norm(w));

	}

};
