# Copyright 2018 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# cmake build file for C++ helloworld example.
# Assumes protobuf and gRPC have been installed using cmake.
# See cmake_externalproject/CMakeLists.txt for all-in-one cmake build
# that automatically builds all the dependencies before building helloworld.

#cmake_minimum_required(VERSION 3.19.6)
cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

project(RL_GRPC C CXX)

set(CMAKE_CXX_EXTENSIONS OFF)

set(protobuf_MODULE_COMPATIBLE TRUE)
find_package(Protobuf CONFIG REQUIRED)
message(STATUS "Using protobuf ${Protobuf_VERSION}")

set(_PROTOBUF_LIBPROTOBUF protobuf::libprotobuf)
set(_REFLECTION gRPC::grpc++_reflection)
if(CMAKE_CROSSCOMPILING)
  find_program(_PROTOBUF_PROTOC protoc)
else()
  set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc>)
endif()

# Find gRPC installation
# Looks for gRPCConfig.cmake file installed by gRPC's cmake installation.
find_package(gRPC CONFIG REQUIRED)
message(STATUS "Using gRPC ${gRPC_VERSION}")

set(_GRPC_GRPCPP gRPC::grpc++)
if(CMAKE_CROSSCOMPILING)
  find_program(_GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin)
else()
  set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:gRPC::grpc_cpp_plugin>)
endif()

#set(gRPC_INCLUDE_DIR "/home/cmd/cpp_libs/grpc/include/")
#include_directories("${gRPC_INCLUDE_DIR}")

# Proto file
get_filename_component(hw_proto "protos/observation_action.proto" ABSOLUTE)
get_filename_component(hw_proto_path "${hw_proto}" PATH)

# Generated sources
set(hw_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/observation_action.pb.cc")
set(hw_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/observation_action.pb.h")
set(hw_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/observation_action.grpc.pb.cc")
set(hw_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/observation_action.grpc.pb.h")
add_custom_command(
      OUTPUT "${hw_proto_srcs}" "${hw_proto_hdrs}" "${hw_grpc_srcs}" "${hw_grpc_hdrs}"
      COMMAND ${_PROTOBUF_PROTOC}
      ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
        --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
        -I "${hw_proto_path}"
        --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
        "${hw_proto}"
      DEPENDS "${hw_proto}")

# Include generated *.pb.h files
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

# include(../cmake/common.cmake)
#set(Torch_DIR "/home/cmd/Documents/cpp_libs/libtorch/share/cmake/Torch")
set(Boost_INCLUDE_DIR "/home/cmd/Documents/cpp_libs/boost_1_78_0")

#find_package(Torch REQUIRED)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

find_package(Boost REQUIRED)

# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

include_directories( "${Boost_INCLUDE_DIR}" )
#link_directories( "${Boost_LIBRARY_DIRS}" )

#set(TORCH_INCLUDE_DIR "/home/cmd/cpp_libs/tch/libtorch/include")
#include_directories( "${TORCH_INCLUDE_DIR}" )
#link_directories( "${TORCH_LIBRARY_DIRS}" )

# hw_grpc_proto
add_library(hw_grpc_proto
  ${hw_grpc_srcs}
  ${hw_grpc_hdrs}
  ${hw_proto_srcs}
  ${hw_proto_hdrs})

target_link_libraries(hw_grpc_proto
  ${_REFLECTION}
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

#add_library(godotSharedInterfaceTorch
#  "godotInterfaceTorch/cGodotSharedInterface.cpp"
#  "godotInterfaceTorch/cGodotSharedInterface.h") 
  
#target_link_libraries(godotSharedInterfaceTorch 
#  "${Boost_LIBRARIES}" "${TORCH_LIBRARIES}" -lrt) ## on lrt https://github.com/boostorg/interprocess/issues/42

#add_executable(rl_agent_trainer "trainer/rl_agent_trainer.cc" "godotInterfaceTorch/cGodotSharedInterface.cpp")
#target_link_libraries(rl_agent_trainer "${Boost_LIBRARIES}" "${TORCH_LIBRARIES}")
#target_include_directories(rl_agent_trainer PRIVATE "/home/ccmd/Documents/cpp_libs/libtorch/include")

add_library(godotSharedInterface
  "godotInterface/cGodotSharedInterface.cpp"
  "godotInterface/cGodotSharedInterface.h") 
  
target_link_libraries(godotSharedInterface
    #"${TORCH_LIBRARIES}" 
    "${Boost_LIBRARIES}"
    -lpthread
    -lrt) ## https://github.com/boostorg/interprocess/issues/42

#set_property(TARGET rl_agent_trainer PROPERTY CXX_STANDARD 14)

# Targets greeter_[async_](client|server)
add_executable(rlc_server "server/rlc_server.cc" )
target_link_libraries(rlc_server 
    hw_grpc_proto
    ${_REFLECTION}
    ${_GRPC_GRPCPP}
    ${_PROTOBUF_LIBPROTOBUF}
    godotSharedInterface)


