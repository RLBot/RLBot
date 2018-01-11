using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

namespace RLBot_Injector
{
    class Injector
    {
        [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
        private static extern IntPtr OpenProcess(int dwDesiredAccess, bool bInheritHandle, int dwProcessId);

        [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
        private static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

        [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
        private static extern bool VirtualFreeEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, int dwFreeType);

        [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
        private static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, uint lpNumberOfBytesWritten);

        [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
        private static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

        [DllImport("kernel32", CharSet = CharSet.Ansi, EntryPoint = "GetModuleHandleA", ExactSpelling = true, SetLastError = true)]
        private static extern IntPtr GetModuleHandle(string lpModuleName);

        [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
        private static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, int dwCreationFlags, IntPtr lpThreadId);

        [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
        private static extern int WaitForSingleObject(IntPtr hHandle, int dwMilliseconds);

        [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
        private static extern bool CloseHandle(IntPtr hObject);

        [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
        private static extern bool GetExitCodeThread(IntPtr hThread, out uint lpExitCode);

        private const int PROCESS_ALL_ACCESS = 0x1f0fff;
        private const int MEM_COMMIT = 0x1000;
        private const int MEM_RELEASE = 0x8000;
        private const int PAGE_READWRITE = 0x4;
        private const int STILL_ACTIVE = 259;

        private static IntPtr hProcess = IntPtr.Zero;
        private static IntPtr allocAddress = IntPtr.Zero;
        private static IntPtr libThread = IntPtr.Zero;
        private static byte[] dllBytes;

        private static string getLastFunctionError(string functionName, int errorCode = -1)
        {
            return string.Format("{0} failed with error code {1}", functionName, errorCode == -1 ? Marshal.GetLastWin32Error() : errorCode);
        }

        private static void cleanUp()
        {
            if (hProcess != IntPtr.Zero)
            {
                if (allocAddress != IntPtr.Zero)
                {
                    VirtualFreeEx(hProcess, allocAddress, (uint)dllBytes.Length, MEM_RELEASE);
                    allocAddress = IntPtr.Zero;
                }

                CloseHandle(hProcess);
                hProcess = IntPtr.Zero;

                if (dllBytes != null)
                    dllBytes = null;
            }

            if (libThread != IntPtr.Zero)
            {
                CloseHandle(libThread);
                libThread = IntPtr.Zero;
            }
        }

        public static bool Inject(int pID, string dllLocation, ref string error)
        {
            if (!File.Exists(dllLocation))
            {
                error = "The RLBot Dll file could not be found";
                return false;
            }

            hProcess = OpenProcess(PROCESS_ALL_ACCESS, true, pID);

            if (hProcess == IntPtr.Zero)
            {
                error = getLastFunctionError("OpenProcess");
                return false;
            }

            dllBytes = Encoding.Unicode.GetBytes(dllLocation);
            allocAddress = VirtualAllocEx(hProcess, IntPtr.Zero, (uint)dllBytes.Length, MEM_COMMIT, PAGE_READWRITE);

            if (allocAddress == IntPtr.Zero)
            {
                error = getLastFunctionError("VirtualAllocEx");
                cleanUp();
                return false;
            }

            IntPtr kernelMod = GetModuleHandle("kernel32.dll");

            if (kernelMod == IntPtr.Zero)
            {
                error = getLastFunctionError("GetModuleHandle");
                cleanUp();
                return false;
            }

            IntPtr loadLibAddr = GetProcAddress(kernelMod, "LoadLibraryW");

            if (loadLibAddr == IntPtr.Zero)
            {
                error = getLastFunctionError("GetProcAddress");
                cleanUp();
                return false;
            }

            if (WriteProcessMemory(hProcess, allocAddress, dllBytes, (uint)dllBytes.Length, 0) == false)
            {
                error = getLastFunctionError("WriteProcessMemory");
                cleanUp();
                return false;
            }

            libThread = CreateRemoteThread(hProcess, IntPtr.Zero, 0, loadLibAddr, allocAddress, 0, IntPtr.Zero);

            if (libThread == IntPtr.Zero)
            {
                error = getLastFunctionError("CreateRemoteThread");
                cleanUp();
                return false;
            }
            else
            {
                WaitForSingleObject(libThread, 5000);

                uint exitCode;
                
                if (GetExitCodeThread(libThread, out exitCode) == false)
                {
                    error = getLastFunctionError("GetExitCodeThread");
                    cleanUp();
                    return false;
                }

                if (exitCode == STILL_ACTIVE)
                {
                    error = "The remote thread has not terminated within 5 seconds";
                    cleanUp();
                    return false;
                }
                else if (exitCode == 0)
                {
                    error = "The remote LoadLibraryW call has failed";
                    cleanUp();
                    return false;
                }
            }

            cleanUp();
            return true;
        }
    }
}
