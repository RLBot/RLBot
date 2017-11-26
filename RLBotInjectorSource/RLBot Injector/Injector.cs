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

        private const int PROCESS_ALL_ACCESS = 0x1f0fff;
        private const int MEM_COMMIT = 0x1000;
        private const int MEM_RELEASE = 0x8000;
        private const int PAGE_READWRITE = 0x4;

        public static bool Inject(int pID, string dllLocation)
        {
            if (!File.Exists(dllLocation))
            {
                return false;
            }

            IntPtr hProcess = OpenProcess(PROCESS_ALL_ACCESS, true, pID);

            if (hProcess == IntPtr.Zero)
            {
                return false;
            }

            byte[] dllBytes = Encoding.ASCII.GetBytes(dllLocation);
            IntPtr allocAddress = VirtualAllocEx(hProcess, IntPtr.Zero, (uint)dllBytes.Length, MEM_COMMIT, PAGE_READWRITE);

            if (allocAddress == IntPtr.Zero)
            {
                return false;
            }

            IntPtr kernelMod = GetModuleHandle("kernel32.dll");
            IntPtr loadLibAddr = GetProcAddress(kernelMod, "LoadLibraryA");

            if (kernelMod == IntPtr.Zero | loadLibAddr == IntPtr.Zero)
            {
                return false;
            }

            WriteProcessMemory(hProcess, allocAddress, dllBytes, (uint)dllBytes.Length, 0);
            IntPtr libThread = CreateRemoteThread(hProcess, IntPtr.Zero, 0, loadLibAddr, allocAddress, 0, IntPtr.Zero);

            if (libThread == IntPtr.Zero)
            {
                return false;
            }
            else
            {
                WaitForSingleObject(libThread, 5000);
                CloseHandle(libThread);
            }

            VirtualFreeEx(hProcess, allocAddress, (uint)dllBytes.Length, MEM_RELEASE);
            CloseHandle(hProcess);

            return true;
        }
    }
}
