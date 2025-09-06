#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QStackedWidget>
#include <QLabel>
#include <QPushButton>
#include <QProgressBar>
#include <QListWidget>
#include <QSplitter>
#include "dataloader.h"
#include "rounddetailwidget.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT
    
public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();
    
private slots:
    void onStartButtonClicked();
    void onDataLoaded();
    void onLoadingProgress(int percentage, const QString &message);
    void onLoadingError(const QString &errorMessage);
    void onRoundSelected(int index);
    
private:
    // 数据加载器
    DataLoader *dataLoader;
    
    // 界面组件
    QStackedWidget *stackedWidget;
    
    // 欢迎页面
    QWidget *welcomePage;
    QLabel *titleLabel;
    QPushButton *startButton;
    
    // 加载页面
    QWidget *loadingPage;
    QProgressBar *progressBar;
    QLabel *loadingLabel;
    
    // 主数据页面
    QWidget *dataPage;
    QSplitter *splitter;
    QListWidget *roundsList;
    RoundDetailWidget *detailWidget;
    
    // 初始化界面
    void setupUI();
    void setupWelcomePage();
    void setupLoadingPage();
    void setupDataPage();
    
    // 更新界面
    void updateRoundsList();
};

#endif // MAINWINDOW_H