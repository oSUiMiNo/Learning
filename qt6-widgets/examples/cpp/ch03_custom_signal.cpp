// ch03_custom_signal.py と同じことを C++ で書いたもの。
//
// 自分でシグナルを作るときだけ、C++ には Python にない手続きが要ります。
//   ・クラスに Q_OBJECT マクロを書く
//   ・そのクラスを moc（メタオブジェクトコンパイラ）に通す
//
// moc の実行は CMake の CMAKE_AUTOMOC が自動でやってくれるので、
// 実際に自分で意識するのは Q_OBJECT を書き忘れないことだけです。

#include <QApplication>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include <QWidget>

class NameForm : public QWidget
{
    Q_OBJECT   // ★ これを書き忘れると、シグナルもスロットも動かない

public:
    NameForm()
    {
        setWindowTitle("自作シグナル（C++）");
        resize(380, 170);

        m_edit = new QLineEdit;
        m_edit->setPlaceholderText("名前を入れて［あいさつ］を押す");

        QPushButton *button = new QPushButton("あいさつ");
        m_result = new QLabel("―");

        QVBoxLayout *layout = new QVBoxLayout(this);
        layout->addWidget(m_edit);
        layout->addWidget(button);
        layout->addWidget(m_result);

        connect(button, &QPushButton::clicked, this, &NameForm::emitSubmitted);
        connect(this, &NameForm::submitted, this, &NameForm::greet);
    }

signals:
    // Python: submitted = Signal(str)
    void submitted(const QString &name);

private slots:
    void emitSubmitted()
    {
        emit submitted(m_edit->text());
    }

    // Python: @Slot(str) def greet(self, name)
    void greet(const QString &name)
    {
        m_result->setText(QString("こんにちは、%1 さん！")
                              .arg(name.isEmpty() ? QString("ななし") : name));
    }

private:
    QLineEdit *m_edit;
    QLabel *m_result;
};

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    NameForm form;
    form.show();

    return app.exec();
}

// 1 ファイルにクラスを書いた場合は、moc の生成結果をここで取り込む。
// ヘッダとソースを分けるふつうの書き方なら、この行は要りません。
#include "ch03_custom_signal.moc"
