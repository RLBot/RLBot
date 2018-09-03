#pragma once

#include "DynamicState.h"

#include "pitch.h"

// This class is responsible for predicting the motion of the ball in Rocket League.
// It deals with gravity, drag, and bounces off of the geometry of the pitch (a.k.a. the field)
// See https://samuelpmish.github.io/notes/RocketLeague/ball_bouncing/ for physics discusison.
class Ball {

	static constexpr float ball_radius = 91.25f;

public:

	int count;
	Pitch p; // The collision model of the pitch being played on

	vec3 x; // location of the ball
	vec3 v; // velocity of the ball
	vec3 w; // angular velocity of the ball

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
		const float G = -650.0f; // Gravity
		const float A = 0.0003f; // Moment of inertia, but without the mass. In other words, the second moment of area of the ball.
		const float Y = 2.0f; // Yield point of the friction model
		const float mu = 0.280f; // Coefficient of friction
		const float C_R = 0.6f; // Coefficient of restitution, i.e. how much energy the ball keeps after a bounce.
		const float drag = -0.0305f; // Drag slows down the ball every frame
		const float w_max = 6.0f; // The game enforces a maximum angular velocity for the ball, so we need to model it.

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

			// The model at https://samuelpmish.github.io/notes/RocketLeague/ball_bouncing/ 
			// describes how to update the velocities of the ball after collision. 
			// The displacement corrections are ambiguous, and this one is arbitrary.
			// There may be room for improvement here.
			x = x + 0.5 * (v + v_pred) * dt;

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
