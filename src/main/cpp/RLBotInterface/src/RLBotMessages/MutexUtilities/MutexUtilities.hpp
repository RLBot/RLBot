#ifndef MUTEXUTILITIES_HPP
#define MUTEXUTILITIES_HPP

namespace MutexUtilities
{
	bool WaitForRLBotExe();
	bool IsBallPredictionServiceRunning();
	bool CreateRLBotExeMutex();
	bool CreateBallPredictionMutex();
	void FreeRLBotExeMutex();
	void FreeBallPredictionMutex();
};

#endif