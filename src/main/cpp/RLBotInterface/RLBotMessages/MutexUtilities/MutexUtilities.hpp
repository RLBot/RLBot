#ifndef MUTEXUTILITIES_HPP
#define MUTEXUTILITIES_HPP

namespace MutexUtilities
{
	bool WaitForCore();
	bool IsBallPredictionServiceRunning();
	bool CreateCoreMutex();
	bool CreateBallPredictionMutex();
};

#endif