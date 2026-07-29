// ch03_signals.py と同じ「押した回数を数える」を C++ で書いたもの。
//
// 注目してほしいのは connect の書き方です。
// Python:  button.clicked.connect(on_clicked)
// C++:     QObject::connect(button, &QPushButton::clicked, ラムダ);
//
// つなぐ相手をラムダにすれば、クラスを作らずに済みます。
// （自分でシグナルを作りたくなったら Q_OBJECT が必要になります。次の例を参照）

#include <QApplication>
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>
#include <QWidget>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    QWidget window;
    window.setWindowTitle("シグナルとスロット（C++）");
    window.resize(360, 150);

    QLabel *label = new QLabel("まだ押されていません");
    QPushButton *button = new QPushButton("押してください");

    QVBoxLayout *layout = new QVBoxLayout(&window);
    layout->addWidget(label);
    layout->addWidget(button);

    int count = 0;

    // 第3引数の &window は「受け手」。これを渡しておくと、
    // window が消えたときに接続も自動で切れる（Python では気にしなくてよい部分）。
    QObject::connect(button, &QPushButton::clicked, &window, [&count, label]() {
        count += 1;
        label->setText(QString("%1 回押されました").arg(count));
    });

    window.show();

    return app.exec();
}
