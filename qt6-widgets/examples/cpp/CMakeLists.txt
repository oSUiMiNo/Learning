# C++ 版サンプルのビルド設定。
#
#   cmake -S . -B build
#   cmake --build build
#   ./build/ch02_window
#
# Python 版で言えば「pip install pyside6 して python xxx.py する」にあたる部分が、
# C++ ではこのファイルになります。

cmake_minimum_required(VERSION 3.16)
project(qt6_widgets_examples LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Q_OBJECT を書いたクラスを moc に通す作業を自動化する。
# これを ON にしておかないと「vtable への未定義参照」でリンクに失敗する。
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)   # .ui を ui_*.h に変換する（pyside6-uic に相当）
set(CMAKE_AUTORCC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets)

foreach(sample ch02_window ch03_signals ch03_custom_signal)
    add_executable(${sample} ${sample}.cpp)
    target_link_libraries(${sample} PRIVATE Qt6::Widgets)
endforeach()
