from ctypes import *
from ctypes.wintypes import *
import os.path, sys, ctypes, ctypes.wintypes

#Process Permission
PROCESS_ALL_ACCESS = 0x1F0FFF # Can maybe look to downgrade to read only access

MAX_PATH = (260)

# const variable
# Establish rights and basic options needed for all process declartion / iteration
TH32CS_SNAPPROCESS = 2
STANDARD_RIGHTS_REQUIRED = 0x000F0000
SYNCHRONIZE = 0x00100000
PROCESS_ALL_ACCESS = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFF)
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPTHREAD = 0x00000004

CreateToolhelp32Snapshot= windll.kernel32.CreateToolhelp32Snapshot
Process32First = windll.kernel32.Process32First
Process32Next = windll.kernel32.Process32Next
Module32First = windll.kernel32.Module32First
Module32Next = windll.kernel32.Module32Next
GetLastError = windll.kernel32.GetLastError
OpenProcess = windll.kernel32.OpenProcess
GetPriorityClass = windll.kernel32.GetPriorityClass
CloseHandle = windll.kernel32.CloseHandle

ReadProcessMemory = windll.kernel32.ReadProcessMemory

class MODULEENTRY32(Structure):
    _fields_ = [( 'dwSize' , DWORD ) , 
                ( 'th32ModuleID' , DWORD ),
                ( 'th32ProcessID' , DWORD ),
                ( 'GlblcntUsage' , DWORD ),
                ( 'ProccntUsage' , DWORD ) ,
                ( 'modBaseAddr' , POINTER(BYTE) ) ,
                ( 'modBaseSize' , DWORD ) , 
                ( 'hModule' , HMODULE ) ,
                ( 'szModule' , c_char * 256 ),
                ( 'szExePath' , c_char * 260 ) ]

