#include "apppaths.h"
#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QStandardPaths>

QString prepareApplicationData()
{
#ifdef Q_OS_MAC
    // Anchor legacy relative settings/output paths independently of Finder's cwd.
    QCoreApplication::setApplicationName("StreamControl");
    const QString dataPath = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation);
    if (dataPath.isEmpty() || !QDir().mkpath(dataPath) || !QDir::setCurrent(dataPath))
        return QStringLiteral("Cannot open the application data folder.");

    if (!QFile::exists("layout.xml")) {
        if (!QFile::copy(":/StreamControl/layout.xml", "layout.xml") ||
            !QFile::setPermissions("layout.xml", QFile::ReadOwner | QFile::WriteOwner))
            return QStringLiteral("Cannot create the default layout.");
    }
#endif
    return QString();
}
