cmake_minimum_required(VERSION 3.1)
project( MechaVision )
#include(/usr/local/lib/cmake)
FIND_FILE(POINTGREY libflycapture.so.2 libflycapture.so /usr/include)
FIND_FILE(ZMQLIB libzmq.so /usr/lib/aarch64-linux-gnu/)
FIND_FILE(JSONCPP libjsoncpp.a /usr/lib/aarch64-linux-gnu/)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

#=============== Find Packages 
add_definitions(-DCUDA_USE_STATIC_CUDA_RUNTIME=OFF -DUSE_OPENCV=1 -DCUDA_API_PER_THREAD_DEFAULT_STREAM -DUSE_GUI=1 -DUSE_GLFW=1 -DUSE_GLES=1 -DUSE_GSTREAMER=1 -DUSE_NVGSTCAMERA=1 -DUSE_GSTREAMER_OMX=1 -O3 -DNDEBUG)
#find_package(VisionWorks REQUIRED)
#find_package(VisionWorks-NVXIO REQUIRED)
find_package(OpenCV COMPONENTS core imgproc video highgui calib3d REQUIRED)

add_definitions(-DCUDA_USE_STATIC_CUDA_RUNTIME=OFF)

include_directories("${OpenCV_INCLUDE_DIRS}")
#include_directories("${VisionWorks_INCLUDE_DIRS}")
#include_directories("${VisionWorks-NVXIO_INCLUDE_DIRS}")
include_directories(include)
include_directories("/usr/local/include")
include_directories("/usr/include")
include_directories("/usr/include/jsoncpp")
include_directories(${DARKNET_WRAPPER_INCLUDE_DIR})
include_directories(${YOLO_INCLUDE_DIR})
include_directories(${CUDA_INCLUDE_DIRS})
file(GLOB SOURCES "*.cpp" "src/*.cpp")

add_executable(MechaVision ${SOURCES})
target_link_libraries(MechaVision ${POINTGREY} ${ZMQLIB} ${JSONCPP} ${Boost_LIBRARIES} ${OpenCV_LIBRARIES}  ${DARKNET_CORE_LIBNAME} ${DARKNET_CUDA_LIBNAME} ${DARKNET_WRAPPER_LIBRARIES} ${CUDA_LIBRARIES} ${CUDA_CUBLAS_LIBRARIES} ${CUDA_curand_LIBRARY} ${CMAKE_THREAD_LIBS_INIT} )

