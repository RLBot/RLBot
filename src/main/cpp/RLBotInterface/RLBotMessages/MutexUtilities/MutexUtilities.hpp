#ifndef MUTEXUTILITIES_HPP
#define MUTEXUTILITIES_HPP

namespace MutexUtilities
{
	bool WaitForMutexes();
	bool CreateCoreMutex();
	bool CreateBallPredictionMutex();
};

#endif