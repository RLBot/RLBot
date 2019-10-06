#pragma once

#include "Color.hpp"

#include "flatbuffers/flatbuffers.h"
#include "rlbot_generated.h"

#include <PacketStructs/LiveDataPacket.hpp>

#include <vector>

class Renderer {
private:
	int _index;
	std::vector<flatbuffers::Offset<rlbot::flat::RenderMessage>> renderMessages;
	flatbuffers::FlatBufferBuilder flatBufferBuilder;

public:
	Renderer(int index);
	void DrawLine3D(Color color, PyStruct::Vector3 start, PyStruct::Vector3 end);
	void DrawPolyLine3D(Color color, PyStruct::Vector3* points, int count);
	void DrawString2D(std::string text, Color color, PyStruct::Vector3 upperLeft, int scaleX, int scaleY);
	void DrawString3D(std::string text, Color color, PyStruct::Vector3 upperLeft, int scaleX, int scaleY);
	void DrawRect2D(Color color, PyStruct::Vector3 upperLeft, int width, int height, bool filled);
	void DrawRect3D(Color color, PyStruct::Vector3 upperLeft, int width, int height, bool filled, bool centered = false);
	void Clear();
	void FinishAndSend();
};