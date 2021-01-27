cmake_minimum_required(VERSION 3.10)
project(RLBot LANGUAGES CXX)

# find boost
add_definitions(-DBOOST_ALL_NO_LIB)
add_definitions(-DBOOST_ERROR_CODE_HEADER_ONLY)

set(Boost_USE_STATIC_LIBS        ON)
set(Boost_USE_MULTITHREADED      ON)
set(Boost_USE_STATIC_RUNTIME    OFF)

find_package(Boost COMPONENTS date_time system REQUIRED)

# Include directories for flatbuffers library and generated files
set(rlbot_generated ${CMAKE_CURRENT_SOURCE_DIR}/../../../generated/cpp/flatbuffers)
set(flatbuffers ${CMAKE_CURRENT_SOURCE_DIR}/lib/flatbuffers/include)


# ---- RLBotMessage ----
file(GLOB_RECURSE rlbotmessages_sources  ${CMAKE_CURRENT_SOURCE_DIR}/src/RLBotMessages/*.?pp)

add_library(RLBotMessages STATIC ${rlbotmessages_sources})
target_include_directories(RLBotMessages PRIVATE
    src/RLBotMessages
    ${rlbot_generated}
    ${flatbuffers}
    ${Boost_INCLUDE_DIRS})
target_link_libraries(RLBotMessages ${Boost_DATETIME_LIBRARY} ${Boost_SYSTEM_LIBRARY})
target_compile_features(RLBotMessages PRIVATE cxx_std_17)

if (UNIX)
    set_target_properties(RLBotMessages PROPERTIES COMPILE_FLAGS -fPIC)
endif (UNIX)

# ---- RLBotInterface ----
file(GLOB_RECURSE rlbotinterface_sources  ${CMAKE_CURRENT_SOURCE_DIR}/src/RLBotInterface/*)

add_library(RLBotInterface SHARED ${rlbotinterface_sources})
target_include_directories(RLBotInterface PRIVATE
    src/RLBotInterface
    src/RLBotMessages
    ${rlbot_generated}
    ${flatbuffers}
    ${Boost_INCLUDE_DIRS})

if (UNIX)
    if (APPLE)
        target_link_libraries(RLBotInterface RLBotMessages ${Boost_DATETIME_LIBRARY} ${Boost_SYSTEM_LIBRARY})
    else (APPLE)
        target_link_libraries(RLBotInterface RLBotMessages ${Boost_LIBRARIES} rt)
    endif (APPLE)
    set_target_properties(RLBotInterface PROPERTIES COMPILE_FLAGS -fPIC)
else (UNIX)
    target_link_libraries(RLBotInterface RLBotMessages ${Boost_LIBRARIES} winmm.lib)
endif (UNIX)

target_compile_features(RLBotInterface PRIVATE cxx_std_17)

# ---- RLBot ----
# Ignore this whole section if the folder is missing, because that will be the case in the open source version of the repo.
if(IS_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/RLBot/") 

file(GLOB_RECURSE rlbot_sources  ${CMAKE_CURRENT_SOURCE_DIR}/src/RLBot/*.c* ${CMAKE_CURRENT_SOURCE_DIR}/src/RLBot/*.h*)

add_executable(RLBot ${rlbot_sources})
target_include_directories(RLBot PRIVATE
    src/RLBot
    src/RLBotMessages
    ${rlbot_generated}
    ${flatbuffers}
    ${Boost_INCLUDE_DIRS})

foreach(_source IN ITEMS ${rlbot_sources})
    get_filename_component(_source_path "${_source}" PATH)
    string(REPLACE "${CMAKE_SOURCE_DIR}" "" _group_path "${_source_path}")
    string(REPLACE "/" "\\" _group_path "${_group_path}")
    source_group("${_group_path}" FILES "${_source}")
endforeach()

if (UNIX)
    if (APPLE)
        add_custom_command(TARGET RLBotMessages
                           PRE_BUILD
                           COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/src/RLBotMessages/generate-flatbuffers-mac.sh )
        add_custom_command(TARGET RLBotMessages
                           PRE_BUILD
                           COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/src/RLBot/generate-flatbuffers-mac.sh )
        target_link_libraries(RLBot RLBotMessages ${Boost_DATETIME_LIBRARY} ${Boost_SYSTEM_LIBRARY} pthread)
    else (APPLE)
        add_custom_command(TARGET RLBotMessages
                           PRE_BUILD
                           COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/src/RLBotMessages/generate-flatbuffers.sh )
        add_custom_command(TARGET RLBotMessages
                           PRE_BUILD
                           COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/src/RLBot/generate-flatbuffers.sh )
        target_link_libraries(RLBot RLBotMessages ${Boost_LIBRARIES} ${CMAKE_DL_LIBS} pthread rt)
    endif (APPLE)
    set_target_properties(RLBotInterface PROPERTIES COMPILE_FLAGS -fPIC)

else (UNIX)
    # Set target version to windows xp. This should in theory work as a minimum supported platform.
    target_compile_definitions(RLBot PRIVATE _WIN32_WINNT=0x501)

    add_custom_command(TARGET RLBotMessages
                       PRE_BUILD
                       COMMAND ${CMAKE_CURRENT_SOURCE_DIR}\\src\\RLBotMessages\\generate-flatbuffers.bat )

    add_custom_command(TARGET RLBotMessages
                       PRE_BUILD
                       COMMAND ${CMAKE_CURRENT_SOURCE_DIR}\\src\\RLBot\\generate-flatbuffers.bat )

    target_link_libraries(RLBot RLBotMessages ${Boost_LIBRARIES})
endif (UNIX)

target_compile_features(RLBot PRIVATE cxx_std_17)

endif()
