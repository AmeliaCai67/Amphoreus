#include "mainwindow.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFont>
#include <QMessageBox>

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent)
{
    // 创建数据加载器
    dataLoader = new DataLoader(this);
    
    // 连接信号
    connect(dataLoader, &DataLoader::dataLoaded, this, &MainWindow::onDataLoaded);
    connect(dataLoader, &DataLoader::loadingProgress, this, &MainWindow::onLoadingProgress);
    connect(dataLoader, &DataLoader::loadingError, this, &MainWindow::onLoadingError);
    
    // 设置界面
    setupUI();
}

MainWindow::~MainWindow()
{
}

void MainWindow::setupUI()
{
    // 创建堆叠窗口部件
    stackedWidget = new QStackedWidget(this);
    setCentralWidget(stackedWidget);
    
    // 设置各个页面
    setupWelcomePage();
    setupLoadingPage();
    setupDataPage();
    
    // 默认显示欢迎页面
    stackedWidget->setCurrentWidget(welcomePage);
}

void MainWindow::setupWelcomePage()
{
    welcomePage = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(welcomePage);
    
    // 标题
    titleLabel = new QLabel("永劫回归模拟器");
    QFont titleFont = titleLabel->font();
    titleFont.setPointSize(24);
    titleFont.setBold(true);
    titleLabel->setFont(titleFont);
    titleLabel->setAlignment(Qt::AlignCenter);
    
    // 描述
    QLabel *descLabel = new QLabel("基于AI多智能体交互的永劫回归模拟");
    descLabel->setAlignment(Qt::AlignCenter);
    
    // 开始按钮
    startButton = new QPushButton("开始模拟");
    startButton->setMinimumSize(200, 50);
    connect(startButton, &QPushButton::clicked, this, &MainWindow::onStartButtonClicked);
    
    // 添加到布局
    layout->addStretch();
    layout->addWidget(titleLabel);
    layout->addWidget(descLabel);
    layout->addSpacing(50);
    layout->addWidget(startButton, 0, Qt::AlignCenter);
    layout->addStretch();
    
    stackedWidget->addWidget(welcomePage);
}

void MainWindow::setupLoadingPage()
{
    loadingPage = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(loadingPage);
    
    // 加载标签
    loadingLabel = new QLabel("正在加载数据...");
    loadingLabel->setAlignment(Qt::AlignCenter);
    
    // 进度条
    progressBar = new QProgressBar();
    progressBar->setMinimum(0);
    progressBar->setMaximum(100);
    progressBar->setValue(0);
    progressBar->setTextVisible(true);
    
    // 添加到布局
    layout->addStretch();
    layout->addWidget(loadingLabel);
    layout->addWidget(progressBar);
    layout->addStretch();
    
    stackedWidget->addWidget(loadingPage);
}

void MainWindow::setupDataPage()
{
    dataPage = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(dataPage);
    
    // 创建分割器
    splitter = new QSplitter(Qt::Horizontal);
    
    // 轮次列表
    roundsList = new QListWidget();
    roundsList->setMinimumWidth(200);
    connect(roundsList, &QListWidget::currentRowChanged, this, &MainWindow::onRoundSelected);
    
    // 详情窗口
    detailWidget = new RoundDetailWidget();
    
    // 添加到分割器
    splitter->addWidget(roundsList);
    splitter->addWidget(detailWidget);
    splitter->setStretchFactor(0, 1);
    splitter->setStretchFactor(1, 3);
    
    // 添加到布局
    layout->addWidget(splitter);
    
    stackedWidget->addWidget(dataPage);
}

void MainWindow::onStartButtonClicked()
{
    // 切换到加载页面
    stackedWidget->setCurrentWidget(loadingPage);
    
    // 开始加载数据
    dataLoader->loadData(6);
}

void MainWindow::onDataLoaded()
{
    // 更新轮次列表
    updateRoundsList();
    
    // 切换到数据页面
    stackedWidget->setCurrentWidget(dataPage);
    
    // 默认选择第一轮
    if (roundsList->count() > 0) {
        roundsList->setCurrentRow(0);
    }
}

void MainWindow::onLoadingProgress(int percentage, const QString &message)
{
    progressBar->setValue(percentage);
    loadingLabel->setText(message);
}

void MainWindow::onLoadingError(const QString &errorMessage)
{
    QMessageBox::critical(this, "加载错误", errorMessage);
    stackedWidget->setCurrentWidget(welcomePage);
}

void MainWindow::updateRoundsList()
{
    roundsList->clear();
    
    QJsonArray rounds = dataLoader->getRoundsData();
    for (int i = 0; i < rounds.size(); ++i) {
        QJsonObject round = rounds[i].toObject();
        QString roundName = round["round"].toString();
        roundsList->addItem(roundName);
    }
}

void MainWindow::onRoundSelected(int index)
{
    if (index >= 0) {
        QJsonObject roundData = dataLoader->getRoundData(index);
        detailWidget->setRoundData(roundData);
    }
}


