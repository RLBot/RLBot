using System;
using System.Runtime.InteropServices;

namespace RLBotDotNet.Utils
{
    public class TimerResolutionInterop
    {
        [DllImport("ntdll.dll", SetLastError = true)]
        static extern int NtSetTimerResolution(int DesiredResolution, bool SetResolution, out int CurrentResolution);
        public static void SetResolution(int desiredResolution) => NtSetTimerResolution(desiredResolution, true, out _);

        [DllImport("ntdll.dll", SetLastError = true)]
        static extern int NtQueryTimerResolution(out int MinimumResolution, out int MaximumResolution, out int CurrentResolution);
        public static void Query(out int minResolution, out int maxResolution, out int currResolution) => NtQueryTimerResolution(out minResolution, out maxResolution, out currResolution);
        public static TimeSpan MinimumResolution { get { NtQueryTimerResolution(out int minRes, out _, out _); return new TimeSpan(minRes); } }
        public static TimeSpan MaximumResolution { get { NtQueryTimerResolution(out _, out int maxRes, out _); return new TimeSpan(maxRes); } }
        public static TimeSpan CurrentResolution { get { NtQueryTimerResolution(out _, out _, out int currRes); return new TimeSpan(currRes); } }
    }
}