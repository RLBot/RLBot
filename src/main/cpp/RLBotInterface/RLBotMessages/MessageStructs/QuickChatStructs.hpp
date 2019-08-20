#pragma once

#define MAX_QUICKCHAT_QUEUE_SIZE 50

struct QuickChatMessage {
	int QuickChatSelection;
	int PlayerIndex;
	bool TeamOnly;
	int TeamIndex;
	int MessageIndex;
	float TimeStamp;
};

struct QuickChatQueue {
	int Count;
	QuickChatMessage Messages[MAX_QUICKCHAT_QUEUE_SIZE];
};