class ReadWriteMem:

    # Credit for this function goes to vsantiago113 on github
    # https://github.com/vsantiago113/ReadWriteMemory
    def GetProcessIdByName(self, pName):
        if pName.endswith('.exe'):
            pass
        else:
            pName = pName+'.exe'
            
        ProcessIds, BytesReturned = self.EnumProcesses()
        for index in range(int(BytesReturned / ctypes.sizeof(ctypes.wintypes.DWORD))):
            ProcessId = ProcessIds[index]
            hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, ProcessId)
            if hProcess:
                ImageFileName = (ctypes.c_char*MAX_PATH)()
                if ctypes.windll.psapi.GetProcessImageFileNameA(hProcess, ImageFileName, MAX_PATH)>0:
                    filename = os.path.basename(ImageFileName.value)
                    if filename.decode("utf-8") == pName:
                        return ProcessId
                self.CloseHandle(hProcess)

    def EnumProcesses(self):
        count = 32
        while True:
            ProcessIds = (ctypes.wintypes.DWORD*count)()
            cb = ctypes.sizeof(ProcessIds)
            BytesReturned = ctypes.wintypes.DWORD()
            if ctypes.windll.Psapi.EnumProcesses(ctypes.byref(ProcessIds), cb, ctypes.byref(BytesReturned)):
                if BytesReturned.value<cb:
                    return ProcessIds, BytesReturned.value
                    break
                else:
                    count *= 2
            else:
                return None

    def CloseHandle(self, hProcess):
        ctypes.windll.kernel32.CloseHandle(hProcess);
        return self.GetLastError()

    def GetLastError(self):
        return ctypes.windll.kernel32.GetLastError()

    def getPointer(self, hProcess, lpBaseAddress, offsets):
        pointer = self.ReadProcessMemory2(hProcess, lpBaseAddress)
        if offsets == None:
            return lpBaseAddress
        elif len(offsets) == 1:
            temp = int(str(pointer), 0) + int(str(offsets[0]), 0)
            return temp
        else:
            count = len(offsets)
            for i in offsets:
                count -= 1
                temp = int(str(pointer), 0) + int(str(i), 0)
                pointer = self.ReadProcessMemory2(hProcess, temp)
                if count == 1:
                    break
            return pointer

    def ReadProcessMemory2(self, hProcess, lpBaseAddress):
        try:
            lpBaseAddress = lpBaseAddress
            ReadBuffer = ctypes.c_uint()
            lpBuffer = ctypes.byref(ReadBuffer)
            nSize = ctypes.sizeof(ReadBuffer)
            lpNumberOfBytesRead = ctypes.c_ulong(0)

            ctypes.windll.kernel32.ReadProcessMemory(
                                                    hProcess,
                                                    lpBaseAddress,
                                                    lpBuffer,
                                                    nSize,
                                                    lpNumberOfBytesRead
                                                    )
            return ReadBuffer.value
        except (BufferError, ValueError, TypeError):
            self.CloseHandle(hProcess)
            e = 'Handle Closed, Error', hProcess, self.GetLastError()
            return e

    def WriteProcessMemory(self, hProcess, lpBaseAddress, Value):
        try:
            lpBaseAddress = lpBaseAddress
            Value = Value
            WriteBuffer = ctypes.c_uint(Value)
            lpBuffer = ctypes.byref(WriteBuffer)
            nSize = ctypes.sizeof(WriteBuffer)
            lpNumberOfBytesWritten = ctypes.c_ulong(0)

            ctypes.windll.kernel32.WriteProcessMemory(
                                                    hProcess,
                                                    lpBaseAddress,
                                                    lpBuffer,
                                                    nSize,
                                                    lpNumberOfBytesWritten
                                                    )
        except (BufferError, ValueError, TypeError):
            self.CloseHandle(hProcess)
            e = 'Handle Closed, Error', hProcess, self.GetLastError()
            return e
            
    def GetBaseAddress(self, pid):
        ProcessID=pid
        hModuleSnap = DWORD
        me32 = MODULEENTRY32()
        me32.dwSize = sizeof( MODULEENTRY32 )
        #me32.dwSize = 5000
        hModuleSnap = CreateToolhelp32Snapshot( TH32CS_SNAPMODULE, ProcessID )
        ret = Module32First( hModuleSnap, pointer(me32) )
        if ret == 0 :
            print('ListProcessModules() Error on Module32First[%d]' % GetLastError())
            CloseHandle( hModuleSnap )
        global PROGMainBase
        PROGMainBase=False
        return ctypes.addressof(me32.modBaseAddr.contents) # Get the base address of first module since this is the RocketLeague.exe one
        '''
        while ret :
            #print me32.dwSize
            #print me32.th32ModuleID
            #print me32.th32ProcessID
            #print me32.GlblcntUsage
            #print me32.ProccntUsage
            #print "Base Address:", me32.modBaseAddr
            #print me32.modBaseSize
            #print me32.hModule
            #print me32.szModule
            #print me32.szExePath
            print "oMg:", ctypes.addressof(me32.modBaseAddr.contents)
            ret = Module32Next( hModuleSnap , pointer(me32) )
        CloseHandle( hModuleSnap )
        baddr = ctypes.addressof(me32.modBaseAddr.contents)
        return baddr
        '''
        
    def GetFinalAddress(self, hProcess, baseAddr, offsets):
        buffer = create_string_buffer(4) 
        convert = c_uint32() # 32bit unsigned integer
        bufferSize = 4
        address = baseAddr
        #print "Base:", hex(address)
        
        for i in (range(len(offsets) - 1)):
            offset = offsets[i]
            #print(hex(address), offset) # I need to print here or else it breaks.  This is a python behing the scenes multithreading issue when using c code.
            # Printing here seems to help with the timing to fix the issue in python 2.7. Hey works fine in python 3.5!
            address = address + offset
            ReadProcessMemory(hProcess, address, buffer, bufferSize, None)
            memmove(byref(convert), buffer, 4)
            address = convert.value
        
        return address + offsets[len(offsets) - 1]
        
    def ReadIntFromAddress(self, hProcess, address):
        buffer = create_string_buffer(4) 
        convert = c_int32() # 32bit signed integer
        bufferSize = 4
        
        ReadProcessMemory(hProcess, address, buffer, bufferSize, None)
        memmove(byref(convert), buffer, 4)
        
        return convert.value
        
    def ReadFloatFromAddress(self, hProcess, address):
        buffer = create_string_buffer(4) 
        convert = c_float() # float
        bufferSize = 4 # Let's assume a 4 byte float (might be 8 bytes)
        
        ReadProcessMemory(hProcess, address, buffer, bufferSize, None)
        memmove(byref(convert), buffer, 4)
        
        return convert.value


rwm = ReadWriteMem()
