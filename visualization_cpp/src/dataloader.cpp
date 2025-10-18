#include "dataloader.h"
#include <QDebug>
#include <QDir>
#include <QRegularExpression>
#include <QFileInfo> // Added for QFileInfo

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
    
    // 使用启动脚本
    QString scriptPath = projectRoot + "/main/run_export.sh";
    QStringList arguments;
    arguments << QString::number(rounds);
    
    emit loadingProgress(0, "启动Python进程...");
    
    // 输出详细的调试信息
    qDebug() << "=== 开始启动Python进程 ===";
    qDebug() << "脚本路径:" << scriptPath;
    qDebug() << "参数:" << arguments;
    qDebug() << "工作目录:" << projectRoot;
    qDebug() << "bash路径: /bin/bash";
    
    // 检查脚本文件是否存在
    QFileInfo scriptFile(scriptPath);
    if (!scriptFile.exists()) {
        qDebug() << "错误: 脚本文件不存在:" << scriptPath;
        emit loadingError("脚本文件不存在: " + scriptPath);
        return;
    }
    
    if (!scriptFile.isExecutable()) {
        qDebug() << "错误: 脚本文件不可执行:" << scriptPath;
        emit loadingError("脚本文件不可执行: " + scriptPath);
        return;
    }
    
    qDebug() << "脚本文件检查通过，开始启动...";
    
    // 启动脚本
    pythonProcess->setProcessChannelMode(QProcess::MergedChannels);
    pythonProcess->start("/bin/bash", QStringList() << scriptPath << arguments);
    
    // 检查进程是否成功启动
    if (!pythonProcess->waitForStarted(3000)) { // 等待3秒
        qDebug() << "错误: 无法启动进程";
        qDebug() << "错误信息:" << pythonProcess->errorString();
        emit loadingError("无法启动进程: " + pythonProcess->errorString());
        return;
    }
    
    qDebug() << "进程启动成功，PID:" << pythonProcess->processId();
    emit loadingProgress(10, "Python进程已启动，等待输出...");
}

void DataLoader::onPythonProcessOutput()
{
    // 读取Python进程的输出
    QByteArray output = pythonProcess->readAllStandardOutput();
    QString outputStr = QString::fromUtf8(output);
    outputBuffer.append(outputStr);
    
    // 实时解析输出
    parseRealTimeOutput(outputStr);
    
    // 输出调试信息
    qDebug() << "收到Python输出，长度:" << outputStr.length();
    qDebug() << "输出内容:" << outputStr;
    qDebug() << "当前缓冲区总长度:" << outputBuffer.length();
    
    // 更新进度
    emit loadingProgress(50, "正在处理数据...");
}

void DataLoader::parseRealTimeOutput(const QString &newOutput)
{
    // 解析每个角色的决策
    QRegularExpression decisionRegex("([A-Za-z0-9]+):\\s*\\{'decision':\\s*'([01])',\\s*'reason':\\s*'([^']+)'\\}");
    QRegularExpressionMatchIterator i = decisionRegex.globalMatch(newOutput);
    
    while (i.hasNext()) {
        QRegularExpressionMatch match = i.next();
        QString character = match.captured(1);
        QString decision = match.captured(2);
        QString reason = match.captured(3);
        
        qDebug() << "解析到决策:" << character << decision << reason;
        emit realTimeLogEntry(character, decision, reason);
    }
}

void DataLoader::onPythonProcessFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    qDebug() << "=== Python进程结束 ===";
    qDebug() << "退出码:" << exitCode;
    qDebug() << "退出状态:" << (exitStatus == QProcess::NormalExit ? "正常" : "异常");
    qDebug() << "完整输出:" << outputBuffer;
    
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
    qDebug() << "=== Python进程错误 ===";
    qDebug() << "错误类型:" << error;
    qDebug() << "错误信息:" << errorMessage;
    qDebug() << "进程状态:" << pythonProcess->state();
    
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