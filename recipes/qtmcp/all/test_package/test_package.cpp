// Checks that the packaged QtMcp libraries link and run: starts a
// streamable HTTP MCP server through the external-backend constructor.

#include <QCoreApplication>
#include <QString>
#include <QTimer>
#include <QtMcpServer/QMcpServer>
#include <QtMcpServer/qmcpserverstreamablehttp.h>

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);
    QCoreApplication::setApplicationName("qtmcp-test-package");

    auto *backend = new QMcpServerStreamableHttp(&app);
    QMcpServer server(backend, &app);

    QObject::connect(&server, &QMcpServer::started, &server, [] {
        qInfo("test_package: QtMcp server started");
        QCoreApplication::exit(0);
    });
    QObject::connect(&server, &QMcpServer::errorOccurred, &server,
                     [](const QString &error) {
        qWarning("test_package: %s", qUtf8Printable(error));
        QCoreApplication::exit(1);
    });
    // Port 0 makes the server listen on an ephemeral port.
    QTimer::singleShot(10000, &app, [] { QCoreApplication::exit(2); });

    server.start(QStringLiteral("127.0.0.1:0"));
    return app.exec();
}
