#include "Renderer.hpp"

#include "RenderFunctions.hpp"

flatbuffers::Offset<rlbot::flat::Color> buildColor(flatbuffers::FlatBufferBuilder &builder, Color color) {
	return rlbot::flat::CreateColor(builder, color.a, color.r, color.g, color.b);
}

Renderer::Renderer(int index) : flatBufferBuilder(1000)
{
	_index = index;
}

void Renderer::DrawLine3D(Color color, PyStruct::Vector3 start, PyStruct::Vector3 end)
{
	auto coloroffset = buildColor(flatBufferBuilder, color);
	auto _start = rlbot::flat::Vector3{ start.x, start.y, start.z };
	auto _end = rlbot::flat::Vector3{ end.x, end.y, end.z };

	renderMessages.push_back(rlbot::flat::CreateRenderMessage(
		flatBufferBuilder, rlbot::flat::RenderType_DrawLine3D, coloroffset,
		&_start, &_end));
}

void Renderer::DrawPolyLine3D(Color color, PyStruct::Vector3* points, int count)
{
	auto coloroffset = buildColor(flatBufferBuilder, color);

	for (int i = 0; i < count - 1; i++) {
		auto _start = rlbot::flat::Vector3{ points[i].x, points[i].y, points[i].z };
		auto _end = rlbot::flat::Vector3{ points[i+1].x, points[i+1].y, points[i+1].z };

		renderMessages.push_back(rlbot::flat::CreateRenderMessage(
			flatBufferBuilder, rlbot::flat::RenderType_DrawLine3D, coloroffset,
			&_start, &_end));
	}
}

void Renderer::DrawString2D(std::string text, Color color, PyStruct::Vector3 upperLeft, int scaleX, int scaleY)
{
	auto coloroffset = buildColor(flatBufferBuilder, color);

	auto stringoffset = flatBufferBuilder.CreateString(text.c_str());

	auto _upperleft = rlbot::flat::Vector3{ upperLeft.x, upperLeft.y, upperLeft.z };

	renderMessages.push_back(rlbot::flat::CreateRenderMessage(
		flatBufferBuilder, rlbot::flat::RenderType_DrawString2D, coloroffset,
		&_upperleft, 0, scaleX, scaleY, stringoffset));
}

void Renderer::DrawString3D(std::string text, Color color, PyStruct::Vector3 upperLeft, int scaleX, int scaleY)
{
	auto coloroffset = buildColor(flatBufferBuilder, color);

	auto stringoffset = flatBufferBuilder.CreateString(text.c_str());

	auto _upperleft = rlbot::flat::Vector3{ upperLeft.x, upperLeft.y, upperLeft.z };

	renderMessages.push_back(rlbot::flat::CreateRenderMessage(
		flatBufferBuilder, rlbot::flat::RenderType_DrawString3D, coloroffset,
		&_upperleft, 0, scaleX, scaleY, stringoffset));
}

void Renderer::DrawRect2D(Color color, PyStruct::Vector3 upperLeft, int width, int height, bool filled)
{
	auto coloroffset = buildColor(flatBufferBuilder, color);

	auto _upperleft = rlbot::flat::Vector3{ upperLeft.x, upperLeft.y, upperLeft.z };

	renderMessages.push_back(rlbot::flat::CreateRenderMessage(
		flatBufferBuilder, rlbot::flat::RenderType_DrawRect2D, coloroffset,
		&_upperleft, 0, width, height, 0, filled));
}

void Renderer::DrawRect3D(Color color, PyStruct::Vector3 upperLeft, int width, int height, bool filled, bool centered)
{
	auto coloroffset = buildColor(flatBufferBuilder, color);

	auto _upperleft = rlbot::flat::Vector3{ upperLeft.x, upperLeft.y, upperLeft.z };

	auto render_type = centered ? rlbot::flat::RenderType_DrawCenteredRect3D
		: rlbot::flat::RenderType_DrawRect3D;

	renderMessages.push_back(rlbot::flat::CreateRenderMessage(
		flatBufferBuilder, render_type, coloroffset,
		&_upperleft, 0, width, height, 0, filled));
}

void Renderer::Clear()
{
	flatBufferBuilder.Clear();
}

void Renderer::FinishAndSend()
{
	auto messageoffsets = flatBufferBuilder.CreateVector(renderMessages);

	auto groupbuilder = rlbot::flat::RenderGroupBuilder(flatBufferBuilder);
	groupbuilder.add_id(_index);
	groupbuilder.add_renderMessages(messageoffsets);

	auto packet = groupbuilder.Finish();

	flatBufferBuilder.Finish(packet);

	RenderFunctions::RenderGroup(flatBufferBuilder.GetBufferPointer(), flatBufferBuilder.GetSize());
}