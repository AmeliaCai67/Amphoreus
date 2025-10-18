#ifndef DATALOADER_H
#define DATALOADER_H

#include <QObject>
#include <QProcess>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QMap>
#include <QString>
#include <QStringList>

class DataLoader : public QObject
{
    Q_OBJECT
    
public:
    explicit DataLoader(QObject *parent = nullptr);
    
    // 加载数据
    void loadData(int rounds = 6);
    
    // 获取轮次数据
    QJsonArray getRoundsData() const;
    
    // 获取全局日志
    QJsonObject getGlobalLogs() const;
    
    // 获取特定轮次的数据
    QJsonObject getRoundData(int roundIndex) const;
    
signals:
    void dataLoaded();
    void loadingProgress(int percentage, const QString &message);
    void loadingError(const QString &errorMessage);
    void realTimeLogEntry(const QString &character, const QString &decision, const QString &reason); // 新增
    
private slots:
    void onPythonProcessFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void onPythonProcessError(QProcess::ProcessError error);
    void onPythonProcessOutput();
    
private:
    QProcess *pythonProcess;
    QJsonDocument jsonData;
    QJsonObject globalLogs;
    QJsonArray roundsData;
    QString outputBuffer;
    
    // 解析Python输出的JSON数据
    bool parseJsonData(const QString &jsonString);
    
    // 从Python脚本输出中提取数据
    void extractDataFromPythonOutput();
    
    // 实时解析Python输出
    void parseRealTimeOutput(const QString &newOutput);
};

#endif // DATALOADER_H