#include "dataloader.h"
#include <QDebug>
#include <QDir>
#include <QRegularExpression>

DataLoader::DataLoader(QObject *parent) : QObject(parent), pythonProcess(nullptr)
{
}

void DataLoader::loadData(int rounds)
{
    // 清除之前的数据
    globalLogs = QJsonObject();
    roundsData = QJsonArray();
    outputBuffer.clear();
    
    // 创建Python进程
    if (pythonProcess) {
        delete pythonProcess;
    }
    pythonProcess = new QProcess(this);
    
    // 连接信号
    connect(pythonProcess, &QProcess::readyReadStandardOutput, this, &DataLoader::onPythonProcessOutput);
    connect(pythonProcess, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished), this, &DataLoader::onPythonProcessFinished);
    connect(pythonProcess, &QProcess::errorOccurred, this, &DataLoader::onPythonProcessError);
    
    // 设置工作目录 - 使用绝对路径
    QString projectRoot = "/Users/kekoukelewenxue/Desktop/jobs/Amphoreus";
    pythonProcess->setWorkingDirectory(projectRoot);
    
    // 准备Python脚本 - 使用绝对路径
    QString scriptPath = projectRoot + "/main/data_export.py";
    QStringList arguments;
    arguments << scriptPath << QString::number(rounds);
    
    emit loadingProgress(0, "启动Python进程...");
    
    // 启动Python进程 - 使用python3而不是python
    pythonProcess->setProcessChannelMode(QProcess::MergedChannels);
    pythonProcess->start("python3", arguments);
    
    // 输出调试信息
    qDebug() << "启动Python进程:" << "python3" << arguments;
    qDebug() << "工作目录:" << projectRoot;
}

void DataLoader::onPythonProcessOutput()
{
    // 读取Python进程的输出
    QByteArray output = pythonProcess->readAllStandardOutput();
    outputBuffer.append(QString::fromUtf8(output));
    
    // 更新进度
    emit loadingProgress(50, "正在处理数据...");
}

void DataLoader::onPythonProcessFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    if (exitCode == 0 && exitStatus == QProcess::NormalExit) {
        // 处理完整的输出
        extractDataFromPythonOutput();
        emit loadingProgress(100, "数据加载完成");
        emit dataLoaded();
    } else {
        qDebug() << "Python进程异常退出，退出码:" << exitCode;
        qDebug() << "Python进程输出:" << outputBuffer;
        qDebug() << "Python进程错误输出:" << pythonProcess->readAllStandardError();
        emit loadingError("Python进程异常退出，退出码: " + QString::number(exitCode));
    }
}

void DataLoader::onPythonProcessError(QProcess::ProcessError error)
{
    QString errorMessage;
    switch (error) {
    case QProcess::FailedToStart:
        errorMessage = "Python进程启动失败 - 可能找不到Python或脚本文件";
        break;
    case QProcess::Crashed:
        errorMessage = "Python进程崩溃";
        break;
    default:
        errorMessage = "Python进程发生未知错误";
    }
    
    // 添加更多调试信息
    errorMessage += "\n" + pythonProcess->errorString();
    qDebug() << "Python进程错误:" << errorMessage;
    
    emit loadingError(errorMessage);
}

void DataLoader::extractDataFromPythonOutput()
{
    // 在输出中查找JSON数据
    QRegularExpression jsonRegex("\\{\\s*\"global_logs\".*\\}");
    QRegularExpressionMatch match = jsonRegex.match(outputBuffer);
    
    if (match.hasMatch()) {
        QString jsonString = match.captured(0);
        if (parseJsonData(jsonString)) {
            return;
        }
    }
    
    // 如果没有找到JSON或解析失败，则手动构建数据
    globalLogs = QJsonObject({
        {"start_message", "=== 开始永劫回归测试 ==="},
        {"end_message", "永劫回归测试完成！"}
    });
    
    // 从输出中提取轮次信息
    QRegularExpression roundRegex("第\\s*(\\d+)\\s*轮永劫回归开始");
    QRegularExpressionMatchIterator i = roundRegex.globalMatch(outputBuffer);
    
    while (i.hasNext()) {
        QRegularExpressionMatch match = i.next();
        int roundNum = match.captured(1).toInt();
        
        QJsonObject roundData;
        roundData["round"] = QString("第%1次永劫回归").arg(roundNum);
        roundData["round_num"] = roundNum;
        
        // 提取统计信息
        QRegularExpression statsRegex(QString("第\\s*%1\\s*轮统计:[\\s\\S]*?逐火者总数:\\s*(\\d+)[\\s\\S]*?主动交出火种:\\s*(\\d+)[\\s\\S]*?被强夺火种:\\s*(\\d+)").arg(roundNum));
        QRegularExpressionMatch statsMatch = statsRegex.match(outputBuffer);
        
        if (statsMatch.hasMatch()) {
            QJsonObject stats;
            stats["逐火者总数"] = statsMatch.captured(1).toInt();
            stats["主动交出火种"] = statsMatch.captured(2).toInt();
            stats["被强夺火种"] = statsMatch.captured(3).toInt();
            stats["不逐火者"] = stats["逐火者总数"].toInt() - stats["主动交出火种"].toInt() - stats["被强夺火种"].toInt();
            
            QJsonObject logs;
            logs["start"] = QString("🔄 第 %1 轮永劫回归开始").arg(roundNum);
            logs["stats"] = stats;
            
            roundData["logs"] = logs;
        }
        
        roundsData.append(roundData);
    }
}

bool DataLoader::parseJsonData(const QString &jsonString)
{
    QJsonParseError error;
    QJsonDocument doc = QJsonDocument::fromJson(jsonString.toUtf8(), &error);
    
    if (error.error != QJsonParseError::NoError) {
        qDebug() << "JSON解析错误:" << error.errorString();
        return false;
    }
    
    if (!doc.isObject()) {
        qDebug() << "JSON不是一个对象";
        return false;
    }
    
    QJsonObject root = doc.object();
    
    if (root.contains("global_logs") && root["global_logs"].isObject()) {
        globalLogs = root["global_logs"].toObject();
    }
    
    if (root.contains("rounds") && root["rounds"].isArray()) {
        roundsData = root["rounds"].toArray();
    }
    
    return true;
}

QJsonArray DataLoader::getRoundsData() const
{
    return roundsData;
}

QJsonObject DataLoader::getGlobalLogs() const
{
    return globalLogs;
}

QJsonObject DataLoader::getRoundData(int roundIndex) const
{
    if (roundIndex >= 0 && roundIndex < roundsData.size()) {
        return roundsData[roundIndex].toObject();
    }
    return QJsonObject();
}