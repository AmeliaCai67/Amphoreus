#ifndef REALTIMEDIALOG_H
#define REALTIMEDIALOG_H

#include <QDialog>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QTextEdit>
#include <QPushButton>
#include <QProgressBar>
#include <QTimer>

class RealTimeDialog : public QDialog
{
    Q_OBJECT
    
public:
    explicit RealTimeDialog(QWidget *parent = nullptr);
    
public slots:
    void addLogEntry(const QString &character, const QString &decision, const QString &reason);
    void updateProgress(int percentage, const QString &message);
    void simulationComplete();
    
private slots:
    void onCloseClicked();
    
private:
    QVBoxLayout *mainLayout;
    QLabel *titleLabel;
    QProgressBar *progressBar;
    QLabel *statusLabel;
    QTextEdit *logTextEdit;
    QPushButton *closeButton;
    
    void setupUI();
};

#endif // REALTIMEDIALOG_H
