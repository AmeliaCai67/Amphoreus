cmake_minimum_required(VERSION 3.5)

project(AmphoreusCppViz VERSION 0.1 LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找Qt包
find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets)

# 添加包含路径
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)

# 源文件
set(PROJECT_SOURCES
    src/main.cpp
    src/mainwindow.cpp
    src/mainwindow.h
    src/dataloader.cpp
    src/dataloader.h
    src/rounddetailwidget.cpp
    src/rounddetailwidget.h
    src/realtimedialog.cpp
    src/realtimedialog.h
)

# 创建可执行文件
if(${QT_VERSION_MAJOR} GREATER_EQUAL 6)
    qt_add_executable(AmphoreusCppViz
        MANUAL_FINALIZATION
        ${PROJECT_SOURCES}
    )
else()
    add_executable(AmphoreusCppViz
        ${PROJECT_SOURCES}
    )
endif()

# 链接Qt库
target_link_libraries(AmphoreusCppViz PRIVATE Qt${QT_VERSION_MAJOR}::Widgets)

# 设置目标属性
set_target_properties(AmphoreusCppViz PROPERTIES
    MACOSX_BUNDLE_GUI_IDENTIFIER my.example.com
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

if(QT_VERSION_MAJOR EQUAL 6)
    qt_finalize_executable(AmphoreusCppViz)
endif()