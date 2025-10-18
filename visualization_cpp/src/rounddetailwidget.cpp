#include "rounddetailwidget.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFont>
#include <QJsonArray>

RoundDetailWidget::RoundDetailWidget(QWidget *parent) : QWidget(parent)
{
    setupUI();
}

void RoundDetailWidget::setupUI()
{
    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    
    // 标题
    titleLabel = new QLabel("轮次详情");
    QFont titleFont = titleLabel->font();
    titleFont.setPointSize(16);
    titleFont.setBold(true);
    titleLabel->setFont(titleFont);
    
    // 标签页
    tabWidget = new QTabWidget();
    
    // 摘要标签页
    summaryTab = new QWidget();
    QVBoxLayout *summaryLayout = new QVBoxLayout(summaryTab);
    summaryText = new QTextBrowser();
    summaryLayout->addWidget(summaryText);
    tabWidget->addTab(summaryTab, "摘要");
    
    // 决策标签页
    decisionsTab = new QWidget();
    QVBoxLayout *decisionsLayout = new QVBoxLayout(decisionsTab);
    decisionsText = new QTextBrowser();
    decisionsLayout->addWidget(decisionsText);
    tabWidget->addTab(decisionsTab, "角色决策");
    
    // 被强夺标签页
    robbedTab = new QWidget();
    QVBoxLayout *robbedLayout = new QVBoxLayout(robbedTab);
    robbedText = new QTextBrowser();
    robbedLayout->addWidget(robbedText);
    tabWidget->addTab(robbedTab, "被强夺角色");
    
    // 添加到主布局
    mainLayout->addWidget(titleLabel);
    mainLayout->addWidget(tabWidget);
}

void RoundDetailWidget::setRoundData(const QJsonObject &roundData)
{
    // 更新标题
    QString roundName = roundData["round"].toString();
    titleLabel->setText(roundName + " 详情");
    
    // 更新摘要
    QString summaryContent;
    if (roundData.contains("logs") && roundData["logs"].isObject()) {
        QJsonObject logs = roundData["logs"].toObject();
        
        // 开始信息
        if (logs.contains("start")) {
            summaryContent += logs["start"].toString() + "\n\n";
        }
        
        // 统计信息
        if (logs.contains("stats") && logs["stats"].isObject()) {
            QJsonObject stats = logs["stats"].toObject();
            summaryContent += "<b>统计信息:</b>\n";
            
            QStringList statKeys = stats.keys();
            for (const QString &key : statKeys) {
                summaryContent += key + ": " + QString::number(stats[key].toInt()) + "\n";
            }
        }
    }
    summaryText->setHtml(summaryContent);
    
    // 更新决策
    QString decisionsContent = "<b>角色决策结果:</b>\n\n";
    if (roundData.contains("decisions") && roundData["decisions"].isObject()) {
        QJsonObject decisions = roundData["decisions"].toObject();
        QStringList characterNames = decisions.keys();
        
        for (const QString &name : characterNames) {
            QString decision = decisions[name].toString();
            decisionsContent += "<b>" + name + ":</b> " + decision + "\n\n";
        }
    }
    decisionsText->setHtml(decisionsContent);
    
    // 更新被强夺角色
    QString robbedContent = "<b>被强夺火种的角色:</b>\n\n";
    if (roundData.contains("robbed") && roundData["robbed"].isArray()) {
        QJsonArray robbed = roundData["robbed"].toArray();
        
        if (robbed.isEmpty()) {
            robbedContent += "无\n";
        } else {
            for (int i = 0; i < robbed.size(); ++i) {
                robbedContent += robbed[i].toString() + "\n";
            }
        }
    }
    robbedText->setHtml(robbedContent);
}