#include <QtTest>
#include <QApplication>
#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLineEdit>
#include <QSpinBox>
#include <QStandardPaths>
#include <QTemporaryDir>
#include "mainwindow.h"
#include "apppaths.h"

class MacTests : public QObject {
    Q_OBJECT
private slots:
    void settingsAndOutputRoundTrip() {
        QTemporaryDir temp;
        QVERIFY(temp.isValid());
        const QString original = QDir::currentPath();
        QVERIFY(QDir::setCurrent(temp.path()));
        QVERIFY(QFile::copy(":/StreamControl/layout.xml", "layout.xml"));
        QFile settings("settings.xml");
        QVERIFY(settings.open(QIODevice::WriteOnly));
        settings.write("<settings><layoutPath>layout.xml</layoutPath><outputPath>./</outputPath><format>3</format></settings>");
        settings.close();
        const QString name = QString::fromUtf8("Player & <one> \xE6\x97\xA5");
        {
            MainWindow window;
            auto player = window.findChild<QLineEdit*>("pName1");
            auto score = window.findChild<QSpinBox*>("pScore1");
            QVERIFY(player);
            QVERIFY(score);
            player->setText(name);
            score->setValue(7);
            window.saveData();
            window.saveSettings();
            QFile json("streamcontrol.json");
            QVERIFY(json.open(QIODevice::ReadOnly));
            const auto data = QJsonDocument::fromJson(json.readAll()).object();
            QCOMPARE(data.value("pName1").toString(), name);
            QCOMPARE(data.value("pScore1").toString(), QString("7"));
            QFile xml("streamcontrol.xml");
            QVERIFY(xml.open(QIODevice::ReadOnly));
            QDomDocument doc;
            QVERIFY(doc.setContent(&xml));
            QCOMPARE(doc.documentElement().firstChildElement("pName1").text(), name);
            QCOMPARE(doc.documentElement().firstChildElement("pScore1").text(), QString("7"));
        }
        {
            MainWindow reopened;
            QCOMPARE(reopened.findChild<QLineEdit*>("pName1")->text(), name);
            QCOMPARE(reopened.findChild<QSpinBox*>("pScore1")->value(), 7);
        }
        QVERIFY(QDir::setCurrent(original));
    }

    void finderStartupUsesWritableData() {
#ifdef Q_OS_MAC
        QStandardPaths::setTestModeEnabled(true);
        // Isolate test data from both real user data and other test runs.
        QCoreApplication::setOrganizationName("StreamControlTests-" + QString::number(QCoreApplication::applicationPid()));
        const QString original = QDir::currentPath();
        QVERIFY(QDir::setCurrent("/"));
        QCOMPARE(prepareApplicationData(), QString());
        const QString path = QDir::currentPath();
        QCOMPARE(path, QStandardPaths::writableLocation(QStandardPaths::AppDataLocation));
        QFile layout("layout.xml");
        QVERIFY(layout.open(QIODevice::WriteOnly | QIODevice::Append));
        layout.write("\n<!-- custom layout retained -->\n");
        layout.close();
        QVERIFY(QDir::setCurrent("/"));
        QCOMPARE(prepareApplicationData(), QString());
        QVERIFY(layout.open(QIODevice::ReadOnly));
        QVERIFY(layout.readAll().contains("custom layout retained"));
        layout.close();
        QVERIFY(QDir::setCurrent(original));
        QVERIFY(QDir(path).removeRecursively());
#else
        QSKIP("macOS-only startup behavior");
#endif
    }
};

QTEST_MAIN(MacTests)
#include "macos-tests.moc"
