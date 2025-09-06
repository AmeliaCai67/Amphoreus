#include "realtimedialog.h"
#include <QScrollBar>
#include <QTime>

RealTimeDialog::RealTimeDialog(QWidget *parent)
    : QDialog(parent)
{
    setupUI();
}

void RealTimeDialog::setupUI()
{
    setWindowTitle("永劫回归实时模拟");
    setModal(true);
    setMinimumSize(800, 600);
    
    mainLayout = new QVBoxLayout(this);
    
    // 标题
    titleLabel = new QLabel("永劫回归模拟进行中...");
    QFont titleFont = titleLabel->font();
    titleFont.setPointSize(16);
    titleFont.setBold(true);
    titleLabel->setFont(titleFont);
    titleLabel->setAlignment(Qt::AlignCenter);
    
    // 进度条
    progressBar = new QProgressBar();
    progressBar->setMinimum(0);
    progressBar->setMaximum(100);
    progressBar->setValue(0);
    progressBar->setTextVisible(true);
    
    // 状态标签
    statusLabel = new QLabel("准备开始...");
    statusLabel->setAlignment(Qt::AlignCenter);
    
    // 日志显示区域
    logTextEdit = new QTextEdit();
    logTextEdit->setReadOnly(true);
    logTextEdit->setFont(QFont("Consolas", 10));
    
    // 关闭按钮
    closeButton = new QPushButton("关闭");
    closeButton->setEnabled(false);
    connect(closeButton, &QPushButton::clicked, this, &RealTimeDialog::onCloseClicked);
    
    // 添加到布局
    mainLayout->addWidget(titleLabel);
    mainLayout->addWidget(progressBar);
    mainLayout->addWidget(statusLabel);
    mainLayout->addWidget(logTextEdit);
    mainLayout->addWidget(closeButton);
}

void RealTimeDialog::addLogEntry(const QString &character, const QString &decision, const QString &reason)
{
    QString logEntry = QString("[%1] %2: %3\n原因: %4\n")
                      .arg(QTime::currentTime().toString("hh:mm:ss"))
                      .arg(character)
                      .arg(decision == "1" ? "接受逐火" : "拒绝逐火")
                      .arg(reason);
    
    logTextEdit->append(logEntry);
    
    // 自动滚动到底部
    QScrollBar *scrollBar = logTextEdit->verticalScrollBar();
    scrollBar->setValue(scrollBar->maximum());
}

void RealTimeDialog::updateProgress(int percentage, const QString &message)
{
    progressBar->setValue(percentage);
    statusLabel->setText(message);
}

void RealTimeDialog::simulationComplete()
{
    titleLabel->setText("永劫回归模拟完成！");
    statusLabel->setText("模拟已完成，可以查看详细结果");
    closeButton->setEnabled(true);
}

void RealTimeDialog::onCloseClicked()
{
    accept();
}


