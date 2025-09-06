#include "mainwindow.h"

#include <QApplication>
#include <QFontDatabase>
#include <QDir>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    
    // 设置应用程序名称
    app.setApplicationName("永劫回归模拟器");
    
    // 使用系统字体
    QFont font("PingFang SC", 10); // macOS 自带中文字体
    app.setFont(font);
    
    MainWindow mainWindow;
    mainWindow.setWindowTitle("永劫回归模拟器");
    mainWindow.resize(1024, 768);
    mainWindow.show();
    
    return app.exec();
}
