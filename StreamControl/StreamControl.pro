#-------------------------------------------------
#
# Project created by QtCreator 2012-01-06T07:56:02
#
#-------------------------------------------------

QT       += core gui xml widgets network
CONFIG += c++11

TARGET = StreamControl
TEMPLATE = app

SOURCES += *.cpp \
    $$files(o2/*.cpp) \
    $$files(dialogs/*.cpp) \
    $$files(widgets/*.cpp)

HEADERS  += *.h \
    $$files(o2/*.h) \
    $$files(dialogs/*.h) \
    $$files(widgets/*.h)

FORMS    += \
    configwindow.ui

RESOURCES += \
    resources.qrc

win32:RC_FILE = streamcontrol.rc

OTHER_FILES += \
    o2/o2.pri

macx {
    CONFIG += app_bundle
    QMAKE_MACOSX_DEPLOYMENT_TARGET = 15.0
    QMAKE_TARGET_BUNDLE_PREFIX = org.streamcontrol
}


win32 {
    LIBS += -luser32
}

CONFIG(release, debug|release):DEFINES += QT_NO_DEBUG_OUTPUT
