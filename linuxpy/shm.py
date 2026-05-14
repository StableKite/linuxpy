"""System V shared memory"""

from enum import IntFlag

from linuxpy import ctypes

HUGETLB_FLAG_ENCODE_SHIFT = 26
HUGETLB_FLAG_ENCODE_MASK = 0x3F

HUGETLB_FLAG_ENCODE_16KB = 14 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_64KB = 16 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_512KB = 19 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_1MB = 20 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_2MB = 21 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_8MB = 23 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_16MB = 24 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_32MB = 25 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_256MB = 28 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_512MB = 29 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_1GB = 30 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_2GB = 31 << HUGETLB_FLAG_ENCODE_SHIFT
HUGETLB_FLAG_ENCODE_16GB = 34 << HUGETLB_FLAG_ENCODE_SHIFT

IPC_PRIVATE = 0

# shmget() shmflg values.
SHM_W = 128
SHM_R = 256
IPC_CREAT = 512  #  create if key is nonexistent */
IPC_EXCL = 1024  #  fail if key exists */
SHM_HUGETLB = 2048
SHM_NORESERVE = 4096

SHM_HUGE_64KB = HUGETLB_FLAG_ENCODE_64KB
SHM_HUGE_512KB = HUGETLB_FLAG_ENCODE_512KB
SHM_HUGE_1MB = HUGETLB_FLAG_ENCODE_1MB
SHM_HUGE_2MB = HUGETLB_FLAG_ENCODE_2MB
SHM_HUGE_8MB = HUGETLB_FLAG_ENCODE_8MB
SHM_HUGE_16MB = HUGETLB_FLAG_ENCODE_16MB
SHM_HUGE_32MB = HUGETLB_FLAG_ENCODE_32MB
SHM_HUGE_256MB = HUGETLB_FLAG_ENCODE_256MB
SHM_HUGE_512MB = HUGETLB_FLAG_ENCODE_512MB
SHM_HUGE_1GB = HUGETLB_FLAG_ENCODE_1GB
SHM_HUGE_2GB = HUGETLB_FLAG_ENCODE_2GB
SHM_HUGE_16GB = HUGETLB_FLAG_ENCODE_16GB

# shmat() shmflg values
SHM_RDONLY = 0o10000  # read-only access */
SHM_RND = 0o20000  # round attach address to SHMLBA boundary */
SHM_REMAP = 0o40000  # take-over region on attach */
SHM_EXEC = 0o100000  # execution access */


class GetFlags(IntFlag):
    Write = SHM_W
    Read = SHM_R
    Create = IPC_CREAT
    Exclusive = IPC_EXCL
    HugeTLB = SHM_HUGETLB
    NoReserve = SHM_NORESERVE
    Huge2MB = SHM_HUGE_2MB
    Huge1GB = SHM_HUGE_1GB


class AtFlags(IntFlag):
    ReadOnly = SHM_RDONLY
    Round = SHM_RND
    Remap = SHM_REMAP
    Exec = SHM_EXEC


shmget = ctypes.c.shmget
shmget.argtypes = [ctypes.cint, ctypes.csize, ctypes.cint]
shmget.restype = ctypes.cint

shmat = ctypes.c.shmat
shmat.argtypes = [ctypes.cint, ctypes.cvoidp, ctypes.cint]
shmat.restype = ctypes.cvoidp

shmdt = ctypes.c.shmdt
shmdt.argtypes = [ctypes.cvoidp]
shmdt.restype = ctypes.cint


class SharedMemory:
    def __init__(self, id, ptr, size):
        self.id = id
        self.ptr = ptr
        self.size = size
        self.mem = ctypes.memoryview_at(ptr, size)

    def close(self):
        if shmdt(self.ptr) != 0:
            raise RuntimeError("Failed to detach ")


def create(size: int, flags=None) -> SharedMemory:
    if flags is None:
        flags = GetFlags.Read | GetFlags.Write
    flags |= GetFlags.Create
    id = shmget(IPC_PRIVATE, size, flags)
    if (ptr := shmat(id, 0, 0)) == -1:
        raise RuntimeError("Failed to attach shared memory")
    return SharedMemory(id, ptr, size)


def get(id: int, size: int) -> SharedMemory:
    if (ptr := shmat(id, 0, 0)) == -1:
        raise RuntimeError("Failed to attach shared memory")
    return SharedMemory(id, ptr, size)
