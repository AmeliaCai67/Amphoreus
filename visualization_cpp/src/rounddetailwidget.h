#ifndef ROUNDDETAILWIDGET_H
#define ROUNDDETAILWIDGET_H

#include <QWidget>
#include <QJsonObject>
#include <QLabel>
#include <QTextBrowser>
#include <QTabWidget>

class RoundDetailWidget : public QWidget
{
    Q_OBJECT
    
public:
    explicit RoundDetailWidget(QWidget *parent = nullptr);
    
    // 设置轮次数据
    void setRoundData(const QJsonObject &roundData);
    
private:
    // 界面组件
    QLabel *titleLabel;
    QTabWidget *tabWidget;
    
    // 各个标签页
    QWidget *summaryTab;
    QWidget *decisionsTab;
    QWidget *robbedTab;
    
    // 内容显示
    QTextBrowser *summaryText;
    QTextBrowser *decisionsText;
    QTextBrowser *robbedText;
    
    // 初始化界面
    void setupUI();
};

#endif // ROUNDDETAILWIDGET_H